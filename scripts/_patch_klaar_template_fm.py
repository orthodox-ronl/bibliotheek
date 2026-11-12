"""Zet template: (en eventueel template_opgegeven:) op _klaar_voor_acceptatie MVSA's.

Controleert daarna her-map tegen de formule. Wijzigt alleen frontmatter.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
KLAAR = REPO / "content-source" / "input" / "_klaar_voor_acceptatie"
sys.path.insert(0, str(REPO.parent / "VSA-tooling" / "src"))

from vsa.template_instance import TemplateInstanceError, map_vsa_to_template
from vsa.template_library import (
    clear_alias_cache,
    infer_template_id,
    load_resolved_template,
)
from vsa.vsa_stanzas import ensure_stanza_stars


def _split_fm(text: str) -> tuple[dict, str, str]:
    if not text.startswith("---"):
        return {}, "", text
    m = re.match(r"^---\n(.*?\n)---\n?", text, flags=re.S)
    if not m:
        return {}, "", text
    raw_fm = m.group(1)
    rest = text[m.end() :]
    data = yaml.safe_load(raw_fm) or {}
    if not isinstance(data, dict):
        data = {}
    return data, raw_fm, rest


def _vsa_from_comment(text: str) -> str | None:
    m = re.search(
        r"# === oorspronkelijke VSA[^\n]*\n(.*?)(?=\n# === |\n@|\Z)",
        text,
        flags=re.S,
    )
    if not m:
        return None
    lines: list[str] = []
    for ln in m.group(1).splitlines():
        if ln.startswith("# "):
            lines.append(ln[2:])
        elif ln == "#":
            lines.append("")
        elif ln.startswith("#"):
            lines.append(ln[1:])
        else:
            break
    body = "\n".join(lines).strip()
    return body + "\n" if body else None


def _infer_for(path: Path, meta: dict) -> tuple[str, str]:
    """Return (formula_id, opgegeven_id)."""
    bron_u = None
    bron = meta.get("bron")
    if isinstance(bron, dict):
        bron_u = bron.get("uitgangspunt")
    elif isinstance(bron, str):
        bron_u = bron
    asked = infer_template_id(
        soort=meta.get("soort") or meta.get("genre"),
        toon=meta.get("toon") or meta.get("tone"),
        bron=str(bron_u) if bron_u else None,
        path=path,
    )
    resolved = load_resolved_template(asked)
    return resolved.formula_id, asked


def _try_map(formula_id: str, vsa: str, source: str) -> Exception | None:
    try:
        resolved = load_resolved_template(formula_id)
        norm, _ = ensure_stanza_stars(vsa)
        map_vsa_to_template(
            resolved.doc,
            norm if norm.strip() else vsa,
            source=source,
        )
        return None
    except Exception as exc:  # noqa: BLE001
        return exc


def main() -> int:
    clear_alias_cache()
    ok = 0
    fail = 0
    for path in sorted(KLAAR.glob("*.mvsa")):
        text = path.read_text(encoding="utf-8")
        meta, _raw_fm, rest = _split_fm(text)
        formula_id, asked = _infer_for(path, meta)

        vsa = _vsa_from_comment(text)
        sibling = path.with_suffix(".vsa")
        if not vsa and sibling.is_file():
            vsa = sibling.read_text(encoding="utf-8")

        err: Exception | None = None
        if vsa:
            err = _try_map(formula_id, vsa, path.name)
            # Tropaar-map faalt soms terwijl Groningen-kondak wél past.
            if err is not None and str(meta.get("soort") or "").lower() == "tropaar":
                alt = infer_template_id(
                    soort="kondak",
                    toon=meta.get("toon"),
                    bron=None,
                    path=path,
                )
                alt_r = load_resolved_template(alt)
                if alt_r.formula_id != formula_id:
                    err2 = _try_map(alt_r.formula_id, vsa, path.name)
                    if err2 is None:
                        asked = formula_id if asked == formula_id else asked
                        formula_id = alt_r.formula_id
                        err = None

        meta["template"] = formula_id
        if asked != formula_id:
            meta["template_opgegeven"] = asked
        else:
            meta.pop("template_opgegeven", None)

        dumped = yaml.safe_dump(
            meta,
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
        ).rstrip()
        body = rest.lstrip("\n")
        new_text = f"---\n{dumped}\n---\n\n{body}"
        if not new_text.endswith("\n"):
            new_text += "\n"
        path.write_text(new_text, encoding="utf-8", newline="\n")

        if not vsa:
            print(
                f"WARN {path.name}: template={formula_id} gezet, "
                "geen VSA om te her-mappen"
            )
            ok += 1
            continue
        if err is None:
            extra = f" (opgegeven {asked})" if asked != formula_id else ""
            print(f"OK   {path.name}: template={formula_id}{extra}")
            ok += 1
        else:
            print(f"FAIL {path.name}: template={formula_id} — {err}")
            fail += 1

    print(f"\n{ok} ok, {fail} fail")
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
