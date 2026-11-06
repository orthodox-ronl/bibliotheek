"""Tests voor lyrics-sync (zonder MuseScore / text_export-heavy pad)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

import sync_lyrics_products as sync


class EnsureMsczMxlTests(unittest.TestCase):
    def test_uses_fresh_sibling(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            mscz = Path(tmp) / "lied.mscz"
            mscz.write_bytes(b"PK\x03\x04fake")
            mxl = sync.product_mxl_for_mscz(mscz)
            mxl.write_bytes(b"PK\x03\x04mxl")

            with (
                mock.patch.object(sync, "_fresh_mscz_mxl", return_value=mxl),
                mock.patch(
                    "sync_mscz_products._run_mscz_mxl"
                ) as run_mxl,
            ):
                got = sync._ensure_mscz_mxl_for_lyrics(mscz)

            self.assertEqual(got, mxl)
            run_mxl.assert_not_called()

    def test_runs_mscz_mxl_when_stale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            mscz = Path(tmp) / "lied.mscz"
            mscz.write_bytes(b"PK\x03\x04fake")
            mxl = sync.product_mxl_for_mscz(mscz)

            def fake_mxl(path: Path) -> None:
                self.assertEqual(path, mscz)
                mxl.write_bytes(b"PK\x03\x04new")

            with (
                mock.patch.object(sync, "_fresh_mscz_mxl", side_effect=[None, mxl]),
                mock.patch(
                    "sync_mscz_products._run_mscz_mxl", side_effect=fake_mxl
                ) as run_mxl,
                mock.patch("street_meta.write_products_meta") as write_meta,
            ):
                got = sync._ensure_mscz_mxl_for_lyrics(mscz)

            run_mxl.assert_called_once_with(mscz)
            write_meta.assert_called_once()
            self.assertEqual(got, mxl)


if __name__ == "__main__":
    unittest.main()
