"""Tests voor bieb_fs (nette I/O-fouten, CLI-vangnet)."""

from __future__ import annotations

from pathlib import Path

import bieb
import bieb_fs
import pytest


def test_format_locus_with_col_and_snippet() -> None:
    assert (
        bieb_fs.format_locus("a/b.md", 3, col=7, snippet='title: "x"')
        == 'a/b.md:3:7: title: "x"'
    )
    assert bieb_fs.format_locus("a.md", 1) == "a.md:1"
    assert bieb_fs.needle_column('id="foo/bar"', "foo/bar") == 5


def test_print_fail_includes_oplossing(capsys) -> None:
    bieb_fs.print_fail("doelmap bestaat al: x", oplossing="kies een ander id.")
    out = capsys.readouterr().out
    assert "FAIL: doelmap bestaat al: x" in out
    assert "Oplossing: kies een ander id." in out


def test_die_os_permission_has_oplossing() -> None:
    with pytest.raises(SystemExit) as ei:
        bieb_fs.die_os(
            "kopiëren",
            Path("a.vsa"),
            Path("b.vsa"),
            exc=PermissionError(32, "locked"),
        )
    msg = str(ei.value)
    assert "Kon niet kopiëren" in msg
    assert "Oplossing:" in msg
    assert "vergrendeld" in msg


def test_run_handler_systemexit_string_no_raise(capsys) -> None:
    def boom(_argv: list[str]) -> int:
        raise SystemExit("Kon niet kopiëren: x → y\nOplossing: sluit het programma.")

    code = bieb_fs.run_handler(boom, [], command="accepteer")
    assert code == 1
    err = capsys.readouterr().err
    assert "Kon niet kopiëren" in err
    assert "Oplossing:" in err


def test_run_handler_unexpected_oserror(capsys) -> None:
    def boom(_argv: list[str]) -> int:
        raise PermissionError(32, "locked", "file.vsa")

    code = bieb_fs.run_handler(boom, [], command="accepteer")
    assert code == 1
    err = capsys.readouterr().err
    assert "bieb accepteer:" in err
    assert "Oplossing:" in err
    assert "Traceback" not in err


def test_main_routes_oserror_through_net(monkeypatch, capsys) -> None:
    def boom(_argv: list[str]) -> int:
        raise OSError(13, "Access denied", "locked.vsa")

    monkeypatch.setitem(bieb._COMMANDS, "accepteer", boom)
    assert bieb.main(["accept", "x"]) == 1
    err = capsys.readouterr().err
    assert "bestandfout" in err or "Oplossing:" in err
    assert "Traceback" not in err


def test_copy2_permission_becomes_systemexit(tmp_path: Path, monkeypatch) -> None:
    src = tmp_path / "src.vsa"
    dest = tmp_path / "dest.vsa"
    src.write_text("x", encoding="utf-8")

    def fail_copy(*_a, **_k):
        raise PermissionError(32, "locked")

    monkeypatch.setattr(bieb_fs.shutil, "copy2", fail_copy)
    monkeypatch.setattr(bieb_fs.time, "sleep", lambda _s: None)
    with pytest.raises(SystemExit) as ei:
        bieb_fs.copy2(src, dest)
    assert "Oplossing:" in str(ei.value)
