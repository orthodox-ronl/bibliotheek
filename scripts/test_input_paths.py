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
    rel_for_log,
    resolve_user_path,
)


def _fake_repo(tmp_path: Path) -> Path:
    """Mini-repo: content-source/catalogus + koormappen."""
    (tmp_path / "content-source" / "catalogus" / "tweede-antifoon").mkdir(
        parents=True
    )
    (tmp_path / "content-source" / "koormappen" / "hemelum").mkdir(parents=True)
    (tmp_path / "content-source" / "handleiding").mkdir(parents=True)
    (
        tmp_path
        / "content-source"
        / "catalogus"
        / "tweede-antifoon"
        / "lied.vsa"
    ).write_text("@title x\n", encoding="utf-8")
    (
        tmp_path / "content-source" / "koormappen" / "hemelum" / "index.md"
    ).write_text("# k\n", encoding="utf-8")
    (
        tmp_path / "content-source" / "handleiding" / "scripts.md"
    ).write_text("# h\n", encoding="utf-8")
    (tmp_path / "scripts").mkdir()
    return tmp_path


def test_resolve_user_path_as_given_absolute(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _fake_repo(tmp_path)
    monkeypatch.chdir(repo)
    target = repo / "content-source" / "handleiding" / "scripts.md"
    assert resolve_user_path(target, repo_root=repo) == target.resolve()


def test_resolve_user_path_cwd_relative(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _fake_repo(tmp_path)
    monkeypatch.chdir(repo)
    got = resolve_user_path(
        Path("content-source/handleiding/scripts.md"), repo_root=repo
    )
    assert got == (
        repo / "content-source" / "handleiding" / "scripts.md"
    ).resolve()


def test_resolve_user_path_repo_relative_when_cwd_elsewhere(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Relatief pad t.o.v. repo_root als cwd iets anders is."""
    repo = _fake_repo(tmp_path)
    elsewhere = tmp_path / "elders"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)
    got = resolve_user_path(
        Path("content-source/handleiding/scripts.md"), repo_root=repo
    )
    assert got == (
        repo / "content-source" / "handleiding" / "scripts.md"
    ).resolve()


def test_resolve_user_path_under_content_source(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _fake_repo(tmp_path)
    monkeypatch.chdir(repo)
    got = resolve_user_path(
        Path("handleiding/scripts.md"), repo_root=repo
    )
    assert got == (
        repo / "content-source" / "handleiding" / "scripts.md"
    ).resolve()


def test_resolve_user_path_under_catalogus(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _fake_repo(tmp_path)
    monkeypatch.chdir(repo)
    got = resolve_user_path(
        Path("tweede-antifoon/lied.vsa"), repo_root=repo
    )
    assert got == (
        repo
        / "content-source"
        / "catalogus"
        / "tweede-antifoon"
        / "lied.vsa"
    ).resolve()


def test_resolve_user_path_under_koormappen(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _fake_repo(tmp_path)
    monkeypatch.chdir(repo)
    got = resolve_user_path(Path("hemelum"), repo_root=repo)
    assert got == (
        repo / "content-source" / "koormappen" / "hemelum"
    ).resolve()


def test_resolve_user_path_catalogus_before_koormappen(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Zelfde relatieve naam: catalogus wint vóór koormappen."""
    repo = _fake_repo(tmp_path)
    monkeypatch.chdir(repo)
    both = "gedeeld-id"
    (repo / "content-source" / "catalogus" / both).mkdir()
    (repo / "content-source" / "koormappen" / both).mkdir()
    got = resolve_user_path(Path(both), repo_root=repo)
    assert got == (repo / "content-source" / "catalogus" / both).resolve()


def test_resolve_user_path_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _fake_repo(tmp_path)
    monkeypatch.chdir(repo)
    with pytest.raises(InputPathError, match="niet gevonden"):
        resolve_user_path(Path("bestaat-niet"), repo_root=repo)


def test_rel_for_log_under_content_source(tmp_path: Path) -> None:
    repo = _fake_repo(tmp_path)
    p = repo / "content-source" / "catalogus" / "tweede-antifoon" / "lied.vsa"
    assert rel_for_log(p, repo_root=repo) == "catalogus/tweede-antifoon/lied.vsa"


def test_rel_for_log_outside_content_under_repo(tmp_path: Path) -> None:
    repo = _fake_repo(tmp_path)
    p = repo / "scripts" / "x.py"
    p.write_text("#\n", encoding="utf-8")
    assert rel_for_log(p, repo_root=repo) == "scripts/x.py"


def test_rel_for_log_outside_repo(tmp_path: Path) -> None:
    repo = _fake_repo(tmp_path)
    outside = tmp_path.parent / f"{tmp_path.name}-buiten"
    outside.mkdir()
    f = outside / "los.txt"
    f.write_text("x", encoding="utf-8")
    assert rel_for_log(f, repo_root=repo) == f.resolve().as_posix()


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
