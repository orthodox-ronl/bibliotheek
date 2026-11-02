"""Maak Coria-``.vsa.mxl`` + muziek-``.vsa.svg`` bij ``.vsa``.

Siblings: ``{stam}.vsa.mxl`` (Coria / Oefenen), ``{stam}.vsa.svg`` (scherm),
plus optioneel ``.vsa.translit-nls.svg`` / ``.vsa.translit-ksl.svg`` (§5a).
Export per slot: ``vsa musicxml --syllabify`` en/of ``vsa svg`` (geen
atomair ``vsa products`` meer — die zou ook mp3/pdf/IR meenemen).
Translit-SVG’s apart via ``vsa svg --translit-modus``. Daarna optioneel
Coria-bron-``identification`` + meta herschrijven (product-hashes),
legacy-opruim. Geen in-file versheidstempels meer (versheid = meta).
A4-``.vsa.pdf`` is geen verplicht product (blad = ``index.md.pdf``);
PDF-export blijft voor optioneel herstel.

Slaat mappen met ``manueel: true`` of ``manual: true`` over. CI genereert niet —
alleen ``check_vsa_products``; vernieuw lokaal met ``scripts\\products.cmd --kinds vsa``.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from dataclasses import dataclass
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
    FIELD_SOURCE_KIND,
    FIELD_SOURCE_SHA,
    GENERATOR_VSA_PDF,
    SOURCE_KIND_VSA,
    read_mxl_stamp,
    read_pdf_stamp,
    read_svg_stamp,
    set_mxl_identification_source,
    source_sha256,
    stamp_pdf,
    utc_now_iso,
)
from product_regen import RegenPolicy, mxl_contract_ok
from street_consumer_stamps import restamp_after_street_products
from street_meta import stamp_ok_or_meta, write_products_meta
from translit_svg_products import (
    product_translit_svg,
    sync_translit_svgs,
    translit_modi_for_source,
    translit_svgs_fresh,
)


def _fm_bool(text: str, key: str) -> bool:
    in_fm = False
    prefix = f"{key.lower()}:"
    for line in text.splitlines():
        if line.strip() == "---":
            if not in_fm:
                in_fm = True
                continue
            break
        if in_fm and line.lower().startswith(prefix):
            val = line.split(":", 1)[1].strip().strip("\"'").lower()
            return val in {"true", "1", "yes"}
    return False


def folder_is_handmatig(folder: Path) -> bool:
    """True als catalogus-``index.md`` ``manueel`` of ``manual`` zet (synoniemen)."""
    index = folder / "index.md"
    if not index.is_file():
        return False
    try:
        text = index.read_text(encoding="utf-8")
    except OSError:
        return False
    return _fm_bool(text, "manueel") or _fm_bool(text, "manual")


def product_path_for_vsa(vsa: Path) -> Path:
    """``naam.vsa`` -> ``naam.vsa.mxl``."""
    return vsa.with_suffix(".vsa.mxl")


def product_pdf_for_vsa(vsa: Path) -> Path:
    """``naam.vsa`` -> ``naam.vsa.pdf``."""
    return vsa.with_suffix(".vsa.pdf")


def product_svg_for_vsa(vsa: Path) -> Path:
    """``naam.vsa`` → ``naam.vsa.svg``."""
    return vsa.with_suffix(".vsa.svg")


def collect_vsa(root: Path) -> list[Path]:
    from product_regen import list_source_paths

    out: list[Path] = []
    for path in list_source_paths(root, pattern="*.vsa"):
        if path.suffix.lower() != ".vsa":
            continue
        if path.name.lower().endswith(".syl.vsa"):
            continue
        if not catalog_eligible(path, folder_is_handmatig=folder_is_handmatig):
            continue
        require_no_spaces(path)
        out.append(path)
    return out


@dataclass
class PlaybackVsaSource:
    path: Path
    _temp: Path | None = None

    def cleanup(self) -> None:
        if self._temp is not None and self._temp.is_file():
            self._temp.unlink(missing_ok=True)


def playback_vsa_for_export(canonical: Path) -> PlaybackVsaSource:
    """Syllabify ongescoopte tekst voor Coria; canonieke bron blijft ongewijzigd.

    Nog gebruikt door ``sync_audio_products`` (audio-keten). MXL gaat via
    ``vsa musicxml --syllabify``; SVG via ``vsa svg``.
    """
    try:
        from vsa.syllabify import syllabify_vsa_source
    except ImportError:
        return PlaybackVsaSource(path=canonical)

    text = canonical.read_text(encoding="utf-8")
    result = syllabify_vsa_source(text)
    if not result.changed:
        return PlaybackVsaSource(path=canonical)
    handle, tmp_name = tempfile.mkstemp(suffix=".vsa", prefix="vsa-coria-")
    tmp_path = Path(tmp_name)
    try:
        with open(handle, "w", encoding="utf-8", closefd=True) as fh:
            fh.write(result.text)
    except OSError:
        tmp_path.unlink(missing_ok=True)
        raise
    return PlaybackVsaSource(path=tmp_path, _temp=tmp_path)


def _stamp_ok_mxl(mxl: Path, source_hash: str) -> bool:
    if not mxl.is_file():
        return False
    stamp = read_mxl_stamp(mxl)
    kind = stamp.get(FIELD_SOURCE_KIND, "")
    if kind and kind != SOURCE_KIND_VSA:
        return stamp.get(FIELD_SOURCE_SHA, "") == source_hash
    return stamp.get(FIELD_SOURCE_SHA, "") == source_hash


def _stamp_ok_pdf(pdf: Path, source_hash: str) -> bool:
    if not pdf.is_file():
        return False
    stamp = read_pdf_stamp(pdf)
    if stamp.get(FIELD_SOURCE_KIND) != SOURCE_KIND_VSA:
        return False
    return stamp.get(FIELD_SOURCE_SHA, "") == source_hash


def _stamp_ok_svg(svg: Path, source_hash: str) -> bool:
    if not svg.is_file():
        return False
    stamp = read_svg_stamp(svg)
    if stamp.get(FIELD_SOURCE_KIND, SOURCE_KIND_VSA) not in {
        "",
        SOURCE_KIND_VSA,
    }:
        return False
    return stamp.get(FIELD_SOURCE_SHA, "") == source_hash


def is_stale(vsa: Path, mxl: Path) -> bool:
    """True als MXL ontbreekt of verouderd is (compat voor callers)."""
    return not _stamp_ok_mxl(mxl, source_sha256(vsa))


def is_stale_pair(vsa: Path) -> tuple[bool, bool]:
    """``(need_mxl, need_svg)`` — product-PDF is geen sync-slot meer."""
    digest = source_sha256(vsa)
    return (
        not _stamp_ok_mxl(product_path_for_vsa(vsa), digest),
        not _stamp_ok_svg(product_svg_for_vsa(vsa), digest),
    )


def _run_vsa_mxl(vsa: Path) -> None:
    """Coria-``.vsa.mxl`` via ``vsa musicxml --syllabify`` (sibling-pad)."""
    mxl = product_path_for_vsa(vsa)
    cmd = [
        sys.executable,
        "-m",
        "vsa.cli",
        "musicxml",
        "--syllabify",
        str(vsa),
        str(mxl),
    ]
    check_call(cmd, cwd=str(REPO_ROOT))
    if not mxl.is_file():
        raise RuntimeError(f"MXL ontbreekt na vsa musicxml: {mxl}")


def _run_vsa_svg(vsa: Path) -> None:
    """Scherm-``.vsa.svg`` via ``vsa svg`` (sibling-pad)."""
    svg = product_svg_for_vsa(vsa)
    cmd = [
        sys.executable,
        "-m",
        "vsa.cli",
        "svg",
        str(vsa),
        "-o",
        str(svg),
    ]
    check_call(cmd, cwd=str(REPO_ROOT))
    if not svg.is_file():
        raise RuntimeError(f"SVG ontbreekt na vsa svg: {svg}")


def _title_for_vsa(vsa: Path) -> str:
    """Titel uit sibling ``index.md`` (frontmatter), anders stam van de ``.vsa``."""
    for name in ("index.md", "_index.md"):
        index = vsa.parent / name
        if not index.is_file():
            continue
        try:
            text = index.read_text(encoding="utf-8")
        except OSError:
            continue
        in_fm = False
        for line in text.splitlines():
            if line.strip() == "---":
                if not in_fm:
                    in_fm = True
                    continue
                break
            if in_fm and line.lower().startswith("title:"):
                val = line.split(":", 1)[1].strip().strip("\"'")
                if val:
                    return val
    return vsa.stem.replace("-", " ")


def _point_pdf_errors_at_source(text: str, *, tmp_path: Path, source: Path) -> str:
    """Vervang temp-Markdown-paden in tool-output door het echte ``.vsa``-pad.

    ``markdown pdf`` valideert een tijdelijk blad; foutregels noemen anders
    ``AppData\\Local\\Temp\\vsa-pdf-….md`` i.p.v. de catalogusbron.
    """
    from input_paths import rel_for_log

    shown = rel_for_log(source, repo_root=REPO_ROOT)
    aliases = {
        str(tmp_path),
        str(tmp_path.resolve()),
        tmp_path.as_posix(),
        Path(tmp_path).resolve().as_posix(),
    }
    out = text
    for alias in aliases:
        if alias:
            out = out.replace(alias, shown)
    return out


def _run_vsa_pdf(vsa: Path, pdf: Path) -> None:
    """A4-PDF via tijdelijke Markdown + ``markdown pdf`` (site-SVG-look).

    Alleen de VSA-notatie (zonder YAML-frontmatter van de ``.vsa``) in
    ``::: vsa-notatie``; anders verschijnen ``do:`` / ``tempo:`` als tekst
    op het blad. Titel komt uit de bladermap-``index.md``.
    """
    from vsa.yaml_frontmatter import parse_vsa_frontmatter

    raw = vsa.read_text(encoding="utf-8")
    _meta, body = parse_vsa_frontmatter(raw)
    body = body.rstrip() + "\n"
    title = _title_for_vsa(vsa)
    md_text = f"# {title}\n\n::: vsa-notatie\n{body}:::\n"
    handle, tmp_name = tempfile.mkstemp(suffix=".md", prefix="vsa-pdf-")
    tmp_path = Path(tmp_name)
    try:
        with open(handle, "w", encoding="utf-8", closefd=True) as fh:
            fh.write(md_text)
        cmd = [
            sys.executable,
            "-m",
            "vsa.cli_md",
            "pdf",
            str(tmp_path),
            "-o",
            str(pdf),
            "--content-root",
            str(REPO_ROOT / "content-source"),
        ]
        proc = subprocess.run(
            cmd,
            cwd=str(REPO_ROOT),
            check=False,
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            combined = (proc.stderr or "") + (proc.stdout or "")
            rewritten = _point_pdf_errors_at_source(
                combined, tmp_path=tmp_path, source=vsa
            )
            if rewritten.strip():
                print(rewritten.rstrip(), file=sys.stderr, flush=True)
            from input_paths import rel_for_log

            rel = rel_for_log(vsa, repo_root=REPO_ROOT)
            raise RuntimeError(
                f"markdown pdf faalde (exit {proc.returncode}) voor {rel}"
            )
    finally:
        tmp_path.unlink(missing_ok=True)
    if not pdf.is_file():
        raise RuntimeError(f"PDF ontbreekt na markdown pdf: {pdf}")


def _apply_bron_identification(vsa: Path, mxl: Path) -> bool:
    """Zet Coria-bron in MXL indien bekend; True als het bestand is gewijzigd."""
    from vsa_bron import bron_uitgangspunt_from_file

    bron = bron_uitgangspunt_from_file(vsa)
    if not bron:
        return False
    require_no_spaces(mxl)
    root = load_score_xml(mxl)
    set_mxl_identification_source(root, bron)
    write_mxl(mxl, root)
    return True


def _remove_legacy_vsa_mxl(vsa: Path, mxl: Path) -> None:
    legacy = vsa.with_suffix(".mxl")
    if legacy.is_file() and legacy.resolve() != mxl.resolve():
        stamp = read_mxl_stamp(legacy)
        if stamp.get(FIELD_SOURCE_KIND, SOURCE_KIND_VSA) in {"", SOURCE_KIND_VSA}:
            detail(f"  remove legacy {legacy.name}")
            legacy.unlink()


def sync_one(
    vsa: Path,
    *,
    dry_run: bool,
    do_mxl: bool = True,
    do_pdf: bool = True,
    do_svg: bool = True,
    do_translit_svg: bool = False,
) -> None:
    from input_paths import rel_for_log

    rel = rel_for_log(vsa, repo_root=REPO_ROOT)
    source_hash = source_sha256(vsa)
    generated_at = utc_now_iso()
    mxl = product_path_for_vsa(vsa)
    pdf = product_pdf_for_vsa(vsa)
    svg = product_svg_for_vsa(vsa)
    # Na bron-SVG-export altijd translit meenemen; anders alleen als stale.
    want_translit = do_translit_svg or do_svg
    if do_mxl:
        detail(f"  EXP  {rel} -> vsa musicxml (--syllabify)")
    if do_svg:
        detail(f"  EXP  {rel} -> vsa svg")
    if do_pdf:
        detail(f"  PDF  {rel} -> {pdf.name}")
    if dry_run:
        if want_translit:
            sync_translit_svgs(vsa, dry_run=True, force=do_svg)
        return

    meta_products: dict[str, Path] = {}
    if do_mxl:
        _run_vsa_mxl(vsa)
        _apply_bron_identification(vsa, mxl)
        _remove_legacy_vsa_mxl(vsa, mxl)
        meta_products["mxl"] = mxl
    if do_svg:
        _run_vsa_svg(vsa)
        meta_products["svg"] = svg
    if meta_products:
        # Tooling merget al meta; hashes opnieuw zetten na bron-id op MXL.
        write_products_meta(vsa, meta_products, merge=True)
        # Bestaande lyrics/mp3 (van eerdere products-run) opnieuw stempelen.
        restamp_after_street_products(vsa)

    if want_translit:
        sync_translit_svgs(vsa, dry_run=False, force=do_svg)

    if do_pdf:
        require_no_spaces(pdf)
        _run_vsa_pdf(vsa, pdf)
        stamp_pdf(
            pdf,
            source_hash=source_hash,
            source_kind=SOURCE_KIND_VSA,
            generated_at=generated_at,
            generator=GENERATOR_VSA_PDF,
        )


class VsaKind:
    id = "vsa"
    label = "VSA-producten"
    source_noun = " .vsa"
    fix_cmd = r"scripts\products.cmd --kinds vsa"

    def collect(self, root: Path) -> list[Path]:
        return collect_vsa(root)

    def slots_for(self, source: Path, policy: RegenPolicy) -> list[ProductSlot]:
        digest = source_sha256(source)
        mxl = product_path_for_vsa(source)
        svg = product_svg_for_vsa(source)
        mxl_exists = mxl.is_file()
        contract = (
            mxl_contract_ok(mxl, profile="mono")
            if policy.invalid and mxl_exists
            else None
        )
        mxl_stamp = stamp_ok_or_meta(
            source,
            required_keys={"mxl", "svg"},
            stamp_ok=_stamp_ok_mxl(mxl, digest),
        )
        svg_stamp = stamp_ok_or_meta(
            source,
            required_keys={"mxl", "svg"},
            stamp_ok=_stamp_ok_svg(svg, digest),
        )
        slots = [
            ProductSlot(
                path=mxl,
                exists=mxl_exists,
                stamp_ok=mxl_stamp,
                contract_ok=contract,
                needs_musescore=False,
            ),
            ProductSlot(
                path=svg,
                exists=svg.is_file(),
                stamp_ok=svg_stamp,
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
                    exists=fresh or all(
                        product_translit_svg(source, m).is_file() for m in modi
                    ),
                    stamp_ok=fresh,
                    contract_ok=None,
                    needs_musescore=False,
                )
            )
        return slots

    def sync(self, source: Path, *, need: Sequence[bool], dry_run: bool) -> None:
        need_mxl = bool(need[0]) if len(need) > 0 else False
        need_svg = bool(need[1]) if len(need) > 1 else False
        need_translit = bool(need[2]) if len(need) > 2 else False
        if need_mxl or need_svg or need_translit:
            sync_one(
                source,
                dry_run=dry_run,
                do_mxl=need_mxl,
                do_pdf=False,
                do_svg=need_svg,
                do_translit_svg=need_translit,
            )


KIND = VsaKind()


def main(argv: list[str] | None = None) -> int:
    return main_for_kind(
        KIND,
        argv,
        description=(
            "Exporteer stale Coria-.mxl en muziek-.vsa.svg vanuit bibliotheek-.vsa "
            "(via vsa musicxml / vsa svg; geen A4-product-PDF; blad = index.md.pdf)."
        ),
        default_root=DEFAULT_ROOT,
    )


if __name__ == "__main__":
    raise SystemExit(main())
