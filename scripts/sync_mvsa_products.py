"""Maak siblings bij catalogus-``.mvsa``.

Roept tooling aan: ``mvsa musicxml`` (Coria), ``mvsa svg`` (scherm-fallback),
``mvsa score-ir --musicxml`` (Score-IR JSON + OSMD-MusicXML). A4-``.mvsa.pdf``
is geen verplicht product meer (blad = ``index.pagina.pdf``); PDF-export in
``sync_one`` blijft voor optioneel herstel.
Zet ``vsa-source-sha256`` + ``vsa-source-kind=mvsa``.

Slaat ``input/``, ``artefacten_handmatig`` en import-siblings ``*.mscz.mvsa``
over. CI genereert niet — alleen ``check_mvsa_products``; vernieuw lokaal met
``scripts\\mvsa-products.cmd``.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Sequence

from coria_mxl import load_score_xml, process_existing_mxl, require_no_spaces, write_mxl
from ensure_bibliotheek_id import id_from_catalogus_path
from product_kind import (
    DEFAULT_ROOT,
    REPO_ROOT,
    ProductSlot,
    catalog_eligible,
    main_for_kind,
)
from product_meta import (
    FIELD_SOURCE_KIND,
    FIELD_SOURCE_SHA,
    GENERATOR_MVSA,
    SOURCE_KIND_MVSA,
    read_from_ir_musicxml_stamp,
    read_mxl_stamp,
    read_pdf_stamp,
    read_score_ir_stamp,
    read_svg_stamp,
    source_sha256,
    stamp_from_ir_musicxml,
    stamp_mxl_source,
    stamp_pdf,
    stamp_score_ir_json,
    stamp_svg,
    utc_now_iso,
)
from product_regen import RegenPolicy, list_source_paths, mxl_contract_ok
from sync_import_mvsa import is_import_mvsa
from sync_vsa_products import folder_is_handmatig


def product_mxl_for_mvsa(mvsa: Path) -> Path:
    """``naam.mvsa`` → ``naam.mvsa.mxl``."""
    return mvsa.with_suffix(".mvsa.mxl")


def product_pdf_for_mvsa(mvsa: Path) -> Path:
    """``naam.mvsa`` → ``naam.mvsa.pdf``."""
    return mvsa.with_suffix(".mvsa.pdf")


def product_svg_for_mvsa(mvsa: Path) -> Path:
    """``naam.mvsa`` → ``naam.mvsa.svg``."""
    return mvsa.with_suffix(".mvsa.svg")


def product_score_ir_for_mvsa(mvsa: Path) -> Path:
    """``naam.mvsa`` → ``naam.mvsa.score-ir.json``."""
    return mvsa.with_suffix(".mvsa.score-ir.json")


def product_from_ir_musicxml_for_mvsa(mvsa: Path) -> Path:
    """``naam.mvsa`` → ``naam.mvsa.from-ir.musicxml``."""
    return mvsa.with_suffix(".mvsa.from-ir.musicxml")


def collect_mvsa(root: Path) -> list[Path]:
    """Canonieke bibliotheek-``.mvsa`` (geen import-``.mscz.mvsa``)."""
    out: list[Path] = []
    for path in list_source_paths(root, pattern="*.mvsa"):
        if not path.is_file():
            continue
        if path.suffix.lower() != ".mvsa":
            continue
        if is_import_mvsa(path):
            continue
        if not catalog_eligible(path, folder_is_handmatig=folder_is_handmatig):
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


def _stamp_ok_svg(svg: Path, source_hash: str) -> bool:
    if not svg.is_file():
        return False
    stamp = read_svg_stamp(svg)
    if stamp.get(FIELD_SOURCE_KIND, SOURCE_KIND_MVSA) not in {
        "",
        SOURCE_KIND_MVSA,
    }:
        return False
    return stamp.get(FIELD_SOURCE_SHA, "") == source_hash


def _stamp_ok_score_ir(path: Path, source_hash: str) -> bool:
    if not path.is_file():
        return False
    stamp = read_score_ir_stamp(path)
    if stamp.get(FIELD_SOURCE_KIND, SOURCE_KIND_MVSA) not in {
        "",
        SOURCE_KIND_MVSA,
    }:
        return False
    return stamp.get(FIELD_SOURCE_SHA, "") == source_hash


def _stamp_ok_from_ir(path: Path, source_hash: str) -> bool:
    if not path.is_file():
        return False
    stamp = read_from_ir_musicxml_stamp(path)
    if stamp.get(FIELD_SOURCE_KIND, SOURCE_KIND_MVSA) not in {
        "",
        SOURCE_KIND_MVSA,
    }:
        return False
    return stamp.get(FIELD_SOURCE_SHA, "") == source_hash


def is_stale(mvsa: Path) -> tuple[bool, bool, bool, bool]:
    """Return (need_mxl, need_svg, need_score_ir, need_from_ir).

    Product-PDF is geen sync-slot meer.
    """
    digest = source_sha256(mvsa)
    need_mxl = not _stamp_ok_mxl(product_mxl_for_mvsa(mvsa), digest)
    need_score_ir = not _stamp_ok_score_ir(product_score_ir_for_mvsa(mvsa), digest)
    need_from_ir = not _stamp_ok_from_ir(
        product_from_ir_musicxml_for_mvsa(mvsa), digest
    )
    # SVG optioneel als from-ir scherm dekt (geen MuseScore-SVG forceren).
    need_svg = (not _stamp_ok_svg(product_svg_for_mvsa(mvsa), digest)) and (
        not _stamp_ok_from_ir(product_from_ir_musicxml_for_mvsa(mvsa), digest)
    )
    return need_mxl, need_svg, need_score_ir, need_from_ir


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


def _run_mvsa_svg(mvsa: Path, svg: Path) -> None:
    cmd = ["mvsa", "svg", str(mvsa), "-o", str(svg)]
    subprocess.check_call(cmd, cwd=str(REPO_ROOT))


def _run_mvsa_score_ir(mvsa: Path, score_ir: Path, from_ir: Path) -> None:
    cmd = [
        "mvsa",
        "score-ir",
        str(mvsa),
        "-o",
        str(score_ir),
        "--musicxml",
        str(from_ir),
    ]
    subprocess.check_call(cmd, cwd=str(REPO_ROOT))


def sync_one(
    mvsa: Path,
    *,
    need_mxl: bool,
    need_pdf: bool,
    need_svg: bool,
    need_score_ir: bool,
    need_from_ir: bool,
    dry_run: bool,
) -> None:
    rel = mvsa.relative_to(REPO_ROOT)
    digest = source_sha256(mvsa)
    generated_at = utc_now_iso()
    mxl = product_mxl_for_mvsa(mvsa)
    pdf = product_pdf_for_mvsa(mvsa)
    svg = product_svg_for_mvsa(mvsa)
    score_ir = product_score_ir_for_mvsa(mvsa)
    from_ir = product_from_ir_musicxml_for_mvsa(mvsa)
    bib = id_from_catalogus_path(mvsa)

    # Score-IR eerst (geen MuseScore): blijft slagen als SVG multipagina faalt.
    if need_score_ir or need_from_ir:
        print(
            f"  IR   {rel} -> {score_ir.name} + {from_ir.name}",
            flush=True,
        )
        if not dry_run:
            require_no_spaces(score_ir)
            require_no_spaces(from_ir)
            _run_mvsa_score_ir(mvsa, score_ir, from_ir)
            if not score_ir.is_file():
                raise RuntimeError(f"Score-IR ontbreekt na mvsa score-ir: {score_ir}")
            if not from_ir.is_file():
                raise RuntimeError(
                    f"from-ir MusicXML ontbreekt na mvsa score-ir: {from_ir}"
                )
            stamp_score_ir_json(
                score_ir,
                source_hash=digest,
                source_kind=SOURCE_KIND_MVSA,
                generated_at=generated_at,
                generator=GENERATOR_MVSA,
            )
            stamp_from_ir_musicxml(
                from_ir,
                source_hash=digest,
                source_kind=SOURCE_KIND_MVSA,
                generated_at=generated_at,
                generator=GENERATOR_MVSA,
            )

    if need_mxl:
        print(f"  MXL  {rel} -> {mxl.name}", flush=True)
        if not dry_run:
            require_no_spaces(mxl)
            _run_mvsa_musicxml(mvsa, mxl)
            if not mxl.is_file():
                raise RuntimeError(f"MXL ontbreekt na mvsa musicxml: {mxl}")
            # Strip Coria-vijandige tags (o.a. identification/source) vóór stamp.
            process_existing_mxl(mxl)
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

    if need_svg:
        print(f"  SVG  {rel} -> {svg.name}", flush=True)
        if not dry_run:
            require_no_spaces(svg)
            _run_mvsa_svg(mvsa, svg)
            if not svg.is_file():
                raise RuntimeError(f"SVG ontbreekt na mvsa svg: {svg}")
            stamp_svg(
                svg,
                source_hash=digest,
                source_kind=SOURCE_KIND_MVSA,
                generated_at=generated_at,
                generator=GENERATOR_MVSA,
            )


class MvsaKind:
    id = "mvsa"
    label = "MVSA-producten"
    source_noun = " .mvsa"
    fix_cmd = r"scripts\mvsa-products.cmd"

    def collect(self, root: Path) -> list[Path]:
        return collect_mvsa(root)

    def slots_for(self, source: Path, policy: RegenPolicy) -> list[ProductSlot]:
        digest = source_sha256(source)
        mxl = product_mxl_for_mvsa(source)
        svg = product_svg_for_mvsa(source)
        score_ir = product_score_ir_for_mvsa(source)
        from_ir = product_from_ir_musicxml_for_mvsa(source)
        mxl_exists = mxl.is_file()
        contract = (
            mxl_contract_ok(mxl, profile="satb")
            if policy.invalid and mxl_exists
            else None
        )
        from_ir_ok = _stamp_ok_from_ir(from_ir, digest)
        svg_exists = svg.is_file()
        # Ontbrekende SVG mag als from-ir scherm dekt (OSMD); anders verplicht.
        svg_covered = svg_exists or from_ir_ok
        svg_stamp_ok = (
            _stamp_ok_svg(svg, digest) if svg_exists else from_ir_ok
        )
        return [
            ProductSlot(
                path=mxl,
                exists=mxl_exists,
                stamp_ok=_stamp_ok_mxl(mxl, digest),
                contract_ok=contract,
                needs_musescore=False,
            ),
            ProductSlot(
                path=svg,
                exists=svg_covered,
                stamp_ok=svg_stamp_ok,
                contract_ok=None,
                needs_musescore=True,
            ),
            ProductSlot(
                path=score_ir,
                exists=score_ir.is_file(),
                stamp_ok=_stamp_ok_score_ir(score_ir, digest),
                contract_ok=None,
                needs_musescore=False,
            ),
            ProductSlot(
                path=from_ir,
                exists=from_ir.is_file(),
                stamp_ok=from_ir_ok,
                contract_ok=None,
                needs_musescore=False,
            ),
        ]

    def sync(self, source: Path, *, need: Sequence[bool], dry_run: bool) -> None:
        need_mxl = bool(need[0]) if len(need) > 0 else False
        need_svg = bool(need[1]) if len(need) > 1 else False
        need_score_ir = bool(need[2]) if len(need) > 2 else False
        need_from_ir = bool(need[3]) if len(need) > 3 else False
        if need_mxl or need_svg or need_score_ir or need_from_ir:
            sync_one(
                source,
                need_mxl=need_mxl,
                need_pdf=False,
                need_svg=need_svg,
                need_score_ir=need_score_ir,
                need_from_ir=need_from_ir,
                dry_run=dry_run,
            )


KIND = MvsaKind()


def main(argv: list[str] | None = None) -> int:
    return main_for_kind(
        KIND,
        argv,
        description=(
            "Exporteer stale Coria-.mxl + koormap-SVG + Score-IR "
            "(+ from-ir MusicXML) vanuit bibliotheek-.mvsa "
            "(geen A4-product-PDF; blad = index.pagina.pdf)."
        ),
        default_root=DEFAULT_ROOT,
    )


if __name__ == "__main__":
    raise SystemExit(main())
