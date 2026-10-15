"""Tests voor list_source_paths / collect met enkel bestand."""

from __future__ import annotations

from pathlib import Path

from product_regen import list_source_paths
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
