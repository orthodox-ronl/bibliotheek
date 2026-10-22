"""Unit tests voor scripts/input_paths.py (bestand-of-map)."""

from __future__ import annotations

from pathlib import Path

import pytest

from input_paths import (
    InputPathError,
    collect_cli_sources,
    collect_input_files,
    normalize_suffixes,
    reject_multi_with_output,
)


def test_normalize_suffixes() -> None:
    assert normalize_suffixes([".mvsa", "MSCZ"]) == frozenset({".mvsa", ".mscz"})
    assert normalize_suffixes(["tekstblad.md"]) == frozenset({".tekstblad.md"})
    with pytest.raises(InputPathError, match="extensie"):
        normalize_suffixes([])


def test_collect_single_file(tmp_path: Path) -> None:
    f = tmp_path / "lied.mvsa"
    f.write_text("@title x\n", encoding="utf-8")
    assert collect_input_files(f, suffixes=[".mvsa"]) == [f]


def test_collect_compound_suffix(tmp_path: Path) -> None:
    f = tmp_path / "x.tekstblad.md"
    f.write_text("---\n", encoding="utf-8")
    other = tmp_path / "readme.md"
    other.write_text("# x\n", encoding="utf-8")
    assert collect_input_files(tmp_path, suffixes=[".tekstblad.md"]) == [f]


def test_collect_file_wrong_suffix(tmp_path: Path) -> None:
    f = tmp_path / "lied.txt"
    f.write_text("x", encoding="utf-8")
    with pytest.raises(InputPathError, match="Verwacht"):
        collect_input_files(f, suffixes=[".mvsa"])


def test_collect_missing_path(tmp_path: Path) -> None:
    with pytest.raises(InputPathError, match="niet gevonden"):
        collect_input_files(tmp_path / "geen", suffixes=[".mvsa"])


def test_collect_directory_recursive(tmp_path: Path) -> None:
    a = tmp_path / "a.mvsa"
    b = tmp_path / "sub" / "b.mvsa"
    skip = tmp_path / "sub" / "c.mscz"
    b.parent.mkdir()
    a.write_text("a", encoding="utf-8")
    b.write_text("b", encoding="utf-8")
    skip.write_text("c", encoding="utf-8")
    got = collect_input_files(tmp_path, suffixes=[".mvsa", ".mscz"])
    assert got == [a, b, skip]


def test_collect_directory_non_recursive(tmp_path: Path) -> None:
    top = tmp_path / "top.mvsa"
    nested = tmp_path / "sub" / "nested.mvsa"
    nested.parent.mkdir()
    top.write_text("t", encoding="utf-8")
    nested.write_text("n", encoding="utf-8")
    assert collect_input_files(
        tmp_path, suffixes=[".mvsa"], recursive=False
    ) == [top]


def test_collect_names_filter(tmp_path: Path) -> None:
    idx = tmp_path / "slot" / "index.md"
    other = tmp_path / "slot" / "notes.md"
    idx.parent.mkdir()
    idx.write_text("# a\n", encoding="utf-8")
    other.write_text("# b\n", encoding="utf-8")
    assert collect_input_files(
        tmp_path, suffixes=[".md"], names=["index.md"]
    ) == [idx]


def test_collect_directory_empty_ok(tmp_path: Path) -> None:
    assert collect_input_files(tmp_path, suffixes=[".mvsa"]) == []


def test_collect_cli_sources_empty_dir_raises(tmp_path: Path) -> None:
    with pytest.raises(InputPathError, match="Geen passende"):
        collect_cli_sources(tmp_path, suffixes=[".mvsa"])


def test_collect_cli_sources_finds_files(tmp_path: Path) -> None:
    a = tmp_path / "a.mvsa"
    a.write_text("@title t\n", encoding="utf-8")
    assert collect_cli_sources(tmp_path, suffixes=[".mvsa"]) == [a]


def test_reject_multi_with_output(tmp_path: Path) -> None:
    a = tmp_path / "a.mscz"
    b = tmp_path / "b.mscz"
    a.write_text("a", encoding="utf-8")
    b.write_text("b", encoding="utf-8")
    reject_multi_with_output([a], tmp_path / "out.mscz")  # ok
    with pytest.raises(InputPathError, match="één bronbestand"):
        reject_multi_with_output([a, b], tmp_path / "out.mscz")
    reject_multi_with_output([a, b], None)  # ok zonder -o
