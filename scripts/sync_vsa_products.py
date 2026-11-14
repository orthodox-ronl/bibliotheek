"""Muziek-``.vsa.svg`` (+ translit) en schets-``.vsa.mvsa`` bij ``.vsa``.

Siblings: ``{stam}.vsa.svg`` (scherm), optioneel translit-SVG’s (§5a),
en via ``vsa mvsa`` (T1–T7) ``{stam}.vsa.mvsa``. Geen Coria-``.vsa.mxl``
meer: playback-MXL hoort bij de afgeleide ``.vsa.mvsa``. Na schrijven of
aanwezigheid van die MVSA cascade: alle mvsa-notatieproducten + lyrics +
preview-mp3 alsof de ``.vsa.mvsa`` de bron is.

Templatekeuze: VSA-tooling T1 (`formule:` / soort+toon / bestaande MVSA).
Geen default-template → soft skip van ``.vsa.mvsa`` (alleen ``--verbose``);
ongeldige ``formule:`` → harde fout.

Slaat mappen met ``manueel: true`` of ``manual: true`` over. CI genereert niet —
vernieuw lokaal met ``scripts\\products.cmd --kinds vsa``.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Sequence

from cli_style import detail
from coria_mxl import require_no_spaces
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
    read_pdf_stamp,
    read_svg_stamp,
    source_sha256,
    stamp_pdf,
    utc_now_iso,
)
from product_regen import RegenPolicy, need_regen
from street_consumer_stamps import restamp_after_street_products
from street_meta import stamp_ok_or_meta, write_products_meta
from translit_svg_products import (
    product_translit_svg,
    sync_translit_svgs,
    translit_modi_for_source,
    translit_svgs_fresh,
)

TemplateDecision = Literal["ok", "soft_skip", "hard"]


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
    """``naam.vsa`` → ``naam.vsa.mxl`` (legacy helper; products schrijft dit niet meer)."""
    return vsa.with_suffix(".vsa.mxl")


def product_pdf_for_vsa(vsa: Path) -> Path:
    """``naam.vsa`` → ``naam.vsa.pdf``."""
    return vsa.with_suffix(".vsa.pdf")


def product_svg_for_vsa(vsa: Path) -> Path:
    """``naam.vsa`` → ``naam.vsa.svg``."""
    return vsa.with_suffix(".vsa.svg")


def product_mvsa_for_vsa(vsa: Path) -> Path:
    """``naam.vsa`` → ``naam.vsa.mvsa`` (T1 schets; stem.brontype.doeltype)."""
    return vsa.with_name(f"{vsa.name}.mvsa")


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
    """Syllabify ongescoopte tekst voor preview-audio; canonieke bron blijft.

    Gebruikt door ``sync_audio_products`` (``vsa mp3``).
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


def _vsa_frontmatter(vsa: Path) -> dict:
    from vsa.yaml_frontmatter import parse_vsa_frontmatter

    raw = vsa.read_text(encoding="utf-8")
    meta, _body = parse_vsa_frontmatter(raw)
    return meta if isinstance(meta, dict) else {}


def classify_vsa_mvsa_template(vsa: Path) -> tuple[TemplateDecision, str | None]:
    """T1-templatekeuze voor ``.vsa`` → ``.vsa.mvsa``.

    Returns ``("ok", id)``, ``("soft_skip", None)`` (geen default-template;
    geen fout), of ``("hard", None)`` waarbij de exception opnieuw wordt
    opgegooid bij aanroep van :func:`raise_vsa_mvsa_template_error` / convert.
    """
    from vsa.template_library import TemplateLibraryError, select_template_id

    meta = _vsa_frontmatter(vsa)
    formule = meta.get("formule")
    has_formule = formule not in (None, "")
    bron_u = None
    bron = meta.get("bron")
    if isinstance(bron, dict):
        bron_u = bron.get("uitgangspunt")
    elif isinstance(bron, str):
        bron_u = bron
    out = product_mvsa_for_vsa(vsa)
    try:
        tpl = select_template_id(
            soort=meta.get("soort") or meta.get("genre"),
            toon=meta.get("toon") or meta.get("tone"),
            formule=str(formule) if has_formule else None,
            bron=str(bron_u) if bron_u else None,
            path=vsa,
            output=out,
        )
    except TemplateLibraryError as exc:
        soft_codes = {"TEMPLATE-SELECT-MISSING", "TEMPLATE-SELECT-META"}
        if not has_formule and exc.code in soft_codes:
            return "soft_skip", None
        raise
    return "ok", tpl


def is_stale_pair(vsa: Path) -> tuple[bool, bool]:
    """``(need_mvsa, need_svg)`` — product-PDF/MXL zijn geen sync-slots meer."""
    digest = source_sha256(vsa)
    mvsa = product_mvsa_for_vsa(vsa)
    try:
        decision, _tpl = classify_vsa_mvsa_template(vsa)
    except Exception:  # noqa: BLE001 — harde T1-fout: slot moet regenereren
        decision = "hard"
    need_mvsa = False
    if decision in {"ok", "hard"}:
        need_mvsa = not stamp_ok_or_meta(
            vsa,
            required_keys={"mvsa"},
            stamp_ok=mvsa.is_file(),
        )
    return (
        need_mvsa,
        not _stamp_ok_svg(product_svg_for_vsa(vsa), digest),
    )


def _run_vsa_svg(vsa: Path) -> None:
    """Scherm-``.vsa.svg`` via ``vsa svg`` (sibling-pad)."""
    from cli_style import check_call

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


def _run_vsa_mvsa(vsa: Path) -> Path:
    """Schets-``.vsa.mvsa`` via tooling ``convert_vsa_to_mvsa`` (T1–T7)."""
    from input_paths import rel_for_log
    from vsa.template_instance import TemplateInstanceError
    from vsa.vsa_mvsa import convert_vsa_to_mvsa

    out = product_mvsa_for_vsa(vsa)
    try:
        convert_vsa_to_mvsa(vsa, output=out, write=True)
    except TemplateInstanceError as exc:
        # Volledig catalogus-pad i.p.v. alleen bestandsnaam (fix/products-samenvatting).
        rel = rel_for_log(vsa, repo_root=REPO_ROOT)
        raise TemplateInstanceError(
            exc.message_nl,
            code=exc.code,
            hint_nl=exc.hint_nl,
            source=rel,
            line=exc.line,
            column=exc.column,
            phrase_id=exc.phrase_id,
            lyric=exc.lyric,
            note_index=exc.note_index,
        ) from exc
    if not out.is_file():
        raise RuntimeError(f"MVSA ontbreekt na vsa mvsa: {out}")
    return out


def _derived_mvsa_cascade_needed(mvsa: Path) -> bool:
    """True als notatie-/lyrics-/audio-siblings van ``mvsa`` ontbreken of stale zijn."""
    from product_meta import SOURCE_KIND_MVSA
    from sync_audio_products import AudioJob
    from sync_audio_products import is_stale as audio_is_stale
    from sync_lyrics_products import is_stale as lyrics_is_stale
    from sync_lyrics_products import product_path_for_source as lyrics_path
    from sync_mvsa_products import KIND as mvsa_kind

    if not mvsa.is_file():
        return False
    policy = RegenPolicy(missing=True, stale=True, invalid=True)
    for slot in mvsa_kind.slots_for(mvsa, policy):
        if need_regen(
            policy,
            exists=slot.exists,
            stamp_ok=slot.stamp_ok,
            contract_ok=slot.contract_ok,
        ):
            return True
    lyrics = lyrics_path(mvsa)
    if (not lyrics.is_file()) or lyrics_is_stale(mvsa, lyrics):
        return True
    if audio_is_stale(AudioJob(mvsa, SOURCE_KIND_MVSA)):
        return True
    return False


def _cascade_vsa_mvsa_products(
    mvsa: Path,
    *,
    dry_run: bool,
    force: bool,
) -> None:
    """Alle producten alsof ``mvsa`` de canonieke bron is (notatie + lyrics + mp3)."""
    from product_meta import SOURCE_KIND_MVSA
    from sync_audio_products import AudioJob, sync_one as audio_sync_one
    from sync_audio_products import is_stale as audio_is_stale
    from sync_lyrics_products import is_stale as lyrics_is_stale
    from sync_lyrics_products import product_path_for_source as lyrics_path
    from sync_lyrics_products import sync_one as lyrics_sync_one
    from sync_mvsa_products import KIND as mvsa_kind

    policy = RegenPolicy(missing=True, stale=True, invalid=True)
    slots = mvsa_kind.slots_for(mvsa, policy)
    if force:
        need = [True] * len(slots)
    else:
        need = [
            need_regen(
                policy,
                exists=slot.exists,
                stamp_ok=slot.stamp_ok,
                contract_ok=slot.contract_ok,
            )
            for slot in slots
        ]
    if any(need):
        detail(f"  CASCADE mvsa-producten → {mvsa.name}")
        mvsa_kind.sync(mvsa, need=need, dry_run=dry_run)

    lyrics = lyrics_path(mvsa)
    if force or (not lyrics.is_file()) or lyrics_is_stale(mvsa, lyrics):
        detail(f"  CASCADE lyrics → {lyrics.name}")
        lyrics_sync_one(mvsa, dry_run=dry_run)

    job = AudioJob(mvsa, SOURCE_KIND_MVSA)
    if force or audio_is_stale(job):
        detail(f"  CASCADE audio → {job.product.name}")
        audio_sync_one(job, dry_run=dry_run)


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


def sync_one(
    vsa: Path,
    *,
    dry_run: bool,
    do_pdf: bool = False,
    do_svg: bool = True,
    do_translit_svg: bool = False,
    do_mvsa: bool = False,
    cascade_mvsa: bool = False,
) -> None:
    from input_paths import rel_for_log

    rel = rel_for_log(vsa, repo_root=REPO_ROOT)
    source_hash = source_sha256(vsa)
    generated_at = utc_now_iso()
    pdf = product_pdf_for_vsa(vsa)
    svg = product_svg_for_vsa(vsa)
    mvsa = product_mvsa_for_vsa(vsa)
    # Na bron-SVG-export altijd translit meenemen; anders alleen als stale.
    want_translit = do_translit_svg or do_svg
    if do_svg:
        detail(f"  EXP  {rel} -> vsa svg")
    if do_mvsa:
        detail(f"  EXP  {rel} -> vsa mvsa → {mvsa.name}")
    if do_pdf:
        detail(f"  PDF  {rel} -> {pdf.name}")
    if dry_run:
        if want_translit:
            sync_translit_svgs(vsa, dry_run=True, force=do_svg)
        if cascade_mvsa and (do_mvsa or mvsa.is_file()):
            _cascade_vsa_mvsa_products(mvsa, dry_run=True, force=do_mvsa)
        return

    meta_products: dict[str, Path] = {}
    regenerated_mvsa = False
    if do_svg:
        _run_vsa_svg(vsa)
        meta_products["svg"] = svg
    if do_mvsa:
        _run_vsa_mvsa(vsa)
        meta_products["mvsa"] = mvsa
        regenerated_mvsa = True
    if meta_products:
        write_products_meta(
            vsa,
            meta_products,
            merge=True,
            drop_keys={"mxl"},
        )
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

    if cascade_mvsa and mvsa.is_file():
        _cascade_vsa_mvsa_products(
            mvsa,
            dry_run=False,
            force=regenerated_mvsa,
        )


class VsaKind:
    id = "vsa"
    label = "VSA-producten"
    source_noun = " .vsa"
    fix_cmd = r"scripts\products.cmd --kinds vsa"

    def collect(self, root: Path) -> list[Path]:
        return collect_vsa(root)

    def slots_for(self, source: Path, policy: RegenPolicy) -> list[ProductSlot]:
        del policy
        digest = source_sha256(source)
        svg = product_svg_for_vsa(source)
        svg_stamp = stamp_ok_or_meta(
            source,
            required_keys={"svg"},
            stamp_ok=_stamp_ok_svg(svg, digest),
        )
        slots = [
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
                    exists=fresh
                    or all(
                        product_translit_svg(source, m).is_file() for m in modi
                    ),
                    stamp_ok=fresh,
                    contract_ok=None,
                    needs_musescore=False,
                )
            )
        mvsa = product_mvsa_for_vsa(source)
        try:
            decision, _tpl = classify_vsa_mvsa_template(source)
        except Exception:  # noqa: BLE001 — T1 harde fout → slot forceren
            decision = "hard"
        if decision == "soft_skip":
            detail(
                f"geen default-template voor {source.name}; "
                ".vsa.mvsa overgeslagen (T1)"
            )
        else:
            meta_ok = stamp_ok_or_meta(
                source,
                required_keys={"mvsa"},
                stamp_ok=mvsa.is_file(),
            )
            # Ook regenereren als de schets vers is maar mvsa-siblings stale zijn.
            cascade_ok = (not mvsa.is_file()) or (
                not _derived_mvsa_cascade_needed(mvsa)
            )
            slots.append(
                ProductSlot(
                    path=mvsa,
                    exists=mvsa.is_file(),
                    stamp_ok=meta_ok and cascade_ok,
                    contract_ok=None,
                    needs_musescore=False,
                )
            )
        return slots

    def sync(self, source: Path, *, need: Sequence[bool], dry_run: bool) -> None:
        need_svg = bool(need[0]) if len(need) > 0 else False
        idx = 1
        need_translit = False
        if translit_modi_for_source(source):
            need_translit = bool(need[idx]) if len(need) > idx else False
            idx += 1
        need_mvsa_slot = False
        has_mvsa_slot = False
        try:
            decision, _tpl = classify_vsa_mvsa_template(source)
        except Exception:  # noqa: BLE001
            decision = "hard"
        mvsa_path = product_mvsa_for_vsa(source)
        if decision != "soft_skip":
            has_mvsa_slot = True
            need_mvsa_slot = bool(need[idx]) if len(need) > idx else False
        # Slot kan "stale" zijn alleen omdat cascade-siblings dat zijn;
        # schets-``.vsa.mvsa`` opnieuw alleen bij ontbrekende/verouderde meta.
        do_mvsa = bool(need_mvsa_slot) and not stamp_ok_or_meta(
            source,
            required_keys={"mvsa"},
            stamp_ok=mvsa_path.is_file(),
        )
        cascade = has_mvsa_slot and (need_mvsa_slot or mvsa_path.is_file())
        if need_svg or need_translit or need_mvsa_slot or cascade:
            sync_one(
                source,
                dry_run=dry_run,
                do_pdf=False,
                do_svg=need_svg,
                do_translit_svg=need_translit,
                do_mvsa=do_mvsa,
                cascade_mvsa=cascade,
            )


KIND = VsaKind()


def main(argv: list[str] | None = None) -> int:
    return main_for_kind(
        KIND,
        argv,
        description=(
            "Exporteer stale muziek-.vsa.svg (+ translit) en schets-.vsa.mvsa "
            "vanuit bibliotheek-.vsa (T1); cascade mvsa-producten. Geen "
            ".vsa.mxl / A4-product-PDF (blad = index.md.pdf)."
        ),
        default_root=DEFAULT_ROOT,
    )


if __name__ == "__main__":
    raise SystemExit(main())
