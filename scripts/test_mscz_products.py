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
    def test_sync_one_mxl_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mscz = root / "lied.mscz"
            mscz.write_bytes(b"PK\x03\x04fake-mscz")
            mxl = sync.product_mxl_for_mscz(mscz)

            def fake_mxl(path: Path) -> None:
                self.assertEqual(path, mscz)
                mxl.write_bytes(b"PK\x03\x04fake-mxl")

            with (
                mock.patch.object(sync, "REPO_ROOT", root),
                mock.patch.object(sync, "_run_mscz_mxl", side_effect=fake_mxl),
                mock.patch.object(sync, "_run_mscz_svg") as run_svg,
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

            write_meta.assert_called_once_with(mscz, {"mxl": mxl}, merge=True)
            run_svg.assert_not_called()

    def test_sync_one_svg_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mscz = root / "lied.mscz"
            mscz.write_bytes(b"PK\x03\x04fake-mscz")
            svg = sync.product_svg_for_mscz(mscz)

            def fake_svg(path: Path) -> None:
                self.assertEqual(path, mscz)
                svg.write_text(
                    '<?xml version="1.0"?>\n<svg xmlns="http://www.w3.org/2000/svg"/>\n',
                    encoding="utf-8",
                )

            with (
                mock.patch.object(sync, "REPO_ROOT", root),
                mock.patch.object(sync, "_run_mscz_mxl") as run_mxl,
                mock.patch.object(sync, "_run_mscz_svg", side_effect=fake_svg),
                mock.patch.object(sync, "write_products_meta") as write_meta,
            ):
                sync.sync_one(
                    mscz,
                    need_pdf=False,
                    need_mxl=False,
                    need_svg=True,
                    dry_run=False,
                )

            run_mxl.assert_not_called()
            write_meta.assert_called_once_with(mscz, {"svg": svg}, merge=True)

    def test_sync_one_mxl_and_svg(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mscz = root / "lied.mscz"
            mscz.write_bytes(b"PK\x03\x04fake-mscz")
            mxl = sync.product_mxl_for_mscz(mscz)
            svg = sync.product_svg_for_mscz(mscz)
            calls: list[str] = []

            def fake_mxl(path: Path) -> None:
                calls.append("mxl")
                mxl.write_bytes(b"PK")

            def fake_svg(path: Path) -> None:
                calls.append("svg")
                svg.write_text(
                    '<?xml version="1.0"?>\n<svg xmlns="http://www.w3.org/2000/svg"/>\n',
                    encoding="utf-8",
                )

            with (
                mock.patch.object(sync, "REPO_ROOT", root),
                mock.patch.object(sync, "_run_mscz_mxl", side_effect=fake_mxl),
                mock.patch.object(sync, "_run_mscz_svg", side_effect=fake_svg),
                mock.patch.object(sync, "_apply_bron_identification"),
                mock.patch.object(sync, "write_products_meta") as write_meta,
            ):
                sync.sync_one(
                    mscz,
                    need_pdf=False,
                    need_mxl=True,
                    need_svg=True,
                    dry_run=False,
                )

            self.assertEqual(calls, ["mxl", "svg"])
            write_meta.assert_called_once_with(
                mscz, {"mxl": mxl, "svg": svg}, merge=True
            )


if __name__ == "__main__":
    unittest.main()
