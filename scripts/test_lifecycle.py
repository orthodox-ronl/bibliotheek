"""Tests voor lifecycle_grenzen en werkbank_status (dunne helpers)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import lifecycle_grenzen as grenzen
import werkbank_status as wb


class LifecycleGrenzenTests(unittest.TestCase):
    def test_clean_tree_ok(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            leaf = root / "a" / "b" / "c"
            leaf.mkdir(parents=True)
            (leaf / "a-b-c.mscz").write_bytes(b"x")
            (leaf / "a-b-c.mscz.mxl").write_bytes(b"y")
            self.assertEqual(grenzen.collect_issues(root), [])

    def test_spaces_and_raw(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            leaf = root / "a" / "b" / "c"
            leaf.mkdir(parents=True)
            (leaf / "bad name.mscz").write_bytes(b"x")
            (leaf / "dump.capx").write_bytes(b"y")
            (leaf / "ruw.mxl").write_bytes(b"z")
            issues = grenzen.collect_issues(root)
            self.assertEqual(len(issues), 3)


class WerkbankStatusTests(unittest.TestCase):
    def test_collect_runs(self) -> None:
        report = wb.collect()
        self.assertIsInstance(report.open_inputs, list)
        self.assertIsInstance(report.stubs, list)


if __name__ == "__main__":
    unittest.main()
