"""Tests voor import-.mscz.mvsa stamp + sync/check (zonder MuseScore)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

import check_import_mvsa as chk
import product_meta as pm
import sync_import_mvsa as sync


class StampTests(unittest.TestCase):
    def test_stamp_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "lied.mscz.mvsa"
            path.write_text("L: a\nS: 1:c\n", encoding="utf-8")
            pm.stamp_mvsa_partituur(
                path,
                partituur_hash="abc123",
                generated_at="2026-01-02T03:04:05+00:00",
            )
            stamp = pm.read_mvsa_stamp(path)
            self.assertEqual(stamp[pm.FIELD_PARTITUUR_SHA], "abc123")
            self.assertEqual(stamp[pm.FIELD_SOURCE_KIND], pm.SOURCE_KIND_PARTITUUR)
            self.assertEqual(stamp[pm.FIELD_GENERATOR], pm.GENERATOR_IMPORT_MVSA)
            body = path.read_text(encoding="utf-8")
            self.assertIn("L: a", body)
            self.assertTrue(body.startswith("# vsa-partituur-sha256:"))

    def test_stamp_after_frontmatter(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "x.mscz.mvsa"
            path.write_text("---\ntitle: t\n---\n\nL: a\n", encoding="utf-8")
            pm.stamp_mvsa_partituur(
                path, partituur_hash="deadbeef", generated_at="2026-01-01T00:00:00+00:00"
            )
            text = path.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("---\n"))
            self.assertIn("# vsa-partituur-sha256: deadbeef", text)
            stamp = pm.read_mvsa_stamp(path)
            self.assertEqual(stamp[pm.FIELD_PARTITUUR_SHA], "deadbeef")

    def test_restamp_replaces(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "x.mscz.mvsa"
            path.write_text("body\n", encoding="utf-8")
            pm.stamp_mvsa_partituur(
                path, partituur_hash="one", generated_at="2026-01-01T00:00:00+00:00"
            )
            pm.stamp_mvsa_partituur(
                path, partituur_hash="two", generated_at="2026-01-02T00:00:00+00:00"
            )
            stamp = pm.read_mvsa_stamp(path)
            self.assertEqual(stamp[pm.FIELD_PARTITUUR_SHA], "two")
            self.assertEqual(path.read_text(encoding="utf-8").count("vsa-partituur"), 1)


class NamingTests(unittest.TestCase):
    def test_product_and_reverse(self) -> None:
        mscz = Path("a/b/lied.mscz")
        mvsa = sync.product_mvsa_for_mscz(mscz)
        self.assertEqual(mvsa.name, "lied.mscz.mvsa")
        self.assertEqual(sync.mscz_for_import_mvsa(mvsa), mscz)


class CheckTests(unittest.TestCase):
    def test_ok_pair(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mscz = root / "lied.mscz"
            mscz.write_bytes(b"fake-mscz")
            mvsa = sync.product_mvsa_for_mscz(mscz)
            mvsa.write_text("L: a\n", encoding="utf-8")
            pm.stamp_mvsa_partituur(
                mvsa,
                partituur_hash=pm.partituur_sha256(mscz),
                generated_at="2026-01-01T00:00:00+00:00",
            )
            status = chk.check_one(mvsa)
            self.assertTrue(status.ok)

    def test_stale_and_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mscz = root / "lied.mscz"
            mscz.write_bytes(b"v1")
            mvsa = sync.product_mvsa_for_mscz(mscz)
            mvsa.write_text("L: a\n", encoding="utf-8")
            pm.stamp_mvsa_partituur(
                mvsa,
                partituur_hash="wrong",
                generated_at="2026-01-01T00:00:00+00:00",
            )
            status = chk.check_one(mvsa)
            self.assertFalse(status.ok)
            self.assertEqual(status.issues[0].kind, "stale_mvsa")

            orphan = root / "ghost.mscz.mvsa"
            orphan.write_text("# vsa-partituur-sha256: x\n", encoding="utf-8")
            status2 = chk.check_one(orphan)
            self.assertEqual(status2.issues[0].kind, "missing_mscz")


class SyncResolveTests(unittest.TestCase):
    def test_default_only_existing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mscz_a = root / "a.mscz"
            mscz_b = root / "b.mscz"
            mscz_a.write_bytes(b"a")
            mscz_b.write_bytes(b"b")
            mvsa_a = sync.product_mvsa_for_mscz(mscz_a)
            mvsa_a.write_text("old\n", encoding="utf-8")
            # geen stamp → stale
            with mock.patch.object(sync, "collect_mscz", return_value=[mscz_a, mscz_b]):
                todo = sync._resolve_targets(root, create=False, force=False)
            self.assertEqual(todo, [mscz_a])

    def test_create_includes_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mscz = root / "a.mscz"
            mscz.write_bytes(b"a")
            with mock.patch.object(sync, "collect_mscz", return_value=[mscz]):
                todo = sync._resolve_targets(root, create=True, force=False)
            self.assertEqual(todo, [mscz])


if __name__ == "__main__":
    unittest.main()
