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
    "zoek",
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

FM_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n?", re.DOTALL)


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


def dump_fm(data: dict) -> str:
    dumped = yaml.safe_dump(
        data,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
    )
    return f"---\n{dumped}---\n"


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


def process(text: str) -> tuple[str, list[str]]:
    notes: list[str] = []
    data, body, has_fm = split_fm(text)
    if not has_fm or data is None:
        notes.append("geen YAML-frontmatter")
        return text, notes
    pruned = prune(data, ALLOWED_TOP)
    if pruned is None:
        pruned = {}
    if not isinstance(pruned, dict):
        pruned = {}
    _note_empties(data, pruned, "", notes)
    if not pruned:
        notes.append("frontmatter volledig leeg na prune — alleen body")
        return body.lstrip("\n"), notes
    new_text = (
        dump_fm(pruned) + body.lstrip("\n")
        if not body.startswith("\n")
        else dump_fm(pruned) + body
    )
    if new_text != text and not notes:
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
    for path in args.paths:
        text = path.read_text(encoding="utf-8")
        new_text, notes = process(text)
        changed = new_text != text
        if changed:
            any_change = True
        print(f"## {path}")
        for n in notes:
            print(f"  - {n}")
        if not notes:
            print("  - (geen wijzigingen)")
        if args.check:
            continue
        if args.in_place:
            if changed:
                path.write_text(new_text, encoding="utf-8", newline="\n")
                print("  -> geschreven")
        else:
            print("--- resultaat ---")
            print(new_text)
    if args.check and any_change:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
