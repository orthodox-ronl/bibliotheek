"""Regressie: translit van een ``@sectie`` bevat alleen die sectie.

Contract: docs/specs/koormap-paginataal.md (``@sectie``).
"""

from __future__ import annotations

import unittest
from pathlib import Path
from unittest import mock

import translit_svg_products as tsp


class SectieTranslitTests(unittest.TestCase):
    def test_names(self) -> None:
        src = Path("lied.mvsa")
        self.assertEqual(
            tsp.product_translit_svg(src, "nls", "een").name,
            "lied.mvsa@een.translit-nls.svg",
        )
        self.assertEqual(
            tsp.product_translit_svg(src, "beide", "een").name,
            "lied.mvsa@een.translit.svg",
        )
        self.assertEqual(
            tsp.product_translit_svg(src, "ksl").name, "lied.mvsa.translit-ksl.svg"
        )

    def test_export_passes_section(self) -> None:
        with mock.patch.object(tsp, "check_call") as call, mock.patch.object(
            Path, "is_file", return_value=True
        ):
            tsp.export_one_translit_svg(Path("lied.mvsa"), "ksl", "een")
        cmd = call.call_args.args[0]
        self.assertEqual(cmd[cmd.index("--section") + 1], "een")


if __name__ == "__main__":
    unittest.main()
