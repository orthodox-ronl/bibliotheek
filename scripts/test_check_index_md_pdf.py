"""Unit tests voor check_index_md_pdf / pagina_pdf_job (geen MuseScore)."""

from __future__ import annotations

from pathlib import Path

import check_index_md_pdf as cp
import index_md_pdf as pp


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
    assert job.out_path == md.with_name("index.md.pdf")
    assert job.md_path == md.resolve()
    assert leaf / "lied.vsa" in job.deps
    assert leaf / "lied.vsa.svg" in job.deps


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


def test_pagina_pdf_job_koormap_tekstblad_bieb(
    tmp_path: Path, monkeypatch
) -> None:
    """Koormap-slot met ``bieb`` naar tekstblad-only leaf → pagina-PDF-job."""
    cat = tmp_path / "catalogus"
    monkeypatch.setattr(pp, "CATALOGUS", cat)
    monkeypatch.setattr(pp, "CONTENT", tmp_path)
    leaf = cat / "dialoog" / "default" / "x"
    leaf.mkdir(parents=True)
    tb = leaf / "dialoog-default-x.tekstblad.md"
    tb.write_text("# Dialoog\n\nPriester: …\n", encoding="utf-8")
    md = tmp_path / "koormappen" / "liturgie" / "07d-dialoog" / "index.md"
    md.parent.mkdir(parents=True)
    md.write_text(
        '---\ntitle: "(7d) Dialoog"\n---\n\n'
        "{{< kop >}}(7d) Dialoog{{< /kop >}}\n\n"
        "***Alleen met diaken.***\n\n"
        '{{< bieb id="dialoog/default/x" />}}\n',
        encoding="utf-8",
    )
    job = pp.pagina_pdf_job(md)
    assert job is not None
    assert job.out_path == md.with_name("index.md.pdf")
    assert tb.resolve() in {p.resolve() for p in job.deps}


def test_resolve_tekstblad_title_prefers_kop(
    tmp_path: Path, monkeypatch
) -> None:
    cat = tmp_path / "catalogus"
    monkeypatch.setattr(pp, "CATALOGUS", cat)
    leaf = cat / "dialoog" / "default" / "x"
    leaf.mkdir(parents=True)
    (leaf / "x.tekstblad.md").write_text(
        '---\ntitle: "Catalogustitel"\n---\nBody\n', encoding="utf-8"
    )
    md = tmp_path / "slot.md"
    text = (
        '---\ntitle: "FM"\n---\n\n'
        "{{< kop >}}(7d) Dialoog met de Diaken{{< /kop >}}\n\n"
        '{{< bieb id="dialoog/default/x" />}}\n'
    )
    md.write_text(text, encoding="utf-8")
    assert (
        pp._tekstblad_pagina_title(md, text, "dialoog/default/x")
        == "(7d) Dialoog met de Diaken"
    )


def test_check_job_missing_and_stale(tmp_path: Path) -> None:
    md = tmp_path / "index.md"
    md.write_text("x", encoding="utf-8")
    pdf = tmp_path / "index.md.pdf"
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
