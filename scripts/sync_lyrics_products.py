"""Maak sibling ``{stam}.vsa.lyrics.txt`` / ``.mvsa.lyrics.txt`` / ``.mscz.lyrics.txt``.

Platte gezongen tekst via ``vsa.text_export`` (``.vsa`` / ``.mvsa`` / MusicXML /
``.mscz``). Stamp-regels bovenaan (``# vsa-source-sha256:`` …). Slaat ``input/``,
``artefacten_handmatig`` en ``*.print.mscz`` over. Bij basispartituur-``.mscz``
bij voorkeur verse sibling-``.mscz.mxl`` (geen MuseScore); anders ``mscz`` →
temp-``.mxl`` via tooling.
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
    SOURCE_KIND_PARTITUUR,
    SOURCE_KIND_VSA,
    partituur_sha256,
    read_mxl_stamp,
    read_mvsa_stamp,
    source_sha256,
    stamp_sha_from_dict,
    utc_now_iso,
)
from score_filenames import is_print_mscz
from sync_mscz_products import legacy_mxl_for_mscz, product_mxl_for_mscz
from sync_vsa_products import folder_is_handmatig

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOT = REPO_ROOT / "content-source" / "catalogus"

_STAMP_PREFIX = "# vsa-"


def product_path_for_source(source: Path) -> Path:
    """``naam.vsa`` → ``naam.vsa.lyrics.txt``; idem ``.mvsa`` / ``.mscz``."""
    return Path(str(source) + ".lyrics.txt")


def collect_lyric_sources(root: Path) -> list[Path]:
    out: list[Path] = []
    if not root.is_dir():
        return out
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        suf = path.suffix.lower()
        if suf not in {".vsa", ".mvsa", ".mscz"}:
            continue
        name = path.name.lower()
        if name.endswith(".syl.vsa"):
            continue
        if name.endswith(".mscz.mvsa"):
            continue
        if suf == ".mscz" and is_print_mscz(path):
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
    suf = path.suffix.lower()
    if suf == ".mvsa":
        return SOURCE_KIND_MVSA
    if suf == ".mscz":
        return SOURCE_KIND_PARTITUUR
    return SOURCE_KIND_VSA


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


def digest_for_source(source: Path) -> str:
    if source.suffix.lower() == ".mscz":
        return partituur_sha256(source)
    return source_sha256(source)


def is_stale(source: Path, lyrics: Path) -> bool:
    if not lyrics.is_file():
        return True
    stamp = read_mvsa_stamp(lyrics)
    if stamp.get(FIELD_SOURCE_KIND) != source_kind_for(source):
        return True
    if stamp.get(FIELD_SOURCE_SHA) != digest_for_source(source):
        return True
    return False


def _fresh_mscz_mxl(source: Path) -> Path | None:
    """Sibling-``.mscz.mxl`` (of legacy ``.mxl``) met passende partituur-stamp."""
    digest = partituur_sha256(source)
    for mxl in (product_mxl_for_mscz(source), legacy_mxl_for_mscz(source)):
        if not mxl.is_file():
            continue
        if stamp_sha_from_dict(read_mxl_stamp(mxl)) == digest:
            return mxl
    return None


def _extract_plain(source: Path) -> str:
    try:
        from vsa.text_export import plain_text_from_path
    except ImportError as exc:
        raise SystemExit(
            "vsa.text_export ontbreekt — update VSA-tooling (vsa text / mscz text) "
            "via scripts\\_ensure.cmd --vsa-tool (tooling ≥ lyrics-uit-mscz)"
        ) from exc
    if source.suffix.lower() == ".mscz":
        mxl = _fresh_mscz_mxl(source)
        if mxl is not None:
            return plain_text_from_path(mxl)
    return plain_text_from_path(source)


def sync_one(source: Path, *, dry_run: bool) -> None:
    lyrics = product_path_for_source(source)
    rel = source.relative_to(REPO_ROOT)
    print(f"  TXT  {rel} -> {lyrics.name}", flush=True)
    if dry_run:
        return
    plain = _extract_plain(source)
    src_hash = digest_for_source(source)
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


def main(argv: list[str] | None = None) -> int:
    from product_regen import add_regen_arguments, need_regen, policy_from_args

    parser = argparse.ArgumentParser(
        description="Genereer stale .lyrics.txt naast bibliotheek-.vsa/.mvsa/.mscz."
    )
    parser.add_argument(
        "root",
        nargs="?",
        type=Path,
        default=DEFAULT_ROOT,
        help="Map onder content-source/catalogus (default: hele bibliotheek).",
    )
    add_regen_arguments(parser)
    args = parser.parse_args(argv)
    policy = policy_from_args(args)
    root = args.root if args.root.is_absolute() else REPO_ROOT / args.root
    if not root.exists():
        print(f"Pad niet gevonden: {root}", file=sys.stderr)
        return 1

    sources = collect_lyric_sources(root)
    if not sources:
        print(f"Geen .vsa/.mvsa/.mscz onder {root}")
        return 0

    n = 0
    for source in sources:
        lyrics = product_path_for_source(source)
        exists = lyrics.is_file()
        stamp_ok = (not is_stale(source, lyrics)) if exists else False
        if not need_regen(
            policy,
            exists=exists,
            stamp_ok=stamp_ok,
            contract_ok=None,
        ):
            continue
        sync_one(source, dry_run=args.dry_run)
        n += 1

    print(f"lyrics-products: {n} bestand(en) {'(dry-run) ' if args.dry_run else ''}bijgewerkt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
