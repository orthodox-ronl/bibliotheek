"""Maak sibling ``{stam}.mscz.pdf`` + ``{stam}.mscz.mxl`` bij basispartituur-``.mscz``.

Roept tooling aan: ``mscz mxl`` (Coria) en ``vsa.musescore_cli`` (PDF).
Zet ``vsa-partituur-sha256``. Slaat ``artefacten_handmatig`` en ``*.print.mscz``
over. CI genereert niet — alleen ``check_mscz_products``; vernieuw lokaal met
``scripts\\mscz-products.cmd``.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

from coria_mxl import load_score_xml, require_no_spaces, write_mxl
from product_meta import (
    partituur_sha256,
    read_mxl_stamp,
    read_pdf_stamp,
    stamp_mxl_partituur,
    stamp_pdf,
    stamp_sha_from_dict,
    utc_now_iso,
)
from sync_vsa_products import folder_is_handmatig

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOT = REPO_ROOT / "content-source" / "bibliotheek"


def _running_in_ci() -> bool:
    return os.environ.get("CI", "").strip().lower() in {"1", "true", "yes"}


def product_pdf_for_mscz(mscz: Path) -> Path:
    """``naam.mscz`` → ``naam.mscz.pdf``."""
    return mscz.with_suffix(".mscz.pdf")


def product_mxl_for_mscz(mscz: Path) -> Path:
    """``naam.mscz`` → ``naam.mscz.mxl``."""
    return mscz.with_suffix(".mscz.mxl")


def legacy_pdf_for_mscz(mscz: Path) -> Path:
    return mscz.with_suffix(".pdf")


def legacy_mxl_for_mscz(mscz: Path) -> Path:
    return mscz.with_suffix(".mxl")


def is_print_mscz(path: Path) -> bool:
    name = path.name.lower()
    return name.endswith(".print.mscz") or ".print." in name


def collect_mscz(root: Path) -> list[Path]:
    out: list[Path] = []
    if not root.is_dir():
        return out
    for path in sorted(root.rglob("*.mscz")):
        if is_print_mscz(path):
            continue
        if "input" in path.parts:
            continue
        if folder_is_handmatig(path.parent):
            continue
        require_no_spaces(path)
        out.append(path)
    return out


def _stamp_ok_pdf(pdf: Path, digest: str) -> bool:
    if not pdf.is_file():
        return False
    return stamp_sha_from_dict(read_pdf_stamp(pdf)) == digest


def _stamp_ok_mxl(mxl: Path, digest: str) -> bool:
    if not mxl.is_file():
        return False
    return stamp_sha_from_dict(read_mxl_stamp(mxl)) == digest


def is_stale(mscz: Path) -> tuple[bool, bool]:
    """Return (need_pdf, need_mxl)."""
    digest = partituur_sha256(mscz)
    pdf = product_pdf_for_mscz(mscz)
    mxl = product_mxl_for_mscz(mscz)
    need_pdf = not _stamp_ok_pdf(pdf, digest)
    need_mxl = not _stamp_ok_mxl(mxl, digest)
    # Legacy korte namen tellen mee tot migratie (geen regenerate als stamp klopt).
    if need_pdf and _stamp_ok_pdf(legacy_pdf_for_mscz(mscz), digest):
        need_pdf = False
    if need_mxl and _stamp_ok_mxl(legacy_mxl_for_mscz(mscz), digest):
        need_mxl = False
    return need_pdf, need_mxl


def _run_mscz_mxl(mscz: Path, mxl: Path) -> None:
    cmd = ["mscz", "mxl", str(mscz), "-o", str(mxl)]
    subprocess.check_call(cmd, cwd=str(REPO_ROOT))


def _export_pdf(mscz: Path, pdf: Path) -> None:
    from vsa.musescore_cli import convert_with_musescore

    convert_with_musescore(mscz, pdf)


def _remove_legacy(canonical: Path, legacy: Path) -> None:
    if not legacy.is_file():
        return
    if legacy.resolve() == canonical.resolve():
        return
    print(f"  remove legacy {legacy.name}", flush=True)
    legacy.unlink()


def sync_one(
    mscz: Path,
    *,
    need_pdf: bool,
    need_mxl: bool,
    dry_run: bool,
) -> None:
    rel = mscz.relative_to(REPO_ROOT)
    digest = partituur_sha256(mscz)
    generated_at = utc_now_iso()
    pdf = product_pdf_for_mscz(mscz)
    mxl = product_mxl_for_mscz(mscz)

    if need_pdf:
        print(f"  PDF  {rel} -> {pdf.name}", flush=True)
        if not dry_run:
            require_no_spaces(pdf)
            _export_pdf(mscz, pdf)
            stamp_pdf(pdf, partituur_hash=digest, generated_at=generated_at)
            _remove_legacy(pdf, legacy_pdf_for_mscz(mscz))
            # Oude representatie-id-namen
            partituur_pdf = mscz.with_suffix(".partituur.pdf")
            _remove_legacy(pdf, partituur_pdf)

    if need_mxl:
        print(f"  MXL  {rel} -> {mxl.name}", flush=True)
        if not dry_run:
            require_no_spaces(mxl)
            _run_mscz_mxl(mscz, mxl)
            root = load_score_xml(mxl)
            stamp_mxl_partituur(
                root, partituur_hash=digest, generated_at=generated_at
            )
            write_mxl(mxl, root)
            _remove_legacy(mxl, legacy_mxl_for_mscz(mscz))
            partituur_mxl = mscz.with_suffix(".partituur.mxl")
            _remove_legacy(mxl, partituur_mxl)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Exporteer stale PDF/Coria-.mxl vanuit basispartituur-.mscz."
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
        help="Ook exporteren als producten al bij de bron passen",
    )
    args = parser.parse_args()
    root = args.root if args.root.is_absolute() else REPO_ROOT / args.root
    msczs = collect_mscz(root)
    todo: list[tuple[Path, bool, bool]] = []
    for mscz in msczs:
        if args.force:
            todo.append((mscz, True, True))
        else:
            need_pdf, need_mxl = is_stale(mscz)
            if need_pdf or need_mxl:
                todo.append((mscz, need_pdf, need_mxl))
    if not todo:
        print(f"MSCZ-producten up-to-date ({len(msczs)} .mscz)", flush=True)
        return 0

    # MuseScore / mscz CLI nodig
    from vsa.musescore_cli import find_musescore

    if find_musescore() is None:
        print(
            f"{len(todo)} stale PDF/MXL t.o.v. .mscz, MuseScore ontbreekt.",
            flush=True,
        )
        if _running_in_ci():
            print("CI: sla lokale MuseScore-export over.", flush=True)
            return 0
        print(r"Installeer MuseScore 4 of: scripts\mscz-products.cmd", flush=True)
        for mscz, need_pdf, need_mxl in todo:
            bits = [mscz.name]
            if need_pdf:
                bits.append(product_pdf_for_mscz(mscz).name)
            if need_mxl:
                bits.append(product_mxl_for_mscz(mscz).name)
            print(f"  - {' / '.join(bits)}", flush=True)
        return 1

    print(f"MSCZ-producten bijwerken: {len(todo)} van {len(msczs)}", flush=True)
    failed = 0
    for mscz, need_pdf, need_mxl in todo:
        print(f"== {mscz.relative_to(REPO_ROOT)}", flush=True)
        try:
            sync_one(
                mscz, need_pdf=need_pdf, need_mxl=need_mxl, dry_run=args.dry_run
            )
        except Exception as exc:  # noqa: BLE001
            print(f"  FAILED {exc}", flush=True)
            failed += 1
    if failed:
        print(f"{failed} mislukt van {len(todo)}", flush=True)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
