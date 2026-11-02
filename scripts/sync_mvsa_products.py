"""Maak siblings bij catalogus-``.mvsa``.

Export per slot: ``mvsa mxl``, ``mvsa svg``, ``mvsa score-ir``
(+ ``--musicxml`` voor from-ir) — geen atomair ``mvsa products`` (dat zou
ook mp3/pdf/mscz meenemen). Translit-SVG’s (``.translit-nls.svg`` /
``.translit-ksl.svg``) apart via ``mvsa svg --translit-modus``; Coria
``{bron}.translit.mxl`` via ``mvsa mxl --translit-as-parts`` (§5a).
Bibliotheek merget die keys in products-meta. Geen in-file
versheidstempels (versheid = meta). A4-``.mvsa.pdf`` is geen verplicht
product (blad = ``index.md.pdf``); PDF-export blijft voor optioneel herstel.

Slaat ``input/``, ``manueel/manual`` en import-siblings ``*.mscz.mvsa``
over. CI genereert niet — alleen ``check_mvsa_products``; vernieuw lokaal met
``scripts\\products.cmd --kinds mvsa``.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Sequence

from cli_style import check_call, detail

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
from street_consumer_stamps import restamp_after_street_products
from street_meta import stamp_ok_or_meta, write_products_meta
from sync_import_mvsa import is_import_mvsa
from sync_vsa_products import folder_is_handmatig
from translit_svg_products import (
    expects_translit_mxl,
    product_translit_mxl,
    product_translit_svg,
    sync_translit_mxl,
    sync_translit_svgs,
    translit_modi_for_source,
    translit_mxl_fresh,
    translit_svgs_fresh,
)

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


def _run_mvsa_mxl(mvsa: Path) -> None:
    """Coria-``.mvsa.mxl`` via ``mvsa mxl``."""
    mxl = product_mxl_for_mvsa(mvsa)
    cmd = [
        sys.executable,
        "-m",
        "vsa.cli_mvsa",
        "mxl",
        str(mvsa),
        "-o",
        str(mxl),
    ]
    check_call(cmd, cwd=str(REPO_ROOT))
    if not mxl.is_file():
        raise RuntimeError(f"MXL ontbreekt na mvsa mxl: {mxl}")


def _run_mvsa_svg(mvsa: Path) -> None:
    """Scherm-``.mvsa.svg`` via ``mvsa svg``."""
    svg = product_svg_for_mvsa(mvsa)
    cmd = [
        sys.executable,
        "-m",
        "vsa.cli_mvsa",
        "svg",
        str(mvsa),
        "-o",
        str(svg),
    ]
    check_call(cmd, cwd=str(REPO_ROOT))
    if not mvsa_svg_outputs(mvsa):
        raise RuntimeError(f"SVG ontbreekt na mvsa svg: {svg}")


def _run_mvsa_score_ir(mvsa: Path, *, with_from_ir: bool) -> None:
    """Score-IR JSON; optioneel sibling from-ir MusicXML via ``--musicxml``."""
    score_ir = product_score_ir_for_mvsa(mvsa)
    cmd = [
        sys.executable,
        "-m",
        "vsa.cli_mvsa",
        "score-ir",
        str(mvsa),
        "-o",
        str(score_ir),
    ]
    if with_from_ir:
        cmd.append("--musicxml")
    check_call(cmd, cwd=str(REPO_ROOT))
    if not score_ir.is_file():
        raise RuntimeError(f"Score-IR ontbreekt na mvsa score-ir: {score_ir}")
    if with_from_ir:
        from_ir = product_from_ir_musicxml_for_mvsa(mvsa)
        if not from_ir.is_file():
            raise RuntimeError(
                f"from-ir MusicXML ontbreekt na mvsa score-ir --musicxml: {from_ir}"
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
    check_call(cmd, cwd=str(REPO_ROOT))


def sync_one(
    mvsa: Path,
    *,
    need_mxl: bool,
    need_pdf: bool,
    need_svg: bool,
    need_score_ir: bool,
    need_from_ir: bool,
    dry_run: bool,
    need_translit_svg: bool = False,
    need_translit_mxl: bool = False,
) -> None:
    from input_paths import rel_for_log

    rel = rel_for_log(mvsa, repo_root=REPO_ROOT)
    digest = source_sha256(mvsa)
    generated_at = utc_now_iso()
    pdf = product_pdf_for_mvsa(mvsa)
    mxl = product_mxl_for_mvsa(mvsa)
    svg = product_svg_for_mvsa(mvsa)
    score_ir = product_score_ir_for_mvsa(mvsa)
    from_ir = product_from_ir_musicxml_for_mvsa(mvsa)
    bib = id_from_catalogus_path(mvsa)

    want_translit_svg = need_translit_svg or need_svg
    # Na kale MXL-export altijd translit-MXL meenemen; anders alleen als stale.
    want_translit_mxl = need_translit_mxl or need_mxl
    if need_mxl:
        detail(f"  EXP  {rel} -> mvsa mxl")
    if need_score_ir or need_from_ir:
        ir_note = "score-ir+from-ir" if need_from_ir else "score-ir"
        detail(f"  EXP  {rel} -> mvsa score-ir ({ir_note})")
    if need_svg:
        detail(f"  EXP  {rel} -> mvsa svg")
    if need_pdf:
        detail(f"  PDF  {rel} -> {pdf.name}")
    if dry_run:
        if want_translit_svg:
            sync_translit_svgs(mvsa, dry_run=True, force=need_svg)
        if want_translit_mxl:
            sync_translit_mxl(mvsa, dry_run=True, force=need_mxl)
        return

    meta_products: dict[str, Path] = {}
    if need_mxl:
        _run_mvsa_mxl(mvsa)
        meta_products["mxl"] = mxl
    if need_score_ir or need_from_ir:
        # Alleen from-ir stale: score-ir --musicxml vernieuwt IR ook (nodig als bron).
        _run_mvsa_score_ir(mvsa, with_from_ir=need_from_ir)
        meta_products["score-ir"] = score_ir
        if need_from_ir:
            meta_products["from-ir"] = from_ir
    if need_svg:
        _run_mvsa_svg(mvsa)
        meta_products["svg"] = svg
    if meta_products:
        write_products_meta(mvsa, meta_products, merge=True)
        # Bestaande lyrics/mp3 (van eerdere products-run) opnieuw stempelen.
        restamp_after_street_products(mvsa)

    if want_translit_svg:
        sync_translit_svgs(mvsa, dry_run=False, force=need_svg)

    if want_translit_mxl:
        sync_translit_mxl(mvsa, dry_run=False, force=need_mxl)

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
        slots = [
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
        modi = translit_modi_for_source(source)
        if modi:
            first = product_translit_svg(source, modi[0])
            fresh = translit_svgs_fresh(source, digest)
            slots.append(
                ProductSlot(
                    path=first,
                    exists=fresh
                    or all(
                        product_translit_svg(source, m).is_file() for m in modi
                    ),
                    stamp_ok=fresh,
                    contract_ok=None,
                    # MuseScore-keten (zelfde als kale mvsa svg).
                    needs_musescore=True,
                )
            )
        if expects_translit_mxl(source):
            tmxl = product_translit_mxl(source)
            tmxl_fresh = translit_mxl_fresh(source, digest)
            slots.append(
                ProductSlot(
                    path=tmxl,
                    exists=tmxl_fresh or tmxl.is_file(),
                    stamp_ok=tmxl_fresh,
                    contract_ok=None,
                    needs_musescore=False,
                )
            )
        return slots

    def sync(self, source: Path, *, need: Sequence[bool], dry_run: bool) -> None:
        need_mxl = bool(need[0]) if len(need) > 0 else False
        need_svg = bool(need[1]) if len(need) > 1 else False
        need_score_ir = bool(need[2]) if len(need) > 2 else False
        need_from_ir = bool(need[3]) if len(need) > 3 else False
        # Slot 4 = translit-SVG (alleen als modi); slot 5 = translit-MXL
        # (alleen als verwacht). Index schuift als SVG-slot ontbreekt.
        idx = 4
        need_translit_svg = False
        if translit_modi_for_source(source):
            need_translit_svg = bool(need[idx]) if len(need) > idx else False
            idx += 1
        need_translit_mxl = False
        if expects_translit_mxl(source):
            need_translit_mxl = bool(need[idx]) if len(need) > idx else False
        if (
            need_mxl
            or need_svg
            or need_score_ir
            or need_from_ir
            or need_translit_svg
            or need_translit_mxl
        ):
            sync_one(
                source,
                need_mxl=need_mxl,
                need_pdf=False,
                need_svg=need_svg,
                need_score_ir=need_score_ir,
                need_from_ir=need_from_ir,
                dry_run=dry_run,
                need_translit_svg=need_translit_svg,
                need_translit_mxl=need_translit_mxl,
            )


KIND = MvsaKind()


def main(argv: list[str] | None = None) -> int:
    return main_for_kind(
        KIND,
        argv,
        description=(
            "Exporteer stale Coria-.mxl + koormap-SVG + Score-IR "
            "(+ from-ir MusicXML) vanuit bibliotheek-.mvsa "
            "(via mvsa mxl / svg / score-ir; geen A4-product-PDF; "
            "blad = index.md.pdf)."
        ),
        default_root=DEFAULT_ROOT,
    )


if __name__ == "__main__":
    raise SystemExit(main())
