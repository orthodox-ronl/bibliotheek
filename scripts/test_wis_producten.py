"""Tests voor wis-producten (regenereerbare producten wissen, bronnen sparen)."""

from __future__ import annotations

from pathlib import Path

import wis_producten as wp


def _touch(path: Path, text: str = "x") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_generated_names() -> None:
    for name in (
        "lied.vsa.svg",
        "lied.vsa.mp3",
        "lied.vsa.mscz",
        "lied.vsa.mvsa",
        "lied.mvsa.mxl",
        "lied.vsa.products-meta.json",
        "lied.vsa.lyrics.txt",
        "lied.mscz.svg",
        "lied.vsa.translit-ksl.svg",
        "index.md.pdf",
        "index.md.translit-ksl.pdf",
    ):
        assert wp.is_generated_name(name), name


def test_sources_are_never_generated() -> None:
    for name in (
        "lied.vsa",
        "lied.mvsa",
        "lied.mscz",
        "lied.print.mscz",
        "lied.mscz.mvsa",
        "lied.tekstblad.md",
        "index.md",
        "_index.md",
        "template.svg",
        "lied.mxl",
    ):
        assert not wp.is_generated_name(name), name


def test_find_generated_spares_sources_formules_and_handmatig(tmp_path: Path) -> None:
    cat = tmp_path / "catalogus"
    normaal = cat / "kondak" / "toon-2" / "hemelum"
    _touch(normaal / "kondak-toon-2-hemelum.vsa")
    _touch(normaal / "kondak-toon-2-hemelum.vsa.svg")
    _touch(normaal / "kondak-toon-2-hemelum.vsa.products-meta.json")
    _touch(normaal / "index.md")
    _touch(normaal / "index.md.pdf")

    formules = cat / "formules" / "stichier-toon-1"
    _touch(formules / "template.svg")
    _touch(formules / "iets.vsa.svg")

    manueel = cat / "moeder-godslied" / "ontslapen" / "hemelum"
    _touch(manueel / "index.md", "---\nmanueel: true\n---\n")
    _touch(manueel / "lied.vsa")
    _touch(manueel / "lied.vsa.svg")

    tekstblad = cat / "dialoog-met-diaken" / "default" / "hemelum"
    _touch(tekstblad / "dialoog.tekstblad.md")
    _touch(tekstblad / "dialoog.tekstblad.scherm.html")
    _touch(tekstblad / "index.md.pdf")

    files, protected = wp.find_generated(cat)
    names = sorted(p.name for p in files)
    assert names == [
        "index.md.pdf",
        "kondak-toon-2-hemelum.vsa.products-meta.json",
        "kondak-toon-2-hemelum.vsa.svg",
    ]
    assert {p.name for p in protected} == {"stichier-toon-1", "hemelum"}
    assert len(protected) == 3


def test_main_dry_run_and_apply(tmp_path: Path, capsys) -> None:
    folder = tmp_path / "catalogus" / "a" / "b" / "c"
    bron = _touch(folder / "a-b-c.vsa")
    prod = _touch(folder / "a-b-c.vsa.svg")

    assert wp.main([str(folder)]) == 0
    assert prod.exists()
    assert "dry-run" in capsys.readouterr().out

    assert wp.main([str(folder), "--apply"]) == 0
    assert not prod.exists()
    assert bron.exists()


def test_main_rejects_both_flags(tmp_path: Path) -> None:
    assert wp.main([str(tmp_path), "--apply", "--dry-run"]) == 1
