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
        self.assertEqual(sync.product_mvsa_for_vsa(vsa).name, "lied.vsa.mvsa")


class SyncCallsToolingProductsTests(unittest.TestCase):
    def test_sync_one_svg_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            vsa = root / "lied.vsa"
            vsa.write_text("[:] Amen. [:]\n", encoding="utf-8")
            svg = sync.product_svg_for_vsa(vsa)

            def fake_svg(path: Path) -> None:
                self.assertEqual(path, vsa)
                svg.write_text(
                    '<?xml version="1.0"?>\n<svg xmlns="http://www.w3.org/2000/svg"/>\n',
                    encoding="utf-8",
                )

            with (
                mock.patch.object(sync, "REPO_ROOT", root),
                mock.patch.object(sync, "_run_vsa_svg", side_effect=fake_svg),
                mock.patch.object(sync, "_run_vsa_mvsa") as run_mvsa,
                mock.patch.object(sync, "write_products_meta") as write_meta,
                mock.patch.object(sync, "sync_translit_svgs") as sync_translit,
                mock.patch.object(sync, "_cascade_vsa_mvsa_products") as cascade,
            ):
                sync.sync_one(
                    vsa,
                    dry_run=False,
                    do_svg=True,
                    do_mvsa=False,
                    cascade_mvsa=False,
                )

            run_mvsa.assert_not_called()
            cascade.assert_not_called()
            write_meta.assert_called_once_with(
                vsa, {"svg": svg}, merge=True, drop_keys={"mxl"}
            )
            sync_translit.assert_called_once_with(vsa, dry_run=False, force=True)

    def test_sync_one_mvsa_cascades(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            vsa = root / "lied.vsa"
            vsa.write_text(
                "---\nsoort: tropaar\ntoon: 1\n---\n[:] Amen. [:]\n",
                encoding="utf-8",
            )
            mvsa = sync.product_mvsa_for_vsa(vsa)

            def fake_mvsa(path: Path) -> Path:
                self.assertEqual(path, vsa)
                mvsa.write_text("@title Amen\nS: a\n", encoding="utf-8")
                return mvsa

            with (
                mock.patch.object(sync, "REPO_ROOT", root),
                mock.patch.object(sync, "_run_vsa_svg") as run_svg,
                mock.patch.object(sync, "_run_vsa_mvsa", side_effect=fake_mvsa),
                mock.patch.object(sync, "write_products_meta") as write_meta,
                mock.patch.object(sync, "sync_translit_svgs"),
                mock.patch.object(sync, "_cascade_vsa_mvsa_products") as cascade,
            ):
                sync.sync_one(
                    vsa,
                    dry_run=False,
                    do_svg=False,
                    do_mvsa=True,
                    cascade_mvsa=True,
                )

            run_svg.assert_not_called()
            write_meta.assert_called_once_with(
                vsa, {"mvsa": mvsa}, merge=True, drop_keys={"mxl"}
            )
            cascade.assert_called_once_with(mvsa, dry_run=False, force=True)


class ClassifyTemplateTests(unittest.TestCase):
    def test_soft_skip_without_soort_toon(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            vsa = Path(tmp) / "los.vsa"
            vsa.write_text("[:] Amen. [:]\n", encoding="utf-8")
            decision, tpl = sync.classify_vsa_mvsa_template(vsa)
            self.assertEqual(decision, "soft_skip")
            self.assertIsNone(tpl)

    def test_hard_error_on_unknown_formule(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            vsa = Path(tmp) / "los.vsa"
            vsa.write_text(
                "---\nsoort: tropaar\ntoon: 1\nformule: bestaat-niet-xyz\n---\n"
                "[:] Amen. [:]\n",
                encoding="utf-8",
            )
            with self.assertRaises(Exception):
                sync.classify_vsa_mvsa_template(vsa)


class StampOkTests(unittest.TestCase):
    def test_stale_without_products(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            vsa = Path(tmp) / "x.vsa"
            vsa.write_text("[:] Amen. [:]\n", encoding="utf-8")
            need_mvsa, need_svg = sync.is_stale_pair(vsa)
            # Geen soort/toon → soft skip → geen mvsa-behoefte.
            self.assertFalse(need_mvsa)
            self.assertTrue(need_svg)

    def test_ok_with_svg_stamp(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            vsa = Path(tmp) / "x.vsa"
            vsa.write_text("[:] Amen. [:]\n", encoding="utf-8")
            with mock.patch.object(sync, "_stamp_ok_svg", return_value=True):
                need_mvsa, need_svg = sync.is_stale_pair(vsa)
            self.assertFalse(need_mvsa)
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
