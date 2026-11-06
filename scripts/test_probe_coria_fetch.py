"""Unit tests for probe_coria_fetch HTML classification and sampling."""

from __future__ import annotations

import json
from pathlib import Path

import probe_coria_fetch as probe


def test_classify_coria_html_fail():
    html = "<html><body>Fout: failed to retrieve file</body></html>"
    assert probe.classify_coria_html(html) == "fail"


def test_classify_coria_html_ok_partijkeuze():
    html = (
        "<html><title>Coria - Untitled score</title>"
        "<body>Kies de partij die je wilt oefenen!"
        '<input type="radio" value="P1">Soprano</body></html>'
    )
    assert probe.classify_coria_html(html) == "ok"


def test_classify_coria_html_translation_failed():
    assert probe.classify_coria_html("translation failed") == "fail"


def test_classify_coria_html_unknown():
    assert probe.classify_coria_html("<html><body>hello</body></html>") == "unknown"


def test_coria_play_url_encodes():
    url = probe.coria_play_url(
        "https://example.test/mxl/c/abc.musicxml"
    )
    assert url.startswith("https://coria.nl/play_from_url?")
    assert "url=" in url
    assert "abc.musicxml" in url


def test_source_kind():
    assert (
        probe.source_kind(
            "mxl__catalogus__x__y.mscz.mxl"
        )
        == "mscz"
    )
    assert probe.source_kind("mxl__a__b.mvsa.mxl") == "mvsa"
    assert probe.source_kind("mxl__a__b.vsa.mxl") == "vsa"
    assert probe.source_kind("mxl__legacy.musicxml") == "other"


def test_candidate_bases_pages_only():
    bases = probe.candidate_bases("development")
    assert list(bases.keys()) == ["pages"]
    assert "raw.githubusercontent" not in bases["pages"]
    assert bases["pages"].startswith(
        "https://orthodox-ronl.github.io/bibliotheek/preview/"
    )


def test_select_sample_canaries_prefers_kinds():
    mapping = {
        "mxl__z__late.mvsa.mxl": "mxl/c/mvsa2.musicxml",
        "mxl__a__early.mscz.mxl": "mxl/c/mscz1.musicxml",
        "mxl__b__mid.mvsa.mxl": "mxl/c/mvsa1.musicxml",
        "mxl__c__v.vsa.mxl": "mxl/c/vsa1.musicxml",
        "mxl__d__also.mscz.mxl": "mxl/c/mscz2.musicxml",
    }
    published = {
        "mxl/c/mscz1.musicxml",
        "mxl/c/mscz2.musicxml",
        "mxl/c/mvsa1.musicxml",
        "mxl/c/mvsa2.musicxml",
        "mxl/c/vsa1.musicxml",
    }
    samples = probe.select_sample_canaries(
        mapping, published=published, per_kind=1
    )
    assert samples[0] == "mxl/c/mscz1.musicxml"
    assert "mxl/c/mvsa1.musicxml" in samples
    assert "mxl/c/vsa1.musicxml" in samples
    assert "mxl/c/mscz2.musicxml" not in samples


def test_host_ok_from_sample_results():
    assert probe.host_ok_from_sample_results(["ok", "ok"]) is True
    assert probe.host_ok_from_sample_results(["ok", "fail"]) is False
    assert probe.host_ok_from_sample_results([]) is False


def test_score_hosts_single_host_counts_all_samples():
    samples = ["mxl/c/good.musicxml", "mxl/c/bad.musicxml"]
    sample_results = {
        "pages": {"mxl/c/good.musicxml": "ok", "mxl/c/bad.musicxml": "fail"},
    }
    assert probe.score_hosts(sample_results, samples, ("pages",)) == {
        "pages": "fail",
    }


def test_score_hosts_multi_ignores_universally_broken():
    samples = ["mxl/c/good.musicxml", "mxl/c/bad.musicxml"]
    sample_results = {
        "raw": {"mxl/c/good.musicxml": "fail", "mxl/c/bad.musicxml": "fail"},
        "pages": {"mxl/c/good.musicxml": "ok", "mxl/c/bad.musicxml": "fail"},
    }
    assert probe.score_hosts(sample_results, samples, ("raw", "pages")) == {
        "raw": "fail",
        "pages": "ok",
    }


def test_kind_sample_limit_boosts_mscz():
    assert probe.kind_sample_limit("mscz", 1) == probe.MSCZ_SAMPLES
    assert probe.kind_sample_limit("mvsa", 1) == 1


def test_apply_probe_skip_network(tmp_path: Path, monkeypatch):
    cfg_path = tmp_path / "coria-public-base.json"
    monkeypatch.setattr(probe, "PUBLIC_BASE_FILE", cfg_path)
    code = probe.apply_probe(branch="development", skip_network=True)
    assert code == 0
    data = json.loads(cfg_path.read_text(encoding="utf-8"))
    assert data["base"].startswith(
        "https://orthodox-ronl.github.io/bibliotheek/preview/"
    )
    assert data["alternate"] == ""
    assert "raw" not in data["results"]
    assert data["results"]["pages"] == "skipped"
    assert data["canaries"] == []


def test_provisional_main_branch():
    cfg = probe.provisional_config("main")
    assert cfg["base"] == "https://orthodox-ronl.github.io/bibliotheek/"
    assert cfg["alternate"] == ""
