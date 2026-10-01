"""Unit tests voor zoek-normalisatie / synoniemen."""

from __future__ import annotations

from pathlib import Path

from build_zoek_index import normalize_text, preferred_audio_url


def test_synonyms_map_variants_to_johannes() -> None:
    synonyms = {
        "joannes": "johannes",
        "ioannes": "johannes",
        "ioannis": "johannes",
        "johannes": "johannes",
    }
    assert normalize_text("Joannes de Doper", synonyms) == "johannes de doper"
    assert normalize_text("ioannes", synonyms) == "johannes"
    assert normalize_text("johannes", synonyms) == "johannes"


def test_normalize_without_synonyms_keeps_tokens() -> None:
    assert normalize_text("Alleluja", {}) == "alleluja"


def test_preferred_audio_prefers_mvsa(tmp_path: Path) -> None:
    (tmp_path / "x.vsa.mp3").write_bytes(b"a")
    (tmp_path / "x.mvsa.mp3").write_bytes(b"b")
    url = preferred_audio_url(tmp_path, "ektinia/kleine/hemelum")
    assert url.endswith("/x.mvsa.mp3")
    assert url.startswith("/catalogus/ektinia/kleine/hemelum/")
