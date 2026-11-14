"""Unit tests voor r2_pdf_upload helpers (geen netwerk)."""

from __future__ import annotations

import json
from pathlib import Path

import r2_pdf_upload as r2


def test_object_key_and_rel(tmp_path: Path, monkeypatch) -> None:
    content = tmp_path / "content-source"
    pdf = content / "catalogus" / "x" / "index.md.pdf"
    pdf.parent.mkdir(parents=True)
    pdf.write_bytes(b"%PDF")
    monkeypatch.setattr(r2, "CONTENT", content)
    assert r2.content_rel(pdf) == "catalogus/x/index.md.pdf"
    assert (
        r2.object_key(pdf, "development")
        == "development/catalogus/x/index.md.pdf"
    )


def test_manifest_rels_from_keys() -> None:
    keys = [
        "development/catalogus/a/index.md.pdf",
        "development/catalogus/b/index.md.translit-ksl.pdf",
        "development/readme.txt",
        "production/catalogus/a/index.md.pdf",
    ]
    assert r2.manifest_rels_from_keys(keys) == [
        "catalogus/a/index.md.pdf",
        "catalogus/b/index.md.translit-ksl.pdf",
    ]


def test_write_development_manifest(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path
    man = root / "data" / "pdf-r2-development.json"
    monkeypatch.setattr(r2, "ROOT", root)
    monkeypatch.setattr(r2, "MANIFEST_PATH", man)
    r2.write_development_manifest(
        ["catalogus/b/index.md.pdf", "catalogus/a/index.md.pdf"]
    )
    data = json.loads(man.read_text(encoding="utf-8"))
    assert data["overrides"] == [
        "catalogus/a/index.md.pdf",
        "catalogus/b/index.md.pdf",
    ]
