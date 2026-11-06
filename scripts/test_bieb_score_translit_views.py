"""Regressie: hybride UV-translit-views (nls/ksl/beide).

Contract: docs/specs/schermpartituur.md (hybride uitvoeringsvorm).
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PARTIAL = REPO / "layouts" / "partials" / "bieb-score.html"


def _view_block(html: str, modus: str) -> str:
    if modus == "beide":
        m = re.search(
            r'data-translit-for-modus="beide"[^>]*>(.*?)</div>\s*'
            r'<div class="score-scherm score-scherm--osmg"',
            html,
            flags=re.S,
        )
    else:
        nxt = "beide" if modus == "ksl" else "ksl"
        m = re.search(
            rf'data-translit-for-modus="{modus}"[^>]*>(.*?)</div>\s*'
            rf'<div data-translit-view="aan" data-translit-for-modus="{nxt}"',
            html,
            flags=re.S,
        )
    if not m:
        raise AssertionError(f"{modus} translit-view-blok niet gevonden")
    return m.group(1)


class HybridTranslitViewTests(unittest.TestCase):
    def test_ksl_view_uses_ksl_svg_even_when_nls_sibling_exists(self) -> None:
        html = PARTIAL.read_text(encoding="utf-8")
        block = _view_block(html, "ksl")
        self.assertIn("$musicSvgsTranslitKsl", block)
        self.assertNotRegex(
            block,
            r"and\s+\$musicSvgsTranslitKsl\s+\(not\s+\$musicSvgsTranslitNls\)",
            msg=(
                "Hybride UV: Nls→Ксл moet .translit-ksl.svg tonen ook als "
                ".translit-nls.svg bestaat (schermpartituur § Translit)."
            ),
        )
        self.assertRegex(
            block,
            r"\{\{\-\s*if\s+\$musicSvgsTranslitKsl\s*\-\}\}",
        )

    def test_beide_view_prefers_translit_beide_svg(self) -> None:
        html = PARTIAL.read_text(encoding="utf-8")
        block = _view_block(html, "beide")
        self.assertRegex(
            block,
            r"\{\{\-\s*if\s+\$musicSvgsTranslitBeide\s*\-\}\}",
            msg="Beide knoppen op hybride: eerst .translit.svg",
        )

    def test_translit_svg_not_classified_as_nls(self) -> None:
        """``.translit.svg`` mag niet in de nls-lijst belanden (HasSuffix-val)."""
        html = PARTIAL.read_text(encoding="utf-8")
        self.assertNotRegex(
            html,
            r"translit-nls\.svg\"\)\s+\(strings\.HasSuffix \$n \"\.translit\.svg\"\)",
        )
        self.assertIn("$musicSvgsTranslitBeide", html)
        self.assertIn('HasSuffix $n ".translit.svg"', html)


if __name__ == "__main__":
    unittest.main()
