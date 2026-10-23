"""Maak sibling ``{stam}.mscz.mxl`` + ``{stam}.mscz.svg`` bij basispartituur-``.mscz``.

Roept tooling aan: ``mscz mxl`` (Coria) en ``mvsa svg`` (scherm). A4-``.mscz.pdf``
is geen verplicht product meer (blad = ``index.pagina.pdf``); PDF-export blijft
in ``sync_one`` voor optioneel herstel. Zet ``vsa-partituur-sha256``.
Slaat ``artefacten_handmatig`` en ``*.print.mscz`` over. CI genereert niet —
alleen ``check_mscz_products``; vernieuw lokaal met ``scripts\\mscz-products.cmd``.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Sequence

from coria_mxl import (
    apply_playback_accidentals,
    load_score_xml,
    require_no_spaces,
    sanitize_coria_importer,
    write_mxl,
)
from product_kind import (
    DEFAULT_ROOT,
    REPO_ROOT,
    ProductSlot,
    catalog_eligible,
    main_for_kind,
)
from product_meta import (
    FIELD_SOURCE_SHA,
    GENERATOR_MSCZ,
    SOURCE_KIND_PARTITUUR,
    partituur_sha256,
    read_mxl_stamp,
    read_pdf_stamp,
    read_svg_stamp,
    set_mxl_identification_source,
    stamp_mxl_partituur,
    stamp_pdf,
    stamp_sha_from_dict,
    stamp_svg,
    utc_now_iso,
)
from product_regen import RegenPolicy, list_source_paths, mxl_contract_ok
from sync_vsa_products import folder_is_handmatig

_SVG_PAGE_RE = re.compile(r"-(\d+)\.svg$", re.IGNORECASE)


def product_pdf_for_mscz(mscz: Path) -> Path:
    """``naam.mscz`` → ``naam.mscz.pdf``."""
    return mscz.with_suffix(".mscz.pdf")


def product_mxl_for_mscz(mscz: Path) -> Path:
    """``naam.mscz`` → ``naam.mscz.mxl``."""
    return mscz.with_suffix(".mscz.mxl")


def product_svg_for_mscz(mscz: Path) -> Path:
    """``naam.mscz`` → ``naam.mscz.svg`` (scherm; bladreeks ``naam.mscz-N.svg``)."""
    return mscz.with_suffix(".mscz.svg")


def legacy_pdf_for_mscz(mscz: Path) -> Path:
    return mscz.with_suffix(".pdf")


def legacy_mxl_for_mscz(mscz: Path) -> Path:
    return mscz.with_suffix(".mxl")


def _svg_page_index(path: Path) -> int:
    match = _SVG_PAGE_RE.search(path.name)
    return int(match.group(1)) if match else 0


def mscz_svg_outputs(mscz: Path) -> list[Path]:
    """Bestaande scherm-SVG('s) bij een ``.mscz`` (enkel of bladreeks)."""
    dest = product_svg_for_mscz(mscz)
    pages = sorted(
        dest.parent.glob(f"{dest.stem}-*.svg"),
        key=_svg_page_index,
    )
    if dest.is_file():
        return [dest, *pages] if pages else [dest]
    return pages


def is_print_mscz(path: Path) -> bool:
    name = path.name.lower()
    return name.endswith(".print.mscz") or ".print." in name


def collect_mscz(root: Path) -> list[Path]:
    out: list[Path] = []
    for path in list_source_paths(root, pattern="*.mscz"):
        if path.suffix.lower() != ".mscz":
            continue
        if is_print_mscz(path):
            continue
        if not catalog_eligible(path, folder_is_handmatig=folder_is_handmatig):
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


def _stamp_ok_svg(svg: Path, digest: str) -> bool:
    if not svg.is_file():
        return False
    stamp = read_svg_stamp(svg)
    got = stamp.get(FIELD_SOURCE_SHA) or stamp_sha_from_dict(stamp)
    return got == digest


def _svg_stamps_ok(mscz: Path, digest: str) -> bool:
    outs = mscz_svg_outputs(mscz)
    if not outs:
        return False
    return all(_stamp_ok_svg(p, digest) for p in outs)


def is_stale(mscz: Path) -> tuple[bool, bool]:
    """Return (need_mxl, need_svg) — product-PDF is geen sync-slot meer."""
    digest = partituur_sha256(mscz)
    mxl = product_mxl_for_mscz(mscz)
    need_mxl = not _stamp_ok_mxl(mxl, digest)
    need_svg = not _svg_stamps_ok(mscz, digest)
    if need_mxl and _stamp_ok_mxl(legacy_mxl_for_mscz(mscz), digest):
        need_mxl = False
    return need_mxl, need_svg


def _run_mscz_mxl(mscz: Path, mxl: Path) -> None:
    cmd = ["mscz", "mxl", str(mscz), "-o", str(mxl)]
    subprocess.check_call(cmd, cwd=str(REPO_ROOT))


def _export_pdf(mscz: Path, pdf: Path) -> None:
    from vsa.musescore_cli import convert_with_musescore

    convert_with_musescore(mscz, pdf)


def _run_mscz_svg(mscz: Path, svg: Path) -> list[Path]:
    """Exporteer scherm-SVG; bij multi-page: ``stem-N.svg`` naast ``-o``."""
    if svg.exists():
        svg.unlink()
    for stale in svg.parent.glob(f"{svg.stem}-*.svg"):
        stale.unlink(missing_ok=True)
    cmd = ["mvsa", "svg", str(mscz), "-o", str(svg)]
    subprocess.check_call(cmd, cwd=str(REPO_ROOT))
    outs = mscz_svg_outputs(mscz)
    if not outs:
        raise RuntimeError(f"SVG ontbreekt na mvsa svg: {svg}")
    return outs


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
    need_svg: bool,
    dry_run: bool,
) -> None:
    rel = mscz.relative_to(REPO_ROOT)
    digest = partituur_sha256(mscz)
    generated_at = utc_now_iso()
    pdf = product_pdf_for_mscz(mscz)
    mxl = product_mxl_for_mscz(mscz)
    svg = product_svg_for_mscz(mscz)

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
            # Zelfde Coria-sanitize als mvsa-products (o.a. notehead).
            sanitize_coria_importer(root)
            apply_playback_accidentals(root)
            stamp_mxl_partituur(
                root, partituur_hash=digest, generated_at=generated_at
            )
            from vsa_bron import bron_uitgangspunt_near

            bron = bron_uitgangspunt_near(mscz)
            if bron:
                set_mxl_identification_source(root, bron)
            write_mxl(mxl, root)
            _remove_legacy(mxl, legacy_mxl_for_mscz(mscz))
            partituur_mxl = mscz.with_suffix(".partituur.mxl")
            _remove_legacy(mxl, partituur_mxl)

    if need_svg:
        print(f"  SVG  {rel} -> {svg.name}", flush=True)
        if not dry_run:
            require_no_spaces(svg)
            outs = _run_mscz_svg(mscz, svg)
            for out in outs:
                stamp_svg(
                    out,
                    source_hash=digest,
                    source_kind=SOURCE_KIND_PARTITUUR,
                    generated_at=generated_at,
                    generator=GENERATOR_MSCZ,
                )


class MsczKind:
    id = "mscz"
    label = "MSCZ-producten"
    source_noun = " .mscz"
    fix_cmd = r"scripts\mscz-products.cmd"

    def collect(self, root: Path) -> list[Path]:
        return collect_mscz(root)

    def slots_for(self, source: Path, policy: RegenPolicy) -> list[ProductSlot]:
        digest = partituur_sha256(source)
        mxl = product_mxl_for_mscz(source)
        svg = product_svg_for_mscz(source)
        mxl_exists = mxl.is_file() or legacy_mxl_for_mscz(source).is_file()
        mxl_stamp_ok = _stamp_ok_mxl(mxl, digest) or _stamp_ok_mxl(
            legacy_mxl_for_mscz(source), digest
        )
        svg_outs = mscz_svg_outputs(source)
        svg_exists = bool(svg_outs)
        svg_stamp_ok = _svg_stamps_ok(source, digest)
        mxl_path = mxl if mxl.is_file() else legacy_mxl_for_mscz(source)
        contract = None
        if policy.invalid and mxl_path.is_file():
            contract = mxl_contract_ok(mxl_path, profile="satb")
        return [
            ProductSlot(
                path=mxl,
                exists=mxl_exists,
                stamp_ok=mxl_stamp_ok,
                contract_ok=contract,
                needs_musescore=True,
            ),
            ProductSlot(
                path=svg,
                exists=svg_exists,
                stamp_ok=svg_stamp_ok,
                contract_ok=None,
                needs_musescore=True,
            ),
        ]

    def sync(self, source: Path, *, need: Sequence[bool], dry_run: bool) -> None:
        need_mxl = bool(need[0]) if len(need) > 0 else False
        need_svg = bool(need[1]) if len(need) > 1 else False
        if need_mxl or need_svg:
            sync_one(
                source,
                need_pdf=False,
                need_mxl=need_mxl,
                need_svg=need_svg,
                dry_run=dry_run,
            )


KIND = MsczKind()


def main(argv: list[str] | None = None) -> int:
    return main_for_kind(
        KIND,
        argv,
        description=(
            "Exporteer stale Coria-.mxl en scherm-.mscz.svg "
            "vanuit basispartituur-.mscz "
            "(geen A4-product-PDF; blad = index.pagina.pdf)."
        ),
        default_root=DEFAULT_ROOT,
    )


if __name__ == "__main__":
    raise SystemExit(main())
