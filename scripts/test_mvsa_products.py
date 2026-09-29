"""Tests voor mvsa-products collect/stamp (zonder MuseScore)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

import product_meta as pm
import sync_mvsa_products as sync


class CollectTests(unittest.TestCase):
    def test_skips_import_sibling(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            canon = root / "lied.mvsa"
            imp = root / "lied.mscz.mvsa"
            canon.write_text("L: a\n", encoding="utf-8")
            imp.write_text("L: a\n", encoding="utf-8")
            found = sync.collect_mvsa(root)
            self.assertEqual(found, [canon])

    def test_product_names(self) -> None:
        mvsa = Path("a/b/lied.mvsa")
        self.assertEqual(sync.product_mxl_for_mvsa(mvsa).name, "lied.mvsa.mxl")
        self.assertEqual(sync.product_pdf_for_mvsa(mvsa).name, "lied.mvsa.pdf")


class StampOkTests(unittest.TestCase):
    def test_stale_without_products(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            mvsa = Path(tmp) / "x.mvsa"
            mvsa.write_text("L: a\n", encoding="utf-8")
            need_mxl, need_pdf = sync.is_stale(mvsa)
            self.assertTrue(need_mxl)
            self.assertTrue(need_pdf)

    def test_ok_with_stamps(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            mvsa = Path(tmp) / "x.mvsa"
            mvsa.write_text("L: a\n", encoding="utf-8")
            digest = pm.source_sha256(mvsa)
            pdf = sync.product_pdf_for_mvsa(mvsa)
            # Minimal fake PDF stamp via mocking read helpers
            with mock.patch.object(sync, "_stamp_ok_mxl", return_value=True), mock.patch.object(
                sync, "_stamp_ok_pdf", return_value=True
            ):
                need_mxl, need_pdf = sync.is_stale(mvsa)
            self.assertFalse(need_mxl)
            self.assertFalse(need_pdf)
            self.assertTrue(digest)


if __name__ == "__main__":
    unittest.main()
