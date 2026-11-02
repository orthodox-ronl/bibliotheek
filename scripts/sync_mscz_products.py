"""Maak sibling ``{stam}.mscz.mxl`` + ``{stam}.mscz.svg`` bij basispartituur-``.mscz``.

Tall compacte SVG (één bestand; geen A4-bladreeks).

Export per slot: ``mscz mxl`` en/of ``mscz svg`` (geen atomair
``mscz products`` — die zou ook mp3/pdf/IR meenemen). Daarna optioneel
Coria-bron-``identification`` op de MXL (wijzigt bytes) → meta mergen.
Legacy-opruim. Geen in-file versheidstempels (versheid = meta).
A4-``.mscz.pdf`` is geen verplicht product (blad = ``index.md.pdf``);
PDF-export blijft voor optioneel herstel. Slaat ``manueel/manual``,
``*.print.mscz`` en afgeleide ``*.vsa.mscz`` / ``*.mvsa.mscz`` over
(tenzij expliciet CLI-bestandspad). CI genereert niet — alleen
``check_mscz_products``; vernieuw lokaal met
``scripts\\products.cmd --kinds mscz``.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Sequence

from cli_style import check_call, detail
from coria_mxl import load_score_xml, require_no_spaces, write_mxl
from product_kind import (
    DEFAULT_ROOT,
    REPO_ROOT,
    ProductSlot,
    catalog_eligible,
    main_for_kind,
)
from product_meta import (
    FIELD_SOURCE_SHA,
    partituur_sha256,
    read_mxl_stamp,
    read_pdf_stamp,
    read_svg_stamp,
    set_mxl_identification_source,
    stamp_pdf,
    stamp_sha_from_dict,
    utc_now_iso,
)
from product_regen import RegenPolicy, list_source_paths, mxl_contract_ok
from score_filenames import is_derived_mscz
from street_consumer_stamps import restamp_after_street_products
from street_meta import stamp_ok_or_meta, write_products_meta
from sync_vsa_products import folder_is_handmatig



def product_pdf_for_mscz(mscz: Path) -> Path:
    """``naam.mscz`` → ``naam.mscz.pdf``."""
    return mscz.with_suffix(".mscz.pdf")


def product_mxl_for_mscz(mscz: Path) -> Path:
    """``naam.mscz`` → ``naam.mscz.mxl``."""
    return mscz.with_suffix(".mscz.mxl")


def product_svg_for_mscz(mscz: Path) -> Path:
    """``naam.mscz`` → ``naam.mscz.svg`` (tall compacte scherm-/print-SVG)."""
    return mscz.with_suffix(".mscz.svg")


def legacy_pdf_for_mscz(mscz: Path) -> Path:
    return mscz.with_suffix(".pdf")


def legacy_mxl_for_mscz(mscz: Path) -> Path:
    return mscz.with_suffix(".mxl")


def mscz_svg_outputs(mscz: Path) -> list[Path]:
    """Bestaande tall scherm-SVG bij een ``.mscz`` (één sibling, geen bladreeks)."""
    dest = product_svg_for_mscz(mscz)
    return [dest] if dest.is_file() else []


def is_print_mscz(path: Path) -> bool:
    name = path.name.lower()
    return name.endswith(".print.mscz") or ".print." in name


def collect_mscz(root: Path) -> list[Path]:
    """Basispartituur-``.mscz`` onder ``root``.

    Map-scan slaat afgeleide namen over (``*.vsa.mscz``, ``*.mvsa.mscz``).
    Een expliciet CLI-bestandspad (ook met meerdere extensies) mag wél.
    """
    out: list[Path] = []
    explicit = root.is_file()
    for path in list_source_paths(root, pattern="*.mscz"):
        if path.suffix.lower() != ".mscz":
            continue
        if is_print_mscz(path):
            continue
        if not explicit and is_derived_mscz(path):
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


def _run_mscz_mxl(mscz: Path) -> None:
    """Coria-``.mscz.mxl`` via ``mscz mxl`` (sibling-pad)."""
    mxl = product_mxl_for_mscz(mscz)
    cmd = [
        sys.executable,
        "-m",
        "vsa.cli_mscz",
        "mxl",
        str(mscz),
        "-o",
        str(mxl),
    ]
    check_call(cmd, cwd=str(REPO_ROOT))
    if not mxl.is_file():
        raise RuntimeError(f"MXL ontbreekt na mscz mxl: {mxl}")


def _run_mscz_svg(mscz: Path) -> None:
    """Scherm-``.mscz.svg`` via ``mscz svg`` (sibling-pad)."""
    svg = product_svg_for_mscz(mscz)
    cmd = [
        sys.executable,
        "-m",
        "vsa.cli_mscz",
        "svg",
        str(mscz),
        "-o",
        str(svg),
    ]
    check_call(cmd, cwd=str(REPO_ROOT))
    if not mscz_svg_outputs(mscz):
        raise RuntimeError(f"SVG ontbreekt na mscz svg: {svg}")


def _export_pdf(mscz: Path, pdf: Path) -> None:
    from vsa.musescore_cli import convert_with_musescore

    convert_with_musescore(mscz, pdf)


def _remove_legacy(canonical: Path, legacy: Path) -> None:
    if not legacy.is_file():
        return
    if legacy.resolve() == canonical.resolve():
        return
    detail(f"  remove legacy {legacy.name}")
    legacy.unlink()


def _apply_bron_identification(mscz: Path, mxl: Path) -> None:
    """Zet Coria-bron in MXL indien bekend (wijzigt bytes → meta herschrijven)."""
    from vsa_bron import bron_uitgangspunt_near

    bron = bron_uitgangspunt_near(mscz)
    if not bron:
        return
    require_no_spaces(mxl)
    root = load_score_xml(mxl)
    set_mxl_identification_source(root, bron)
    write_mxl(mxl, root)


def sync_one(
    mscz: Path,
    *,
    need_pdf: bool,
    need_mxl: bool,
    need_svg: bool,
    dry_run: bool,
) -> None:
    from input_paths import rel_for_log

    rel = rel_for_log(mscz, repo_root=REPO_ROOT)
    digest = partituur_sha256(mscz)
    generated_at = utc_now_iso()
    pdf = product_pdf_for_mscz(mscz)
    mxl = product_mxl_for_mscz(mscz)
    svg = product_svg_for_mscz(mscz)

    if need_pdf:
        detail(f"  PDF  {rel} -> {pdf.name}")
    if need_mxl:
        detail(f"  EXP  {rel} -> mscz mxl")
    if need_svg:
        detail(f"  EXP  {rel} -> mscz svg")
    if dry_run:
        return

    if need_pdf:
        require_no_spaces(pdf)
        _export_pdf(mscz, pdf)
        stamp_pdf(pdf, partituur_hash=digest, generated_at=generated_at)
        _remove_legacy(pdf, legacy_pdf_for_mscz(mscz))
        _remove_legacy(pdf, mscz.with_suffix(".partituur.pdf"))

    meta_products: dict[str, Path] = {}
    if need_mxl:
        _run_mscz_mxl(mscz)
        _apply_bron_identification(mscz, mxl)
        _remove_legacy(mxl, legacy_mxl_for_mscz(mscz))
        _remove_legacy(mxl, mscz.with_suffix(".partituur.mxl"))
        meta_products["mxl"] = mxl
    if need_svg:
        _run_mscz_svg(mscz)
        meta_products["svg"] = svg
    if meta_products:
        write_products_meta(mscz, meta_products, merge=True)
        # Bestaande lyrics/mp3 (van eerdere products-run) opnieuw stempelen.
        restamp_after_street_products(mscz)


class MsczKind:
    id = "mscz"
    label = "MSCZ-producten"
    source_noun = " .mscz"
    fix_cmd = r"scripts\products.cmd --kinds mscz"

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
        meta_keys = {"mxl", "svg"} if len(svg_outs) <= 1 else {"mxl", "svg-1"}
        mxl_stamp_ok = stamp_ok_or_meta(
            source, required_keys=meta_keys, stamp_ok=mxl_stamp_ok
        )
        svg_stamp_ok = stamp_ok_or_meta(
            source, required_keys=meta_keys, stamp_ok=svg_stamp_ok
        )
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
            "(via mscz mxl / mscz svg; geen A4-product-PDF; blad = index.md.pdf)."
        ),
        default_root=DEFAULT_ROOT,
    )


if __name__ == "__main__":
    raise SystemExit(main())
