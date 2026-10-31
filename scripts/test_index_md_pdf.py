"""Unit tests voor index_md_pdf parsing (geen MuseScore)."""

from __future__ import annotations

from pathlib import Path

import index_md_pdf as pp


def test_parse_vredeslitanie_bijelkaar() -> None:
    text = """---
title: "Vredeslitanie"
---

{{< pdf-bijelkaar >}}

{{< kop >}}(1a) Vredeslitanie{{< /kop >}}

{{< bieb id="ektinia/vrede/hemelum" >}}

{{< muziek >}}

{{< /bieb >}}

{{< bieb id="ektinia/vrede/hemelum-ksl" >}}

{{< muziek >}}

{{< /bieb >}}

{{< /pdf-bijelkaar >}}
"""
    flows = pp.parse_page_flows(text)
    assert len(flows) == 1
    assert flows[0].any_compact
    assert [i.text for i in flows[0].items if isinstance(i, pp.TitleItem)] == [
        "(1a) Vredeslitanie"
    ]
    assert flows[0].music_ids == [
        "ektinia/vrede/hemelum",
        "ektinia/vrede/hemelum-ksl",
    ]
    assert all(
        isinstance(i, pp.MusicItem) and i.compact
        for i in flows[0].items
        if isinstance(i, pp.MusicItem)
    )


def test_pdf_pagina_splits_flows() -> None:
    text = """
{{< bieb id="a/b/c" >}}
{{< muziek >}}
{{< /bieb >}}
{{< pdf-pagina >}}
{{< bieb id="d/e/f" muziek />}}
"""
    flows = pp.parse_page_flows(text)
    assert len(flows) == 2
    assert flows[0].music_ids == ["a/b/c"]
    assert flows[1].music_ids == ["d/e/f"]
    assert not flows[0].any_compact


def test_alleluia_twee_bijelkaar_flows() -> None:
    """Elk pdf-bijelkaar = eigen bladgroep; kop buiten blok alleen op eerste blad."""
    text = """---
title: "9b Alleluia"
---

{{< kop >}}(9b) Alleluia{{< /kop >}}

{{< pdf-bijelkaar >}}

{{< kop links middel >}}Toon 1{{< /kop >}}

{{< bieb id="alleluia/9a-toon-1/groningen" />}}

{{< kop links middel >}}Toon 2{{< /kop >}}

{{< bieb id="alleluia/9a-toon-2/groningen" />}}

{{< /pdf-bijelkaar >}}

{{< pdf-bijelkaar >}}

{{< kop links middel >}}Toon 5{{< /kop >}}

{{< bieb id="alleluia/9a-toon-5/groningen" />}}

{{< /pdf-bijelkaar >}}
"""
    flows = pp.parse_page_flows(text)
    assert len(flows) == 2
    assert all(f.any_compact for f in flows)

    assert flows[0].music_ids == [
        "alleluia/9a-toon-1/groningen",
        "alleluia/9a-toon-2/groningen",
    ]
    assert flows[1].music_ids == ["alleluia/9a-toon-5/groningen"]

    t0 = [i for i in flows[0].items if isinstance(i, pp.TitleItem)]
    assert [(i.text, i.prominent) for i in t0] == [
        ("(9b) Alleluia", True),
        ("Toon 1", False),
        ("Toon 2", False),
    ]
    t1 = [i for i in flows[1].items if isinstance(i, pp.TitleItem)]
    assert [(i.text, i.prominent) for i in t1] == [
        ("Toon 5", False),
    ]


def test_legacy_h1_and_hash_titles_still_parsed() -> None:
    """Legacy HTML-h1 en Markdown-``#`` blijven leesbaar (veel slots gebruiken ``#``)."""
    text = """
{{< pdf-bijelkaar >}}
<h1 style="text-align: center">(1a) Oud</h1>
{{< bieb id="a/b/c" />}}
{{< /pdf-bijelkaar >}}
"""
    flows = pp.parse_page_flows(text)
    titles = [(i.text, i.prominent) for i in flows[0].items if isinstance(i, pp.TitleItem)]
    assert titles == [("(1a) Oud", True)]

    text_md = """
# Bladtitel uit hekje
{{< bieb id="x/y/z" />}}
"""
    flows_md = pp.parse_page_flows(text_md)
    assert [(i.text, i.prominent) for i in flows_md[0].items if isinstance(i, pp.TitleItem)] == [
        ("Bladtitel uit hekje", True)
    ]


def test_witruimte_between_music() -> None:
    text = """
{{< pdf-bijelkaar >}}
{{< bieb id="a/b/c" />}}
{{< witruimte groot >}}
{{< bieb id="d/e/f" />}}
{{< /pdf-bijelkaar >}}
"""
    flows = pp.parse_page_flows(text)
    assert len(flows) == 1
    kinds = [type(i).__name__ for i in flows[0].items]
    assert kinds == ["MusicItem", "SpaceItem", "MusicItem"]
    space = flows[0].items[1]
    assert isinstance(space, pp.SpaceItem)
    assert space.points == pp._WITRUIMTE_PT["groot"]


def test_koormap_two_kops_keep_document_order() -> None:
    """Koormap-paginataal §6/§10: elke ``kop`` blijft vóór zijn ``bieb``.

    Regressie: groot-koppen buiten ``pdf-bijelkaar`` werden gebundeld vóór
    alle muziek → NL-titel + KSL-titel, daarna beide partituren.
    """
    text = """---
title: "Eerste Kleine Litanie"
---

{{< kop >}}1e Kleine Ektinia{{< /kop >}}

{{< bieb id="ektinia/eerste-kleine/hemelum" />}}

{{< witruimte groot >}}

{{< kop >}}Малая ектения{{< /kop >}}

{{< bieb id="ektinia/eerste-kleine/hemelum-ksl" />}}
"""
    flows = pp.parse_page_flows(text)
    assert len(flows) == 1
    kinds = [
        (
            type(i).__name__,
            getattr(i, "text", None) or getattr(i, "uv_id", None) or getattr(i, "points", None),
        )
        for i in flows[0].items
    ]
    assert kinds == [
        ("TitleItem", "1e Kleine Ektinia"),
        ("MusicItem", "ektinia/eerste-kleine/hemelum"),
        ("SpaceItem", pp._WITRUIMTE_PT["groot"]),
        ("TitleItem", "Малая ектения"),
        ("MusicItem", "ektinia/eerste-kleine/hemelum-ksl"),
    ]


def test_find_notation_source_prefers_mvsa(tmp_path, monkeypatch) -> None:
    leaf = tmp_path / "catalogus" / "a" / "b" / "c"
    leaf.mkdir(parents=True)
    (leaf / "x.vsa").write_text("L: a\n", encoding="utf-8")
    mvsa = leaf / "x.mvsa"
    mvsa.write_text("@do C4\nL: a |\nS: c |\n", encoding="utf-8")
    monkeypatch.setattr(pp, "CATALOGUS", tmp_path / "catalogus")
    assert pp.find_notation_source("a/b/c") == mvsa


def test_svg_page_index_order() -> None:
    paths = [
        Path("lied-10.svg"),
        Path("lied-2.svg"),
        Path("lied-1.svg"),
    ]
    assert sorted(paths, key=pp._svg_page_index)[0].name == "lied-1.svg"
    assert sorted(paths, key=pp._svg_page_index)[-1].name == "lied-10.svg"


def test_cyrillic_kop_in_composed_pdf(tmp_path: Path) -> None:
    """Koppen gebruiken Unicode-font; Cyrillisch mag geen '?' worden."""
    import pymupdf

    dest = tmp_path / "titel.pdf"
    flow = pp.PageFlow(
        items=[pp.TitleItem("Малая ектения", size="groot", align="midden")]
    )
    pp._compose_flow_svg(flow, dest, work=tmp_path / "work")
    doc = pymupdf.open(dest)
    try:
        extracted = doc[0].get_text()
    finally:
        doc.close()
    assert "Малая" in extracted
    assert "ектения" in extracted
    assert "?????" not in extracted


def test_parse_prose_and_bieb_copyright(tmp_path, monkeypatch) -> None:
    """Proza tussen shortcodes + ``bieb copyright`` horen in de flow."""
    cat = tmp_path / "catalogus"
    leaf = cat / "vriendelijk-licht" / "default" / "x"
    leaf.mkdir(parents=True)
    (leaf / "lied.mvsa").write_text(
        '@do C4\n@copyright "CC BY-SA 4.0 — zie colofon"\nL: a |\nS: c |\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(pp, "CATALOGUS", cat)
    text = """---
title: "Demo"
---

{{< kop >}}Vriendelijk Licht{{< /kop >}}

bron: Groningen

{{< bieb id="vriendelijk-licht/default/x" />}}

{{< bieb id="vriendelijk-licht/default/x" copyright />}}
"""
    flows = pp.parse_page_flows(text)
    assert len(flows) == 1
    kinds = [type(i).__name__ for i in flows[0].items]
    assert kinds == ["TitleItem", "TextItem", "MusicItem", "TextItem"]
    assert flows[0].items[0].text == "Vriendelijk Licht"
    assert flows[0].items[0].align == "midden"
    assert flows[0].items[0].size == "groot"
    assert flows[0].items[1].text == "bron: Groningen"
    assert "CC BY-SA" in flows[0].items[3].text


def test_markdown_heading_and_prose_are_left_aligned() -> None:
    text = """
{{< kop links middel >}}Rubriek{{< /kop >}}

## Markdown tussenkop

gewone alinea links
"""
    flows = pp.parse_page_flows(text)
    items = flows[0].items
    assert isinstance(items[0], pp.TitleItem)
    assert items[0].align == "links" and items[0].size == "middel"
    assert isinstance(items[1], pp.TitleItem)
    assert items[1].text == "Markdown tussenkop"
    assert items[1].align == "links" and items[1].size == "middel"
    assert isinstance(items[2], pp.TextItem)
    assert items[2].text == "gewone alinea links"


def test_build_colofon_when_missing_vbox(tmp_path, monkeypatch) -> None:
    cat = tmp_path / "catalogus"
    leaf = cat / "a" / "b" / "c"
    leaf.mkdir(parents=True)
    (leaf / "x.mvsa").write_text(
        '@do C4\n@copyright "CC BY-SA 4.0 — zie colofon"\n'
        '@bron "Groningen"\nL: a |\nS: c |\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(pp, "CATALOGUS", cat)
    text = pp.resolve_bieb_onderdeel("a/b/c", "colofon")
    assert text.startswith("Colofon")
    assert "CC BY-SA 4.0" in text
    assert "Bibliotheek-id: a/b/c" in text
    assert "Bron: Groningen" in text


def test_copyright_falls_back_to_mscz_metatag(tmp_path, monkeypatch) -> None:
    """Geïmporteerde sketch zonder ``@copyright``: lees MuseScore-metaTag."""
    import zipfile

    cat = tmp_path / "catalogus"
    leaf = cat / "a" / "b" / "c"
    leaf.mkdir(parents=True)
    (leaf / "a.mscz.mvsa").write_text("@do C4\nL: a |\nS: c |\n", encoding="utf-8")
    mscx = (
        '<?xml version="1.0"?>\n<museScore>\n'
        '<metaTag name="copyright">CC BY-SA 4.0 — zie colofon</metaTag>\n'
        "</museScore>\n"
    )
    mscz = leaf / "a.mscz"
    with zipfile.ZipFile(mscz, "w") as zf:
        zf.writestr("score.mscx", mscx)
    monkeypatch.setattr(pp, "CATALOGUS", cat)
    assert "CC BY-SA" in pp.resolve_bieb_onderdeel("a/b/c", "copyright")


def test_expand_pagina_md_path_directory(tmp_path, monkeypatch) -> None:
    """Map → recursief index.md (bestand-of-map)."""
    slot = tmp_path / "koormappen" / "x" / "slot"
    slot.mkdir(parents=True)
    idx = slot / "index.md"
    other = slot / "notes.md"
    idx.write_text("---\ntitle: X\n---\n", encoding="utf-8")
    other.write_text("# n\n", encoding="utf-8")
    monkeypatch.setattr(pp, "ROOT", tmp_path)
    monkeypatch.setattr(pp, "CONTENT", tmp_path)
    got = pp.expand_pagina_md_path(tmp_path / "koormappen")
    assert got == [idx.resolve()]


def test_catalogus_leaf_id(tmp_path, monkeypatch) -> None:
    cat = tmp_path / "catalogus"
    leaf = cat / "tropaar" / "zondag-toon-1" / "groningen"
    leaf.mkdir(parents=True)
    md = leaf / "index.md"
    md.write_text("{{< bieb id=\"tropaar/zondag-toon-1/groningen\" />}}\n", encoding="utf-8")
    monkeypatch.setattr(pp, "CATALOGUS", cat)
    assert pp.catalogus_leaf_id(md) == "tropaar/zondag-toon-1/groningen"
    koor = tmp_path / "koormappen" / "x" / "index.md"
    koor.parent.mkdir(parents=True)
    koor.write_text("x\n", encoding="utf-8")
    assert pp.catalogus_leaf_id(koor) is None


def test_ensure_catalogus_derived_titles_injects(tmp_path, monkeypatch) -> None:
    cat = tmp_path / "catalogus"
    leaf = cat / "tropaar" / "zondag-toon-1" / "groningen"
    leaf.mkdir(parents=True)
    (leaf / "x.vsa").write_text(
        "---\ntitel: Tropaar zondag toon 1\nsoort: tropaar\n---\nL: a\n",
        encoding="utf-8",
    )
    md = leaf / "index.md"
    md.write_text(
        '{{< bieb id="tropaar/zondag-toon-1/groningen" />}}\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(pp, "CATALOGUS", cat)
    flows = pp.parse_page_flows(md.read_text(encoding="utf-8"))
    assert not any(
        isinstance(i, pp.TitleItem) for i in flows[0].items
    )
    flows = pp.ensure_catalogus_derived_titles(flows, md)
    titles = [i.text for i in flows[0].items if isinstance(i, pp.TitleItem)]
    assert len(titles) == 1
    assert "Tropaar" in titles[0]
    assert "Groningen" in titles[0]


def test_ensure_catalogus_derived_titles_skips_existing_hash(
    tmp_path, monkeypatch
) -> None:
    cat = tmp_path / "catalogus"
    leaf = cat / "a" / "b" / "c"
    leaf.mkdir(parents=True)
    md = leaf / "index.md"
    md.write_text("# Handmatig\n{{< bieb id=\"a/b/c\" />}}\n", encoding="utf-8")
    monkeypatch.setattr(pp, "CATALOGUS", cat)
    flows = pp.parse_page_flows(md.read_text(encoding="utf-8"))
    flows = pp.ensure_catalogus_derived_titles(flows, md)
    titles = [i.text for i in flows[0].items if isinstance(i, pp.TitleItem)]
    assert titles == ["Handmatig"]


def test_ensure_catalogus_derived_titles_skips_koormap(
    tmp_path, monkeypatch
) -> None:
    cat = tmp_path / "catalogus"
    cat.mkdir()
    monkeypatch.setattr(pp, "CATALOGUS", cat)
    md = tmp_path / "koormappen" / "slot" / "index.md"
    md.parent.mkdir(parents=True)
    md.write_text('{{< bieb id="a/b/c" />}}\n', encoding="utf-8")
    flows = pp.parse_page_flows(md.read_text(encoding="utf-8"))
    flows = pp.ensure_catalogus_derived_titles(flows, md)
    assert not any(isinstance(i, pp.TitleItem) for i in flows[0].items)


def test_compose_voorzien_pdf_contains_marker(tmp_path: Path) -> None:
    import pymupdf

    dest = tmp_path / "index.md.pdf"
    pp.compose_voorzien_pdf(dest, title="Prokimen Test (Groningen)")
    doc = pymupdf.open(dest)
    try:
        text = doc[0].get_text()
    finally:
        doc.close()
    assert "Voorzien" in text
    assert "gereserveerd" in text
    assert "Prokimen" in text


def test_prose_notes_from_catalogus_md() -> None:
    text = """---
title: X
---

Dit is alleen van toepassing in een Liturgie waarin ook een Diaken deelneemt.

{{< bieb id="dialoog-met-diaken/default/hemelum" />}}
"""
    assert pp.prose_notes_from_catalogus_md(text) == [
        "Dit is alleen van toepassing in een Liturgie waarin ook een Diaken deelneemt."
    ]


def test_compose_tekstblad_pagina_pdf_trims_and_titles(tmp_path: Path) -> None:
    import pymupdf

    src_path = tmp_path / "x.tekstblad.pdf"
    src = pymupdf.open()
    sp = src.new_page(width=595, height=842)
    sp.insert_text((50, 80), "D: Laat ons de Here bidden", fontsize=12)
    sp.insert_text((50, 120), "P: Want heilig zijt Gij", fontsize=12)
    src.save(src_path)
    src.close()

    dest = tmp_path / "index.md.pdf"
    pp.compose_tekstblad_pagina_pdf_from_body(
        dest,
        title="(7d) Dialoog met Diaken",
        notes=[
            "Dit is alleen van toepassing in een Liturgie waarin ook een Diaken deelneemt."
        ],
        body_pdf=src_path,
    )
    doc = pymupdf.open(dest)
    try:
        assert len(doc) == 1
        text = doc[0].get_text().replace("\xa0", " ")
    finally:
        doc.close()
    assert "(7d) Dialoog met Diaken" in text
    assert "Diaken deelneemt" in text
    assert "Laat ons de Here bidden" in text


def test_build_one_voorzien_without_bieb(tmp_path, monkeypatch) -> None:
    cat = tmp_path / "catalogus"
    leaf = cat / "prokimen" / "x" / "groningen"
    leaf.mkdir(parents=True)
    md = leaf / "index.md"
    md.write_text(
        "---\npublicatiestatus: voorzien\nautomatische_inhoud: false\n---\n\n"
        "Nog geen bron.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(pp, "CATALOGUS", cat)
    monkeypatch.setattr(pp, "ROOT", tmp_path)
    out = pp.build_one(md, force=True)
    assert out is not None
    assert out.name == "index.md.pdf"
    import pymupdf

    assert "Voorzien" in pymupdf.open(out)[0].get_text()


def test_export_blad_svgs_mscz_uses_mscz_cli(tmp_path, monkeypatch) -> None:
    source = tmp_path / "lied.mscz"
    source.write_bytes(b"fake")
    dest = tmp_path / "out.svg"
    calls: list[list[str]] = []

    def fake_call(cmd: list[str], cwd: str | None = None) -> None:
        calls.append(list(cmd))
        dest.write_text("<svg/>", encoding="utf-8")

    monkeypatch.setattr(pp, "_mscz_cli", lambda: ["mscz"])
    monkeypatch.setattr(pp.subprocess, "check_call", fake_call)
    pages = pp.export_blad_svgs(source, dest)
    assert pages == [dest]
    assert calls[0][:2] == ["mscz", "svg"]
    assert str(source) in calls[0]


def test_export_blad_svgs_mvsa_uses_mvsa_cli(tmp_path, monkeypatch) -> None:
    source = tmp_path / "lied.mvsa"
    source.write_text("x", encoding="utf-8")
    dest = tmp_path / "out.svg"
    calls: list[list[str]] = []

    def fake_call(cmd: list[str], cwd: str | None = None) -> None:
        calls.append(list(cmd))
        dest.write_text("<svg/>", encoding="utf-8")

    monkeypatch.setattr(pp, "_mvsa_cli", lambda: ["mvsa"])
    monkeypatch.setattr(pp.subprocess, "check_call", fake_call)
    pp.export_blad_svgs(source, dest, compact=True)
    assert calls[0][:2] == ["mvsa", "svg"]
    assert "--compact" in calls[0]


def test_resolve_svgs_prefers_product(tmp_path: Path) -> None:
    source = tmp_path / "lied.mscz"
    source.write_bytes(b"fake")
    product = tmp_path / "lied.mscz.svg"
    product.write_text("<svg/>", encoding="utf-8")
    work = tmp_path / "work"
    work.mkdir()
    paths = pp.resolve_svgs_for_pdf(source, work, uv_id="a/b")
    assert paths == [product]


def test_resolve_svgs_uses_legacy_bladreeks(tmp_path: Path) -> None:
    source = tmp_path / "lied.mscz"
    source.write_bytes(b"fake")
    p1 = tmp_path / "lied.mscz-1.svg"
    p2 = tmp_path / "lied.mscz-2.svg"
    p1.write_text("<svg>1</svg>", encoding="utf-8")
    p2.write_text("<svg>2</svg>", encoding="utf-8")
    work = tmp_path / "work"
    work.mkdir()
    paths = pp.resolve_svgs_for_pdf(source, work, uv_id="a/b")
    assert paths == [p1, p2]


def test_resolve_svgs_exports_when_missing(tmp_path, monkeypatch) -> None:
    source = tmp_path / "lied.mscz"
    source.write_bytes(b"fake")
    work = tmp_path / "work"
    work.mkdir()
    exported: list[Path] = []

    def fake_export(src: Path, dest: Path, *, compact: bool = False):
        exported.append(dest)
        dest.write_text("<svg/>", encoding="utf-8")
        return [dest]

    monkeypatch.setattr(pp, "export_blad_svgs", fake_export)
    paths = pp.resolve_svgs_for_pdf(source, work, uv_id="x/y")
    assert paths == [tmp_path / "lied.mscz.svg"]
    assert exported == [paths[0]]


def test_system_cut_points_between_staff_clusters(tmp_path: Path) -> None:
    """Snijpunten vallen in de gap tussen systemen, niet midden in een balk."""
    # Twee systemen: staflijnen ~100–140 en ~400–440 (gap > 200)
    svg = tmp_path / "tall.svg"
    svg.write_text(
        """<?xml version="1.0"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="500"
     viewBox="0 0 100 500">
  <polyline class="StaffLines" points="0,100 100,100"/>
  <polyline class="StaffLines" points="0,110 100,110"/>
  <polyline class="StaffLines" points="0,120 100,120"/>
  <polyline class="StaffLines" points="0,130 100,130"/>
  <polyline class="StaffLines" points="0,140 100,140"/>
  <polyline class="StaffLines" points="0,400 100,400"/>
  <polyline class="StaffLines" points="0,410 100,410"/>
  <polyline class="StaffLines" points="0,420 100,420"/>
  <polyline class="StaffLines" points="0,430 100,430"/>
  <polyline class="StaffLines" points="0,440 100,440"/>
</svg>
""",
        encoding="utf-8",
    )
    pdf_h = 500.0
    cuts = pp.system_cut_points_pdf(svg, pdf_h)
    assert cuts[-1] == pdf_h
    assert len(cuts) == 2
    # Middelste snede ≈ (140+400)/2 = 270
    assert 250.0 < cuts[0] < 290.0
    systems = pp._cluster_systems(pp._staff_line_ys(svg.read_text(encoding="utf-8")))
    assert len(systems) == 2


def test_system_cut_points_between_vsa_lines(tmp_path: Path) -> None:
    """Pure .vsa.svg: snede tussen vsa-line-groepen (geen StaffLines)."""
    svg = tmp_path / "vsa.svg"
    svg.write_text(
        """<?xml version="1.0"?>
<svg class="vsa-svg" xmlns="http://www.w3.org/2000/svg" width="100" height="200"
     viewBox="0 0 100 200">
  <g class="vsa-score">
    <g class="vsa-line" data-vsa-line="1">
      <text class="vsa-text" x="10" y="40">regel een</text>
      <line x1="10" y1="45" x2="90" y2="45"/>
    </g>
    <g class="vsa-line" data-vsa-line="2">
      <text class="vsa-text" x="10" y="140">regel twee</text>
      <line x1="10" y1="145" x2="90" y2="145"/>
    </g>
  </g>
</svg>
""",
        encoding="utf-8",
    )
    pdf_h = 200.0
    assert pp._staff_line_ys(svg.read_text(encoding="utf-8")) == []
    systems = pp._vsa_line_systems(svg.read_text(encoding="utf-8"))
    assert len(systems) == 2
    cuts = pp.system_cut_points_pdf(svg, pdf_h)
    assert cuts[-1] == pdf_h
    assert len(cuts) == 2
    # Mid tussen max(regel1)≈45 en min(regel2)≈140 → ≈92.5
    assert 80.0 < cuts[0] < 110.0


def test_system_cut_points_real_hemelum_deel2_vsa() -> None:
    """Catalogus-leaf hemelum-deel-2: tientallen vsa-line-sneden."""
    svg = (
        pp.CATALOGUS
        / "geloofsbelijdenis"
        / "default"
        / "hemelum-deel-2"
        / "geloofsbelijdenis-default-hemelum-deel-2.vsa.svg"
    )
    if not svg.is_file():
        return
    cuts = pp.system_cut_points_pdf(svg, 968.0)
    assert cuts[-1] == 968.0
    assert len(cuts) >= 20
    assert pp._staff_line_ys(svg.read_text(encoding="utf-8")) == []

def test_open_svg_as_pdf_uses_dejavu_not_times(tmp_path: Path) -> None:
    """VSA-SVG-tekst moet DejaVu houden (geen Times-substitutie van MuPDF)."""
    import pymupdf

    font = pp._notation_font_file("DejaVu Sans")
    if font is None:
        import pytest

        pytest.skip("DejaVu Sans TTF niet gevonden (VSA-tooling assets)")

    svg = tmp_path / "sample.vsa.svg"
    svg.write_text(
        """<?xml version="1.0"?>
<svg xmlns="http://www.w3.org/2000/svg" width="200" height="80"
     viewBox="0 0 200 80">
  <text class="vsa-text" x="10.00" y="40.00" xml:space="preserve"
        font-family="DejaVu Sans" font-size="20.00">Laat</text>
  <text class="vsa-text" x="60.00" y="40.00" xml:space="preserve"
        font-family="DejaVu Sans" font-size="20.00">ons</text>
</svg>
""",
        encoding="utf-8",
    )
    doc = pp.open_svg_as_pdf(svg)
    try:
        fonts = " ".join(f[3] for f in doc[0].get_fonts())
        assert "DejaVu" in fonts
        assert "Times" not in fonts
        assert "Nimbus" not in fonts
        spans = []
        for block in doc[0].get_text("dict")["blocks"]:
            if block.get("type") != 0:
                continue
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    if span["text"].strip():
                        spans.append((span["text"], span["font"], span["bbox"][0]))
        assert spans[0][0] == "Laat"
        assert "DejaVu" in spans[0][1] or "dejavu" in spans[0][1].lower()
        assert abs(spans[0][2] - 10.0) < 0.1
        assert abs(spans[1][2] - 60.0) < 0.1
    finally:
        doc.close()
