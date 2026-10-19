"""Tests voor bieb verwijder (dry-run + dangling refs + auto-clean)."""

from __future__ import annotations

from pathlib import Path

import bieb_verwijder as bv
import catalogus as cat


def _make_leaf(cat_root: Path, slash: str) -> Path:
    parts = slash.split("/")
    leaf = cat_root.joinpath(*parts)
    leaf.mkdir(parents=True)
    (leaf / "index.md").write_text(
        f'---\npublicatiestatus: reviewable\n---\n'
        f'{{{{< bieb id="{slash}" >}}}}\n',
        encoding="utf-8",
    )
    stem = slash.replace("/", "-")
    (leaf / f"{stem}.vsa").write_text(
        "---\ntitel: T\n---\n[/:] a [:]\n", encoding="utf-8"
    )
    return leaf


def test_verwijder_dry_run_clean(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "repo"
    cat_root = root / "content-source" / "catalogus"
    slash = "demo/var/hemelum"
    leaf = _make_leaf(cat_root, slash)
    (root / "content-source" / "koormappen").mkdir(parents=True)
    (root / "docs").mkdir()

    monkeypatch.setattr(cat, "CATALOGUS_ROOT", cat_root)
    monkeypatch.setattr(cat, "REPO_ROOT", root)
    monkeypatch.setattr(bv, "REPO_ROOT", root)
    monkeypatch.setattr(bv, "KOORMAPPEN_ROOT", root / "content-source" / "koormappen")

    code = bv.verwijder(slash, dry_run=True, force=False)
    assert code == 0
    assert leaf.is_dir()


def test_verwijder_koormap_dangling_stops(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "repo"
    cat_root = root / "content-source" / "catalogus"
    slash = "demo/var/hemelum"
    _make_leaf(cat_root, slash)
    koor = root / "content-source" / "koormappen" / "parochie" / "slot"
    koor.mkdir(parents=True)
    (koor / "index.md").write_text(
        f'{{{{< bieb id="{slash}" >}}}}\n', encoding="utf-8"
    )
    (root / "docs").mkdir()

    monkeypatch.setattr(cat, "CATALOGUS_ROOT", cat_root)
    monkeypatch.setattr(cat, "REPO_ROOT", root)
    monkeypatch.setattr(bv, "REPO_ROOT", root)
    monkeypatch.setattr(bv, "KOORMAPPEN_ROOT", root / "content-source" / "koormappen")

    code = bv.verwijder(slash, dry_run=True, force=False)
    assert code == 1
    code2 = bv.verwijder(slash, dry_run=False, force=True)
    assert code2 == 0
    assert not (cat_root / "demo" / "var" / "hemelum").exists()


def test_verwijder_auto_cleans_register_and_werkvoorraad(
    tmp_path: Path, monkeypatch
) -> None:
    root = tmp_path / "repo"
    cat_root = root / "content-source" / "catalogus"
    slash = "demo/var/hemelum"
    leaf = _make_leaf(cat_root, slash)
    (root / "content-source" / "koormappen").mkdir(parents=True)
    (root / "docs").mkdir()

    reg = root / "content-source" / "overzichten" / "id-register.md"
    reg.parent.mkdir(parents=True)
    reg.write_text(
        "# Id\n"
        "| a | `demo/var/hemelum` | x |\n"
        "| b | other | y |\n"
        "| c | `demo/var/hemelum` | z |\n",
        encoding="utf-8",
    )
    wv = root / "content-source" / "input" / "werkvoorraad.md"
    wv.parent.mkdir(parents=True)
    wv.write_text(
        "| Input | Doel-id | Koormap | Doelvorm | Stap | Volgende | Notitie |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
        "| `vow/x.mscz` | `demo/var/hemelum` |  | `.mscz` | ontvangen | layout | n |\n"
        "| `vow/y.mscz` |  |  | `.mscz` | ontvangen | doel-id |  |\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(cat, "CATALOGUS_ROOT", cat_root)
    monkeypatch.setattr(cat, "REPO_ROOT", root)
    monkeypatch.setattr(bv, "REPO_ROOT", root)
    monkeypatch.setattr(bv, "KOORMAPPEN_ROOT", root / "content-source" / "koormappen")

    assert bv.verwijder(slash, dry_run=True, force=False) == 0
    assert leaf.is_dir()
    assert "`demo/var/hemelum`" in reg.read_text(encoding="utf-8")

    assert bv.verwijder(slash, dry_run=False, force=False) == 0
    assert not leaf.exists()
    reg_txt = reg.read_text(encoding="utf-8")
    assert "`demo/var/hemelum`" not in reg_txt
    assert "| b | other | y |" in reg_txt
    wv_txt = wv.read_text(encoding="utf-8")
    assert "`demo/var/hemelum`" not in wv_txt
    assert "| `vow/x.mscz` |" in wv_txt
    assert "doel-id" in wv_txt


def test_find_dangling_ignores_inside_tree(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "repo"
    cat_root = root / "content-source" / "catalogus"
    slash = "demo/var/hemelum"
    leaf = _make_leaf(cat_root, slash)
    (root / "docs").mkdir()
    monkeypatch.setattr(bv, "REPO_ROOT", root)

    hits = bv._find_dangling(delete_root=leaf, needles=[slash, "demo-var-hemelum"])
    assert hits == []


def test_format_manual_dangling_report(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "repo"
    koor = root / "content-source" / "koormappen" / "p" / "slot" / "index.md"
    koor.parent.mkdir(parents=True)
    koor.write_text("x\n", encoding="utf-8")
    monkeypatch.setattr(bv, "REPO_ROOT", root)
    monkeypatch.setattr(cat, "REPO_ROOT", root)

    dangling = [(koor, 1, 5, '{{< bieb id="demo/var/hemelum" >}}')]
    text = "\n".join(bv._format_manual_dangling_report(dangling))
    assert "Nog 1 ongeldige verwijzing(en) (handmatig)" in text
    assert "1. Koormap: 1 treffer(s)" in text
    assert "Locaties: regel 1 kolom 5" in text
    assert "Actie:" in text
