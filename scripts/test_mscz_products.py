"""Tests voor mscz-products collect/sync (zonder MuseScore)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

import sync_mscz_products as sync


class ProductNameTests(unittest.TestCase):
    def test_product_names(self) -> None:
        mscz = Path("a/b/lied.mscz")
        self.assertEqual(sync.product_mxl_for_mscz(mscz).name, "lied.mscz.mxl")
        self.assertEqual(sync.product_pdf_for_mscz(mscz).name, "lied.mscz.pdf")
        self.assertEqual(sync.product_svg_for_mscz(mscz).name, "lied.mscz.svg")


class SyncCallsToolingProductsTests(unittest.TestCase):
    def test_sync_one_calls_mscz_products_skip_svg(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mscz = root / "lied.mscz"
            mscz.write_bytes(b"PK\x03\x04fake-mscz")
            mxl = sync.product_mxl_for_mscz(mscz)

            def fake_products(path: Path, *, skip_svg: bool) -> None:
                self.assertEqual(path, mscz)
                self.assertTrue(skip_svg)
                mxl.write_bytes(b"PK\x03\x04fake-mxl")

            with (
                mock.patch.object(sync, "REPO_ROOT", root),
                mock.patch.object(sync, "_run_mscz_products", side_effect=fake_products),
                mock.patch.object(sync, "_apply_bron_identification"),
                mock.patch.object(sync, "write_products_meta") as write_meta,
            ):
                sync.sync_one(
                    mscz,
                    need_pdf=False,
                    need_mxl=True,
                    need_svg=False,
                    dry_run=False,
                )

            write_meta.assert_called_once()

    def test_sync_one_requests_svg_when_needed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mscz = root / "lied.mscz"
            mscz.write_bytes(b"PK\x03\x04fake-mscz")
            calls: list[bool] = []

            def fake_products(path: Path, *, skip_svg: bool) -> None:
                calls.append(skip_svg)
                sync.product_mxl_for_mscz(mscz).write_bytes(b"PK")
                sync.product_svg_for_mscz(mscz).write_text(
                    '<?xml version="1.0"?>\n<svg xmlns="http://www.w3.org/2000/svg"/>\n',
                    encoding="utf-8",
                )

            with (
                mock.patch.object(sync, "REPO_ROOT", root),
                mock.patch.object(sync, "_run_mscz_products", side_effect=fake_products),
                mock.patch.object(sync, "_apply_bron_identification"),
                mock.patch.object(sync, "write_products_meta"),
            ):
                sync.sync_one(
                    mscz,
                    need_pdf=False,
                    need_mxl=True,
                    need_svg=True,
                    dry_run=False,
                )

            self.assertEqual(calls, [False])


if __name__ == "__main__":
    unittest.main()
