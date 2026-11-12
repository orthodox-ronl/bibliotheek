"""Vul ontbrekende soort/toon op .vsa en herorden frontmatter (soort+toon bij elkaar).

Zie docs/specs/vsa-frontmatter.md. Afleiden uit pad/bestandsnaam waar mogelijk.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from frontmatter_canoniek import (  # noqa: E402
    FM_ANY_RE,
    KEY_ORDER,
    SOORTEN_MET_TOON,
    TOON_IN_NAME_RE,
    check_required_vsa,
    is_syntax_walkthrough,
    order_keys,
    toon_required_for,
)

SKIP_PARTS = {
    ".git",
    "node_modules",
    "generated",
    "vendor",
    ".venv",
    "__pycache__",
    "zzz",
}

KNOWN_SOORT_PREFIXES = (
    "kondak",
    "tropaar",
    "stichier",
    "vers",
    "prokimen",
    "prijslied",
    "communievers",
    "moeder-godslied",
    "eerste-antifoon",
    "tweede-antifoon",
    "derde-antifoon",
    "eer-aan-de-vader",
    "geloofsbelijdenis",
    "trisagion",
    "onze-vader",
    "vriendelijk-licht",
    "onder-uwe-hoede",
    "vredeswens",
    "wij-hebben-het-ware-licht",
)


def _norm_soort(raw: str) -> str:
    s = raw.strip().lower().replace(" ", "-")
    s = s.replace("_", "-")
    return s


_SOORT_TOON_DIR_RE = re.compile(
    r"^(" + "|".join(re.escape(s) for s in sorted(KNOWN_SOORT_PREFIXES, key=len, reverse=True))
    + r")-toon-[1-8](?:-|$)",
    re.I,
)


def derive_soort(path: Path, data: dict) -> str | None:
    cur = data.get("soort") or data.get("genre")
    if cur not in (None, ""):
        return _norm_soort(str(cur))
    stem = path.stem.lower()
    for pref in sorted(KNOWN_SOORT_PREFIXES, key=len, reverse=True):
        if stem.startswith(pref + "-") or stem == pref:
            return pref
    # catalogus/…/soort/…
    parts = [p.lower() for p in path.parts]
    if "catalogus" in parts:
        i = parts.index("catalogus")
        if i + 1 < len(parts):
            return _norm_soort(parts[i + 1])
    # formule-map of template-id: kondak-toon-2-groningen
    for part in parts:
        m = _SOORT_TOON_DIR_RE.match(part)
        if m:
            return _norm_soort(m.group(1))
    for key in ("template", "template_opgegeven"):
        raw = data.get(key)
        if raw in (None, ""):
            continue
        m = _SOORT_TOON_DIR_RE.match(str(raw).strip())
        if m:
            return _norm_soort(m.group(1))
    # legacy docs-frontmatter
    ident = data.get("identificatie")
    if isinstance(ident, dict):
        title = str(ident.get("title") or "")
        for pref in sorted(KNOWN_SOORT_PREFIXES, key=len, reverse=True):
            if pref.replace("-", " ") in title.lower() or pref in title.lower():
                return pref
    title = str(data.get("title") or data.get("titel") or "")
    for pref in sorted(KNOWN_SOORT_PREFIXES, key=len, reverse=True):
        label = pref.replace("-", " ")
        if label in title.lower() or pref in title.lower():
            return pref
    return None


# Zangstukken zonder toon-N in pad, wel bekende Oktoëchos-toon (siblings/comment).
KNOWN_TOON_BY_STEM_PREFIX = {
    "tropaar-uw-heilig-kruis": 1,
    "tropaar-heer-red-uw-volk": 1,
}


def derive_toon(path: Path, data: dict, text: str = "") -> int | None:
    cur = data.get("toon")
    if cur is None:
        cur = data.get("tone")
    if cur not in (None, ""):
        try:
            return int(cur)
        except (TypeError, ValueError):
            pass
    m = TOON_IN_NAME_RE.search(str(path).replace("\\", "/"))
    if m:
        return int(m.group(1))
    m2 = re.search(r"toon-([1-8])", path.stem, flags=re.I)
    if m2:
        return int(m2.group(1))
    # HTML-/VSA-comment: <!-- Toon: 8 --> of (Toon 1 - …)
    if text:
        m3 = re.search(
            r"(?is)(?:<!--\s*)?(?:Toon|tone)\s*[:=]?\s*([1-8])\b",
            text,
        )
        if m3:
            return int(m3.group(1))
    stem = path.stem.lower()
    for pref, n in KNOWN_TOON_BY_STEM_PREFIX.items():
        if stem.startswith(pref):
            return n
    return None


class _LiteralStr(str):
    """Multiline zoektekst als YAML ``|`` (frase per regel)."""


class _FmDumper(yaml.SafeDumper):
    pass


def _represent_literal(dumper: yaml.SafeDumper, data: _LiteralStr) -> yaml.Node:
    return dumper.represent_scalar("tag:yaml.org,2002:str", str(data), style="|")


_FmDumper.add_representer(_LiteralStr, _represent_literal)


def _prepare_fm_for_dump(data: dict) -> dict:
    out = order_keys(data)
    zt = out.get("zoektekst")
    if isinstance(zt, str) and ("\n" in zt or len(zt) > 60):
        out["zoektekst"] = _LiteralStr(zt.replace("\r\n", "\n").strip("\n"))
    return out


def rewrite_fm_block(text: str, new_fm: dict) -> str:
    """Vervang eerste YAML-frontmatterblok; behoud diagnose-kop erboven."""
    prepared = _prepare_fm_for_dump(new_fm)
    dumped = yaml.dump(
        prepared,
        Dumper=_FmDumper,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
        width=1000,
    )
    m = FM_ANY_RE.search(text)
    if not m:
        return f"---\n{dumped}---\n\n{text.lstrip()}"
    block = f"---\n{dumped}---\n"
    return text[: m.start()] + block + text[m.end() :]


def load_fm(text: str) -> tuple[dict | None, re.Match[str] | None, str | None]:
    m = FM_ANY_RE.search(text)
    if not m:
        return None, None, None
    try:
        data = yaml.safe_load(m.group(1))
    except yaml.YAMLError as exc:
        return None, m, str(exc).split("\n")[0]
    if not isinstance(data, dict):
        return {}, m, None
    return data, m, None


def process_file(path: Path) -> tuple[str, list[str]]:
    notes: list[str] = []
    text = path.read_text(encoding="utf-8")
    data, m, yaml_err = load_fm(text)
    if yaml_err:
        notes.append(f"KON NIET: ongeldige YAML-frontmatter ({yaml_err})")
        return "fail", notes
    if data is None:
        notes.append("geen frontmatter")
        return "skip", notes

    changed = False
    if "genre" in data and "soort" not in data:
        data["soort"] = data.pop("genre")
        notes.append("genre→soort")
        changed = True
    elif "genre" in data:
        data.pop("genre", None)
        changed = True

    if "tone" in data and "toon" not in data:
        data["toon"] = data.pop("tone")
        notes.append("tone→toon")
        changed = True
    elif "tone" in data:
        data.pop("tone", None)
        changed = True

    soort = derive_soort(path, data)
    if soort and data.get("soort") != soort:
        if data.get("soort") in (None, ""):
            notes.append(f"soort←{soort}")
        else:
            # normaliseer schrijfwijze
            if _norm_soort(str(data["soort"])) != soort:
                notes.append(f"soort {data['soort']!r}→{soort}")
        data["soort"] = soort
        changed = True
    elif data.get("soort") not in (None, ""):
        norm = _norm_soort(str(data["soort"]))
        if norm != data["soort"]:
            data["soort"] = norm
            notes.append(f"soort genormaliseerd→{norm}")
            changed = True

    toon = derive_toon(path, data, text)
    if toon is not None and data.get("toon") != toon:
        if data.get("toon") in (None, ""):
            notes.append(f"toon←{toon}")
        data["toon"] = toon
        changed = True

    # Verplichtingen (zelfde regels als frontmatter_canoniek)
    for req in check_required_vsa(data, path):
        if req == "ontbreekt verplicht veld: soort":
            notes.append("KON NIET: soort ontbreekt en niet afleidbaar")
        elif req == "ontbreekt verplicht veld: toon":
            notes.append("KON NIET: toon verplicht maar niet afleidbaar")
        elif req.startswith("volgorde:") or "horen direct" in req:
            notes.append(req)
            changed = True
        else:
            notes.append(f"KON NIET: {req}")
    if is_syntax_walkthrough(path) and data.get("soort") in (None, ""):
        notes.append("docs-walkthrough: soort niet verplicht")

    ordered = order_keys({k: v for k, v in data.items() if v is not None and v != ""})
    # check adjacency after order
    keys = list(ordered.keys())
    if "soort" in ordered and "toon" in ordered:
        if abs(keys.index("soort") - keys.index("toon")) != 1:
            notes.append("herorden soort/toon")
            changed = True
        elif keys.index("soort") > keys.index("toon"):
            changed = True
            notes.append("herorden soort boven toon")

    # Always rewrite through order_keys for consistent grouping when we touch file
    # or when order differs from KEY_ORDER for present keys
    ideal = [k for k in KEY_ORDER if k in ordered]
    actual = [k for k in ordered.keys() if k in KEY_ORDER]
    if ideal != actual:
        changed = True
        if "herorden" not in " ".join(notes):
            notes.append("herorden frontmatter")

    if not changed and not any(n.startswith("KON NIET") for n in notes):
        return "ok", notes

    if any(n.startswith("KON NIET") for n in notes) and not changed:
        return "fail", notes

    new_text = rewrite_fm_block(text, ordered)
    if new_text != text:
        path.write_text(new_text, encoding="utf-8", newline="\n")
        return "fixed", notes
    return "ok", notes


def iter_vsa(roots: list[Path]) -> list[Path]:
    out: list[Path] = []
    for root in roots:
        if not root.is_dir():
            continue
        for p in root.rglob("*.vsa"):
            if any(part in SKIP_PARTS for part in p.parts):
                continue
            out.append(p)
    return sorted(out)


def main() -> int:
    roots = [
        REPO / "content-source",
        REPO / "docs" / "voorbeelden",
        REPO.parent / "VSA-tooling" / "docs" / "specification-vsa-templates" / "library",
        REPO.parent / "VSA-tooling" / "examples",
    ]
    files = iter_vsa(roots)
    stats = {"ok": 0, "fixed": 0, "fail": 0, "skip": 0}
    fails: list[str] = []
    for path in files:
        status, notes = process_file(path)
        stats[status] = stats.get(status, 0) + 1
        interesting = [
            n
            for n in notes
            if n.startswith("KON NIET")
            or "←" in n
            or "→" in n
            or n.startswith("herorden")
        ]
        if status in ("fixed", "fail") or interesting:
            rel = path
            try:
                rel = path.relative_to(REPO)
            except ValueError:
                try:
                    rel = path.relative_to(REPO.parent)
                except ValueError:
                    pass
            print(f"{status:5} {rel}")
            for n in notes:
                print(f"      - {n}")
        if status == "fail":
            fails.append(str(path))
    print(
        f"\n{stats['fixed']} fixed, {stats['ok']} ok, "
        f"{stats['fail']} fail, {stats['skip']} skip; total {len(files)}"
    )
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
