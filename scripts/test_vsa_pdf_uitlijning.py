"""Blad-PDF: tekst en accenttekens op dezelfde plaats als op het scherm.

Contract: docs/specs/schermpartituur.md §2.3. Draai deze test bij elke
wijziging aan de SVG-naar-PDF-omzetting of aan de VSA-tooling-pin.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import index_md_pdf as pp

pymupdf = pytest.importorskip("pymupdf")

_ECHT = sorted(pp.CATALOGUS.rglob("*.vsa.svg"))[:25]


def _svg(body: str) -> str:
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="200" height="100" '
        f'viewBox="0 0 200 100">{body}</svg>'
    )


def _plaatsen(path: Path):
    """Oorsprong van alle tekst en beginpunt van alle lijnen in de PDF."""
    doc = pp.open_svg_as_pdf(path)
    try:
        page = doc[0]
        tekst = [
            span["origin"]
            for block in page.get_text("dict")["blocks"]
            for line in block.get("lines", [])
            for span in line["spans"]
            if span["text"].strip()
        ]
        lijnen = [
            (d["rect"].x0, d["rect"].y0)
            for d in page.get_drawings()
            if d["items"][0][0] == "l"
        ]
        return tekst, lijnen
    finally:
        doc.close()


@pytest.mark.parametrize(
    "transform", ["", "translate(-2.00 -9.07)", "translate(5,4) scale(0.5)"]
)
def test_tekst_en_lijn_schuiven_samen(tmp_path: Path, transform: str) -> None:
    if pp._notation_font_file("DejaVu Sans") is None:
        pytest.skip("DejaVu Sans TTF niet gevonden")
    svg = tmp_path / "x.vsa.svg"
    svg.write_text(
        _svg(
            f'<g transform="{transform}"><g class="vsa-line">'
            '<text x="20" y="50" font-family="DejaVu Sans" font-size="20">Laat</text>'
            '<line x1="20" y1="50" x2="60" y2="50" stroke="red"/>'
            "</g></g>"
        ),
        encoding="utf-8",
    )
    tekst, lijnen = _plaatsen(svg)
    assert tekst[0][0] == pytest.approx(lijnen[0][0], abs=0.6)
    assert tekst[0][1] == pytest.approx(lijnen[0][1], abs=0.6)


def test_snijpunten_tellen_buitenste_verschuiving_mee() -> None:
    svg = _svg(
        '<g transform="translate(0 -9)">'
        '<g class="vsa-line"><text y="30">a</text></g>'
        '<g class="vsa-line" transform="translate(0 40)"><text y="30">b</text></g>'
        "</g>"
    )
    assert pp._vsa_line_systems(svg) == [(21.0, 21.0), (61.0, 61.0)]


@pytest.mark.skipif(not _ECHT, reason="geen .vsa.svg in de catalogus")
@pytest.mark.parametrize("svg", _ECHT, ids=lambda p: p.name)
def test_echte_bladen_tekst_op_zijn_plaats(svg: Path) -> None:
    """Vergelijk met MuPDF zelf, dat transforms op tekst wél toepast."""
    if pp._notation_font_file("DejaVu Sans") is None:
        pytest.skip("DejaVu Sans TTF niet gevonden")
    eigen, _ = _plaatsen(svg)
    ref = pymupdf.open(svg)
    try:
        page = pymupdf.open("pdf", ref.convert_to_pdf())[0]
        verwacht = [
            span["origin"]
            for block in page.get_text("dict")["blocks"]
            for line in block.get("lines", [])
            for span in line["spans"]
            if span["text"].strip()
        ]
    finally:
        ref.close()
    # Zelfde basislijnen (breedtes verschillen door het vervangende lettertype).
    assert sorted({round(y) for _, y in eigen}) == sorted({round(y) for _, y in verwacht})
