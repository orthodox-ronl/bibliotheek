"""Tests voor korte check-rapportage."""

from __future__ import annotations

from dataclasses import dataclass

from check_report import (
    print_check_findings,
    short_hint,
    short_kind,
    template_fix_cmd,
)


def test_short_kind_and_hint():
    assert short_kind("meta_stale") == "meta"
    assert short_kind("stale_pdf") == "stale-pdf"
    assert short_hint("meta_stale", "product 'mxl' sha256 wijkt af") == "foute sha256"
    assert short_hint("stale_pdf", "index.md.pdf is ouder dan …") == ""


def test_template_fix_cmd():
    raw = (
        r"scripts\products.cmd --kinds mvsa --reasons missing,stale "
        r"--skip-post catalogus\a\b\c\file.mvsa"
    )
    assert template_fix_cmd(raw) == (
        "products --kinds mvsa --reasons missing,stale --skip-post {file}"
    )
    assert template_fix_cmd(
        r"scripts\pdf.cmd koormappen\x\y\index.md"
    ) == r"scripts\pdf.cmd {file}"


def test_print_check_findings_compact(capsys):
    @dataclass
    class Issue:
        kind: str
        file: str
        detail: str

    @dataclass
    class St:
        dir: str
        issues: list
        fix_cmd: str

    bad = [
        St(
            dir="catalogus/a/b/c",
            issues=[
                Issue(
                    "meta_stale",
                    "catalogus/a/b/c/x.mvsa.products-meta.json",
                    "product 'mxl' sha256 wijkt af van bestand",
                )
            ],
            fix_cmd=(
                r"scripts\products.cmd --kinds mvsa --reasons missing,stale "
                r"--skip-post catalogus\a\b\c\x.mvsa"
            ),
        )
    ]
    print_check_findings(
        headline="MVSA-producten: 0 ok, 1 probleem",
        what="Controle: of .mvsa-afgeleiden bij de bron passen",
        bad=bad,
        fix_page="/handleiding/scripts/mvsa-products/",
        verbose=False,
    )
    out = capsys.readouterr().out
    assert "Controle: of .mvsa-afgeleiden" in out
    assert "  1  niet-in-orde" in out
    assert "  1  meta  foute sha256" in out
    assert "catalogus/a/b/c" in out
    assert "products-meta.json" not in out.split("fix:")[0]
    assert "fix: `products --kinds mvsa" in out
    assert "{file}" in out
    assert "sha256 wijkt af van bestand" not in out
