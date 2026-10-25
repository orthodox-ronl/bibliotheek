"""Maak siblings bij catalogus-``.mvsa``.

Export via tooling ``mvsa products`` (schrijft schema-2 products-meta,
inclusief bladreeks ``svg-1``…). Bibliotheek schrijft die meta niet
opnieuw. Geen in-file versheidstempels (versheid = meta).
A4-``.mvsa.pdf`` is geen verplicht product (blad = ``index.md.pdf``);
PDF-export blijft voor optioneel herstel.

Slaat ``input/``, ``manueel/manual`` en import-siblings ``*.mscz.mvsa``
over. CI genereert niet — alleen ``check_mvsa_products``; vernieuw lokaal met
``scripts\\products.cmd --kinds mvsa``.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from typing import Sequence

_SVG_PAGE_RE = re.compile(r"-(\d+)\.svg$", re.IGNORECASE)

from coria_mxl import require_no_spaces
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
    stamp_pdf,
    utc_now_iso,
)
from product_regen import RegenPolicy, list_source_paths, mxl_contract_ok
from street_meta import stamp_ok_or_meta
from sync_import_mvsa import is_import_mvsa
from sync_vsa_products import folder_is_handmatig

_MVSA_META_KEYS = {"mxl", "score-ir", "from-ir"}


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


def _svg_page_index(path: Path) -> int:
    match = _SVG_PAGE_RE.search(path.name)
    return int(match.group(1)) if match else 0


def mvsa_svg_outputs(mvsa: Path) -> list[Path]:
    """Bestaande scherm-SVG('s) bij een ``.mvsa`` (enkel of bladreeks)."""
    dest = product_svg_for_mvsa(mvsa)
    pages = sorted(
        dest.parent.glob(f"{dest.stem}-*.svg"),
        key=_svg_page_index,
    )
    if dest.is_file():
        return [dest, *pages] if pages else [dest]
    return pages


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


def _svg_stamps_ok(mvsa: Path, digest: str) -> bool:
    outs = mvsa_svg_outputs(mvsa)
    if not outs:
        return False
    return all(_stamp_ok_svg(p, digest) for p in outs)


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
    need_svg = (not _svg_stamps_ok(mvsa, digest)) and (
        not _stamp_ok_from_ir(product_from_ir_musicxml_for_mvsa(mvsa), digest)
    )
    return need_mxl, need_svg, need_score_ir, need_from_ir


def _run_mvsa_products(mvsa: Path, *, skip_svg: bool) -> None:
    """Kale export via tooling ``mvsa products`` (+ optioneel ``--skip-svg``)."""
    cmd = [
        sys.executable,
        "-m",
        "vsa.cli_mvsa",
        "products",
        "--force",
        str(mvsa),
    ]
    if skip_svg:
        cmd.append("--skip-svg")
    subprocess.check_call(cmd, cwd=str(REPO_ROOT))
    mxl = product_mxl_for_mvsa(mvsa)
    score_ir = product_score_ir_for_mvsa(mvsa)
    from_ir = product_from_ir_musicxml_for_mvsa(mvsa)
    if not mxl.is_file():
        raise RuntimeError(f"MXL ontbreekt na mvsa products: {mxl}")
    if not score_ir.is_file():
        raise RuntimeError(f"Score-IR ontbreekt na mvsa products: {score_ir}")
    if not from_ir.is_file():
        raise RuntimeError(f"from-ir MusicXML ontbreekt na mvsa products: {from_ir}")
    if not skip_svg:
        outs = mvsa_svg_outputs(mvsa)
        if not outs:
            raise RuntimeError(
                f"SVG ontbreekt na mvsa products: {product_svg_for_mvsa(mvsa)}"
            )


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
    need_svg: bool,
    need_score_ir: bool,
    need_from_ir: bool,
    dry_run: bool,
) -> None:
    rel = mvsa.relative_to(REPO_ROOT)
    digest = source_sha256(mvsa)
    generated_at = utc_now_iso()
    pdf = product_pdf_for_mvsa(mvsa)
    bib = id_from_catalogus_path(mvsa)

    need_export = need_mxl or need_svg or need_score_ir or need_from_ir
    skip_svg = not need_svg
    if need_export:
        svg_note = "mxl+ir+svg" if need_svg else "mxl+ir (--skip-svg)"
        print(f"  EXP  {rel} -> mvsa products ({svg_note})", flush=True)
    if need_pdf:
        print(f"  PDF  {rel} -> {pdf.name}", flush=True)
    if dry_run:
        return

    if need_export:
        _run_mvsa_products(mvsa, skip_svg=skip_svg)

    if need_pdf:
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


class MvsaKind:
    id = "mvsa"
    label = "MVSA-producten"
    source_noun = " .mvsa"
    fix_cmd = r"scripts\products.cmd --kinds mvsa"

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
        from_ir_ok = stamp_ok_or_meta(
            source,
            required_keys=_MVSA_META_KEYS,
            stamp_ok=_stamp_ok_from_ir(from_ir, digest),
        )
        svg_outs = mvsa_svg_outputs(source)
        svg_exists = bool(svg_outs)
        # Ontbrekende SVG mag als from-ir scherm dekt (OSMD); anders verplicht.
        svg_covered = svg_exists or from_ir_ok
        svg_stamp_ok = (
            all(_stamp_ok_svg(p, digest) for p in svg_outs)
            if svg_exists
            else from_ir_ok
        )
        return [
            ProductSlot(
                path=mxl,
                exists=mxl_exists,
                stamp_ok=stamp_ok_or_meta(
                    source,
                    required_keys=_MVSA_META_KEYS,
                    stamp_ok=_stamp_ok_mxl(mxl, digest),
                ),
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
                stamp_ok=stamp_ok_or_meta(
                    source,
                    required_keys=_MVSA_META_KEYS,
                    stamp_ok=_stamp_ok_score_ir(score_ir, digest),
                ),
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
            "(via mvsa products; geen A4-product-PDF; blad = index.md.pdf)."
        ),
        default_root=DEFAULT_ROOT,
    )


if __name__ == "__main__":
    raise SystemExit(main())
