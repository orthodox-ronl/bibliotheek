"""Bouw pagina-PDF's voor bladermap-index.md (koormap/catalogus).

A4-compositie uit shortcode ``kop`` (en legacy ``#`` / HTML-titels) + kale
muziek-SVG's (geen catalogus-product-PDF's plakken). Binnen ``pdf-bijelkaar``
exporteert de pijplijn opnieuw met tooling ``--compact``. Meerdere
MuseScore-pagina's → bladreeks ``stem-N.svg`` (VSA-tooling fase 1).

Catalogus-leaves zonder Markdown-titel: afgeleide leaf-titel injecteren
(zelfde algoritme als Hugo; zie ``ensure_catalogus_derived_titles``).
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content-source"
CATALOGUS = CONTENT / "catalogus"

# A4 in PDF-punten (1 pt = 1/72 inch)
_A4_W = 595.28
_A4_H = 841.89
_MARGIN = 28.0  # ~10 mm; tooling --compact zet Style-marges al strakker

_SC = re.compile(
    r"\{\{<\s*(/?)\s*([a-z0-9_-]+)([^>]*)>\}\}",
    re.IGNORECASE,
)
_ID = re.compile(r'\bid\s*=\s*"([^"]+)"', re.IGNORECASE)
_H1_HTML = re.compile(
    r"<h1\b[^>]*>(.*?)</h1>",
    re.IGNORECASE | re.DOTALL,
)
_H1_MD = re.compile(r"(?m)^#\s+(.+?)\s*$")
_ONDERDELEN = frozenset(
    {"titel", "title", "muziek", "bron", "copyright", "veld"}
)


@dataclass
class TitleItem:
    text: str
    prominent: bool = True  # False = lichte tussenkop (Toon n)


@dataclass
class MusicItem:
    uv_id: str
    compact: bool


@dataclass
class SpaceItem:
    """Verticale witruimte (shortcode ``witruimte``); hoogte in PDF-punten."""

    points: float


# klein / middel (default) / groot — zelfde namen als shortcode-knoppen
_WITRUIMTE_PT = {"klein": 10.0, "middel": 20.0, "groot": 40.0}


@dataclass
class PageFlow:
    """Eén PDF-bladgroep (pdf-pagina of apart pdf-bijelkaar-blok)."""

    items: list[TitleItem | MusicItem | SpaceItem] = field(default_factory=list)

    @property
    def music_ids(self) -> list[str]:
        return [i.uv_id for i in self.items if isinstance(i, MusicItem)]

    @property
    def any_compact(self) -> bool:
        return any(isinstance(i, MusicItem) and i.compact for i in self.items)


def _parse_onderdeel(params: str) -> str | None:
    params = params.replace("/", " ")
    stripped = _ID.sub(" ", params)
    stripped = re.sub(r'"[^"]*"', " ", stripped)
    for tok in stripped.split():
        t = tok.strip().lower()
        if t in _ONDERDELEN:
            return t
    return None


def _strip_tags(html: str) -> str:
    text = re.sub(r"<[^>]+>", "", html)
    text = re.sub(r"\{\{[^}]+\}\}", "", text)
    return " ".join(text.split()).strip()


def _kop_prominent(params: str) -> bool:
    """groot (default) = prominent; middel/klein = tussenkop."""
    tokens = {t.strip().lower() for t in params.replace("/", " ").split() if t.strip()}
    if "middel" in tokens or "klein" in tokens:
        return False
    return True


def _witruimte_points(params: str) -> float:
    tokens = [t.strip().lower() for t in params.replace("/", " ").split() if t.strip()]
    if not tokens:
        return _WITRUIMTE_PT["middel"]
    if len(tokens) > 1:
        raise ValueError(
            f"shortcode witruimte: hoogstens één grootte, kreeg {tokens!r}"
        )
    key = tokens[0]
    if key not in _WITRUIMTE_PT:
        raise ValueError(
            f"shortcode witruimte: onbekende knop {key!r} "
            "(klein, middel of groot)"
        )
    return _WITRUIMTE_PT[key]


@lru_cache(maxsize=1)
def _title_font_files() -> tuple[Path, Path]:
    """Unicode-lettertypen voor koppen (Cyrillisch e.d.; niet de PDF-standaard helv).

    Terug: (regular, bold). Helvetica mist Cyrillisch → vraagtekens in de PDF.
    """
    windir = Path(os.environ.get("WINDIR", r"C:\Windows"))
    candidates_reg = [
        windir / "Fonts" / "arial.ttf",
        windir / "Fonts" / "calibri.ttf",
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"),
        Path("/Library/Fonts/Arial.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
    ]
    candidates_bold = [
        windir / "Fonts" / "arialbd.ttf",
        windir / "Fonts" / "calibrib.ttf",
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        Path("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
        Path("/Library/Fonts/Arial Bold.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
    ]
    regular = next((p for p in candidates_reg if p.is_file()), None)
    bold = next((p for p in candidates_bold if p.is_file()), None)
    if regular is None:
        raise RuntimeError(
            "Geen Unicode-font voor pagina-PDF-koppen gevonden "
            "(verwacht o.a. Arial of DejaVu Sans). "
            "Oplossing: installeer Arial (Windows) of fonts-dejavu (Linux)."
        )
    if bold is None:
        bold = regular
    return regular, bold


def _titles_in_gap(gap: str) -> list[TitleItem]:
    """Legacy titels in Markdown-gaten: HTML-h1 of ``#`` (zonder shortcodes).

    Canonieke beheerderstaal is shortcode ``kop`` (zie parse_page_flows).
    """
    marks: list[tuple[int, TitleItem]] = []
    for m in _H1_HTML.finditer(gap):
        t = _strip_tags(m.group(1))
        if t:
            marks.append((m.start(), TitleItem(t, prominent=True)))
    if not any(it.prominent for _, it in marks):
        for m in _H1_MD.finditer(gap):
            t = m.group(1).strip()
            if t and "{{" not in t:
                marks.append((m.start(), TitleItem(t, prominent=True)))
    marks.sort(key=lambda x: x[0])
    return [it for _, it in marks]


def parse_page_flows(text: str) -> list[PageFlow]:
    """Bladgroepen: ``pdf-pagina`` of elk apart ``pdf-bijelkaar``-blok.

    Muziek binnen ``pdf-bijelkaar`` krijgt ``compact=True``. Paginatitels
    buiten de blokken (``kop`` / legacy ``<h1>`` / ``#``) horen alleen bij
    het **eerste** blad; latere bijelkaar-blokken krijgen die titel niet
    opnieuw.
    """
    finished: list[PageFlow] = []
    current = PageFlow()
    stack: list[str] = []
    bijelkaar = 0
    pending_titles: list[TitleItem] = []  # prominente titel buiten blokken → eenmalig
    kop_stack: list[tuple[str, int]] = []  # (params, inner_start)
    pos = 0

    def flush_current() -> None:
        nonlocal current
        if current.items:
            # Prominente titel buiten pdf-bijelkaar (``kop`` / ``#``) hoort
            # bij het eerste blad met inhoud.
            if pending_titles:
                current.items = [
                    TitleItem(t.text, prominent=t.prominent)
                    for t in pending_titles
                ] + current.items
                pending_titles.clear()
            finished.append(current)
            current = PageFlow()

    def add_title(t: TitleItem) -> None:
        if bijelkaar == 0:
            if t.prominent:
                pending_titles.append(t)
            else:
                current.items.append(t)
        else:
            current.items.append(t)

    def gap_before(end: int) -> None:
        nonlocal pos
        gap = text[pos:end]
        # Binnen ``kop … /kop``: tekst wordt bij sluiten gelezen, niet hier.
        if not kop_stack:
            for t in _titles_in_gap(gap):
                add_title(t)
        pos = end

    def add_music(uv_id: str) -> None:
        current.items.append(MusicItem(uv_id, compact=bijelkaar > 0))

    for m in _SC.finditer(text):
        gap_before(m.start())
        closing, name, params = m.group(1), m.group(2).lower(), m.group(3)
        pos = m.end()

        if closing:
            if name == "kop" and kop_stack:
                open_params, inner_start = kop_stack.pop()
                raw = text[inner_start : m.start()]
                label = _strip_tags(raw)
                if label:
                    add_title(
                        TitleItem(label, prominent=_kop_prominent(open_params))
                    )
            elif name == "bieb" and stack:
                stack.pop()
            elif name == "pdf-bijelkaar" and bijelkaar:
                bijelkaar -= 1
            continue

        if name == "kop":
            if params.rstrip().endswith("/"):
                continue
            kop_stack.append((params, m.end()))
            continue

        if name == "witruimte":
            current.items.append(SpaceItem(_witruimte_points(params)))
            continue

        if name == "pdf-pagina" or name == "pagina":
            flush_current()
            continue

        if name == "pdf-bijelkaar":
            self_closing = params.rstrip().endswith("/")
            if self_closing:
                continue
            # Nieuw bijelkaar-blok = nieuwe bladgroep (na een vorige met muziek)
            if current.music_ids:
                flush_current()
            # Paginatitel(s) alleen op het eerste bijelkaar-blad
            if pending_titles:
                current.items = [
                    TitleItem(t.text, prominent=t.prominent)
                    for t in pending_titles
                ] + current.items
                pending_titles.clear()
            bijelkaar += 1
            continue

        if name == "muziek":
            if not stack:
                raise ValueError(
                    "shortcode muziek buiten een bieb-blok (geen id-context)"
                )
            add_music(stack[-1])
            continue

        if name != "bieb":
            continue

        id_m = _ID.search(params)
        uv_id = id_m.group(1).strip() if id_m else None
        onderdeel = _parse_onderdeel(params)
        self_closing = params.rstrip().endswith("/")

        if not self_closing and uv_id and onderdeel is None:
            stack.append(uv_id)
            continue

        if not uv_id:
            if not stack:
                raise ValueError(
                    f"bieb zonder id en zonder ouder-blok: {m.group(0)!r}"
                )
            uv_id = stack[-1]

        if onderdeel is None:
            onderdeel = "muziek"
        if onderdeel == "muziek":
            add_music(uv_id)

    gap_before(len(text))
    flush_current()
    return [f for f in finished if f.items]


def music_ids_from_markdown(text: str) -> list[str]:
    """Volgorde van uitvoeringsvorm-ids (compat voor tests/oude callers)."""
    ids: list[str] = []
    for flow in parse_page_flows(text):
        ids.extend(flow.music_ids)
    return ids


def catalogus_leaf_id(md_path: Path) -> str | None:
    """``zangstuk/variant/uv`` als ``md_path`` een catalogus-leaf-``index.md`` is."""
    try:
        rel = md_path.resolve().relative_to(CATALOGUS.resolve())
    except ValueError:
        return None
    if md_path.name != "index.md" or len(rel.parts) != 4:
        return None
    return "/".join(rel.parts[:3])


def _flow_has_prominent_title(flow: PageFlow) -> bool:
    return any(
        isinstance(item, TitleItem) and item.prominent for item in flow.items
    )


def ensure_catalogus_derived_titles(
    flows: list[PageFlow], md_path: Path
) -> list[PageFlow]:
    """Op catalogus-leaves: ontbrekende prominente titel → afgeleide leaf-titel.

    Koormap-slots (buiten ``content-source/catalogus``) blijven ongewijzigd:
    daar komen titels uit ``kop`` / ``#``. Zie
    ``docs/plans/catalogus-pagina-pdf.md`` §2.
    """
    leaf_id = catalogus_leaf_id(md_path)
    if not leaf_id:
        return flows

    from catalogus import derived_leaf_title

    leaf_dir = CATALOGUS.joinpath(*leaf_id.split("/"))
    title = derived_leaf_title(leaf_id, leaf_dir=leaf_dir)
    for flow in flows:
        if not flow.music_ids or _flow_has_prominent_title(flow):
            continue
        flow.items = [TitleItem(title, prominent=True), *flow.items]
    return flows


def find_mvsa(uv_id: str) -> Path:
    leaf = CATALOGUS.joinpath(*uv_id.split("/"))
    if not leaf.is_dir():
        raise FileNotFoundError(f"catalogusmap ontbreekt: {leaf}")
    mvsas = sorted(
        p
        for p in leaf.glob("*.mvsa")
        if not p.name.lower().endswith(".mscz.mvsa")
    )
    if not mvsas:
        raise FileNotFoundError(f"geen .mvsa in {leaf}")
    return mvsas[0]


def try_find_notation_source(uv_id: str) -> Path | None:
    """``.mvsa`` / ``.vsa`` / ``.mscz`` in de catalogusmap, of ``None``.

    Ontbrekende map → ``FileNotFoundError``.
    """
    leaf = CATALOGUS.joinpath(*uv_id.split("/"))
    if not leaf.is_dir():
        raise FileNotFoundError(f"catalogusmap ontbreekt: {leaf}")
    mvsas = sorted(
        p
        for p in leaf.glob("*.mvsa")
        if not p.name.lower().endswith(".mscz.mvsa")
    )
    if mvsas:
        return mvsas[0]
    vsas = sorted(leaf.glob("*.vsa"))
    if vsas:
        return vsas[0]
    msczs = sorted(leaf.glob("*.mscz"))
    if msczs:
        return msczs[0]
    return None


def find_notation_source(uv_id: str) -> Path:
    """Bron voor kale SVG: ``.mvsa``, anders ``.vsa``, anders ``.mscz``."""
    found = try_find_notation_source(uv_id)
    if found is None:
        leaf = CATALOGUS.joinpath(*uv_id.split("/"))
        raise FileNotFoundError(
            f"geen .mvsa/.vsa/.mscz in {leaf} (pagina-pdf plakt geen catalogus-PDF)"
        )
    return found


def leaf_has_tekstblad(uv_id: str) -> bool:
    leaf = CATALOGUS.joinpath(*uv_id.split("/"))
    if not leaf.is_dir():
        return False
    return any(
        p.is_file()
        and "tekstblad" in p.name.lower()
        and p.suffix.lower() == ".md"
        for p in leaf.iterdir()
    )


def find_tekstblad_pdf(uv_id: str) -> Path | None:
    leaf = CATALOGUS.joinpath(*uv_id.split("/"))
    if not leaf.is_dir():
        return None
    pdfs = sorted(
        p
        for p in leaf.iterdir()
        if p.is_file()
        and p.suffix.lower() == ".pdf"
        and ".tekstblad." in p.name.lower()
    )
    return pdfs[0] if pdfs else None


def find_tekstblad_md(uv_id: str) -> Path | None:
    leaf = CATALOGUS.joinpath(*uv_id.split("/"))
    if not leaf.is_dir():
        return None
    mds = sorted(
        p
        for p in leaf.iterdir()
        if p.is_file()
        and p.suffix.lower() == ".md"
        and ".tekstblad." in p.name.lower()
    )
    return mds[0] if mds else None


def _frontmatter_title(path: Path) -> str | None:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    if not text.lstrip().startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    for line in parts[1].splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("title:"):
            return stripped.split(":", 1)[1].strip().strip("\"'")
    return None


def prose_notes_from_catalogus_md(text: str) -> list[str]:
    """Gewone alinea’s in de leaf-body (geen shortcodes, geen ``#``-titels)."""
    body = text
    if body.lstrip().startswith("---"):
        parts = body.split("---", 2)
        if len(parts) >= 3:
            body = parts[2]
    notes: list[str] = []
    for raw in body.splitlines():
        line = raw.strip()
        if not line or line.startswith("{{") or line.startswith("#"):
            continue
        notes.append(line)
    return notes


def _pagina_pdf_out_path(md_path: Path) -> Path:
    if md_path.name == "index.md":
        return md_path.with_name("index.pagina.pdf")
    return md_path.with_name(md_path.stem + ".pagina.pdf")


@dataclass(frozen=True)
class PaginaPdfJob:
    """Wat ``pagina-pdf`` zou moeten bouwen (zonder te exporteren)."""

    md_path: Path
    out_path: Path
    deps: tuple[Path, ...]


def pagina_pdf_job(md_path: Path) -> PaginaPdfJob | None:
    """Zelfde selectie als ``build_one`` / batch-OVERGESLAGEN, zonder schrijven.

    ``None`` = geen pagina-PDF verwacht (geen ``bieb``/``muziek``, lege flow,
    of notatiebron ontbreekt zoals bij SKIP in de batch).
    ``ValueError`` = kapotte shortcodes (zelfde als ``parse_page_flows``).
    """
    md_path = md_path.resolve()
    out = _pagina_pdf_out_path(md_path)
    text = md_path.read_text(encoding="utf-8")

    if catalogus_needs_voorzien_pdf(md_path) is not None:
        return PaginaPdfJob(md_path, out, (md_path,))

    tekstblad_job = catalogus_tekstblad_pagina_job(md_path)
    if tekstblad_job is not None:
        _leaf_id, tb_md = tekstblad_job
        return PaginaPdfJob(md_path, out, (md_path, tb_md))

    if "bieb" not in text and "muziek" not in text:
        return None
    flows = parse_page_flows(text)
    flows = ensure_catalogus_derived_titles(flows, md_path)
    if not flows:
        return None

    deps: list[Path] = [md_path]
    try:
        for flow in flows:
            for mid in flow.music_ids:
                deps.append(find_notation_source(mid))
    except FileNotFoundError:
        return None
    return PaginaPdfJob(md_path, out, tuple(deps))


def iter_bladermap_index_md() -> list[Path]:
    """``index.md`` onder koormappen + catalogus (geen ``_dirvolgorde``)."""
    out: list[Path] = []
    for base in (CONTENT / "koormappen", CONTENT / "catalogus"):
        if not base.is_dir():
            continue
        for md in sorted(base.rglob("index.md")):
            if "_dirvolgorde" in md.as_posix():
                continue
            out.append(md.resolve())
    return out


def _pdf_page_content_clip(page: object, *, pad: float = 6.0) -> object:
    """Inhoudsrechthoek van een PDF-pagina (zonder onderste witruimte)."""
    import pymupdf

    bbox: object | None = None
    for block in page.get_text("blocks"):
        if len(block) < 5:
            continue
        if isinstance(block[4], str) and not block[4].strip():
            continue
        rect = pymupdf.Rect(block[:4])
        bbox = rect if bbox is None else (bbox | rect)
    for drawing in page.get_drawings():
        rect = drawing.get("rect")
        if rect is None:
            continue
        r = pymupdf.Rect(rect)
        if r.is_empty or r.is_infinite:
            continue
        bbox = r if bbox is None else (bbox | r)
    if bbox is None:
        return page.rect
    clip = pymupdf.Rect(bbox)
    clip.x0 = max(0.0, clip.x0 - pad)
    clip.y0 = max(0.0, clip.y0 - pad)
    clip.x1 = min(page.rect.width, clip.x1 + pad)
    clip.y1 = min(page.rect.height, clip.y1 + pad)
    return clip


def export_tekstblad_md_pdf(md: Path, dest: Path) -> None:
    """Render ``.tekstblad.md`` naar PDF via ``vsa pdf`` (HTML + ``::: vsa-notatie``)."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        "-m",
        "vsa.cli",
        "pdf",
        str(md),
        "-o",
        str(dest),
        "--content-root",
        str(CONTENT),
    ]
    print(f"  tekstblad-body {md.name}", flush=True)
    subprocess.check_call(cmd, cwd=str(ROOT))
    if not dest.is_file():
        raise RuntimeError(f"tekstblad-body-PDF ontbreekt na vsa pdf: {dest}")


def compose_tekstblad_pagina_pdf(
    dest: Path,
    *,
    title: str,
    notes: list[str],
    tekstblad_md: Path,
) -> None:
    """A4: titel + toelichting + body uit ``.tekstblad.md`` (geen product-PDF)."""
    if not tekstblad_md.is_file():
        raise FileNotFoundError(f"tekstblad-md ontbreekt: {tekstblad_md}")
    with tempfile.TemporaryDirectory(prefix="pagina-tekstblad-") as tmp:
        body = Path(tmp) / "body.pdf"
        export_tekstblad_md_pdf(tekstblad_md, body)
        compose_tekstblad_pagina_pdf_from_body(
            dest, title=title, notes=notes, body_pdf=body
        )


def compose_tekstblad_pagina_pdf_from_body(
    dest: Path,
    *,
    title: str,
    notes: list[str],
    body_pdf: Path,
) -> None:
    """A4: gecentreerde titel + toelichting + getrimde body-PDF-inhoud."""
    try:
        import pymupdf
    except ImportError as exc:
        raise RuntimeError(
            "pymupdf ontbreekt; installeer met: python -m pip install pymupdf"
        ) from exc

    if not body_pdf.is_file():
        raise FileNotFoundError(f"tekstblad-body-PDF ontbreekt: {body_pdf}")

    font_reg, _font_bold = _title_font_files()
    src = pymupdf.open(body_pdf)
    try:
        doc = pymupdf.open()
        page = doc.new_page(width=_A4_W, height=_A4_H)
        y = _MARGIN
        content_w = _A4_W - 2 * _MARGIN

        title_h = max(28.0, 13.0 * 1.85)
        title_rect = pymupdf.Rect(_MARGIN, y, _A4_W - _MARGIN, y + title_h)
        rc = page.insert_textbox(
            title_rect,
            title,
            fontsize=13.0,
            fontname="koormap-kop",
            fontfile=str(font_reg),
            align=pymupdf.TEXT_ALIGN_CENTER,
        )
        if rc < 0:
            raise RuntimeError(f"pagina-titel past niet: {title!r}")
        y += title_h + 10.0

        for note in notes:
            note_h = max(36.0, 11.0 * 2.4)
            note_rect = pymupdf.Rect(_MARGIN, y, _A4_W - _MARGIN, y + note_h)
            rc = page.insert_textbox(
                note_rect,
                note,
                fontsize=11.0,
                fontname="koormap-note",
                fontfile=str(font_reg),
                align=pymupdf.TEXT_ALIGN_CENTER,
            )
            if rc < 0:
                # Meer regels: hoger vak
                note_h = 72.0
                note_rect = pymupdf.Rect(_MARGIN, y, _A4_W - _MARGIN, y + note_h)
                rc = page.insert_textbox(
                    note_rect,
                    note,
                    fontsize=11.0,
                    fontname="koormap-note",
                    fontfile=str(font_reg),
                    align=pymupdf.TEXT_ALIGN_CENTER,
                )
                if rc < 0:
                    raise RuntimeError(f"toelichting past niet: {note!r}")
            y += note_h + 8.0

        y += 4.0
        avail_h = _A4_H - _MARGIN - y
        if avail_h < 40.0:
            raise RuntimeError("geen ruimte meer voor tekstblad-inhoud op A4")

        # Eén blad: inhoud van alle bronpagina’s onder elkaar, getrimd.
        clips: list[tuple[object, object]] = []
        total_h = 0.0
        max_w = 0.0
        for i in range(len(src)):
            sp = src[i]
            clip = _pdf_page_content_clip(sp)
            clips.append((sp, clip))
            total_h += float(clip.height)
            max_w = max(max_w, float(clip.width))
        if total_h <= 0 or max_w <= 0:
            raise RuntimeError(f"lege tekstblad-body-PDF: {body_pdf}")

        gap = 6.0
        gaps = gap * max(0, len(clips) - 1)
        scale = min(content_w / max_w, (avail_h - gaps) / total_h, 1.0)
        scale = max(0.15, scale)

        for i, (sp, clip) in enumerate(clips):
            draw_w = float(clip.width) * scale
            draw_h = float(clip.height) * scale
            if y + draw_h > _A4_H - _MARGIN + 0.5:
                raise RuntimeError(
                    f"tekstblad-inhoud past niet op één A4 na trim "
                    f"(schaal={scale:.3f}, nodig={draw_h:.1f}pt)"
                )
            x0 = _MARGIN + max(0.0, (content_w - draw_w) / 2)
            dest_rect = pymupdf.Rect(x0, y, x0 + draw_w, y + draw_h)
            page.show_pdf_page(dest_rect, src, sp.number, clip=clip)
            y += draw_h
            if i < len(clips) - 1:
                y += gap

        dest.parent.mkdir(parents=True, exist_ok=True)
        tmp = dest.with_suffix(dest.suffix + ".tmp")
        doc.save(tmp)
        doc.close()
        tmp.replace(dest)
    finally:
        src.close()


def compose_voorzien_pdf(dest: Path, *, title: str) -> None:
    """A4-placeholder: afgeleide titel + korte «voorzien»-tekst (geen notatie)."""
    try:
        import pymupdf
    except ImportError as exc:
        raise RuntimeError(
            "pymupdf ontbreekt; installeer met: python -m pip install pymupdf"
        ) from exc

    font_reg, _font_bold = _title_font_files()
    doc = pymupdf.open()
    page = doc.new_page(width=_A4_W, height=_A4_H)
    y = _MARGIN
    title_h = max(28.0, 13.0 * 1.85)
    rect = pymupdf.Rect(_MARGIN, y, _A4_W - _MARGIN, y + title_h)
    page.insert_textbox(
        rect,
        title,
        fontsize=13.0,
        fontname="koormap-kop",
        fontfile=str(font_reg),
        align=pymupdf.TEXT_ALIGN_CENTER,
    )
    y += title_h + 24.0
    body = (
        "Voorzien\n\n"
        "Er is nog geen partituur voor dit blad. "
        "Het catalogus-id is gereserveerd."
    )
    body_rect = pymupdf.Rect(_MARGIN, y, _A4_W - _MARGIN, _A4_H - _MARGIN)
    page.insert_textbox(
        body_rect,
        body,
        fontsize=12.0,
        fontname="koormap-voorzien",
        fontfile=str(font_reg),
        align=pymupdf.TEXT_ALIGN_CENTER,
    )
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".tmp")
    doc.save(tmp)
    doc.close()
    tmp.replace(dest)


def _catalogus_voorzien_title(md_path: Path, leaf_id: str) -> str:
    from catalogus import derived_leaf_title

    leaf_dir = CATALOGUS.joinpath(*leaf_id.split("/"))
    return derived_leaf_title(leaf_id, leaf_dir=leaf_dir)


def catalogus_needs_voorzien_pdf(md_path: Path) -> str | None:
    """Als deze catalogus-leaf een voorzien-placeholder mag: leaf-id, anders None.

    Geen notatie (``.vsa``/``.mvsa``/``.mscz``) en geen tekstblad-bron.
    """
    leaf_id = catalogus_leaf_id(md_path)
    if not leaf_id:
        return None
    if leaf_has_tekstblad(leaf_id) or find_tekstblad_md(leaf_id):
        return None
    if try_find_notation_source(leaf_id) is not None:
        return None
    return leaf_id


def catalogus_tekstblad_pagina_job(
    md_path: Path,
) -> tuple[str, Path] | None:
    """Leaf-id + ``*.tekstblad.md`` als deze leaf een tekstblad-pagina.pdf krijgt."""
    leaf_id = catalogus_leaf_id(md_path)
    if not leaf_id:
        return None
    if try_find_notation_source(leaf_id) is not None:
        return None
    tb_md = find_tekstblad_md(leaf_id)
    if tb_md is None:
        return None
    return leaf_id, tb_md


def _catalogus_tekstblad_pagina_title(leaf_id: str) -> str:
    md = find_tekstblad_md(leaf_id)
    if md is not None:
        hint = _frontmatter_title(md)
        if hint:
            return hint
    from catalogus import derived_leaf_title

    return derived_leaf_title(
        leaf_id, leaf_dir=CATALOGUS.joinpath(*leaf_id.split("/"))
    )


def _svg_page_index(path: Path) -> int:
    match = re.search(r"-(\d+)\.svg$", path.name, re.IGNORECASE)
    return int(match.group(1)) if match else 0


def stitch_pdfs(sources: list[Path], dest: Path) -> None:
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError as exc:
        raise RuntimeError(
            "pypdf ontbreekt; installeer met: python -m pip install pypdf"
        ) from exc

    writer = PdfWriter()
    for src in sources:
        writer.append(PdfReader(str(src)))
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".tmp")
    with tmp.open("wb") as fh:
        writer.write(fh)
    tmp.replace(dest)


def _vsa_exe() -> str:
    sibling_vsa = (
        ROOT.parent / "VSA-tooling" / ".venv" / "Scripts" / "vsa.exe"
    )
    if sibling_vsa.is_file():
        return str(sibling_vsa)
    which = shutil.which("vsa")
    if which:
        return which
    raise RuntimeError(
        "vsa niet op PATH. Oplossing: scripts\\_ensure.cmd --vsa-tool "
        "(sibling ..\\VSA-tooling of pin)."
    )


def _mvsa_cli() -> list[str]:
    # ``mvsa`` is een apart CLI-entry (mvsa.exe), geen subcommando van ``vsa``.
    sibling_mvsa = (
        ROOT.parent / "VSA-tooling" / ".venv" / "Scripts" / "mvsa.exe"
    )
    if sibling_mvsa.is_file():
        return [str(sibling_mvsa)]
    if shutil.which("mvsa"):
        return ["mvsa"]
    raise RuntimeError(
        "mvsa niet op PATH. Oplossing: scripts\\_ensure.cmd --vsa-tool "
        "(sibling ..\\VSA-tooling of pin)."
    )


def export_blad_svgs(
    source: Path, dest: Path, *, compact: bool = False
) -> list[Path]:
    """Exporteer kale blad-SVG('s); bij multi-page: ``dest.stem-N.svg``."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        dest.unlink()
    for stale in dest.parent.glob(f"{dest.stem}-*.svg"):
        stale.unlink(missing_ok=True)

    suffix = source.suffix.lower()
    if suffix in {".mvsa", ".mscz"}:
        cmd = [*_mvsa_cli(), "svg", str(source), "-o", str(dest)]
        if compact and suffix == ".mvsa":
            cmd.append("--compact")
        label = "SVG --compact" if compact and suffix == ".mvsa" else "SVG"
    elif suffix == ".vsa":
        cmd = [_vsa_exe(), "svg", str(source), "-o", str(dest)]
        label = "SVG (vsa)"
    else:
        raise RuntimeError(f"SVG-export: onverwacht brontype {source.name}")

    print(f"  {label} {source}", flush=True)
    subprocess.check_call(cmd, cwd=str(ROOT))
    pages = sorted(
        dest.parent.glob(f"{dest.stem}-*.svg"),
        key=_svg_page_index,
    )
    if dest.is_file():
        return [dest]
    if pages:
        return pages
    raise RuntimeError(f"SVG ontbreekt na export: {dest}")


def export_compact_svg(mvsa: Path, dest: Path) -> None:
    """Compat: schrijf compacte SVG (of bladreeks) voor ``dest``."""
    export_blad_svgs(mvsa, dest, compact=True)


def _compose_flow_svg(flow: PageFlow, dest: Path, *, work: Path) -> None:
    """Zet titel(s) + kale blad-SVG's op A4.

    Doel (koormap-dichtheid, zie scan-referentie alleluja's): één
    ``pdf-bijelkaar``-blok idealiter op **één** A4 — uniforme schaal zodat
    alle stukken + koppen in de bladhoogte passen. Tussenkop-pt schaalt mee
    met de lyrics in die SVG. Lange stukken: bladreeks pagina voor pagina.
    """
    try:
        import pymupdf
    except ImportError as exc:
        raise RuntimeError(
            "pymupdf ontbreekt; installeer met: python -m pip install pymupdf"
        ) from exc

    svg_series: dict[str, list[Path]] = {}
    for item in flow.items:
        if isinstance(item, MusicItem):
            if item.uv_id in svg_series:
                continue
            source = find_notation_source(item.uv_id)
            out = work / f"{item.uv_id.replace('/', '__')}.svg"
            try:
                rel = source.relative_to(ROOT)
            except ValueError:
                rel = source
            print(f"  bron {rel}", flush=True)
            svg_series[item.uv_id] = export_blad_svgs(
                source, out, compact=item.compact
            )

    # Per blad-SVG een PDF-pagina (afmetingen + place)
    svg_pdfs: dict[str, list[object]] = {}
    sizes: dict[str, list[tuple[float, float]]] = {}
    for uv_id, paths in svg_series.items():
        docs: list[object] = []
        dims: list[tuple[float, float]] = []
        for svg_path in paths:
            svg_doc = pymupdf.open(svg_path)
            try:
                src = pymupdf.open("pdf", svg_doc.convert_to_pdf())
            finally:
                svg_doc.close()
            sw, sh = src[0].rect.width, src[0].rect.height
            if sw <= 0 or sh <= 0:
                src.close()
                raise RuntimeError(f"ongeldige SVG-afmeting: {svg_path}")
            docs.append(src)
            dims.append((sw, sh))
        svg_pdfs[uv_id] = docs
        sizes[uv_id] = dims

    try:
        content_w = _A4_W - 2 * _MARGIN
        avail = _A4_H - 2 * _MARGIN
        gap = 4.0  # strak, vergelijkbaar met scan-koormap

        music_ids = [
            i.uv_id for i in flow.items if isinstance(i, MusicItem)
        ]
        n_prom = sum(
            1
            for i in flow.items
            if isinstance(i, TitleItem) and i.prominent
        )
        n_tussen = sum(
            1
            for i in flow.items
            if isinstance(i, TitleItem) and not i.prominent
        )
        space_pts = sum(
            i.points for i in flow.items if isinstance(i, SpaceItem)
        )
        n_items = len(flow.items)
        n_gaps = max(0, n_items - 1)
        # Extra gaps tussen bladreeks-pagina's van hetzelfde stuk
        n_page_gaps = sum(max(0, len(sizes[mid]) - 1) for mid in music_ids)
        sum_sh = sum(h for mid in music_ids for _, h in sizes[mid])
        max_sw = max(
            (w for mid in music_ids for w, _ in sizes[mid]),
            default=content_w,
        )

        # Schaal: binnen pdf-bijelkaar (--compact) streven naar één A4
        # (min breedte/hoogte). Zonder bijelkaar: leesbare breedte-schaal;
        # bladreeks mag over meerdere A4 (catalogus lange mvsa e.d.).
        # Tussenkop-vak ≥ 24 pt hoog (anders weigert pymupdf insert_textbox).
        lyric_k = 13.0 * 1.15
        fixed = (
            n_prom * 30.0
            + n_tussen * 26.0
            + (n_gaps + n_page_gaps) * gap
            + space_pts
        )
        s_h = ((avail - fixed) / sum_sh) if sum_sh > 1e-6 else 1.0
        s_w = content_w / max_sw if max_sw > 0 else 1.0
        if flow.any_compact:
            scale = max(0.12, min(s_w, s_h))
        else:
            scale = max(0.12, min(s_w, 1.0))
        print(
            f"  compose-schaal {scale:.3f} "
            f"(breedte-max {s_w:.3f}, hoogte-fit {s_h:.3f}"
            f"{', bijelkaar' if flow.any_compact else ', meerbladig-ok'})",
            flush=True,
        )

        doc = pymupdf.open()
        page = doc.new_page(width=_A4_W, height=_A4_H)
        y = _MARGIN

        def new_page() -> None:
            nonlocal page, y
            page = doc.new_page(width=_A4_W, height=_A4_H)
            y = _MARGIN

        font_reg, font_bold = _title_font_files()

        for idx, item in enumerate(flow.items):
            if isinstance(item, TitleItem):
                if item.prominent:
                    fontsize, pad = 13.0, 4.0
                    fontfile, fontname = font_reg, "koormap-kop"
                else:
                    # Zelfde optische maat als lyrics in de geschaalde SVG
                    fontsize = max(8.0, lyric_k * scale)
                    pad = 1.0
                    fontfile, fontname = font_bold, "koormap-tussenkop"
                # pymupdf insert_textbox faalt stil als het vak te laag is
                # (rc < 0); ~1.85× fontsize is veilig voor latijnse metrics.
                box_h = max(24.0, fontsize * 1.85)
                if y + box_h > _A4_H - _MARGIN and y > _MARGIN + 1:
                    new_page()
                rect = pymupdf.Rect(_MARGIN, y, _A4_W - _MARGIN, y + box_h)
                rc = page.insert_textbox(
                    rect,
                    item.text,
                    fontsize=fontsize,
                    fontname=fontname,
                    fontfile=str(fontfile),
                    align=pymupdf.TEXT_ALIGN_CENTER,
                )
                if rc < 0:
                    raise RuntimeError(
                        f"titel past niet in PDF-vak ({item.text!r}, "
                        f"fontsize={fontsize}, box_h={box_h}, rc={rc})"
                    )
                y += box_h + pad
            elif isinstance(item, SpaceItem):
                if y + item.points > _A4_H - _MARGIN and y > _MARGIN + 1:
                    new_page()
                y += item.points
            else:
                docs = svg_pdfs[item.uv_id]
                dims = sizes[item.uv_id]
                for page_i, (src, (sw, sh)) in enumerate(zip(docs, dims)):
                    draw_w = sw * scale
                    draw_h = sh * scale
                    if y + draw_h > _A4_H - _MARGIN and y > _MARGIN + 1:
                        new_page()
                    x0 = _MARGIN + max(0.0, (content_w - draw_w) / 2)
                    dest_rect = pymupdf.Rect(x0, y, x0 + draw_w, y + draw_h)
                    page.show_pdf_page(dest_rect, src, 0)
                    y += draw_h
                    if page_i < len(docs) - 1:
                        y += gap
            if idx < n_items - 1:
                y += gap

        dest.parent.mkdir(parents=True, exist_ok=True)
        tmp = dest.with_suffix(dest.suffix + ".tmp")
        doc.save(tmp)
        doc.close()
        tmp.replace(dest)
    finally:
        for docs in svg_pdfs.values():
            for src in docs:
                src.close()


def build_one(md_path: Path, *, force: bool = False) -> Path | None:
    md_path = md_path.resolve()
    out = _pagina_pdf_out_path(md_path)
    text = md_path.read_text(encoding="utf-8")

    voorzien_id = catalogus_needs_voorzien_pdf(md_path)
    if voorzien_id is not None:
        if out.is_file() and not force:
            if out.stat().st_mtime >= md_path.stat().st_mtime:
                return out
        title = _catalogus_voorzien_title(md_path, voorzien_id)
        print(f"  voorzien-placeholder {voorzien_id}", flush=True)
        compose_voorzien_pdf(out, title=title)
        return out

    tekstblad_job = catalogus_tekstblad_pagina_job(md_path)
    if tekstblad_job is not None:
        leaf_id, tb_md = tekstblad_job
        deps = [md_path, tb_md]
        if out.is_file() and not force:
            newest = max(p.stat().st_mtime for p in deps if p.is_file())
            if out.stat().st_mtime >= newest:
                return out
        title = _catalogus_tekstblad_pagina_title(leaf_id)
        notes = prose_notes_from_catalogus_md(text)
        print(f"  tekstblad-pagina {leaf_id}", flush=True)
        compose_tekstblad_pagina_pdf(
            out, title=title, notes=notes, tekstblad_md=tb_md
        )
        return out

    if "bieb" not in text and "muziek" not in text:
        return None
    try:
        flows = parse_page_flows(text)
    except ValueError as exc:
        raise ValueError(f"{md_path}: {exc}") from exc
    flows = ensure_catalogus_derived_titles(flows, md_path)
    if not flows:
        return None

    # Bronnen voor mtime-check (notatiebestanden, geen catalogus-PDF)
    deps = [md_path]
    for flow in flows:
        for mid in flow.music_ids:
            deps.append(find_notation_source(mid))

    if out.is_file() and not force:
        newest = max(p.stat().st_mtime for p in deps if p.is_file())
        if out.stat().st_mtime >= newest:
            return out

    with tempfile.TemporaryDirectory(prefix="pagina-pdf-") as tmp:
        work = Path(tmp)
        parts: list[Path] = []
        for i, flow in enumerate(flows):
            if not flow.items:
                continue
            part = work / f"flow-{i}.pdf"
            _compose_flow_svg(flow, part, work=work / f"svg-{i}")
            parts.append(part)
        if not parts:
            return None
        if len(parts) == 1:
            shutil.copy2(parts[0], out)
        else:
            stitch_pdfs(parts, out)
    return out


def expand_pagina_md_path(path: Path) -> list[Path]:
    """Eén ``index.md`` of een map → recursief alle ``index.md``."""
    from input_paths import InputPathError, collect_cli_sources

    p = path if path.is_absolute() else ROOT / path
    if not p.exists():
        raise SystemExit(f"Pad niet gevonden: {p}")
    if p.is_file():
        if p.suffix.lower() != ".md":
            raise SystemExit(f"Verwacht .md-bestand of map; kreeg: {p.name}")
        return [p.resolve()]
    try:
        return [
            f.resolve()
            for f in collect_cli_sources(p, suffixes=[".md"], names=["index.md"])
        ]
    except InputPathError as exc:
        raise SystemExit(str(exc)) from exc


def iter_targets(explicit: list[Path], all_koormappen: bool) -> list[Path]:
    """Paden (bestand of map) en/of suiker ``--all-koormappen``."""
    paths = list(explicit)
    if all_koormappen:
        paths.append(CONTENT / "koormappen")
    if not paths:
        raise SystemExit(
            "Geef een .md-pad of map, of gebruik --all-koormappen "
            "(suiker voor content-source\\koormappen)."
        )
    out: list[Path] = []
    seen: set[Path] = set()
    for raw in paths:
        for md in expand_pagina_md_path(raw):
            if md in seen:
                continue
            seen.add(md)
            out.append(md)
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=(
            "Bouw index.pagina.pdf uit kale blad-SVG's + Markdown-koppen "
            "(pdf-bijelkaar → --compact). Pad = één .md of een map "
            "(recursief index.md)."
        )
    )
    ap.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Pad(en) naar index.md of map(pen) met index.md eronder",
    )
    ap.add_argument(
        "--all-koormappen",
        action="store_true",
        help="Suiker: zelfde als pad content-source\\koormappen",
    )
    ap.add_argument(
        "--force",
        action="store_true",
        help="Overschrijf ook als de PDF nieuwer lijkt dan de bronnen",
    )
    from batch_guard import (
        SKIP,
        add_yes_argument,
        confirm_batch,
        run_timed_batch,
    )

    add_yes_argument(ap)
    args = ap.parse_args(argv)

    targets = iter_targets(args.paths, args.all_koormappen)
    kind = "pagina_pdf"
    if not confirm_batch(
        kind,
        n=len(targets),
        headline=f"{len(targets)}× index.md → pagina-PDF",
        details=[
            "Actie: bouw/vernieuw index.pagina.pdf (MuseScore bij pdf-bijelkaar)",
            f"--force={'ja' if args.force else 'nee (sla over als PDF nieuwer lijkt)'}",
        ],
        yes=args.yes,
    ):
        return 2

    failed_paths: list[str] = []

    def _one(md: Path) -> int:
        if not md.is_file():
            print(f"OVERGESLAGEN (bestaat niet): {md}", file=sys.stderr)
            return SKIP
        try:
            out = build_one(md, force=args.force)
        except FileNotFoundError as exc:
            msg = str(exc)
            # Leaf zonder notatiebron (voorzien / tekstblad): geen harde fout
            if "geen .mvsa/.vsa/.mscz" in msg or "plakt geen catalogus-PDF" in msg:
                print(f"OVERGESLAGEN: {exc}", file=sys.stderr)
                return SKIP
            print(f"FOUT: {exc}", file=sys.stderr)
            failed_paths.append(str(md))
            return 1
        except (
            ValueError,
            RuntimeError,
            subprocess.CalledProcessError,
        ) as exc:
            print(f"FOUT: {exc}", file=sys.stderr)
            failed_paths.append(str(md))
            return 1
        if out is None:
            return SKIP
        print(f"OK {out.relative_to(ROOT)} ({md.relative_to(ROOT)})")
        return 0

    written, failed, skipped = run_timed_batch(
        kind,
        targets,
        _one,
        label=lambda p: p.as_posix(),
    )
    if failed_paths:
        print("Mislukt:", flush=True)
        for p in failed_paths:
            print(f"  - {p}", flush=True)
    print(f"Klaar: {written} PDF(s), {skipped} overgeslagen, {failed} mislukt.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
