"""Tests voor cleanup_chained_products."""

from __future__ import annotations

from pathlib import Path

import cleanup_chained_products as ccp


def test_is_chained_keeps_single_products() -> None:
    assert not ccp.is_chained_product_name("lied.mvsa.mscz")
    assert not ccp.is_chained_product_name("lied.mvsa.mp3")
    assert not ccp.is_chained_product_name("lied.vsa.svg")
    assert not ccp.is_chained_product_name("lied.mscz.mvsa")
    assert not ccp.is_chained_product_name("lied.mscz.mp3")
    assert not ccp.is_chained_product_name("lied.mscz-1.svg")
    assert not ccp.is_chained_product_name("lied.mvsa.score-ir.json")
    assert not ccp.is_chained_product_name("lied.mvsa.from-ir.musicxml")
    assert not ccp.is_chained_product_name("index.md.pdf")


def test_is_chained_detects_product_of_product() -> None:
    assert ccp.is_chained_product_name("lied.mvsa.mscz.mp3")
    assert ccp.is_chained_product_name("lied.mvsa.mscz.mscz")
    assert ccp.is_chained_product_name("lied.mvsa.mscz.mscz.mp3")
    assert ccp.is_chained_product_name("lied.vsa.mscz.lyrics.txt")
    assert ccp.is_chained_product_name(
        "lied.vsa.mscz.mscz.products-meta.json"
    )
    assert ccp.is_chained_product_name("lied.mscz.mvsa.mp3")
    assert ccp.is_chained_product_name("lied.mscz.mvsa.lyrics.txt")
    assert ccp.is_chained_product_name("lied.mscz.mscz")
    assert ccp.is_chained_product_name("lied.mscz.mscz.mp3")
    assert ccp.is_chained_product_name("lied.mscz.mscz-1.svg")
    assert ccp.is_chained_product_name("lied.mscz.score-ir.json")
    assert ccp.is_chained_product_name("lied.mscz.from-ir.musicxml")
    assert ccp.is_chained_product_name("lied.vsa.score-ir.json")
    assert ccp.is_chained_product_name("lied.vsa.from-ir.musicxml")


def test_find_and_apply(tmp_path: Path) -> None:
    leaf = tmp_path / "zang" / "var" / "uv"
    leaf.mkdir(parents=True)
    keep = leaf / "demo.mvsa.mscz"
    keep.write_bytes(b"keep")
    (leaf / "demo.mvsa.mp3").write_bytes(b"ok")
    (leaf / "demo.mscz").write_bytes(b"src")
    (leaf / "demo.mscz-1.svg").write_bytes(b"svg")
    (leaf / "demo.mvsa.score-ir.json").write_text("{}", encoding="utf-8")
    junk = leaf / "demo.mvsa.mscz.mp3"
    junk.write_bytes(b"junk")
    junk2 = leaf / "demo.mscz.mscz.mp3"
    junk2.write_bytes(b"junk2")
    junk3 = leaf / "demo.mscz.score-ir.json"
    junk3.write_text("{}", encoding="utf-8")

    found = ccp.find_chained_products(tmp_path)
    assert {p.name for p in found} == {
        "demo.mvsa.mscz.mp3",
        "demo.mscz.mscz.mp3",
        "demo.mscz.score-ir.json",
    }

    assert ccp.main([str(tmp_path), "--apply"]) == 0
    assert keep.is_file()
    assert (leaf / "demo.mvsa.mp3").is_file()
    assert (leaf / "demo.mscz-1.svg").is_file()
    assert (leaf / "demo.mvsa.score-ir.json").is_file()
    assert not junk.exists()
    assert not junk2.exists()
    assert not junk3.exists()
