"""Weergave-keuze op blad-PDF's (geen MuseScore nodig)."""

from __future__ import annotations

from pathlib import Path

import pytest

import check_index_md_pdf as check
import index_md_pdf as pp
import weergave


def _leaf(root: Path, *, soorten=("vsa", "mvsa"), front: str = "") -> Path:
    root.mkdir(parents=True)
    (root / "index.md").write_text(f"---\ntitle: t\n{front}---\n", encoding="utf-8")
    for ext in soorten:
        (root / f"x.{ext}").write_text("bron", encoding="utf-8")
        (root / f"x.{ext}.svg").write_text("<svg/>", encoding="utf-8")
    return root


def test_soort_van_svg() -> None:
    assert weergave.soort_van_svg("a.vsa.svg") == "vsa"
    assert weergave.soort_van_svg("a.mvsa.vsa.svg") == "vsa"
    assert weergave.soort_van_svg("a.vsa.mvsa.svg") == "partituur"
    assert weergave.soort_van_svg("a.print.mscz.svg") == "partituur"
    assert weergave.soort_van_svg("a.vsa.translit-ksl.svg") is None


def test_volgorde_van_voorrang(tmp_path: Path) -> None:
    leaf = _leaf(tmp_path / "uv", front="weergave: partituur\n")
    assert weergave.wisselbaar(leaf, None).standaard == "partituur"
    assert weergave.wisselbaar(leaf, "vsa").standaard == "vsa"
    plain = _leaf(tmp_path / "uv2")
    assert weergave.wisselbaar(plain, None).standaard == "vsa"
    assert weergave.wisselbaar(_leaf(tmp_path / "een", soorten=("vsa",)), None) is None


def test_onbekende_waarde(tmp_path: Path) -> None:
    leaf = _leaf(tmp_path / "uv", front="weergave: noten\n")
    with pytest.raises(ValueError, match="kies vsa of partituur"):
        weergave.blad_weergave(leaf)


def test_parse_weergave_en_blokovererving() -> None:
    md = (
        '{{< bieb id="a/b/c" weergave="partituur" >}}\n'
        "{{< muziek >}}\n"
        '{{< muziek weergave="vsa" >}}\n'
        "{{< /bieb >}}\n"
        '{{< bieb id="d/e/f" >}}\n{{< muziek >}}\n{{< /bieb >}}\n'
    )
    items = [
        i
        for f in pp.parse_page_flows(md)
        for i in f.items
        if isinstance(i, pp.MusicItem)
    ]
    assert [i.weergave for i in items] == ["partituur", "vsa", None]


def test_combinaties_en_grens(tmp_path: Path) -> None:
    stuk = weergave.wisselbaar(_leaf(tmp_path / "uv"), None)
    assert weergave.andere_combinaties([]) == []
    assert len(weergave.andere_combinaties([stuk] * 2)) == 3
    assert len(weergave.andere_combinaties([stuk] * 4)) == 15
    assert weergave.andere_combinaties([stuk] * 5) == []


def test_check_meldt_ontbrekende_variant_en_grens(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(check, "_rel", lambda p: p.name)
    monkeypatch.setattr(check, "_bladermap_key", lambda p: p.parent.name)
    md = tmp_path / "index.md"
    md.write_text("x", encoding="utf-8")
    out = tmp_path / "index.md.pdf"
    out.write_text("x", encoding="utf-8")
    variant = weergave.variant_pad(md, ["partituur"])
    assert variant.name == "index.md.weergave-p.pdf"
    job = pp.PaginaPdfJob(md, out, (md,), (variant,), 1)
    assert [i.kind for i in check.check_job(job).issues] == ["missing_pdf"]
    variant.write_text("x", encoding="utf-8")
    assert check.check_job(job).ok
    teveel = pp.PaginaPdfJob(md, out, (md,), (), 5)
    assert [i.kind for i in check.check_job(teveel).issues] == ["grens_weergave"]
