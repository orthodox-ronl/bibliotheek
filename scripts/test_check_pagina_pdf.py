"""Unit tests voor check_pagina_pdf / pagina_pdf_job (geen MuseScore)."""

from __future__ import annotations

from pathlib import Path

import check_pagina_pdf as cp
import pagina_pdf as pp


def test_pagina_pdf_job_none_without_bieb(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(pp, "CATALOGUS", tmp_path / "catalogus")
    monkeypatch.setattr(pp, "CONTENT", tmp_path)
    md = tmp_path / "koormappen" / "x" / "index.md"
    md.parent.mkdir(parents=True)
    md.write_text("---\ntitle: x\n---\n\nAlleen tekst.\n", encoding="utf-8")
    assert pp.pagina_pdf_job(md) is None


def test_pagina_pdf_job_requires_notation(
    tmp_path: Path, monkeypatch
) -> None:
    cat = tmp_path / "catalogus"
    monkeypatch.setattr(pp, "CATALOGUS", cat)
    monkeypatch.setattr(pp, "CONTENT", tmp_path)
    leaf = cat / "a" / "b" / "c"
    leaf.mkdir(parents=True)
    (leaf / "lied.vsa").write_text("L: a\n", encoding="utf-8")
    md = tmp_path / "koormappen" / "slot" / "index.md"
    md.parent.mkdir(parents=True)
    md.write_text(
        '---\ntitle: Slot\n---\n{{< bieb id="a/b/c" />}}\n',
        encoding="utf-8",
    )
    job = pp.pagina_pdf_job(md)
    assert job is not None
    assert job.out_path == md.with_name("index.pagina.pdf")
    assert job.md_path == md.resolve()
    assert leaf / "lied.vsa" in job.deps


def test_pagina_pdf_job_skips_missing_notation(
    tmp_path: Path, monkeypatch
) -> None:
    cat = tmp_path / "catalogus"
    monkeypatch.setattr(pp, "CATALOGUS", cat)
    monkeypatch.setattr(pp, "CONTENT", tmp_path)
    leaf = cat / "a" / "b" / "c"
    leaf.mkdir(parents=True)
    md = tmp_path / "koormappen" / "slot" / "index.md"
    md.parent.mkdir(parents=True)
    md.write_text(
        '---\ntitle: Slot\n---\n{{< bieb id="a/b/c" />}}\n',
        encoding="utf-8",
    )
    assert pp.pagina_pdf_job(md) is None


def test_check_job_missing_and_stale(tmp_path: Path) -> None:
    md = tmp_path / "index.md"
    md.write_text("x", encoding="utf-8")
    pdf = tmp_path / "index.pagina.pdf"
    src = tmp_path / "bron.vsa"
    src.write_text("L: a\n", encoding="utf-8")
    job = pp.PaginaPdfJob(md, pdf, (md, src))

    missing = cp.check_job(job)
    assert not missing.ok
    assert missing.issues[0].kind == "missing_pdf"

    pdf.write_bytes(b"%PDF-1.4")
    # Oudere PDF dan bron
    older = src.stat().st_mtime - 100
    import os

    os.utime(pdf, (older, older))
    stale = cp.check_job(job)
    assert not stale.ok
    assert stale.issues[0].kind == "stale_pdf"

    newer = src.stat().st_mtime + 100
    os.utime(pdf, (newer, newer))
    ok = cp.check_job(job)
    assert ok.ok
