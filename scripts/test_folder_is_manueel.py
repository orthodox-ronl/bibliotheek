"""folder_is_handmatig leest manueel / manual."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from sync_vsa_products import folder_is_handmatig


class FolderIsManueelTests(unittest.TestCase):
    def test_manueel_and_manual(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "index.md").write_text(
                "---\nmanueel: true\n---\n", encoding="utf-8"
            )
            self.assertTrue(folder_is_handmatig(root))
            (root / "index.md").write_text(
                "---\nmanual: true\n---\n", encoding="utf-8"
            )
            self.assertTrue(folder_is_handmatig(root))
            (root / "index.md").write_text(
                "---\npublicatiestatus: oefenbaar\n---\n", encoding="utf-8"
            )
            self.assertFalse(folder_is_handmatig(root))
            (root / "index.md").write_text(
                "---\nartefacten_handmatig: true\n---\n", encoding="utf-8"
            )
            self.assertFalse(folder_is_handmatig(root))


if __name__ == "__main__":
    unittest.main()
