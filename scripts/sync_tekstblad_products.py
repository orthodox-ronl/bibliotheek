"""Maak sibling ``{stam}.tekstblad.pdf`` bij bibliotheek-``.tekstblad.md``.

Roept ``vsa pdf`` aan; zet ``vsa-source-sha256`` + ``vsa-source-kind=tekstblad``.
Slaat ``input/`` en ``artefacten_handmatig`` over. CI genereert niet —
alleen ``check_tekstblad_products``; vernieuw lokaal met
``scripts\\tekstblad-products.cmd``.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from product_meta import (
    FIELD_SOURCE_KIND,
    FIELD_SOURCE_SHA,
    GENERATOR_TEKSTBLAD,
    SOURCE_KIND_TEKSTBLAD,
    read_pdf_stamp,
    source_sha256,
    stamp_pdf,
    utc_now_iso,
)
from sync_vsa_products import folder_is_handmatig

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOT = REPO_ROOT / "content-source" / "bibliotheek"


def is_tekstblad_md(path: Path) -> bool:
    return path.name.lower().endswith(".tekstblad.md")


def product_pdf_for_md(md: Path) -> Path:
    """``naam.tekstblad.md`` → ``naam.tekstblad.pdf``."""
    return md.with_suffix(".pdf")


def collect_tekstblad(root: Path) -> list[Path]:
    out: list[Path] = []
    if not root.is_dir():
        return out
    for path in sorted(root.rglob("*")):
        if not path.is_file() or not is_tekstblad_md(path):
            continue
        if "input" in path.parts:
            continue
        if folder_is_handmatig(path.parent):
            continue
        if " " in path.name:
            raise SystemExit(f"bestandsnaam mag geen spaties hebben: {path.name}")
        out.append(path)
    return out


def is_stale(md: Path, pdf: Path) -> bool:
    if not pdf.is_file():
        return True
    stamp = read_pdf_stamp(pdf)
    if stamp.get(FIELD_SOURCE_KIND) != SOURCE_KIND_TEKSTBLAD:
        return True
    if stamp.get(FIELD_SOURCE_SHA) != source_sha256(md):
        return True
    return False


def sync_one(md: Path, *, dry_run: bool) -> None:
    pdf = product_pdf_for_md(md)
    rel = md.relative_to(REPO_ROOT)
    print(f"  PDF  {rel} -> {pdf.name}", flush=True)
    if dry_run:
        return
    cmd = [
        sys.executable,
        "-m",
        "vsa.cli",
        "pdf",
        str(md),
        "-o",
        str(pdf),
        "--content-root",
        str(REPO_ROOT / "content-source"),
    ]
    proc = subprocess.run(cmd, cwd=str(REPO_ROOT), check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"vsa pdf faalde (exit {proc.returncode})")
    if not pdf.is_file():
        raise RuntimeError(f"PDF ontbreekt na vsa pdf: {pdf}")
    stamp_pdf(
        pdf,
        source_hash=source_sha256(md),
        source_kind=SOURCE_KIND_TEKSTBLAD,
        generated_at=utc_now_iso(),
        generator=GENERATOR_TEKSTBLAD,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Exporteer stale tekstblad-PDF vanuit .tekstblad.md."
    )
    parser.add_argument(
        "root",
        nargs="?",
        type=Path,
        default=DEFAULT_ROOT,
        help="Zoekroot (default: content-source/bibliotheek)",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Ook exporteren als PDF al bij de bron past",
    )
    args = parser.parse_args()
    root = args.root if args.root.is_absolute() else REPO_ROOT / args.root
    sources = collect_tekstblad(root)
    todo = [
        md
        for md in sources
        if args.force or is_stale(md, product_pdf_for_md(md))
    ]
    if not todo:
        print(f"Tekstblad-producten up-to-date ({len(sources)} .tekstblad.md)", flush=True)
        return 0
    print(
        f"Tekstblad-producten bijwerken: {len(todo)} van {len(sources)}",
        flush=True,
    )
    failed = 0
    for md in todo:
        print(f"== {md.relative_to(REPO_ROOT)}", flush=True)
        try:
            sync_one(md, dry_run=args.dry_run)
        except Exception as exc:  # noqa: BLE001
            print(f"  FAILED {exc}", flush=True)
            failed += 1
    if failed:
        print(f"{failed} mislukt van {len(todo)}", flush=True)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
