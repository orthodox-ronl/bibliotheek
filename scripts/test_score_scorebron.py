"""Regressie: weergave-classificatie (VSA vs partituur).

Spiegel van ``static/js/score-scorebron.js`` → ``bronFromSrc``.
Contract: docs/specs/schermpartituur.md §2.1.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
JS = REPO / "static" / "js" / "score-scorebron.js"


def bron_from_src(src: str) -> str:
    n = (src or "").lower()
    if (
        ".vsa.mvsa." in n
        or ".mvsa.translit" in n
        or ".mscz.translit" in n
        or re.search(r"\.mvsa\.svg(\?|#|$)", n)
        or re.search(r"\.mscz\.svg(\?|#|$)", n)
        or ".from-ir.musicxml" in n
    ):
        return "partituur"
    if (
        "/vsa/bladermap/" in n
        or ".vsa.translit" in n
        or re.search(r"\.vsa\.svg(\?|#|$)", n)
    ):
        return "vsa"
    return "partituur"


class ScorebronFromSrcTests(unittest.TestCase):
    def test_js_exports_classifier(self) -> None:
        text = JS.read_text(encoding="utf-8")
        self.assertNotIn("localStorage.", text)
        self.assertIn("__bibliotheekScorebronFromSrc", text)
        self.assertIn("data-weergave-kies", text)

    def test_vsa_vs_partituur(self) -> None:
        cases = [
            ("/x/lied.vsa.svg", "vsa"),
            ("/x/lied.vsa.translit-ksl.svg", "vsa"),
            ("/vsa/bladermap/a/b.svg", "vsa"),
            ("/x/lied.vsa.mvsa.svg", "partituur"),
            ("/x/lied.vsa.mvsa.translit-ksl.svg", "partituur"),
            ("/x/lied.mvsa.svg", "partituur"),
            ("/x/lied.mvsa.from-ir.musicxml", "partituur"),
            ("/x/lied.mscz.svg", "partituur"),
            ("/x/lied.mvsa.vsa.svg", "vsa"),
            ("/x/lied.mvsa.vsa.translit-ksl.svg", "vsa"),
        ]
        for src, want in cases:
            with self.subTest(src=src):
                self.assertEqual(bron_from_src(src), want)


if __name__ == "__main__":
    unittest.main()
