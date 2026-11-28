"""Tests voor sync_inline_vsa.py (scherm-SVG voor ::: vsa in index.md)."""

from __future__ import annotations

from pathlib import Path

from sync_inline_vsa import block_key, collect_blocks


def test_collect_blocks_vindt_beide_namen_en_negeert_crlf(tmp_path: Path) -> None:
    page = tmp_path / "koormappen" / "x" / "index.md"
    page.parent.mkdir(parents=True)
    page.write_bytes(
        b"# Titel\r\n\r\n::: vsa\r\n[:] een [:]\r\n:::\r\n"
        b"\r\n::: vsa-notatie\r\n[:] twee [:]\r\n:::\r\n"
    )
    (tmp_path / "catalogus").mkdir()

    blocks = collect_blocks(tmp_path)

    assert sorted(blocks) == sorted(
        [block_key("[:] een [:]"), block_key("[:] twee [:]")]
    )
