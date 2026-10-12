"""Tests voor bieb multi-command (o.a. Engelse aliassen)."""

from __future__ import annotations

import bieb


def test_resolve_subcommand_nl() -> None:
    assert bieb.resolve_subcommand("accepteer") == "accepteer"
    assert bieb.resolve_subcommand("hernoem") == "hernoem"
    assert bieb.resolve_subcommand("verwijder") == "verwijder"
    assert bieb.resolve_subcommand("kopieer") == "kopieer"


def test_resolve_subcommand_en_aliases() -> None:
    assert bieb.resolve_subcommand("accept") == "accepteer"
    assert bieb.resolve_subcommand("rename") == "hernoem"
    assert bieb.resolve_subcommand("delete") == "verwijder"
    assert bieb.resolve_subcommand("copy") == "kopieer"
    assert bieb.resolve_subcommand("Rename") == "hernoem"


def test_resolve_subcommand_unknown() -> None:
    assert bieb.resolve_subcommand("foo") is None


def test_main_routes_alias_to_handler(monkeypatch) -> None:
    seen: list[list[str]] = []

    def fake_hernoem(argv: list[str]) -> int:
        seen.append(argv)
        return 0

    monkeypatch.setitem(bieb._COMMANDS, "hernoem", fake_hernoem)
    assert bieb.main(["rename", "a/b/c", "d", "--dry-run"]) == 0
    assert seen == [["a/b/c", "d", "--dry-run"]]
