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


def test_development_slaat_ongewijzigde_over(tmp_path: Path, monkeypatch) -> None:
    content = tmp_path / "content-source"
    oud, nieuw = (content / "catalogus" / n / "index.md.pdf" for n in "ab")
    for pdf, data in ((oud, b"%PDF oud"), (nieuw, b"%PDF nieuw")):
        pdf.parent.mkdir(parents=True)
        pdf.write_bytes(data)
    oud_sha = r2.sha256_file(oud)
    geplaatst: list[str] = []

    class Client:
        def head_bucket(self, **_kw):
            return {}

    monkeypatch.setattr(r2, "ROOT", tmp_path)
    monkeypatch.setattr(r2, "CONTENT", content)
    monkeypatch.setattr(r2, "MANIFEST_PATH", tmp_path / "data" / "m.json")
    monkeypatch.setattr(r2, "r2_client", lambda: (Client(), "b", "e", "account"))
    monkeypatch.setattr(
        r2,
        "r2_object_sha256",
        lambda _c, _b, key: oud_sha if key == "development/catalogus/a/index.md.pdf" else None,
    )
    monkeypatch.setattr(
        r2, "_upload_file", lambda _c, _b, _p, key, _d: geplaatst.append(key)
    )
    monkeypatch.setattr(r2, "list_keys", lambda *_a: [])
    assert r2.main(["--env", "development"]) == 0
    assert geplaatst == ["development/catalogus/b/index.md.pdf"]
