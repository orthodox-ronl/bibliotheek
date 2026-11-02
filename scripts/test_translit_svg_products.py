"""Unit tests voor translit-SVG productnamen en moduskeuze."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

import translit_svg_products as tsp


class NamingTests(unittest.TestCase):
    def test_product_names(self) -> None:
        vsa = Path("a/lied.vsa")
        self.assertEqual(
            tsp.product_translit_svg(vsa, "nls").name,
            "lied.vsa.translit-nls.svg",
        )
        self.assertEqual(
            tsp.product_translit_svg(vsa, "ksl").name,
            "lied.vsa.translit-ksl.svg",
        )
        mvsa = Path("b/score.mvsa")
        self.assertEqual(
            tsp.product_translit_svg(mvsa, "nls").name,
            "score.mvsa.translit-nls.svg",
        )

    def test_meta_keys(self) -> None:
        self.assertEqual(tsp.meta_key_for_modus("nls"), "svg-translit-nls")
        self.assertEqual(tsp.meta_key_for_modus("ksl"), "svg-translit-ksl")


class ModiTests(unittest.TestCase):
    def test_pure_latin_needs_ksl(self) -> None:
        self.assertEqual(tsp.translit_modi_for_text("Amen Heer."), ("ksl",))

    def test_pure_cyrillic_needs_nls(self) -> None:
        self.assertEqual(tsp.translit_modi_for_text("Аминь Господи."), ("nls",))

    def test_hybrid_needs_both(self) -> None:
        self.assertEqual(
            tsp.translit_modi_for_text("Amen и Аминь"),
            ("nls", "ksl"),
        )

    def test_empty_or_digits_only(self) -> None:
        self.assertEqual(tsp.translit_modi_for_text(""), ())
        self.assertEqual(tsp.translit_modi_for_text("123"), ())


class PagePdfNamingTests(unittest.TestCase):
    def test_pagina_translit_pdf_path(self) -> None:
        md = Path("content-source/catalogus/x/index.md")
        self.assertEqual(
            tsp.pagina_translit_pdf_path(md, "nls").name,
            "index.md.translit-nls.pdf",
        )
        self.assertEqual(
            tsp.pagina_translit_pdf_path(md, "ksl").name,
            "index.md.translit-ksl.pdf",
        )

    def test_page_translit_modi_union(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            nl = root / "nl.vsa"
            ksl = root / "ksl.vsa"
            nl.write_text("[:] Amen. [:]\n", encoding="utf-8")
            ksl.write_text("[:] Аминь. [:]\n", encoding="utf-8")
            self.assertEqual(tsp.page_translit_modi([nl]), ("ksl",))
            self.assertEqual(tsp.page_translit_modi([ksl]), ("nls",))
            self.assertEqual(tsp.page_translit_modi([nl, ksl]), ("nls", "ksl"))
            mscz = root / "x.mscz"
            mscz.write_bytes(b"PK")
            self.assertEqual(tsp.page_translit_modi([mscz]), ())


class TranslitMxlNamingTests(unittest.TestCase):
    def test_product_translit_mxl_name(self) -> None:
        mvsa = Path("a/lied.mvsa")
        self.assertEqual(
            tsp.product_translit_mxl(mvsa).name, "lied.mvsa.translit.mxl"
        )

    def test_expects_only_mvsa_with_script(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mvsa = root / "nl.mvsa"
            mvsa.write_text("L: Amen\n", encoding="utf-8")
            self.assertTrue(tsp.expects_translit_mxl(mvsa))
            vsa = root / "x.vsa"
            vsa.write_text("[:] Amen. [:]\n", encoding="utf-8")
            self.assertFalse(tsp.expects_translit_mxl(vsa))


class SyncTranslitMxlTests(unittest.TestCase):
    def test_sync_exports_and_merges_meta(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mvsa = root / "lied.mvsa"
            mvsa.write_text("L: Amen\nS: a\n", encoding="utf-8")
            dest = tsp.product_translit_mxl(mvsa)

            def fake_export(source: Path) -> Path:
                self.assertEqual(source, mvsa)
                dest.write_bytes(b"PK\x03\x04fake")
                return dest

            with (
                mock.patch.object(tsp, "REPO_ROOT", root),
                mock.patch.object(
                    tsp, "export_one_translit_mxl", side_effect=fake_export
                ),
                mock.patch.object(tsp, "_stamp_translit_mxl_file"),
                mock.patch.object(tsp, "write_products_meta") as write_meta,
            ):
                out = tsp.sync_translit_mxl(mvsa, dry_run=False, force=True)

            self.assertEqual(out, {"mxl-translit": dest})
            write_meta.assert_called_once_with(
                mvsa, {"mxl-translit": dest}, merge=True
            )


class SyncTranslitTests(unittest.TestCase):
    def test_sync_exports_and_merges_meta(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            vsa = root / "lied.vsa"
            vsa.write_text("[:] Amen. [:]\n", encoding="utf-8")
            dest = tsp.product_translit_svg(vsa, "ksl")

            def fake_export(source: Path, modus: str) -> Path:
                self.assertEqual(source, vsa)
                self.assertEqual(modus, "ksl")
                dest.write_text(
                    '<?xml version="1.0"?>\n<svg xmlns="http://www.w3.org/2000/svg"/>\n',
                    encoding="utf-8",
                )
                return dest

            with (
                mock.patch.object(tsp, "REPO_ROOT", root),
                mock.patch.object(
                    tsp, "export_one_translit_svg", side_effect=fake_export
                ),
                mock.patch.object(tsp, "write_products_meta") as write_meta,
            ):
                out = tsp.sync_translit_svgs(vsa, dry_run=False, force=True)

            self.assertEqual(out, {"svg-translit-ksl": dest})
            write_meta.assert_called_once_with(
                vsa, {"svg-translit-ksl": dest}, merge=True
            )
            self.assertTrue(dest.is_file())


if __name__ == "__main__":
    unittest.main()
