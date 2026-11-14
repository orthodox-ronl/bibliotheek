"""Unit tests voor commit_sources (geen echte git-commit)."""

from __future__ import annotations

from commit_sources import (
    build_parser,
    in_scope,
    is_commit_source,
    is_product_artifact,
    select_all_non_artifacts,
    select_sources,
    source_kinds,
)


def test_in_scope():
    assert in_scope("content-source/catalogus/x/a.vsa")
    assert in_scope("content-source/koormappen/p/index.md")
    assert not in_scope("content-source/handleiding/x.md")
    assert not in_scope("content-source/input/x.vsa")


def test_source_kinds_canonical():
    assert source_kinds("lied.vsa") == frozenset({"vsa"})
    assert source_kinds("lied.syl.vsa") == frozenset({"vsa"})
    assert source_kinds("lied.mvsa") == frozenset({"mvsa"})
    assert source_kinds("lied.mscz") == frozenset({"mscz"})
    assert source_kinds("lied.print.mscz") == frozenset({"mscz"})
    assert source_kinds("index.md") == frozenset({"md"})
    assert source_kinds("lied.tekstblad.md") == frozenset({"tekstblad", "md"})


def test_source_kinds_reject_derived():
    assert source_kinds("lied.vsa.svg") is None
    assert source_kinds("lied.vsa.mvsa") is None
    assert source_kinds("lied.mvsa.mxl") is None
    assert source_kinds("lied.mscz.mvsa") is None
    assert source_kinds("lied.vsa.mscz") is None
    assert source_kinds("lied.mvsa.mscz") is None
    assert source_kinds("lied.mvsa.mp3") is None
    assert source_kinds("lied.vsa.lyrics.txt") is None
    assert source_kinds("lied.mvsa.score-ir.json") is None
    assert source_kinds("lied.mvsa.from-ir.musicxml") is None
    assert source_kinds("lied.mscz-1.svg") is None
    assert source_kinds("lied.tekstblad.pdf") is None


def test_is_commit_source_scope():
    assert is_commit_source("content-source/catalogus/z/lied.vsa") == frozenset(
        {"vsa"}
    )
    assert is_commit_source("content-source/handleiding/z.md") is None
    assert is_commit_source("content-source/catalogus/z/lied.vsa.svg") is None


def test_select_sources_default_and_flags():
    rels = [
        "content-source/catalogus/z/lied.vsa",
        "content-source/catalogus/z/lied.vsa.svg",
        "content-source/catalogus/z/lied.mvsa",
        "content-source/catalogus/z/lied.mscz",
        "content-source/koormappen/p/index.md",
        "content-source/catalogus/z/lied.tekstblad.md",
        "content-source/handleiding/x.md",
    ]
    all_src = select_sources(rels, wanted=None)
    assert all_src == [
        "content-source/catalogus/z/lied.vsa",
        "content-source/catalogus/z/lied.mvsa",
        "content-source/catalogus/z/lied.mscz",
        "content-source/koormappen/p/index.md",
        "content-source/catalogus/z/lied.tekstblad.md",
    ]
    only_vsa = select_sources(rels, wanted=frozenset({"vsa"}))
    assert only_vsa == ["content-source/catalogus/z/lied.vsa"]
    mscz_mvsa = select_sources(rels, wanted=frozenset({"mscz", "mvsa"}))
    assert mscz_mvsa == [
        "content-source/catalogus/z/lied.mvsa",
        "content-source/catalogus/z/lied.mscz",
    ]
    only_md = select_sources(rels, wanted=frozenset({"md"}))
    assert only_md == [
        "content-source/koormappen/p/index.md",
        "content-source/catalogus/z/lied.tekstblad.md",
    ]
    only_tekstblad = select_sources(rels, wanted=frozenset({"tekstblad"}))
    assert only_tekstblad == ["content-source/catalogus/z/lied.tekstblad.md"]


def test_stage_parser_has_no_message():
    stage_p = build_parser(mode="stage")
    commit_p = build_parser(mode="commit")
    stage_opts = {a.dest for a in stage_p._actions}
    commit_opts = {a.dest for a in commit_p._actions}
    assert "message" not in stage_opts
    assert "message" in commit_opts
    assert {"vsa", "mvsa", "mscz", "md", "tekstblad", "dry_run", "all"} <= stage_opts


def test_product_artifact_notation_and_json():
    assert is_product_artifact("content-source/catalogus/z/lied.vsa.svg")
    assert is_product_artifact("content-source/catalogus/z/lied.mvsa.mxl")
    assert is_product_artifact("content-source/catalogus/z/lied.vsa.mvsa")
    assert is_product_artifact("content-source/catalogus/z/lied.mscz.mvsa")
    assert is_product_artifact(
        "content-source/catalogus/z/lied.mvsa.products-meta.json"
    )
    assert is_product_artifact("content-source/catalogus/z/lied.mscz-1.svg")
    assert is_product_artifact("data/vsa-product-status.json")
    assert is_product_artifact("data/check-fixlist.json")
    assert is_product_artifact("data/pdf-r2-development.json")
    assert is_product_artifact("static/zoek/index.json")
    assert not is_product_artifact("content-source/catalogus/z/lied.vsa")
    assert not is_product_artifact("content-source/catalogus/z/index.md")
    assert not is_product_artifact("scripts/commit_sources.py")
    assert not is_product_artifact("layouts/_default/baseof.html")
    assert not is_product_artifact("data/bronnen.yaml")
    assert not is_product_artifact("data/zoek-synoniemen.yaml")
    assert not is_product_artifact("data/uitvoeringsvorm-link-titles.yaml")


def test_select_all_non_artifacts():
    rels = [
        "scripts/foo.py",
        "layouts/_default/baseof.html",
        "content-source/catalogus/z/lied.vsa",
        "content-source/catalogus/z/lied.vsa.svg",
        "data/check-fixlist.json",
        "data/bronnen.yaml",
        "static/zoek/index.json",
        "content-source/handleiding/x.md",
    ]
    assert select_all_non_artifacts(rels) == [
        "scripts/foo.py",
        "layouts/_default/baseof.html",
        "content-source/catalogus/z/lied.vsa",
        "data/bronnen.yaml",
        "content-source/handleiding/x.md",
    ]
