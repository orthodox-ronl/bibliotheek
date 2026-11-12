"""Controleer VSA↔template-koppeling op afgeleide .mvsa (T1/T6).

Voor bestanden met frontmatter ``template:`` én oorspronkelijke VSA
(in commentaarblok of sibling ``.vsa``): opnieuw mappen. Faalt bij
onbekend template of ``VSA-TEMPLATE-PITCH-MISMATCH`` e.d.

Geen byte-vergelijking met de bestaande MVSA (handpolish mag).

Gebruik::

  python scripts\\check_template_provenance.py
  python scripts\\check_template_provenance.py --fail
  python scripts\\check_template_provenance.py --root content-source\\input\\_werk
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _ensure_vsa_tooling() -> None:
    sibling = REPO.parent / "VSA-tooling" / "src"
    if sibling.is_dir():
        sys.path.insert(0, str(sibling))


def _split_fm(text: str) -> tuple[dict, str]:
    from vsa.yaml_frontmatter import parse_vsa_frontmatter

    if not text.lstrip().startswith("---"):
        return {}, text
    return parse_vsa_frontmatter(text)


def _vsa_from_mvsa_comment(text: str) -> str | None:
    m = re.search(
        r"# === oorspronkelijke VSA[^\n]*\n(.*?)(?=\n# === |\Z)",
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


def _iter_mvsa(root: Path) -> list[Path]:
    return sorted(
        p
        for p in root.rglob("*.mvsa")
        if p.is_file() and ".mscz.mvsa" not in p.name
    )


def check_one(path: Path) -> list[str]:
    from vsa.template_instance import TemplateInstanceError, map_vsa_to_template
    from vsa.template_library import TemplateLibraryError, load_resolved_template
    from vsa.vsa_stanzas import ensure_stanza_stars

    text = path.read_text(encoding="utf-8")
    meta, _ = _split_fm(text)
    tid = meta.get("template")
    if tid in (None, ""):
        return []  # geen provenance-plicht

    issues: list[str] = []
    try:
        # ``template`` = feitelijk gebruikte formule; ``template_opgegeven`` is
        # documentatie (alias of andere gevraagde id) en hoeft niet same_as te zijn.
        resolved = load_resolved_template(str(tid))
    except TemplateLibraryError as exc:
        return [f"{path}: onbekend template {tid!r} ({exc})"]
    asked = meta.get("template_opgegeven")
    if asked not in (None, ""):
        try:
            load_resolved_template(str(asked))
        except TemplateLibraryError as exc:
            issues.append(
                f"{path}: onbekend template_opgegeven {asked!r} ({exc})"
            )

    vsa_body = _vsa_from_mvsa_comment(text)
    sibling = path.with_suffix(".vsa")
    if not vsa_body and sibling.is_file():
        vsa_body = sibling.read_text(encoding="utf-8")
    if not vsa_body:
        return [
            f"{path}: template={tid!r} maar geen VSA-commentaar/sibling "
            "(her-map overgeslagen)"
        ]

    raw = vsa_body
    try:
        norm, _ = ensure_stanza_stars(raw)
        map_vsa_to_template(
            resolved.doc,
            norm if norm.strip() else raw,
            source=path.name,
        )
    except TemplateInstanceError as exc:
        issues.append(f"{path}: her-map faalt ({exc})")
    except Exception as exc:  # noqa: BLE001 — CLI-inventarisatie
        issues.append(f"{path}: her-map fout ({type(exc).__name__}: {exc})")
    return issues


def main(argv: list[str] | None = None) -> int:
    _ensure_vsa_tooling()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--root",
        type=Path,
        default=REPO / "content-source",
        help="Scanroot (default: content-source)",
    )
    ap.add_argument(
        "--fail",
        action="store_true",
        help="Exit 1 bij problemen (voor check --strict)",
    )
    args = ap.parse_args(argv)

    root = args.root if args.root.is_absolute() else REPO / args.root
    if not root.is_dir():
        print(f"root ontbreekt: {root}", file=sys.stderr)
        return 2

    all_issues: list[str] = []
    n_checked = 0
    for mvsa in _iter_mvsa(root):
        text = mvsa.read_text(encoding="utf-8")
        meta, _ = _split_fm(text)
        if meta.get("template") in (None, ""):
            continue
        n_checked += 1
        all_issues.extend(check_one(mvsa))

    if all_issues:
        print(f"template-provenance: {len(all_issues)} probleem(en), {n_checked} gecontroleerd")
        for line in all_issues:
            print(f"  - {line}")
        return 1 if args.fail else 0

    print(f"template-provenance: ok ({n_checked} met template:)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
