"""Unit tests for check_fixlist + fix dry-run (geen MuseScore/Hugo)."""

from __future__ import annotations

import json
from pathlib import Path

import fix as fix_mod
from check_fixlist import (
    FixItem,
    collect_items,
    load_fixlist,
    save_fixlist,
    write_fixlist,
)


def _write_pdf_status(data_dir: Path, *, stale: bool) -> None:
    folders = {
        "catalogus/x/ok": {
            "source": "content-source/catalogus/x/ok/index.md",
            "ok": True,
            "fix_cmd": r"scripts\pdf.cmd content-source\catalogus\x\ok\index.md",
            "issues": [],
        },
    }
    if stale:
        folders["catalogus/x/stale"] = {
            "source": "content-source/catalogus/x/stale/index.md",
            "ok": False,
            "fix_cmd": (
                r"scripts\pdf.cmd content-source\catalogus\x\stale\index.md"
            ),
            "issues": [
                {
                    "kind": "stale_pdf",
                    "file": "content-source/catalogus/x/stale/index.md.pdf",
                    "detail": "ouder dan bron",
                }
            ],
        }
    (data_dir / "pdf-status.json").write_text(
        json.dumps({"folders": folders}, indent=2) + "\n",
        encoding="utf-8",
    )


def test_collect_only_not_ok(tmp_path: Path):
    data = tmp_path / "data"
    data.mkdir()
    _write_pdf_status(data, stale=True)
    items = collect_items(data)
    assert len(items) == 1
    assert items[0].checker == "pdf"
    assert items[0].kind == "stale_pdf"
    assert "pdf.cmd" in items[0].fix_cmd


def test_write_and_load_roundtrip(tmp_path: Path):
    data = tmp_path / "data"
    data.mkdir()
    _write_pdf_status(data, stale=True)
    out = tmp_path / "check-fixlist.json"
    items = write_fixlist(path=out, data_dir=data)
    assert len(items) == 1
    loaded = load_fixlist(out)
    assert loaded[0].id == items[0].id
    assert loaded[0].fix_cmd == items[0].fix_cmd


def test_save_removes_item(tmp_path: Path):
    path = tmp_path / "check-fixlist.json"
    items = [
        FixItem(
            id="pdf:a",
            checker="pdf",
            summary="a",
            fix_cmd=r"scripts\pdf.cmd a\index.md",
        ),
        FixItem(
            id="pdf:b",
            checker="pdf",
            summary="b",
            fix_cmd=r"scripts\pdf.cmd b\index.md",
        ),
    ]
    save_fixlist(items, path=path)
    save_fixlist(items[1:], path=path)
    left = load_fixlist(path)
    assert [x.id for x in left] == ["pdf:b"]


def test_fix_dry_run_prints(tmp_path: Path, monkeypatch, capsys):
    path = tmp_path / "check-fixlist.json"
    save_fixlist(
        [
            FixItem(
                id="pdf:a",
                checker="pdf",
                summary="[stale_pdf] x",
                fix_cmd=r"scripts\pdf.cmd x\index.md",
            )
        ],
        path=path,
    )
    monkeypatch.setattr(fix_mod, "FIXLIST_PATH", path)
    monkeypatch.setattr(
        "check_fixlist.FIXLIST_PATH",
        path,
    )
    # load_fixlist uses FIXLIST_PATH from check_fixlist at call time
    monkeypatch.setattr(fix_mod, "load_fixlist", lambda: load_fixlist(path))
    code = fix_mod.main(["--dry-run"])
    assert code == 0
    out = capsys.readouterr().out
    assert "pdf.cmd" in out
    assert "dry-run" in out.lower()


def test_fix_check_dry_run_refreshes(tmp_path: Path, monkeypatch, capsys):
    data = tmp_path / "data"
    data.mkdir()
    _write_pdf_status(data, stale=True)
    out = tmp_path / "check-fixlist.json"

    times = {"n": 0}

    def fake_mtime() -> float:
        times["n"] += 1
        # vóór check: 1.0; ná check: 2.0 (verse lijst)
        return 1.0 if times["n"] == 1 else 2.0

    monkeypatch.setattr(fix_mod, "_run_check_strict", lambda **_k: 1)
    monkeypatch.setattr(fix_mod, "_fixlist_mtime", fake_mtime)
    monkeypatch.setattr(
        fix_mod,
        "_refresh_fixlist_from_status",
        lambda: write_fixlist(path=out, data_dir=data),
    )
    monkeypatch.setattr(fix_mod, "load_fixlist", lambda: load_fixlist(out))

    code = fix_mod.main(["--check", "--dry-run"])
    assert code == 0
    assert out.is_file()
    assert len(load_fixlist(out)) == 1
    assert "stale_pdf" in capsys.readouterr().out


def test_fix_check_hard_fail_exit2(monkeypatch):
    monkeypatch.setattr(fix_mod, "_run_check_strict", lambda **_k: 2)
    monkeypatch.setattr(fix_mod, "_fixlist_mtime", lambda: 1.0)
    assert fix_mod.main(["--check", "--dry-run"]) == 2


def test_fix_check_hard_fail_stale_list(monkeypatch):
    """Exit 1 maar fixlist niet vernieuwd (bijv. validate-stop) → stop."""
    monkeypatch.setattr(fix_mod, "_run_check_strict", lambda **_k: 1)
    monkeypatch.setattr(fix_mod, "_fixlist_mtime", lambda: 10.0)
    assert fix_mod.main(["--check", "--dry-run"]) == 2


def test_fix_run_removes_success(tmp_path: Path, monkeypatch):
    path = tmp_path / "check-fixlist.json"
    save_fixlist(
        [
            FixItem(
                id="pdf:a",
                checker="pdf",
                summary="a",
                fix_cmd=r"scripts\pdf.cmd a\index.md",
            ),
            FixItem(
                id="pdf:b",
                checker="pdf",
                summary="b",
                fix_cmd=r"scripts\pdf.cmd b\index.md",
            ),
        ],
        path=path,
    )
    monkeypatch.setattr(fix_mod, "load_fixlist", lambda: load_fixlist(path))
    monkeypatch.setattr(
        fix_mod,
        "save_fixlist",
        lambda items: save_fixlist(items, path=path),
    )
    monkeypatch.setattr(fix_mod, "_run_fix_cmd", lambda *_a, **_k: 0)
    monkeypatch.setattr(
        fix_mod,
        "confirm_batch",
        lambda *_a, **_k: True,
    )
    assert fix_mod.main(["-y"]) == 0
    assert load_fixlist(path) == []
