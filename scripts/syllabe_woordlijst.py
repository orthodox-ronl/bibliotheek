"""Unieke meerlettergrepige woorden uit catalogus-``.vsa`` (nakijklĳst).

Per ``.vsa`` onder ``content-source/catalogus``:

1. Tijdelijke Pyphen-syllabify (bronbestanden worden **niet** gewijzigd).
2. Notatie weg (scopes → alleen gezongen tekst; markers/barlines → spatie).
3. Woorden met soft ``-`` of hard ``=`` verzamelen, uniek (case-fold).

Eenlettergrepige woorden (geen streepje na syllabify) vallen af.

Gebruik::

    python scripts\\syllabe_woordlijst.py
    python scripts\\syllabe_woordlijst.py -o content-source\\input\\_werk\\syllabe-woorden-review.txt
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_DEFAULT_OUT = (
    ROOT / "content-source" / "input" / "_werk" / "syllabe-woorden-review.txt"
)
_CATALOGUS = ROOT / "content-source" / "catalogus"
_EDGE_PUNCT = re.compile(r"^[^\w=]+|[^\w=]+$", re.UNICODE)
_TOKEN = re.compile(r"\S+", re.UNICODE)


def _ensure_vsa_import() -> None:
    sibling = ROOT.parent / "VSA-tooling" / "src"
    if sibling.is_dir():
        path = str(sibling)
        if path not in sys.path:
            sys.path.insert(0, path)


def _hyphenated_bare_text(source: str) -> str:
    from vsa.ast import ControlTokenNode, ScopeNode, TextNode
    from vsa.markdown_newline_policy import preserve_vsa_source_newlines
    from vsa.parser import Parser
    from vsa.syllabify import syllabify_vsa_source
    from vsa.vsa_comments import strip_vsa_html_comments_with_offset_map
    from vsa.yaml_frontmatter import parse_vsa_frontmatter

    syl = syllabify_vsa_source(source).text
    _fm, body = parse_vsa_frontmatter(syl)
    body, _ = strip_vsa_html_comments_with_offset_map(body)
    document = Parser(preserve_vsa_source_newlines(body)).parse()
    chunks: list[str] = []
    for node in document.nodes:
        if isinstance(node, TextNode):
            chunks.append(node.text or "")
        elif isinstance(node, ScopeNode):
            chunks.append(node.text or "")
        elif isinstance(node, ControlTokenNode):
            chunks.append(" ")
    return "".join(chunks)


def _words_with_hyphens(bare: str) -> set[str]:
    found: set[str] = set()
    for match in _TOKEN.finditer(bare):
        core = _EDGE_PUNCT.sub("", match.group(0))
        if not core:
            continue
        if "-" not in core and "=" not in core:
            continue
        if not any(ch.isalpha() for ch in core):
            continue
        found.add(core.casefold())
    return found


def collect_review_words(catalogus: Path) -> tuple[list[str], int, list[str]]:
    """Retourneert (gesorteerde woorden, aantal bestanden, foutpaden)."""
    words: set[str] = set()
    errors: list[str] = []
    files = sorted(catalogus.rglob("*.vsa"))
    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
            bare = _hyphenated_bare_text(text)
            words |= _words_with_hyphens(bare)
        except Exception as exc:  # noqa: BLE001 — verzamel, ga door
            errors.append(f"{path.relative_to(ROOT).as_posix()}: {exc}")
    return sorted(words), len(files), errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Bouw een unieke nakijklĳst van meerlettergrepige woorden "
            "uit catalogus-.vsa (tijdelijke syllabify; bronnen ongewijzigd)."
        )
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=_DEFAULT_OUT,
        help=f"Uitvoerbestand (default: {_DEFAULT_OUT})",
    )
    parser.add_argument(
        "--catalogus",
        type=Path,
        default=_CATALOGUS,
        help="Map met .vsa-bestanden (default: content-source/catalogus)",
    )
    args = parser.parse_args(argv)

    _ensure_vsa_import()
    catalogus = args.catalogus
    if not catalogus.is_dir():
        print(f"Catalogusmap ontbreekt: {catalogus}", file=sys.stderr)
        return 1

    words, n_files, errors = collect_review_words(catalogus)
    out: Path = args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    header = (
        "# Nakijklĳst syllabificatie (catalogus .vsa)\n"
        "#\n"
        "# Hoe gemaakt: per .vsa tijdelijke Pyphen-syllabify (bron niet "
        "geschreven),\n"
        "# notatie weggehaald (scopes → gezongen tekst), woorden met soft "
        "'-' of hard '='.\n"
        "# Eenlettergrepige woorden (geen streepje) zijn weggelaten.\n"
        "# Controleer twijfelgevallen (zing-deling ≠ orthografie); zet "
        "daarna soft '-' in de bron\n"
        "# of voeg bewuste eenlettergrepigen toe aan "
        "VSA-tooling monosyllable_exceptions.nl.txt.\n"
        f"# Bronbestanden: {n_files} onder {catalogus.relative_to(ROOT).as_posix()}\n"
        f"# Unieke woorden: {len(words)}\n"
        "#\n"
    )
    out.write_text(header + "\n".join(words) + ("\n" if words else ""), encoding="utf-8")
    print(f"Geschreven: {out} ({len(words)} woorden uit {n_files} .vsa)")
    if errors:
        print(f"{len(errors)} bestand(en) overgeslagen:", file=sys.stderr)
        for line in errors[:20]:
            print(f"  {line}", file=sys.stderr)
        if len(errors) > 20:
            print(f"  … en {len(errors) - 20} meer", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
