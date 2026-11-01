"""Unit tests for products_changed classification (geen MuseScore)."""

from __future__ import annotations

from pathlib import Path

import pytest

from cli_style import run_quiet
from products_changed import (
    build_plan,
    is_koormap_index,
    kinds_for_source,
    print_plan,
    resolve_base_ref,
)


def test_kinds_mvsa():
    assert kinds_for_source("content-source/catalogus/x/a.mvsa") == (
        "mvsa",
        "audio",
        "lyrics",
    )


def test_kinds_vsa():
    assert kinds_for_source("content-source/catalogus/x/a.vsa") == (
        "vsa",
        "audio",
        "lyrics",
    )


def test_kinds_mscz():
    assert kinds_for_source("content-source/catalogus/x/a.mscz") == (
        "mscz",
        "audio",
        "lyrics",
    )


def test_kinds_skip_derived_mscz():
    assert kinds_for_source("content-source/catalogus/x/a.mvsa.mscz") is None
    assert kinds_for_source("content-source/catalogus/x/a.vsa.mscz") is None
    assert kinds_for_source("content-source/catalogus/x/a.print.mscz") is None


def test_kinds_import_mscz_mvsa():
    assert kinds_for_source("content-source/catalogus/x/a.mscz.mvsa") == ("import",)


def test_kinds_tekstblad():
    assert kinds_for_source("content-source/catalogus/x/a.tekstblad.md") == (
        "tekstblad",
    )


def test_kinds_product_artifacts_ignored():
    assert kinds_for_source("content-source/catalogus/x/a.mvsa.mxl") is None
    assert kinds_for_source("content-source/catalogus/x/a.lyrics.txt") is None
    assert kinds_for_source("content-source/catalogus/x/index.md") is None


def test_koormap_index():
    assert is_koormap_index("content-source/koormappen/groningen/liturgie/index.md")
    assert not is_koormap_index("content-source/catalogus/x/index.md")
    assert not is_koormap_index("content-source/koormappen/groningen/readme.md")


def test_build_plan_mix(tmp_path: Path):
    rels = [
        "content-source/catalogus/z/lied.mvsa",
        "content-source/catalogus/z/lied.mvsa.mxl",
        "content-source/koormappen/p/a/index.md",
        "content-source/handleiding/x.md",
    ]
    plan = build_plan(rels, repo=tmp_path)
    assert len(plan.products) == 1
    assert plan.products[0].kinds == ("mvsa", "audio", "lyrics")
    assert len(plan.pdfs) == 1
    assert plan.pdfs[0].name == "index.md"
    assert "content-source/catalogus/z/lied.mvsa.mxl" in plan.ignored
    assert "content-source/handleiding/x.md" in plan.ignored


def test_resolve_base_head(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        "products_changed._git_ok",
        lambda _repo, *args: False,
    )
    assert resolve_base_ref(tmp_path, "HEAD") == "HEAD"
    assert resolve_base_ref(tmp_path, "head") == "HEAD"


def test_resolve_base_falls_back_to_origin(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    seen: list[str] = []

    def fake_ok(_repo, *args: str) -> bool:
        # rev-parse --verify --quiet REF^{commit}
        ref = args[-1].removesuffix("^{commit}")
        seen.append(ref)
        return ref == "origin/main"

    monkeypatch.setattr("products_changed._git_ok", fake_ok)
    assert resolve_base_ref(tmp_path, "main") == "origin/main"
    assert "main" in seen
    assert "origin/main" in seen


def test_resolve_base_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("products_changed._git_ok", lambda *_a, **_k: False)
    with pytest.raises(SystemExit, match="niet gevonden"):
        resolve_base_ref(tmp_path, "geen-tak")


def test_print_plan_dry_run_only_actions(capsys: pytest.CaptureFixture[str]):
    plan = build_plan(
        [
            "content-source/catalogus/z/lied.mvsa",
            "content-source/catalogus/z/lied.mvsa.mxl",
            "content-source/koormappen/p/a/index.md",
            "content-source/handleiding/x.md",
        ],
        repo=Path("."),
    )
    print_plan(plan, dry_run=True, base="HEAD", scanned=4)
    out = capsys.readouterr().out
    assert "Gaat doen:" in out
    assert "lied.mvsa" in out
    assert "--kinds mvsa,audio,lyrics" in out
    assert "index.md" in out
    assert "Bekeken: 4 git-pad(en)" in out
    assert "2 met actie, 2 zonder" in out
    # Geen rommel-lijst van overgeslagen paden zonder --verbose
    assert "lied.mvsa.mxl" not in out
    assert "handleiding/x.md" not in out


def test_print_plan_empty_is_short(capsys: pytest.CaptureFixture[str]):
    plan = build_plan(
        [
            "content-source/catalogus/z/lied.mvsa.mxl",
            "content-source/handleiding/x.md",
        ],
        repo=Path("."),
    )
    print_plan(plan, dry_run=True, base="HEAD", scanned=2)
    out = capsys.readouterr().out
    assert "Niets te doen." in out
    assert "Bekeken: 2 git-pad(en)" in out
    assert "Tip:" not in out  # tip alleen bij --verbose


def test_run_quiet_on_success(capsys: pytest.CaptureFixture[str]):
    def noisy(_argv: list[str]) -> int:
        print("interne rommel")
        return 0

    assert run_quiet("demo", noisy, [], verbose=False) == 0
    assert capsys.readouterr().out == ""


def test_run_quiet_shows_log_on_failure(capsys: pytest.CaptureFixture[str]):
    def noisy(_argv: list[str]) -> int:
        print("waarom het misging")
        return 1

    assert run_quiet("demo", noisy, [], verbose=False) == 1
    err = capsys.readouterr().err
    assert "FAILED demo" in err
    assert "waarom het misging" in err
