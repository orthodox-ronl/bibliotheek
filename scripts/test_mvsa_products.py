"""Tests voor mvsa-products collect/stamp (zonder MuseScore)."""

from __future__ import annotations

import json
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
    def test_sync_one_mxl_and_ir_without_svg(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mvsa = root / "lied.mvsa"
            mvsa.write_text("L: a\nS: a\nA: a\nT: a\nB: a\n", encoding="utf-8")
            mxl = sync.product_mxl_for_mvsa(mvsa)
            score_ir = sync.product_score_ir_for_mvsa(mvsa)
            from_ir = sync.product_from_ir_musicxml_for_mvsa(mvsa)
            calls: list[str] = []

            def fake_mxl(path: Path) -> None:
                calls.append("mxl")
                mxl.write_bytes(b"PK\x03\x04fake")

            def fake_ir(path: Path, *, with_from_ir: bool) -> None:
                self.assertTrue(with_from_ir)
                calls.append("ir")
                score_ir.write_text('{"format":"score-ir"}\n', encoding="utf-8")
                from_ir.write_text(
                    '<?xml version="1.0"?>\n<score-partwise/>\n',
                    encoding="utf-8",
                )

            with (
                mock.patch.object(sync, "REPO_ROOT", root),
                mock.patch.object(sync, "_run_mvsa_mxl", side_effect=fake_mxl),
                mock.patch.object(sync, "_run_mvsa_score_ir", side_effect=fake_ir),
                mock.patch.object(sync, "_run_mvsa_svg") as run_svg,
                mock.patch.object(sync, "write_products_meta") as write_meta,
                mock.patch.object(sync, "sync_translit_svgs") as sync_translit_svg,
                mock.patch.object(sync, "sync_translit_mxl") as sync_translit_mxl,
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

            self.assertEqual(calls, ["mxl", "ir"])
            run_svg.assert_not_called()
            write_meta.assert_called_once_with(
                mvsa,
                {"mxl": mxl, "score-ir": score_ir, "from-ir": from_ir},
                merge=True,
            )
            sync_translit_svg.assert_not_called()
            sync_translit_mxl.assert_called_once_with(mvsa, dry_run=False, force=True)

    def test_mvsa_svg_outputs_bladreeks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            mvsa = Path(tmp) / "lied.mvsa"
            mvsa.write_text("L: a\n", encoding="utf-8")
            p1 = Path(tmp) / "lied.mvsa-1.svg"
            p2 = Path(tmp) / "lied.mvsa-2.svg"
            p1.write_text("<svg/>\n", encoding="utf-8")
            p2.write_text("<svg/>\n", encoding="utf-8")
            self.assertEqual(sync.mvsa_svg_outputs(mvsa), [p1, p2])

    def test_sync_one_svg_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mvsa = root / "lied.mvsa"
            mvsa.write_text("L: a\n", encoding="utf-8")
            svg = sync.product_svg_for_mvsa(mvsa)

            def fake_svg(path: Path) -> None:
                svg.write_text(
                    '<?xml version="1.0"?>\n<svg xmlns="http://www.w3.org/2000/svg"/>\n',
                    encoding="utf-8",
                )

            with (
                mock.patch.object(sync, "REPO_ROOT", root),
                mock.patch.object(sync, "_run_mvsa_mxl") as run_mxl,
                mock.patch.object(sync, "_run_mvsa_score_ir") as run_ir,
                mock.patch.object(sync, "_run_mvsa_svg", side_effect=fake_svg),
                mock.patch.object(sync, "write_products_meta") as write_meta,
                mock.patch.object(sync, "sync_translit_svgs") as sync_translit_svg,
                mock.patch.object(sync, "sync_translit_mxl") as sync_translit_mxl,
            ):
                sync.sync_one(
                    mvsa,
                    need_mxl=False,
                    need_pdf=False,
                    need_svg=True,
                    need_score_ir=False,
                    need_from_ir=False,
                    dry_run=False,
                )

            run_mxl.assert_not_called()
            run_ir.assert_not_called()
            write_meta.assert_called_once_with(mvsa, {"svg": svg}, merge=True)
            sync_translit_svg.assert_called_once_with(mvsa, dry_run=False, force=True)
            sync_translit_mxl.assert_not_called()


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

    def test_sectie_ir_gets_bibliotheek_stamp(self) -> None:
        """Na sectie score-ir: from-ir/score-ir moeten gestempeld zijn."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            content = root / "content-source"
            leaf = content / "catalogus" / "z" / "v" / "u"
            leaf.mkdir(parents=True)
            mvsa = leaf / "lied.mvsa"
            mvsa.write_text("@sectie a\nL: x |\nS: do |\n", encoding="utf-8")
            (content / "koormappen").mkdir(parents=True)
            (content / "koormappen" / "blad.md").write_text(
                '{{< bieb id="z/v/u@a" >}}\n',
                encoding="utf-8",
            )
            digest = pm.source_sha256(mvsa)
            score_ir = leaf / "lied.mvsa@a.score-ir.json"
            from_ir = leaf / "lied.mvsa@a.from-ir.musicxml"
            svg = leaf / "lied.mvsa@a.svg"

            def fake_ir(path: Path, section: str) -> None:
                self.assertEqual(section, "a")
                score_ir.write_text('{"format":"score-ir"}\n', encoding="utf-8")
                from_ir.write_text(
                    '<?xml version="1.0"?>\n<score-partwise/>\n',
                    encoding="utf-8",
                )

            def fake_svg(path: Path, *, section: str | None = None) -> None:
                self.assertEqual(section, "a")
                svg.write_text(
                    '<?xml version="1.0"?>\n<svg xmlns="http://www.w3.org/2000/svg"/>\n',
                    encoding="utf-8",
                )

            with (
                mock.patch.object(sync, "REPO_ROOT", root),
                mock.patch.object(
                    sync, "_run_mvsa_score_ir_section", side_effect=fake_ir
                ),
                mock.patch.object(sync, "_run_mvsa_svg", side_effect=fake_svg),
            ):
                n = sync.sync_referenced_sectie_products(
                    content / "catalogus", dry_run=False
                )
            self.assertGreaterEqual(n, 1)
            self.assertTrue(sync._stamp_ok_svg(svg, digest))
            self.assertTrue(sync._stamp_ok_score_ir(score_ir, digest))
            self.assertTrue(sync._stamp_ok_from_ir(from_ir, digest))

    def test_sectie_ir_restores_whole_piece_meta(self) -> None:
        """Sectie-export mag meta from-ir/score-ir niet op @sectie laten staan."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            content = root / "content-source"
            leaf = content / "catalogus" / "z" / "v" / "u"
            leaf.mkdir(parents=True)
            mvsa = leaf / "lied.mvsa"
            mvsa.write_text("@sectie a\nL: x |\nS: do |\n", encoding="utf-8")
            (content / "koormappen").mkdir(parents=True)
            (content / "koormappen" / "blad.md").write_text(
                '{{< bieb id="z/v/u@a" >}}\n',
                encoding="utf-8",
            )
            whole_ir = sync.product_score_ir_for_mvsa(mvsa)
            whole_from = sync.product_from_ir_musicxml_for_mvsa(mvsa)
            whole_ir.write_text('{"format":"score-ir","whole":true}\n', encoding="utf-8")
            whole_from.write_text(
                '<?xml version="1.0"?>\n<score-partwise id="whole"/>\n',
                encoding="utf-8",
            )
            # Meta alsof tooling die al naar @sectie wees.
            sync.write_products_meta(
                mvsa,
                {
                    "score-ir": leaf / "lied.mvsa@a.score-ir.json",
                    "from-ir": leaf / "lied.mvsa@a.from-ir.musicxml",
                },
                merge=False,
            )

            def fake_ir(path: Path, section: str) -> None:
                (leaf / f"lied.mvsa@{section}.score-ir.json").write_text(
                    '{"format":"score-ir"}\n', encoding="utf-8"
                )
                (leaf / f"lied.mvsa@{section}.from-ir.musicxml").write_text(
                    '<?xml version="1.0"?>\n<score-partwise/>\n',
                    encoding="utf-8",
                )
                sync.write_products_meta(
                    mvsa,
                    {
                        "score-ir": leaf / f"lied.mvsa@{section}.score-ir.json",
                        "from-ir": leaf / f"lied.mvsa@{section}.from-ir.musicxml",
                    },
                    merge=True,
                )

            def fake_svg(path: Path, *, section: str | None = None) -> None:
                (leaf / f"lied.mvsa@{section}.svg").write_text(
                    '<?xml version="1.0"?>\n<svg xmlns="http://www.w3.org/2000/svg"/>\n',
                    encoding="utf-8",
                )

            with (
                mock.patch.object(sync, "REPO_ROOT", root),
                mock.patch.object(
                    sync, "_run_mvsa_score_ir_section", side_effect=fake_ir
                ),
                mock.patch.object(sync, "_run_mvsa_svg", side_effect=fake_svg),
            ):
                sync.sync_referenced_sectie_products(
                    content / "catalogus", dry_run=False
                )

            meta = json.loads(
                (leaf / "lied.mvsa.products-meta.json").read_text(encoding="utf-8")
            )
            self.assertEqual(meta["products"]["score-ir"]["file"], whole_ir.name)
            self.assertEqual(meta["products"]["from-ir"]["file"], whole_from.name)


if __name__ == "__main__":
    unittest.main()
