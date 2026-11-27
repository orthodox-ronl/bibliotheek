"""Regressie: pagina-download volgt de translit-knoppen, ook zonder lokale PDF's.

Op de gebouwde site staan blad-PDF's alleen op R2. De koppeling naar de
translit-PDF's mag daarom niet van lokale bestanden afhangen.
Contract: docs/specs/schermpartituur.md §1.
"""

from __future__ import annotations

import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PARTIALS = REPO / "layouts" / "partials"


class PaginaTranslitDownloadTests(unittest.TestCase):
    def test_score_registers_translit_directions(self) -> None:
        text = (PARTIALS / "bieb-score.html").read_text(encoding="utf-8")
        for stand in ("nls", "ksl"):
            self.assertIn(f'.Store.Add "translitPdf" (slice "{stand}")', text)

    def test_download_links_follow_page_content(self) -> None:
        text = (PARTIALS / "pagina-acties.html").read_text(encoding="utf-8")
        self.assertIn("if or $paginaPdfNls $metNls", text)
        self.assertIn("if or $paginaPdfKsl $metKsl", text)
        self.assertIn("if or $paginaPdfBeide (and $metNls $metKsl)", text)
        self.assertLess(
            text.index("$_ := .Content"), text.index('.Store.Get "translitPdf"')
        )


if __name__ == "__main__":
    unittest.main()
