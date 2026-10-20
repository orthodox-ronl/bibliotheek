"""products / sync_*: verkeerd brontype = overslaan, geen exit 1."""

from __future__ import annotations

from pathlib import Path

import sync_import_mvsa as imp
import sync_mscz_products as mscz


def test_mscz_skips_mvsa_file(tmp_path: Path, monkeypatch) -> None:
    mvsa = tmp_path / "lied.mvsa"
    mvsa.write_text("L: a\n", encoding="utf-8")
    monkeypatch.setattr(mscz, "REPO_ROOT", tmp_path)
    assert mscz.main([str(mvsa)]) == 0


def test_import_skips_mvsa_file(tmp_path: Path, monkeypatch) -> None:
    mvsa = tmp_path / "lied.mvsa"
    mvsa.write_text("L: a\n", encoding="utf-8")
    monkeypatch.setattr(imp, "REPO_ROOT", tmp_path)
    assert imp.main([str(mvsa)]) == 0


def test_import_skips_print_mscz(tmp_path: Path, monkeypatch) -> None:
    print_mscz = tmp_path / "lied.print.mscz"
    print_mscz.write_bytes(b"PK")
    monkeypatch.setattr(imp, "REPO_ROOT", tmp_path)
    assert imp.main([str(print_mscz)]) == 0
