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
        self.assertEqual(sync.product_svg_for_mvsa(mvsa).name, "lied.mvsa.svg")
        self.assertEqual(
            sync.product_score_ir_for_mvsa(mvsa).name, "lied.mvsa.score-ir.json"
        )
        self.assertEqual(
            sync.product_from_ir_musicxml_for_mvsa(mvsa).name,
            "lied.mvsa.from-ir.musicxml",
        )


class SyncCallsToolingProductsTests(unittest.TestCase):
    def test_sync_one_calls_mvsa_products_skip_svg(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mvsa = root / "lied.mvsa"
            mvsa.write_text("L: a\nS: a\nA: a\nT: a\nB: a\n", encoding="utf-8")
            mxl = sync.product_mxl_for_mvsa(mvsa)
            score_ir = sync.product_score_ir_for_mvsa(mvsa)
            from_ir = sync.product_from_ir_musicxml_for_mvsa(mvsa)

            def fake_products(path: Path, *, skip_svg: bool) -> None:
                self.assertEqual(path, mvsa)
                self.assertTrue(skip_svg)
                mxl.write_bytes(b"PK\x03\x04fake")
                score_ir.write_text('{"format":"score-ir"}\n', encoding="utf-8")
                from_ir.write_text(
                    '<?xml version="1.0"?>\n<score-partwise/>\n',
                    encoding="utf-8",
                )

            with (
                mock.patch.object(sync, "REPO_ROOT", root),
                mock.patch.object(sync, "_run_mvsa_products", side_effect=fake_products),
                mock.patch.object(sync, "write_products_meta") as write_meta,
            ):
                sync.sync_one(
                    mvsa,
                    need_mxl=True,
                    need_pdf=False,
                    need_svg=False,
                    need_score_ir=True,
                    need_from_ir=True,
                    dry_run=False,
                )

            write_meta.assert_called_once()

    def test_mvsa_svg_outputs_bladreeks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            mvsa = Path(tmp) / "lied.mvsa"
            mvsa.write_text("L: a\n", encoding="utf-8")
            p1 = Path(tmp) / "lied.mvsa-1.svg"
            p2 = Path(tmp) / "lied.mvsa-2.svg"
            p1.write_text("<svg/>\n", encoding="utf-8")
            p2.write_text("<svg/>\n", encoding="utf-8")
            self.assertEqual(sync.mvsa_svg_outputs(mvsa), [p1, p2])

    def test_sync_one_requests_svg_when_needed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mvsa = root / "lied.mvsa"
            mvsa.write_text("L: a\n", encoding="utf-8")
            calls: list[bool] = []

            def fake_products(path: Path, *, skip_svg: bool) -> None:
                calls.append(skip_svg)
                sync.product_mxl_for_mvsa(mvsa).write_bytes(b"PK")
                sync.product_score_ir_for_mvsa(mvsa).write_text("{}\n", encoding="utf-8")
                sync.product_from_ir_musicxml_for_mvsa(mvsa).write_text(
                    "<score/>\n", encoding="utf-8"
                )
                sync.product_svg_for_mvsa(mvsa).write_text(
                    '<?xml version="1.0"?>\n<svg xmlns="http://www.w3.org/2000/svg"/>\n',
                    encoding="utf-8",
                )

            with (
                mock.patch.object(sync, "REPO_ROOT", root),
                mock.patch.object(sync, "_run_mvsa_products", side_effect=fake_products),
                mock.patch.object(sync, "write_products_meta"),
            ):
                sync.sync_one(
                    mvsa,
                    need_mxl=True,
                    need_pdf=False,
                    need_svg=True,
                    need_score_ir=False,
                    need_from_ir=False,
                    dry_run=False,
                )

            self.assertEqual(calls, [False])


class StampOkTests(unittest.TestCase):
    def test_stale_without_products(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            mvsa = Path(tmp) / "x.mvsa"
            mvsa.write_text("L: a\n", encoding="utf-8")
            need_mxl, need_svg, need_ir, need_from = sync.is_stale(mvsa)
            self.assertTrue(need_mxl)
            self.assertTrue(need_svg)
            self.assertTrue(need_ir)
            self.assertTrue(need_from)

    def test_ok_with_stamps(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            mvsa = Path(tmp) / "x.mvsa"
            mvsa.write_text("L: a\n", encoding="utf-8")
            digest = pm.source_sha256(mvsa)
            with mock.patch.object(sync, "_stamp_ok_mxl", return_value=True), mock.patch.object(
                sync, "_stamp_ok_svg", return_value=True
            ), mock.patch.object(sync, "_stamp_ok_score_ir", return_value=True), mock.patch.object(
                sync, "_stamp_ok_from_ir", return_value=True
            ):
                need_mxl, need_svg, need_ir, need_from = sync.is_stale(mvsa)
            self.assertFalse(need_mxl)
            self.assertFalse(need_svg)
            self.assertFalse(need_ir)
            self.assertFalse(need_from)
            self.assertTrue(digest)

    def test_svg_stamp_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            svg = Path(tmp) / "x.mvsa.svg"
            svg.write_text(
                '<?xml version="1.0"?>\n<svg xmlns="http://www.w3.org/2000/svg"/>\n',
                encoding="utf-8",
            )
            pm.stamp_svg(
                svg,
                source_hash="abc123",
                source_kind=pm.SOURCE_KIND_MVSA,
                generated_at="2026-01-01T00:00:00+00:00",
                generator=pm.GENERATOR_MVSA,
            )
            stamp = pm.read_svg_stamp(svg)
            self.assertEqual(stamp.get(pm.FIELD_SOURCE_SHA), "abc123")
            self.assertEqual(stamp.get(pm.FIELD_SOURCE_KIND), pm.SOURCE_KIND_MVSA)
            self.assertTrue(sync._stamp_ok_svg(svg, "abc123"))
            self.assertFalse(sync._stamp_ok_svg(svg, "other"))

    def test_svg_not_needed_when_from_ir_ok(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            mvsa = Path(tmp) / "x.mvsa"
            mvsa.write_text("L: a\n", encoding="utf-8")
            digest = pm.source_sha256(mvsa)
            from_ir = sync.product_from_ir_musicxml_for_mvsa(mvsa)
            from_ir.write_text(
                '<?xml version="1.0"?>\n<score-partwise/>\n',
                encoding="utf-8",
            )
            pm.stamp_from_ir_musicxml(
                from_ir,
                source_hash=digest,
                source_kind=pm.SOURCE_KIND_MVSA,
                generated_at="2026-01-01T00:00:00+00:00",
                generator=pm.GENERATOR_MVSA,
            )
            with mock.patch.object(sync, "_stamp_ok_mxl", return_value=True), mock.patch.object(
                sync, "_stamp_ok_score_ir", return_value=True
            ):
                _need_mxl, need_svg, _need_ir, need_from = sync.is_stale(mvsa)
            self.assertFalse(need_svg)
            self.assertFalse(need_from)

    def test_score_ir_and_from_ir_stamp_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ir = Path(tmp) / "x.mvsa.score-ir.json"
            ir.write_text(
                '{"format": "score-ir", "version": "0.1", "meta": {}}\n',
                encoding="utf-8",
            )
            mxl = Path(tmp) / "x.mvsa.from-ir.musicxml"
            mxl.write_text(
                '<?xml version="1.0"?>\n<score-partwise/>\n',
                encoding="utf-8",
            )
            pm.stamp_score_ir_json(
                ir,
                source_hash="abc123",
                source_kind=pm.SOURCE_KIND_MVSA,
                generated_at="2026-01-01T00:00:00+00:00",
                generator=pm.GENERATOR_MVSA,
            )
            pm.stamp_from_ir_musicxml(
                mxl,
                source_hash="abc123",
                source_kind=pm.SOURCE_KIND_MVSA,
                generated_at="2026-01-01T00:00:00+00:00",
                generator=pm.GENERATOR_MVSA,
            )
            self.assertTrue(sync._stamp_ok_score_ir(ir, "abc123"))
            self.assertFalse(sync._stamp_ok_score_ir(ir, "other"))
            self.assertTrue(sync._stamp_ok_from_ir(mxl, "abc123"))
            self.assertFalse(sync._stamp_ok_from_ir(mxl, "other"))


if __name__ == "__main__":
    unittest.main()
