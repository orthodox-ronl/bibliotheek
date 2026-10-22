"""Unit tests voor pagina_pdf parsing (geen MuseScore)."""

from __future__ import annotations

from pathlib import Path

import pagina_pdf as pp


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
        items=[pp.TitleItem("Малая ектения", prominent=True)]
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
