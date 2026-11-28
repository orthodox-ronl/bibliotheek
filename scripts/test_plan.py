"""Tests voor plan.py: graafcontroles (volgorde, diepte, ketens) en samenvatting."""

from __future__ import annotations

import plan as pl


def _p(kind, bron, pad, *, bestaat=True, stempel=True, lokaal=False):
    return pl.Product(kind, bron, pad, bestaat, stempel, None, lokaal)


VOLGORDE = ("vsa", "mvsa", "audio")


def test_afgeleide_bron_in_goede_volgorde_geeft_geen_probleem():
    plan = pl.Plan(producten=[_p("vsa", "a.vsa", "a.vsa.mvsa")])
    pl._controleer_graaf(plan, {"a.vsa": "vsa", "a.vsa.mvsa": "mvsa"}, VOLGORDE)
    assert plan.problemen == []
    assert plan.randen == [("a.vsa", "vsa", "a.vsa.mvsa", "mvsa")]


def test_afgeleide_bron_te_vroeg_is_volgordefout():
    plan = pl.Plan(producten=[_p("mvsa", "a.mvsa", "a.mvsa.vsa")])
    pl._controleer_graaf(plan, {"a.mvsa": "mvsa", "a.mvsa.vsa": "vsa"}, VOLGORDE)
    assert any(p.startswith("volgorde:") for p in plan.problemen)


def test_keten_vsa_mvsa_vsa_wordt_gemeld():
    plan = pl.Plan()
    pl._controleer_graaf(plan, {"a.vsa.mvsa.vsa": "vsa"}, VOLGORDE)
    assert any(p.startswith("keten:") for p in plan.problemen)


def test_diepte_twee_wordt_gemeld():
    plan = pl.Plan(
        producten=[
            _p("vsa", "a.vsa", "a.vsa.mvsa"),
            _p("mvsa", "a.vsa.mvsa", "a.vsa.mvsa.x"),
        ]
    )
    pl._controleer_graaf(
        plan,
        {"a.vsa": "vsa", "a.vsa.mvsa": "mvsa", "a.vsa.mvsa.x": "audio"},
        VOLGORDE,
    )
    assert any(p.startswith("diepte:") for p in plan.problemen)


def test_samenvatting_telt_te_maken_en_lokaal():
    plan = pl.Plan(
        producten=[
            _p("vsa", "a.vsa", "a.vsa.svg"),
            _p("vsa", "a.vsa", "a.vsa.mp3", bestaat=False, lokaal=True),
        ],
        bronnen={"vsa": ["a.vsa"]},
    )
    tekst = "\n".join(pl.samenvatting(plan))
    assert "1 te maken (1 alleen lokaal" in tekst
    assert "Graaf in orde" in tekst


def test_sluit_af_markeert_afgeleiden_van_een_vernieuwde_bron():
    plan = pl.Plan(
        producten=[
            _p("vsa", "a.vsa", "a.vsa.mvsa", stempel=False),  # te maken
            _p("mvsa", "a.vsa.mvsa", "a.vsa.mvsa.svg"),  # nu ok, straks niet
            _p("audio", "a.vsa.mvsa", "a.vsa.mvsa.mp3"),
            _p("vsa", "b.vsa", "b.vsa.svg"),  # onaangeroerd
        ]
    )
    pl.sluit_af(plan)
    assert [p.reden for p in plan.producten] == ["verouderd", "gevolg", "gevolg", "ok"]
    assert plan.producten[1].te_maken


def test_pdf_wordt_gevolg_als_een_afhankelijkheid_vernieuwd_wordt(tmp_path):
    svg = tmp_path / "a.vsa.svg"
    svg.write_text("x")
    pdf = tmp_path / "index.md.pdf"
    pdf.write_text("p")
    import os

    os.utime(svg, (1, 1))
    os.utime(pdf, (2, 2))  # pdf nieuwer dan svg: nu in orde

    class Job:
        out_path = pdf
        variants = []
        deps = [svg]

    plan = pl.Plan(producten=[pl.Product("vsa", "a.vsa", "a.vsa.svg", True, False, None, False)])
    pl.beoordeel_pdfs(plan, [Job()], tmp_path)
    assert [(x.reden, x.via) for x in plan.pdfs] == [("gevolg", "a.vsa.svg")]


def test_pdf_ontbreekt_en_verouderd(tmp_path):
    import os

    dep = tmp_path / "index.md"
    dep.write_text("m")
    pdf = tmp_path / "index.md.pdf"
    pdf.write_text("p")
    os.utime(pdf, (1, 1))
    os.utime(dep, (5, 5))

    class Job:
        out_path = pdf
        variants = [tmp_path / "index.md.weergave-p.pdf"]
        deps = [dep]

    plan = pl.Plan()
    pl.beoordeel_pdfs(plan, [Job()], tmp_path)
    assert [x.reden for x in plan.pdfs] == ["verouderd", "ontbreekt"]
