#!/usr/bin/env python3
"""Canonieke-vorm-gate voor VSA/MVSA-frontmatter.

Verwijdert lege/null-sleutels en ongedocumenteerde sleutels.
Wijzigt de notatie-body niet.

Documentatie: docs/specs/vsa-frontmatter.md
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

# Gedocumenteerde top-level sleutels (proefschema).
# Zie docs/specs/vsa-frontmatter.md
ALLOWED_TOP = {
    "afspelen",
    "partituur",
    "titel",
    "taal",
    "toon",
    "soort",
    "soorten",
    "gelegenheid",
    "gelegenheden",
    "bron",
    "corpus_id",
    "gebruikt-in",
    "zoek",
    # Formule-id (VSA + template → MVSA); zie vsa-frontmatter.md
    "template",
    "template_opgegeven",
    # Tijdelijk plat tot tooling `afspelen` leest
    "do",
    "mode",
    "tempo",
}

ALLOWED_NESTED: dict[str, set[str]] = {
    "afspelen": {"do", "mode", "tempo"},
    # MuseScore-Engels (tijdelijke keuze)
    "partituur": {
        "title",
        "subtitle",
        "composer",
        "arranger",
        "layout",
    },
    "bron": {
        "uitgangspunt",
        "tekst",
        "melodie",
        "bewerking",
        "korte_vermelding",
    },
    "zoek": {"aliases", "tags"},
}

# vaste volgorde: soort + toon bij elkaar (docs/specs/vsa-frontmatter.md)
KEY_ORDER = (
    "titel",
    "taal",
    "soort",
    "toon",
    "template",
    "template_opgegeven",
    "soorten",
    "partituur",
    "bron",
    "gelegenheid",
    "gelegenheden",
    "zoektekst",
    "zoek",
    "corpus_id",
    "gebruikt-in",
    "do",
    "mode",
    "tempo",
    "afspelen",
)

# Soorten die een Oktoëchos-toon verwachten (toon verplicht op .vsa).
SOORTEN_MET_TOON = frozenset(
    {
        "tropaar",
        "kondak",
        "stichier",
        "vers",
        "prokimen",
    }
)

FM_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n?", re.DOTALL)
# Ook frontmatter ná diagnose-kop (eerste ---…----blok).
FM_ANY_RE = re.compile(r"---\r?\n(.*?)\r?\n---\r?\n?", re.DOTALL)

TOON_IN_NAME_RE = re.compile(r"(?:^|[-_/])toon-([1-8])(?:[-_/]|$)", re.I)


def is_empty(val: object) -> bool:
    if val is None:
        return True
    if val == "":
        return True
    if isinstance(val, (list, dict)) and len(val) == 0:
        return True
    return False


def prune(obj: object, allowed_keys: set[str] | None = None) -> object | None:
    if isinstance(obj, dict):
        out: dict = {}
        for k, v in obj.items():
            if allowed_keys is not None and k not in allowed_keys:
                continue
            if k in ALLOWED_NESTED and isinstance(v, dict):
                nested = prune(v, ALLOWED_NESTED[k])
                if nested is not None and not is_empty(nested):
                    out[k] = nested
                continue
            pruned = prune(v, None)
            if not is_empty(pruned):
                out[k] = pruned
        return out if out else None
    if isinstance(obj, list):
        items = [prune(x, None) for x in obj]
        items = [x for x in items if not is_empty(x)]
        return items if items else None
    return obj


def split_fm(text: str) -> tuple[dict | None, str, bool]:
    m = FM_RE.match(text)
    if not m:
        return None, text, False
    raw = m.group(1)
    body = text[m.end() :]
    if yaml is None:
        raise SystemExit("PyYAML ontbreekt (pip install pyyaml)")
    data = yaml.safe_load(raw)
    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise SystemExit("Frontmatter is geen mapping")
    return data, body, True


def order_keys(data: dict) -> dict:
    """Zet bekende sleutels in KEY_ORDER; rest behoudt invoervolgorde."""
    out: dict = {}
    for key in KEY_ORDER:
        if key in data:
            out[key] = data[key]
    for key, val in data.items():
        if key not in out:
            out[key] = val
    return out


def dump_fm(data: dict) -> str:
    ordered = order_keys(data)
    dumped = yaml.safe_dump(
        ordered,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
    )
    return f"---\n{dumped}---\n"


def toon_required_for(data: dict, path: Path | None = None) -> bool:
    soort = str(data.get("soort") or data.get("genre") or "").strip().lower()
    if soort in SOORTEN_MET_TOON:
        return True
    name = ""
    if path is not None:
        name = str(path).replace("\\", "/")
    if TOON_IN_NAME_RE.search(name):
        return True
    return False


def is_syntax_walkthrough(path: Path | None) -> bool:
    """Pure notatie-demo’s zonder catalogus-metadata (vsa-frontmatter.md)."""
    if path is None:
        return False
    parts = {p.lower() for p in path.parts}
    return "docs-walkthroughs" in parts


def check_required_vsa(data: dict, path: Path | None = None) -> list[str]:
    """Verplichte soort/toon op .vsa (zie vsa-frontmatter.md)."""
    notes: list[str] = []
    if path is not None and path.suffix.lower() != ".vsa":
        return notes
    if is_syntax_walkthrough(path):
        # Alleen vrijstellen als er geen liturgische soort/toon-hint is.
        hinted = bool(
            data.get("soort")
            or data.get("genre")
            or TOON_IN_NAME_RE.search(str(path).replace("\\", "/"))
        )
        if not hinted:
            title = ""
            ident = data.get("identificatie")
            if isinstance(ident, dict):
                title = str(ident.get("title") or "")
            title += " " + str(data.get("titel") or data.get("title") or "")
            if not re.search(
                r"tropaar|kondak|stichier|prokimen|vers\b",
                title,
                flags=re.I,
            ):
                return notes
    soort = data.get("soort")
    if soort in (None, "") and data.get("genre") in (None, ""):
        notes.append("ontbreekt verplicht veld: soort")
    toon = data.get("toon")
    if toon is None:
        toon = data.get("tone")
    if toon_required_for(data, path) and toon in (None, ""):
        notes.append("ontbreekt verplicht veld: toon")
    elif toon not in (None, ""):
        try:
            n = int(toon)
        except (TypeError, ValueError):
            notes.append(f"toon moet geheel 1–8 zijn, kreeg {toon!r}")
        else:
            if n < 1 or n > 8:
                notes.append(f"toon moet 1–8 zijn, kreeg {n}")
    # soort en toon moeten naast elkaar in KEY_ORDER staan als beide aanwezig
    keys = [k for k in data.keys() if k in ("soort", "toon")]
    if keys == ["toon", "soort"]:
        notes.append("volgorde: zet soort direct boven toon")
    elif "soort" in data and "toon" in data:
        key_list = list(data.keys())
        try:
            i_s = key_list.index("soort")
            i_t = key_list.index("toon")
            if abs(i_s - i_t) != 1:
                notes.append("soort en toon horen direct onder elkaar")
        except ValueError:
            pass
    return notes


def _note_empties(before: object, after: object, prefix: str, notes: list[str]) -> None:
    """Vergelijk voor/na prune; noteer lege of ongedocumenteerde weggehaalde sleutels."""
    if not isinstance(before, dict):
        return
    after_d = after if isinstance(after, dict) else {}
    for k, v in before.items():
        path = f"{prefix}.{k}" if prefix else k
        if k not in after_d:
            if prefix == "" and k not in ALLOWED_TOP:
                notes.append(f"verwijderd (ongedocumenteerd): {path}")
            elif is_empty(v):
                notes.append(f"verwijderd (leeg): {path}")
            elif isinstance(v, dict) and k in ALLOWED_NESTED:
                notes.append(f"verwijderd (leeg): {path}")
            elif prefix and k not in ALLOWED_NESTED.get(prefix.split(".")[-1], set()):
                notes.append(f"verwijderd (ongedocumenteerd): {path}")
            else:
                notes.append(f"verwijderd (leeg): {path}")
            continue
        if isinstance(v, dict):
            _note_empties(v, after_d[k], path, notes)


def process(text: str, *, path: Path | None = None) -> tuple[str, list[str]]:
    notes: list[str] = []
    data, body, has_fm = split_fm(text)
    if not has_fm or data is None:
        notes.append("geen YAML-frontmatter")
        return text, notes
    # genre/tone → soort/toon vóór prune
    if "soort" not in data and data.get("genre") not in (None, ""):
        data["soort"] = data.pop("genre")
        notes.append("genre → soort")
    if "toon" not in data and data.get("tone") not in (None, ""):
        data["toon"] = data.pop("tone")
        notes.append("tone → toon")
    pruned = prune(data, ALLOWED_TOP)
    if pruned is None:
        pruned = {}
    if not isinstance(pruned, dict):
        pruned = {}
    _note_empties(data, pruned, "", notes)
    notes.extend(check_required_vsa(pruned if pruned else data, path))
    if not pruned:
        notes.append("frontmatter volledig leeg na prune — alleen body")
        return body.lstrip("\n"), notes
    pruned = order_keys(pruned)
    new_text = (
        dump_fm(pruned) + body.lstrip("\n")
        if not body.startswith("\n")
        else dump_fm(pruned) + body
    )
    if new_text != text and not any(
        n.startswith("verwijderd") or "→" in n or n.startswith("ontbreekt")
        for n in notes
    ):
        notes.append("herordend / genormaliseerd (YAML-dump)")
    return new_text, notes


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Canonieke VSA/MVSA-frontmatter")
    p.add_argument("paths", nargs="+", type=Path, help=".vsa / .mvsa bestanden")
    p.add_argument(
        "--check",
        action="store_true",
        help="Alleen melden of er iets gestript zou worden (exit 1 bij werk)",
    )
    p.add_argument(
        "--in-place",
        action="store_true",
        help="Bestand herschrijven (anders: stdout per bestand)",
    )
    args = p.parse_args(argv)

    any_change = False
    any_problem = False
    for path in args.paths:
        text = path.read_text(encoding="utf-8")
        new_text, notes = process(text, path=path)
        changed = new_text != text
        if changed:
            any_change = True
        if any(
            n.startswith("ontbreekt")
            or n.startswith("toon moet")
            or n.startswith("volgorde:")
            or "horen direct" in n
            for n in notes
        ):
            any_problem = True
        print(f"## {path}")
        for n in notes:
            print(f"  - {n}")
        if not notes:
            print("  - (geen wijzigingen)")
        if args.check:
            continue
        if args.in_place:
            if changed:
                from cli_style import atomic_write_text

                atomic_write_text(path, new_text, newline="\n")
                print("  -> geschreven")
        else:
            print("--- resultaat ---")
            print(new_text)
    if args.check and (any_change or any_problem):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
