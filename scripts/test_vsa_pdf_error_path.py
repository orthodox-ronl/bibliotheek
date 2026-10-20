"""Temp-pad in vsa-pdf-fouten → catalogus-.vsa."""

from __future__ import annotations

from pathlib import Path

import sync_vsa_products as sync


def test_point_pdf_errors_at_source_replaces_temp(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(sync, "REPO_ROOT", tmp_path)
    source = tmp_path / "content-source" / "catalogus" / "lied.vsa"
    source.parent.mkdir(parents=True)
    source.write_text("L: a\n", encoding="utf-8")
    tmp = Path(r"C:\Users\rj200\AppData\Local\Temp\vsa-pdf-g65gtr29.md")
    raw = (
        f"{tmp}:8:9\n"
        "ERROR: VSA-SEMANTIC-HEIGHT-MARKER-MISMATCH\n"
        f"ook {tmp.as_posix()} in hint\n"
    )
    out = sync._point_pdf_errors_at_source(raw, tmp_path=tmp, source=source)
    assert "AppData" not in out
    assert "vsa-pdf-" not in out
    assert "content-source\\catalogus\\lied.vsa" in out or "content-source/catalogus/lied.vsa" in out
    assert ":8:9" in out
