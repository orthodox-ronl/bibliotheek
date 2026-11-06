"""Tests voor ``catalogus_sectie`` (id@sectie-split en productnamen)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from catalogus_sectie import (
    collect_sectie_refs,
    product_svg_for_sectie,
    split_catalogus_ref,
)


class SplitCatalogusRefTests(unittest.TestCase):
    def test_plain(self) -> None:
        self.assertEqual(
            split_catalogus_ref("ektinia/vrede/hemelum"),
            ("ektinia/vrede/hemelum", None),
        )

    def test_with_sectie(self) -> None:
        self.assertEqual(
            split_catalogus_ref("ektinia/vrede/hemelum@openingsfrase"),
            ("ektinia/vrede/hemelum", "openingsfrase"),
        )

    def test_rejects_blok_style_digit(self) -> None:
        with self.assertRaises(ValueError):
            split_catalogus_ref("ektinia/vrede/hemelum@1")

    def test_rejects_double_at(self) -> None:
        with self.assertRaises(ValueError):
            split_catalogus_ref("a/b/c@d@e")


class ProductNamesTests(unittest.TestCase):
    def test_svg_name(self) -> None:
        mvsa = Path("leaf/lied.mvsa")
        self.assertEqual(
            product_svg_for_sectie(mvsa, "vrede").name,
            "lied.mvsa@vrede.svg",
        )


class CollectRefsTests(unittest.TestCase):
    def test_finds_shortcode_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            md = root / "blad" / "index.md"
            md.parent.mkdir(parents=True)
            md.write_text(
                '{{< bieb id="ektinia/vrede/hemelum@openingsfrase" />}}\n',
                encoding="utf-8",
            )
            refs = collect_sectie_refs(root)
            self.assertEqual(
                refs.get("ektinia/vrede/hemelum"),
                {"openingsfrase"},
            )


if __name__ == "__main__":
    unittest.main()
