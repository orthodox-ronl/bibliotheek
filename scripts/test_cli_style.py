"""Tests voor cli_style (foutuitleg + verbose-gate)."""

from __future__ import annotations

from pathlib import Path

import cli_style as cs


def test_explain_winerror_32() -> None:
    exc = RuntimeError(
        "x.mscz: ERROR: [WinError 32] Het proces heeft geen toegang tot het "
        "bestand omdat het door een ander proces wordt gebruikt: 'x-1.svg'"
    )
    explained = cs.explain_sync_failure(exc)
    assert "WinError 32" in explained.reason or "vergrendeld" in explained.reason.lower()
    assert explained.solution.startswith("Oplossing:")
    assert "MuseScore" in explained.solution or "viewer" in explained.solution.lower()


def test_explain_errno_22() -> None:
    exc = OSError(22, "Invalid argument", r"C:\tmp\lied.vsa.mxl")
    explained = cs.explain_sync_failure(exc)
    assert "22" in explained.reason or "overschrijven" in explained.reason.lower()
    assert explained.solution.startswith("Oplossing:")


def test_detail_silent_by_default(capsys) -> None:
    cs.set_verbose(False)
    cs.detail("geheim")
    assert capsys.readouterr().out == ""


def test_detail_when_verbose(capsys) -> None:
    cs.set_verbose(True)
    try:
        cs.detail("zichtbaar")
        assert "zichtbaar" in capsys.readouterr().out
    finally:
        cs.set_verbose(False)


def test_atomic_write_text(tmp_path: Path) -> None:
    dest = tmp_path / "out.json"
    cs.atomic_write_text(dest, '{"ok": true}\n')
    assert dest.read_text(encoding="utf-8") == '{"ok": true}\n'
    assert not (tmp_path / "out.json.tmp").exists()
    cs.atomic_write_text(dest, '{"ok": false}\n')
    assert dest.read_text(encoding="utf-8") == '{"ok": false}\n'
