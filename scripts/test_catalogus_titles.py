"""Tests voor afgeleide catalogus-titels (docs/catalogus-titels.md)."""

from __future__ import annotations

from pathlib import Path

from catalogus import (
    UITVOERINGSVORM_LINK_TITLES,
    derived_leaf_link_title,
    derived_leaf_title,
    derived_leaf_title_from_id,
    section_title,
    title_hint_from_source,
    words_title,
)
from check_catalogus_leaf_titles import find_issues


def test_words_and_section_title() -> None:
    assert words_title("johannes-de-theoloog") == "Johannes De Theoloog"
    assert section_title("default") == "Standaard"
    assert section_title("zondag-toon-1") == "Zondag Toon 1"


def test_derived_leaf_from_id() -> None:
    ident = "kondak/johannes-de-theoloog-toon-2/liturgikon"
    assert derived_leaf_link_title(ident) == "Liturgikon"
    assert derived_leaf_title_from_id(ident) == (
        "Kondak Johannes De Theoloog Toon 2 (Liturgikon)"
    )


def test_derived_leaf_from_source(tmp_path: Path) -> None:
    vsa = tmp_path / "x.vsa"
    vsa.write_text(
        "---\nsoort: tropaar\ntitel: Opgestane Heer\n---\n[/:] a [:]\n",
        encoding="utf-8",
    )
    ident = "tropaar/zondag-toon-1/hemelum"
    assert title_hint_from_source(vsa) == "Tropaar — Opgestane Heer"
    assert derived_leaf_title(ident, source_paths=[vsa]) == (
        "Tropaar — Opgestane Heer (Hemelum)"
    )


def test_uv_data_file_matches_python() -> None:
    assert find_issues() == []
    assert "hemelum" in UITVOERINGSVORM_LINK_TITLES
