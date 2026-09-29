"""Tests voor audio-products collect/stamp (zonder MuseScore)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import product_meta as pm
import sync_audio_products as sync


class CollectTests(unittest.TestCase):
    def test_collects_three_kinds_skips_import(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.mvsa").write_text("L: a\n", encoding="utf-8")
            (root / "a.mscz.mvsa").write_text("L: a\n", encoding="utf-8")
            (root / "b.mscz").write_bytes(b"mscz")
            (root / "c.vsa").write_text("L: c\n", encoding="utf-8")
            (root / "c.syl.vsa").write_text("L: x\n", encoding="utf-8")
            jobs = sync.collect_audio_jobs(root)
            kinds = sorted(j.kind for j in jobs)
            self.assertEqual(
                kinds,
                [pm.SOURCE_KIND_MVSA, pm.SOURCE_KIND_PARTITUUR, pm.SOURCE_KIND_VSA],
            )

    def test_product_names(self) -> None:
        mvsa = Path("a/lied.mvsa")
        mscz = Path("a/lied.mscz")
        vsa = Path("a/lied.vsa")
        self.assertEqual(
            sync.AudioJob(mvsa, pm.SOURCE_KIND_MVSA).product.name, "lied.mvsa.mp3"
        )
        self.assertEqual(
            sync.AudioJob(mscz, pm.SOURCE_KIND_PARTITUUR).product.name,
            "lied.mscz.mp3",
        )
        self.assertEqual(
            sync.AudioJob(vsa, pm.SOURCE_KIND_VSA).product.name, "lied.vsa.mp3"
        )


class StampOkTests(unittest.TestCase):
    def test_stale_without_mp3(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            mvsa = Path(tmp) / "x.mvsa"
            mvsa.write_text("L: a\n", encoding="utf-8")
            job = sync.AudioJob(mvsa, pm.SOURCE_KIND_MVSA)
            self.assertTrue(sync.is_stale(job))

    def test_ok_after_stamp(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            mvsa = Path(tmp) / "x.mvsa"
            mvsa.write_text("L: a\n", encoding="utf-8")
            job = sync.AudioJob(mvsa, pm.SOURCE_KIND_MVSA)
            mp3 = job.product
            # Minimale fake-mp3 (geen echte frames); alleen stamp-header.
            mp3.write_bytes(b"\xff\xfb\x90\x00fake-audio")
            pm.stamp_audio(
                mp3,
                source_hash=pm.source_sha256(mvsa),
                source_kind=pm.SOURCE_KIND_MVSA,
                generated_at=pm.utc_now_iso(),
            )
            self.assertFalse(sync.is_stale(job))
            stamp = pm.read_audio_stamp(mp3)
            self.assertEqual(stamp[pm.FIELD_SOURCE_KIND], pm.SOURCE_KIND_MVSA)
            self.assertEqual(stamp[pm.FIELD_SOURCE_SHA], pm.source_sha256(mvsa))


if __name__ == "__main__":
    unittest.main()
