"""Maak sibling ``{stam}.mvsa.mxl`` + ``{stam}.mvsa.pdf`` bij bibliotheek-``.mvsa``.

Roept tooling aan: ``mvsa musicxml`` (Coria) en ``mvsa pdf`` (MuseScore +
layoutprofiel ``partituur``). Zet ``vsa-source-sha256`` + ``vsa-source-kind=mvsa``.

Slaat ``input/``, ``artefacten_handmatig`` en import-siblings ``*.mscz.mvsa``
over. CI genereert niet — alleen ``check_mvsa_products``; vernieuw lokaal met
``scripts\\mvsa-products.cmd``.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

from coria_mxl import load_score_xml, require_no_spaces, write_mxl
from ensure_bibliotheek_id import id_from_bibliotheek_path
from product_meta import (
    FIELD_SOURCE_KIND,
    FIELD_SOURCE_SHA,
    GENERATOR_MVSA,
    SOURCE_KIND_MVSA,
    read_mxl_stamp,
    read_pdf_stamp,
    source_sha256,
    stamp_mxl_source,
    stamp_pdf,
    utc_now_iso,
)
from sync_import_mvsa import is_import_mvsa
from sync_vsa_products import folder_is_handmatig

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOT = REPO_ROOT / "content-source" / "bibliotheek"


def _running_in_ci() -> bool:
    return os.environ.get("CI", "").strip().lower() in {"1", "true", "yes"}


def product_mxl_for_mvsa(mvsa: Path) -> Path:
    """``naam.mvsa`` → ``naam.mvsa.mxl``."""
    return mvsa.with_suffix(".mvsa.mxl")


def product_pdf_for_mvsa(mvsa: Path) -> Path:
    """``naam.mvsa`` → ``naam.mvsa.pdf``."""
    return mvsa.with_suffix(".mvsa.pdf")


def collect_mvsa(root: Path) -> list[Path]:
    """Canonieke bibliotheek-``.mvsa`` (geen import-``.mscz.mvsa``)."""
    out: list[Path] = []
    if not root.is_dir():
        return out
    for path in sorted(root.rglob("*.mvsa")):
        if not path.is_file():
            continue
        if is_import_mvsa(path):
            continue
        if "input" in path.parts:
            continue
        if folder_is_handmatig(path.parent):
            continue
        require_no_spaces(path)
        out.append(path)
    return out


def _stamp_ok_mxl(mxl: Path, source_hash: str) -> bool:
    if not mxl.is_file():
        return False
    stamp = read_mxl_stamp(mxl)
    if stamp.get(FIELD_SOURCE_KIND, SOURCE_KIND_MVSA) not in {
        "",
        SOURCE_KIND_MVSA,
    }:
        return False
    return stamp.get(FIELD_SOURCE_SHA, "") == source_hash


def _stamp_ok_pdf(pdf: Path, source_hash: str) -> bool:
    if not pdf.is_file():
        return False
    stamp = read_pdf_stamp(pdf)
    if stamp.get(FIELD_SOURCE_KIND, SOURCE_KIND_MVSA) not in {
        "",
        SOURCE_KIND_MVSA,
    }:
        return False
    return stamp.get(FIELD_SOURCE_SHA, "") == source_hash


def is_stale(mvsa: Path) -> tuple[bool, bool]:
    """Return (need_mxl, need_pdf)."""
    digest = source_sha256(mvsa)
    need_mxl = not _stamp_ok_mxl(product_mxl_for_mvsa(mvsa), digest)
    need_pdf = not _stamp_ok_pdf(product_pdf_for_mvsa(mvsa), digest)
    return need_mxl, need_pdf


def _run_mvsa_musicxml(mvsa: Path, mxl: Path) -> None:
    cmd = ["mvsa", "musicxml", str(mvsa), "-o", str(mxl)]
    subprocess.check_call(cmd, cwd=str(REPO_ROOT))


def _run_mvsa_pdf(mvsa: Path, pdf: Path, *, bibliotheek_id: str | None) -> None:
    cmd = [
        "mvsa",
        "pdf",
        str(mvsa),
        "-o",
        str(pdf),
        "--layout",
        "partituur",
    ]
    if bibliotheek_id:
        cmd.extend(["--bibliotheek-id", bibliotheek_id])
    subprocess.check_call(cmd, cwd=str(REPO_ROOT))


def sync_one(
    mvsa: Path,
    *,
    need_mxl: bool,
    need_pdf: bool,
    dry_run: bool,
) -> None:
    rel = mvsa.relative_to(REPO_ROOT)
    digest = source_sha256(mvsa)
    generated_at = utc_now_iso()
    mxl = product_mxl_for_mvsa(mvsa)
    pdf = product_pdf_for_mvsa(mvsa)
    bib = id_from_bibliotheek_path(mvsa)

    if need_mxl:
        print(f"  MXL  {rel} -> {mxl.name}", flush=True)
        if not dry_run:
            require_no_spaces(mxl)
            _run_mvsa_musicxml(mvsa, mxl)
            if not mxl.is_file():
                raise RuntimeError(f"MXL ontbreekt na mvsa musicxml: {mxl}")
            root = load_score_xml(mxl)
            stamp_mxl_source(
                root,
                source_hash=digest,
                source_kind=SOURCE_KIND_MVSA,
                generated_at=generated_at,
                generator=GENERATOR_MVSA,
            )
            write_mxl(mxl, root)

    if need_pdf:
        print(f"  PDF  {rel} -> {pdf.name}", flush=True)
        if not dry_run:
            require_no_spaces(pdf)
            _run_mvsa_pdf(mvsa, pdf, bibliotheek_id=bib)
            if not pdf.is_file():
                raise RuntimeError(f"PDF ontbreekt na mvsa pdf: {pdf}")
            stamp_pdf(
                pdf,
                source_hash=digest,
                source_kind=SOURCE_KIND_MVSA,
                generated_at=generated_at,
                generator=GENERATOR_MVSA,
            )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Exporteer stale Coria-.mxl + PDF vanuit bibliotheek-.mvsa."
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
    args = parser.parse_args(argv)
    root = args.root if args.root.is_absolute() else REPO_ROOT / args.root
    sources = collect_mvsa(root)
    todo: list[tuple[Path, bool, bool]] = []
    for mvsa in sources:
        if args.force:
            todo.append((mvsa, True, True))
        else:
            need_mxl, need_pdf = is_stale(mvsa)
            if need_mxl or need_pdf:
                todo.append((mvsa, need_mxl, need_pdf))
    if not todo:
        print(f"MVSA-producten up-to-date ({len(sources)} .mvsa)", flush=True)
        return 0

    need_any_pdf = any(need_pdf for _, _, need_pdf in todo)
    if need_any_pdf:
        from vsa.musescore_cli import find_musescore

        if find_musescore() is None:
            # Probeer MXL-only verder; PDF later lokaal.
            mxl_only = [(m, nm, False) for m, nm, np in todo if nm]
            pdf_pending = [(m, np) for m, nm, np in todo if np]
            if pdf_pending:
                print(
                    f"{len(pdf_pending)} stale .mvsa.pdf; MuseScore ontbreekt.",
                    flush=True,
                )
                if _running_in_ci():
                    print("CI: sla MuseScore-PDF over; MXL wel bijwerken.", flush=True)
                else:
                    print(r"Installeer MuseScore 4 of: scripts\mvsa-products.cmd", flush=True)
                    for mscz_path, _ in pdf_pending:
                        print(
                            f"  - {mscz_path.name} -> {product_pdf_for_mvsa(mscz_path).name}",
                            flush=True,
                        )
                    if not mxl_only:
                        return 1
            todo = mxl_only if mxl_only else []
            if not todo:
                return 0 if _running_in_ci() else 1

    print(f"MVSA-producten bijwerken: {len(todo)} van {len(sources)}", flush=True)
    failed = 0
    for mvsa, need_mxl, need_pdf in todo:
        print(f"== {mvsa.relative_to(REPO_ROOT)}", flush=True)
        try:
            sync_one(
                mvsa, need_mxl=need_mxl, need_pdf=need_pdf, dry_run=args.dry_run
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
