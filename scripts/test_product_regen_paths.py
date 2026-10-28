"""Tests voor list_source_paths / collect met enkel bestand."""

from __future__ import annotations

from pathlib import Path

import sync_audio_products as audio
import sync_lyrics_products as lyrics
from product_regen import list_source_paths
from score_filenames import is_chained_product_name, is_derived_mscz
from sync_mscz_products import collect_mscz


def test_list_source_paths_file_and_dir(tmp_path: Path) -> None:
    f = tmp_path / "a.mscz"
    f.write_bytes(b"PK")
    (tmp_path / "b.mscz").write_bytes(b"PK")
    assert list_source_paths(f, pattern="*.mscz") == [f]
    found = list_source_paths(tmp_path, pattern="*.mscz")
    assert {p.name for p in found} == {"a.mscz", "b.mscz"}
    assert list_source_paths(tmp_path / "missing", pattern="*.mscz") == []


def test_collect_mscz_accepts_single_file(tmp_path: Path) -> None:
    leaf = tmp_path / "zang" / "var" / "uv"
    leaf.mkdir(parents=True)
    (leaf / "index.md").write_text(
        "---\npublicatiestatus: reviewable\n---\n", encoding="utf-8"
    )
    mscz = leaf / "zang-var-uv.mscz"
    mscz.write_bytes(b"PK")
    assert collect_mscz(mscz) == [mscz]
    assert collect_mscz(leaf) == [mscz]


def test_derived_mscz_helpers() -> None:
    assert is_derived_mscz("lied.mvsa.mscz")
    assert is_derived_mscz("lied.vsa.mscz")
    assert is_derived_mscz("lied.mscz.mscz")
    assert not is_derived_mscz("lied.mscz")
    assert not is_derived_mscz("lied.print.mscz")
    assert is_chained_product_name("lied.mvsa.mscz.mp3")
    assert not is_chained_product_name("lied.mvsa.mscz")


def test_collect_skips_derived_mscz_in_dir_allows_explicit(tmp_path: Path) -> None:
    leaf = tmp_path / "zang" / "var" / "uv"
    leaf.mkdir(parents=True)
    (leaf / "index.md").write_text(
        "---\npublicatiestatus: reviewable\n---\n", encoding="utf-8"
    )
    basis = leaf / "zang-var-uv.mscz"
    basis.write_bytes(b"PK")
    derived = leaf / "zang-var-uv.mvsa.mscz"
    derived.write_bytes(b"PK")
    (leaf / "zang-var-uv.mvsa").write_text("L: a\n", encoding="utf-8")

    assert {p.name for p in collect_mscz(leaf)} == {"zang-var-uv.mscz"}
    assert collect_mscz(derived) == [derived]

    audio_names = {j.source.name for j in audio.collect_audio_jobs(leaf)}
    assert "zang-var-uv.mscz" in audio_names
    assert "zang-var-uv.mvsa.mscz" not in audio_names
    assert "zang-var-uv.mvsa" in audio_names
    assert audio.collect_audio_jobs(derived)[0].source == derived

    lyric_names = {p.name for p in lyrics.collect_lyric_sources(leaf)}
    assert "zang-var-uv.mscz" in lyric_names
    assert "zang-var-uv.mvsa.mscz" not in lyric_names
    assert lyrics.collect_lyric_sources(derived) == [derived]
