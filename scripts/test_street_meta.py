"""Tests voor street_meta (schrijven/lezen products-meta)."""

from __future__ import annotations

from pathlib import Path

import street_meta as sm


def test_write_and_freshness_ok(tmp_path: Path) -> None:
    bron = tmp_path / "lied.vsa"
    bron.write_text("L: a\n", encoding="utf-8")
    mxl = tmp_path / "lied.vsa.mxl"
    svg = tmp_path / "lied.vsa.svg"
    mxl.write_bytes(b"mxl")
    svg.write_text("<svg/>", encoding="utf-8")
    dest = sm.write_products_meta(bron, {"mxl": mxl, "svg": svg})
    assert dest is not None
    assert dest.name == "lied.vsa.products-meta.json"
    assert sm.meta_ok(bron, required_keys={"mxl", "svg"})


def test_stamp_ok_or_meta_falls_back(tmp_path: Path) -> None:
    bron = tmp_path / "x.vsa"
    bron.write_text("x", encoding="utf-8")
    assert sm.stamp_ok_or_meta(
        bron, required_keys={"mxl"}, stamp_ok=True
    )
    assert not sm.stamp_ok_or_meta(
        bron, required_keys={"mxl"}, stamp_ok=False
    )


def test_assign_svg_keys_multipage(tmp_path: Path) -> None:
    products: dict[str, Path] = {}
    a = tmp_path / "a-1.svg"
    b = tmp_path / "a-2.svg"
    sm.assign_svg_keys(products, [a, b])
    assert products == {"svg-1": a, "svg-2": b}
