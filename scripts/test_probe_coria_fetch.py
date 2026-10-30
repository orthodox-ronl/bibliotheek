"""Unit tests for probe_coria_fetch HTML classification and config write."""

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


def test_apply_probe_skip_network(tmp_path: Path, monkeypatch):
    cfg_path = tmp_path / "coria-public-base.json"
    monkeypatch.setattr(probe, "PUBLIC_BASE_FILE", cfg_path)
    # Avoid git in detect when branch given
    code = probe.apply_probe(branch="development", skip_network=True)
    assert code == 0
    data = json.loads(cfg_path.read_text(encoding="utf-8"))
    assert data["base"].startswith(
        "https://raw.githubusercontent.com/orthodox-ronl/bibliotheek/gh-pages/preview/"
    )
    assert data["alternate"].startswith(
        "https://orthodox-ronl.github.io/bibliotheek/preview/"
    )
    assert data["results"]["raw"] == "skipped"


def test_provisional_main_branch():
    cfg = probe.provisional_config("main")
    assert cfg["base"].endswith("gh-pages/")
    assert "preview" not in cfg["base"]
    assert cfg["alternate"] == "https://orthodox-ronl.github.io/bibliotheek/"
