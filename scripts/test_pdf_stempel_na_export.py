"""Na een SVG-export door pdf.cmd staat de gebreken-stempel er meteen op."""

from __future__ import annotations

from pathlib import Path

import gebreken
import index_md_pdf as pp


def test_export_stempelt_voor_de_pdf(tmp_path: Path, monkeypatch) -> None:
    source = tmp_path / "x.mvsa"
    source.write_text("bron", encoding="utf-8")
    (tmp_path / "index.md").write_text(
        "---\ntitle: t\ngebreken: true\n---\n", encoding="utf-8"
    )
    dest = tmp_path / "x.mvsa.svg"

    def export(_source, out, **_kw):
        out.write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 50"></svg>',
            encoding="utf-8",
        )
        return [out]

    monkeypatch.setattr(gebreken, "effective_gebreken_for_folder", lambda _f: (True, None))
    monkeypatch.setattr(pp, "export_blad_svgs", export)
    monkeypatch.setattr(pp, "refresh_svg_products_meta", lambda *a: None)
    pp._export_product_svg_for_pdf(source, dest)
    assert gebreken.svg_has_gebreken_stempel(dest)
    # De nabewerking verandert daarna niets meer, dus de PDF blijft actueel.
    assert gebreken.sync_leaf_svg_stempels(tmp_path)[0] == 0
