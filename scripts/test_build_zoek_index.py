"""Unit tests voor zoek-normalisatie / synoniemen."""

from __future__ import annotations

from build_zoek_index import normalize_text


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
