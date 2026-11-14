"""Tests voor check_vsa_products (svg + T1 .vsa.mvsa; geen .vsa.mxl)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

import check_vsa_products as check


class CheckOneTests(unittest.TestCase):
    def test_soft_skip_requires_svg_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            vsa = root / "los.vsa"
            vsa.write_text("[:] Amen. [:]\n", encoding="utf-8")
            with (
                mock.patch.object(check, "REPO_ROOT", root),
                mock.patch.object(
                    check,
                    "classify_vsa_mvsa_template",
                    return_value=("soft_skip", None),
                ),
            ):
                status = check.check_one(vsa)
            kinds = {i.kind for i in status.issues}
            self.assertIn("missing_svg", kinds)
            self.assertNotIn("missing_mvsa", kinds)
            self.assertNotIn("missing_mxl", kinds)

    def test_ok_template_requires_mvsa(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            vsa = root / "lied.vsa"
            vsa.write_text(
                "---\nsoort: tropaar\ntoon: 1\n---\n[:] Amen. [:]\n",
                encoding="utf-8",
            )
            svg = check.product_svg_for_vsa(vsa)
            svg.write_text(
                '<?xml version="1.0"?>\n<svg xmlns="http://www.w3.org/2000/svg"/>\n',
                encoding="utf-8",
            )
            with (
                mock.patch.object(check, "REPO_ROOT", root),
                mock.patch.object(
                    check,
                    "classify_vsa_mvsa_template",
                    return_value=("ok", "tropaar-toon-1-groningen"),
                ),
                mock.patch.object(
                    check,
                    "issues_from_meta_or",
                    side_effect=lambda *a, **k: k["stamp_issues"](),
                ),
                mock.patch.object(
                    check,
                    "_stamp_issues_svg",
                    return_value=[],
                ),
            ):
                status = check.check_one(vsa)
            kinds = {i.kind for i in status.issues}
            self.assertIn("missing_mvsa", kinds)
            self.assertNotIn("missing_mxl", kinds)

    def test_hard_template_reports_error_not_missing_mvsa(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            vsa = root / "lied.vsa"
            vsa.write_text(
                "---\nformule: bestaat-niet\ntoon: 1\n---\n[:] Amen. [:]\n",
                encoding="utf-8",
            )
            with (
                mock.patch.object(check, "REPO_ROOT", root),
                mock.patch.object(
                    check,
                    "classify_vsa_mvsa_template",
                    side_effect=RuntimeError("geen template"),
                ),
                mock.patch.object(
                    check,
                    "issues_from_meta_or",
                    side_effect=lambda *a, **k: k["stamp_issues"](),
                ),
                mock.patch.object(
                    check,
                    "_stamp_issues_svg",
                    return_value=[],
                ),
            ):
                status = check.check_one(vsa)
            kinds = {i.kind for i in status.issues}
            self.assertIn("template_error", kinds)
            self.assertNotIn("missing_mvsa", kinds)


if __name__ == "__main__":
    unittest.main()
