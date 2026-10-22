"""Tests voor vsa-products collect/stamp (zonder Chrome/renderer-heavy pad)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

import product_meta as pm
import sync_vsa_products as sync


class ProductNameTests(unittest.TestCase):
    def test_product_names(self) -> None:
        vsa = Path("a/b/lied.vsa")
        self.assertEqual(sync.product_path_for_vsa(vsa).name, "lied.vsa.mxl")
        self.assertEqual(sync.product_pdf_for_vsa(vsa).name, "lied.vsa.pdf")
        self.assertEqual(sync.product_svg_for_vsa(vsa).name, "lied.vsa.svg")


class StampOkTests(unittest.TestCase):
    def test_stale_without_products(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            vsa = Path(tmp) / "x.vsa"
            vsa.write_text("[:] Amen. [:]\n", encoding="utf-8")
            need_mxl, need_pdf, need_svg = sync.is_stale_pair(vsa)
            self.assertTrue(need_mxl)
            self.assertTrue(need_pdf)
            self.assertTrue(need_svg)

    def test_ok_with_stamps(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            vsa = Path(tmp) / "x.vsa"
            vsa.write_text("[:] Amen. [:]\n", encoding="utf-8")
            with mock.patch.object(sync, "_stamp_ok_mxl", return_value=True), mock.patch.object(
                sync, "_stamp_ok_pdf", return_value=True
            ), mock.patch.object(sync, "_stamp_ok_svg", return_value=True):
                need_mxl, need_pdf, need_svg = sync.is_stale_pair(vsa)
            self.assertFalse(need_mxl)
            self.assertFalse(need_pdf)
            self.assertFalse(need_svg)

    def test_svg_stamp_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            svg = Path(tmp) / "x.vsa.svg"
            svg.write_text(
                '<?xml version="1.0"?>\n<svg xmlns="http://www.w3.org/2000/svg"/>\n',
                encoding="utf-8",
            )
            pm.stamp_svg(
                svg,
                source_hash="abc123",
                source_kind=pm.SOURCE_KIND_VSA,
                generated_at="2026-01-01T00:00:00+00:00",
                generator=pm.GENERATOR_VSA_PDF,
            )
            stamp = pm.read_svg_stamp(svg)
            self.assertEqual(stamp.get(pm.FIELD_SOURCE_SHA), "abc123")
            self.assertEqual(stamp.get(pm.FIELD_SOURCE_KIND), pm.SOURCE_KIND_VSA)
            self.assertTrue(sync._stamp_ok_svg(svg, "abc123"))
            self.assertFalse(sync._stamp_ok_svg(svg, "other"))


if __name__ == "__main__":
    unittest.main()
