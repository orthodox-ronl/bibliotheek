"""Unit tests for pad-specifieke fix_cmd helpers."""

from __future__ import annotations

from pathlib import Path

from fix_cmds import (
    REPO_ROOT,
    coria_source_for_mxl,
    import_mvsa_fix_cmd,
    is_products_fix_cmd,
    products_fix_cmd,
    products_only_invalid_fix_cmd,
    win_repo_rel,
)


def test_win_repo_rel():
    path = REPO_ROOT / "content-source" / "catalogus" / "x" / "y.mvsa"
    assert win_repo_rel(path) == r"catalogus\x\y.mvsa"


def test_products_fix_cmd_scoped():
    source = REPO_ROOT / "content-source" / "catalogus" / "a" / "b.mvsa"
    cmd = products_fix_cmd("mvsa", source)
    assert cmd.startswith(r"scripts\products.cmd --kinds mvsa")
    assert "--reasons missing,stale" in cmd
    assert "--skip-post" in cmd
    assert cmd.endswith(r"catalogus\a\b.mvsa")
    assert "content-source" not in cmd


def test_products_only_invalid_picks_kind():
    mvsa = REPO_ROOT / "content-source" / "catalogus" / "x.mvsa"
    cmd = products_only_invalid_fix_cmd(mvsa)
    assert "--kinds mvsa" in cmd
    assert "--only-invalid" in cmd
    assert cmd.endswith(r"catalogus\x.mvsa")


def test_coria_source_for_mxl():
    mxl = Path(r"C:\tmp\lied.mvsa.mxl")
    src = coria_source_for_mxl(mxl)
    assert src is not None
    assert src.name == "lied.mvsa"


def test_import_mvsa_fix_cmd():
    mscz = REPO_ROOT / "content-source" / "catalogus" / "a" / "a.mscz"
    cmd = import_mvsa_fix_cmd(mscz)
    assert cmd == rf"scripts\import-mvsa.cmd catalogus\a\a.mscz"


def test_is_products_fix_cmd():
    assert is_products_fix_cmd(
        r"scripts\products.cmd --kinds mvsa --skip-post x.mvsa"
    )
    assert not is_products_fix_cmd(r"scripts\pdf.cmd catalogus\a\index.md")
