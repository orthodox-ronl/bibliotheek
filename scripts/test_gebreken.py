"""Unit tests voor gebreken-markering (geen MuseScore)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import gebreken as g


class GebrekenParseTests(unittest.TestCase):
    def test_actief_en_toelichting(self) -> None:
        params = g.parse_frontmatter_params(
            "---\npublicatiestatus: reviewable\ngebreken: true\n"
            'gebreken_toelichting: "Fout in couplet 2"\n---\n\nbody\n'
        )
        self.assertTrue(g.gebreken_actief(params))
        self.assertEqual(g.gebreken_toelichting(params), "Fout in couplet 2")
        self.assertEqual(g.publicatiestatus(params), "reviewable")

    def test_uit_zonder_veld(self) -> None:
        params = g.parse_frontmatter_params(
            "---\npublicatiestatus: reviewable\n---\n"
        )
        self.assertFalse(g.gebreken_actief(params))
        self.assertIsNone(g.gebreken_expliciet(params))

    def test_expliciet_false(self) -> None:
        params = g.parse_frontmatter_params("---\ngebreken: false\n---\n")
        self.assertEqual(g.gebreken_expliciet(params), False)

    def test_bieb_ids(self) -> None:
        ids = g.bieb_ids_in_markdown(
            '{{< bieb id="tropaar/x/y" />}}\n{{< bieb id="tropaar/x/y@a" />}}\n'
        )
        self.assertEqual(ids, ["tropaar/x/y"])


class GebrekenInheritanceTests(unittest.TestCase):
    def test_zangstuk_erft_naar_leaf_met_opt_out(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # Tijdelijke catalogus-root injecteren
            z = root / "tropaar" / "demo-toon-1"
            v = z / "hemelum"
            leaf_ok = v / "groningen"
            leaf_bad = v / "ander"
            for d in (leaf_ok, leaf_bad):
                d.mkdir(parents=True)
            (z / "_index.md").write_text(
                "---\npublicatiestatus: concept\ngebreken: true\n"
                'gebreken_toelichting: "Hele zangstuk herzien"\n---\n',
                encoding="utf-8",
            )
            (v / "_index.md").write_text(
                "---\npublicatiestatus: concept\n---\n",
                encoding="utf-8",
            )
            (leaf_ok / "index.md").write_text(
                "---\npublicatiestatus: reviewable\ngebreken: false\n---\n",
                encoding="utf-8",
            )
            (leaf_bad / "index.md").write_text(
                "---\npublicatiestatus: reviewable\n---\n",
                encoding="utf-8",
            )
            old = g.CATALOGUS_ROOT
            try:
                g.CATALOGUS_ROOT = root
                act_ok, tip_ok = g.effective_gebreken_for_folder(leaf_ok)
                act_bad, tip_bad = g.effective_gebreken_for_folder(leaf_bad)
            finally:
                g.CATALOGUS_ROOT = old
            self.assertFalse(act_ok)
            self.assertIsNone(tip_ok)
            self.assertTrue(act_bad)
            self.assertEqual(tip_bad, "Hele zangstuk herzien")

    def test_leaf_toelichting_wint(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            z = root / "kondak" / "demo"
            v = z / "default"
            leaf = v / "hemelum"
            leaf.mkdir(parents=True)
            (z / "_index.md").write_text(
                "---\ngebreken: true\n"
                'gebreken_toelichting: "Zangstuk-tip"\n---\n',
                encoding="utf-8",
            )
            (v / "_index.md").write_text("---\n---\n", encoding="utf-8")
            (leaf / "index.md").write_text(
                "---\ngebreken: true\n"
                'gebreken_toelichting: "Alleen deze leaf"\n---\n',
                encoding="utf-8",
            )
            old = g.CATALOGUS_ROOT
            try:
                g.CATALOGUS_ROOT = root
                actief, tip = g.effective_gebreken_for_folder(leaf)
            finally:
                g.CATALOGUS_ROOT = old
            self.assertTrue(actief)
            self.assertEqual(tip, "Alleen deze leaf")


class GebrekenSvgTests(unittest.TestCase):
    def test_inject_and_strip(self) -> None:
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" '
            'viewBox="0 0 400 200"><g id="music"/></svg>'
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "lied.vsa.svg"
            path.write_text(svg, encoding="utf-8")
            self.assertTrue(g.ensure_svg_gebreken_stempel(path, actief=True))
            text = path.read_text(encoding="utf-8")
            self.assertIn(g.SVG_MARKER_ID, text)
            self.assertIn(g.STEMPEL_TEKST, text)
            self.assertFalse(g.ensure_svg_gebreken_stempel(path, actief=True))
            self.assertTrue(g.ensure_svg_gebreken_stempel(path, actief=False))
            self.assertNotIn(g.SVG_MARKER_ID, path.read_text(encoding="utf-8"))


class GebrekenPdfTests(unittest.TestCase):
    def test_watermark(self) -> None:
        try:
            import pymupdf
        except ImportError:
            self.skipTest("pymupdf ontbreekt")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "index.md.pdf"
            doc = pymupdf.open()
            page = doc.new_page(width=595, height=842)
            page.insert_text((72, 72), "partituur")
            doc.save(path)
            doc.close()
            g.apply_pdf_gebreken_watermark(
                path, toelichting="Alleen voor tests"
            )
            self.assertTrue(g.pdf_has_gebreken_stempel(path))


def test_stempel_ververst_meta_hash(tmp_path, monkeypatch) -> None:
    """Stempelen wijzigt de SVG; de sha256 in products-meta moet meegaan."""
    import json

    from vsa.products_meta import write_meta

    leaf = tmp_path / "leaf"
    leaf.mkdir()
    (leaf / "index.md").write_text("---\ntitle: x\n---\n", encoding="utf-8")
    bron = leaf / "x.vsa"
    bron.write_text("L: a\n", encoding="utf-8")
    svg = leaf / "x.vsa.svg"
    svg.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 50"></svg>',
        encoding="utf-8",
    )
    write_meta(bron, {"svg": svg})
    monkeypatch.setattr(g, "effective_gebreken_for_folder", lambda _f: (True, None))
    changed, seen = g.sync_leaf_svg_stempels(leaf)
    assert (changed, seen) == (1, 1)
    meta = json.loads((leaf / "x.vsa.products-meta.json").read_text("utf-8"))
    import hashlib

    assert meta["products"]["svg"]["sha256"] == hashlib.sha256(svg.read_bytes()).hexdigest()
    # tweede run: niets meer te doen
    assert g.sync_leaf_svg_stempels(leaf) == (0, 1)


if __name__ == "__main__":
    unittest.main()
