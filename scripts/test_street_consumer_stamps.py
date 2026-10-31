"""Tests: bibliotheek-stempels na kale tooling-products (lyrics/mp3)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

import product_meta as pm
import street_consumer_stamps as scs
import sync_mvsa_products as mvsa_sync


class RestampHelpersTests(unittest.TestCase):
    def test_restamp_lyrics_adds_sha_header(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            mvsa = Path(tmp) / "lied.mvsa"
            mvsa.write_text("L: a\n", encoding="utf-8")
            lyrics = Path(str(mvsa) + ".lyrics.txt")
            lyrics.write_text("Amen\n", encoding="utf-8")
            self.assertTrue(scs.restamp_lyrics_sibling(mvsa))
            text = lyrics.read_text(encoding="utf-8")
            self.assertIn("# vsa-source-sha256:", text)
            self.assertIn("# vsa-source-kind: mvsa", text)
            self.assertTrue(text.rstrip().endswith("Amen"))
            stamp = pm.read_mvsa_stamp(lyrics)
            self.assertEqual(stamp.get(pm.FIELD_SOURCE_SHA), pm.source_sha256(mvsa))

    def test_restamp_mp3_writes_id3(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            mvsa = Path(tmp) / "lied.mvsa"
            mvsa.write_text("L: a\n", encoding="utf-8")
            mp3 = Path(str(mvsa) + ".mp3")
            # Minimale "audio": genoeg bytes voor stamp_audio strip/prepend
            mp3.write_bytes(b"\xff\xfb\x90\x00" + b"\x00" * 32)
            self.assertTrue(scs.restamp_mp3_sibling(mvsa))
            stamp = pm.read_audio_stamp(mp3)
            self.assertEqual(stamp.get(pm.FIELD_SOURCE_SHA), pm.source_sha256(mvsa))
            self.assertEqual(stamp.get(pm.FIELD_SOURCE_KIND), pm.SOURCE_KIND_MVSA)

    def test_restamp_skips_missing_siblings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            mvsa = Path(tmp) / "lied.mvsa"
            mvsa.write_text("L: a\n", encoding="utf-8")
            self.assertFalse(scs.restamp_lyrics_sibling(mvsa))
            self.assertFalse(scs.restamp_mp3_sibling(mvsa))


class MetaAfterRestampTests(unittest.TestCase):
    def test_restamp_updates_meta_hashes(self) -> None:
        from vsa.products_meta import freshness, sha256_file, write_meta

        with tempfile.TemporaryDirectory() as tmp:
            mvsa = Path(tmp) / "lied.mvsa"
            mvsa.write_text("L: a\n", encoding="utf-8")
            lyrics = Path(str(mvsa) + ".lyrics.txt")
            lyrics.write_text("Amen\n", encoding="utf-8")
            mp3 = Path(str(mvsa) + ".mp3")
            mp3.write_bytes(b"\xff\xfb\x90\x00" + b"\x00" * 32)
            mxl = Path(str(mvsa) + ".mxl")
            mxl.write_bytes(b"PK\x03\x04")
            write_meta(mvsa, {"mxl": mxl, "lyrics": lyrics, "mp3": mp3})
            bare_lyrics_hash = sha256_file(lyrics)
            scs.restamp_after_street_products(mvsa)
            status, detail = freshness(mvsa)
            self.assertEqual(status, "ok", detail)
            self.assertNotEqual(sha256_file(lyrics), bare_lyrics_hash)
            self.assertTrue(pm.read_mvsa_stamp(lyrics).get(pm.FIELD_SOURCE_SHA))
            self.assertTrue(pm.read_audio_stamp(mp3).get(pm.FIELD_SOURCE_SHA))


class MvsaSyncRestampsTests(unittest.TestCase):
    def test_sync_one_restamps_after_products(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mvsa = root / "lied.mvsa"
            mvsa.write_text("L: a\n", encoding="utf-8")
            lyrics = Path(str(mvsa) + ".lyrics.txt")
            mp3 = Path(str(mvsa) + ".mp3")

            def fake_products(path: Path, *, skip_svg: bool) -> None:
                del skip_svg
                mvsa_sync.product_mxl_for_mvsa(path).write_bytes(b"PK")
                mvsa_sync.product_score_ir_for_mvsa(path).write_text(
                    "{}\n", encoding="utf-8"
                )
                mvsa_sync.product_from_ir_musicxml_for_mvsa(path).write_text(
                    "<score/>\n", encoding="utf-8"
                )
                lyrics.write_text("kaal amen\n", encoding="utf-8")
                mp3.write_bytes(b"\xff\xfb\x90\x00" + b"\x00" * 32)

            with (
                mock.patch.object(mvsa_sync, "REPO_ROOT", root),
                mock.patch.object(
                    mvsa_sync, "_run_mvsa_products", side_effect=fake_products
                ),
            ):
                mvsa_sync.sync_one(
                    mvsa,
                    need_mxl=True,
                    need_pdf=False,
                    need_svg=False,
                    need_score_ir=True,
                    need_from_ir=True,
                    dry_run=False,
                )

            self.assertIn("vsa-source-sha256", lyrics.read_text(encoding="utf-8"))
            self.assertEqual(
                pm.read_audio_stamp(mp3).get(pm.FIELD_SOURCE_SHA),
                pm.source_sha256(mvsa),
            )


if __name__ == "__main__":
    unittest.main()
