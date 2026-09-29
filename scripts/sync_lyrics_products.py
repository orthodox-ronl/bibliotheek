"""Maak sibling ``{stam}.vsa.lyrics.txt`` / ``{stam}.mvsa.lyrics.txt``.

Platte gezongen tekst via ``vsa.text_export``. Stamp-regels bovenaan
(``# vsa-source-sha256:`` …) zoals bij import-mvsa. Slaat ``input/`` en
``artefacten_handmatig`` over.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from product_meta import (
    FIELD_GENERATED_AT,
    FIELD_GENERATOR,
    FIELD_SOURCE_KIND,
    FIELD_SOURCE_SHA,
    GENERATOR_LYRICS,
    SOURCE_KIND_MVSA,
    SOURCE_KIND_VSA,
    read_mvsa_stamp,
    source_sha256,
    utc_now_iso,
)
from sync_vsa_products import folder_is_handmatig

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOT = REPO_ROOT / "content-source" / "bibliotheek"

_STAMP_PREFIX = "# vsa-"


def product_path_for_source(source: Path) -> Path:
    """``naam.vsa`` → ``naam.vsa.lyrics.txt``; idem ``.mvsa``."""
    return Path(str(source) + ".lyrics.txt")


def collect_lyric_sources(root: Path) -> list[Path]:
    out: list[Path] = []
    if not root.is_dir():
        return out
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        suf = path.suffix.lower()
        if suf not in {".vsa", ".mvsa"}:
            continue
        if path.name.lower().endswith(".syl.vsa"):
            continue
        if "input" in path.parts:
            continue
        if folder_is_handmatig(path.parent):
            continue
        if " " in path.name:
            raise SystemExit(f"bestandsnaam mag geen spaties hebben: {path.name}")
        out.append(path)
    return out


def source_kind_for(path: Path) -> str:
    return SOURCE_KIND_MVSA if path.suffix.lower() == ".mvsa" else SOURCE_KIND_VSA


def lyrics_body(path: Path) -> str:
    """Platte tekst zonder stamp-header."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return ""
    lines = text.splitlines()
    i = 0
    while i < len(lines) and lines[i].startswith(_STAMP_PREFIX):
        i += 1
    if i < len(lines) and lines[i].strip() == "":
        i += 1
    return "\n".join(lines[i:]).strip()


def is_stale(source: Path, lyrics: Path) -> bool:
    if not lyrics.is_file():
        return True
    stamp = read_mvsa_stamp(lyrics)
    if stamp.get(FIELD_SOURCE_KIND) != source_kind_for(source):
        return True
    if stamp.get(FIELD_SOURCE_SHA) != source_sha256(source):
        return True
    return False


def _extract_plain(source: Path) -> str:
    try:
        from vsa.text_export import plain_text_from_path
    except ImportError as exc:
        raise SystemExit(
            "vsa.text_export ontbreekt — update VSA-tooling (vsa text) "
            "via scripts\\_ensure.cmd --vsa-tool"
        ) from exc
    return plain_text_from_path(source)


def sync_one(source: Path, *, dry_run: bool) -> None:
    lyrics = product_path_for_source(source)
    rel = source.relative_to(REPO_ROOT)
    print(f"  TXT  {rel} -> {lyrics.name}", flush=True)
    if dry_run:
        return
    plain = _extract_plain(source)
    src_hash = source_sha256(source)
    generated_at = utc_now_iso()
    kind = source_kind_for(source)
    header = "\n".join(
        [
            f"# {FIELD_SOURCE_SHA}: {src_hash}",
            f"# {FIELD_SOURCE_KIND}: {kind}",
            f"# {FIELD_GENERATED_AT}: {generated_at}",
            f"# {FIELD_GENERATOR}: {GENERATOR_LYRICS}",
            "",
            "",
        ]
    )
    body = plain.strip() + ("\n" if plain.strip() else "")
    lyrics.write_text(header + body, encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Genereer stale .lyrics.txt naast bibliotheek-.vsa/.mvsa."
    )
    parser.add_argument(
        "root",
        nargs="?",
        type=Path,
        default=DEFAULT_ROOT,
        help="Map onder content-source/bibliotheek (default: hele bibliotheek).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Toon wat zou worden geschreven, zonder te schrijven.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Schrijf alle lyrics opnieuw, ook als de stamp nog klopt.",
    )
    args = parser.parse_args()
    root = args.root if args.root.is_absolute() else REPO_ROOT / args.root
    if not root.exists():
        print(f"Pad niet gevonden: {root}", file=sys.stderr)
        return 1

    sources = collect_lyric_sources(root)
    if not sources:
        print(f"Geen .vsa/.mvsa onder {root}")
        return 0

    n = 0
    for source in sources:
        lyrics = product_path_for_source(source)
        if not args.force and not is_stale(source, lyrics):
            continue
        sync_one(source, dry_run=args.dry_run)
        n += 1

    print(f"lyrics-products: {n} bestand(en) {'(dry-run) ' if args.dry_run else ''}bijgewerkt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
