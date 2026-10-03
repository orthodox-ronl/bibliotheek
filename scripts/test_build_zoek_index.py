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


def test_build_entries_includes_mscz_only_cherubijnen() -> None:
    """Route 1: leaves zonder .vsa/.mvsa (alleen .mscz) staan in de index."""
    from build_zoek_index import DEFAULT_ROOT, build_entries

    entries = build_entries(DEFAULT_ROOT)
    by_id = {e["id"]: e for e in entries}
    assert "cherubijnenhymne/15c-kastorski/hemelum" in by_id
    assert "cherubijnenhymne/15e-bortnjanski/hemelum" in by_id
    kastorski = by_id["cherubijnenhymne/15c-kastorski/hemelum"]
    assert "kastorski" in kastorski["text"]
    assert "cherubijnenhymne" in kastorski["text"]


def test_build_entries_includes_artefacten_handmatig() -> None:
    """artefacten_handmatig slaat producten over, niet de zoekindex."""
    from build_zoek_index import DEFAULT_ROOT, build_entries

    entries = build_entries(DEFAULT_ROOT)
    by_id = {e["id"]: e for e in entries}
    assert "moeder-godslied/ontslapen-moeder-gods/hemelum" in by_id
    entry = by_id["moeder-godslied/ontslapen-moeder-gods/hemelum"]
    assert "ontslapen" in entry["text"]
    assert "engelen" in entry["text"]
