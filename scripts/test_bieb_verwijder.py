"""Tests voor bieb verwijder (dry-run + dangling refs)."""

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


def test_verwijder_dangling_stops(tmp_path: Path, monkeypatch) -> None:
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


def test_find_dangling_ignores_inside_tree(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "repo"
    cat_root = root / "content-source" / "catalogus"
    slash = "demo/var/hemelum"
    leaf = _make_leaf(cat_root, slash)
    (root / "docs").mkdir()
    monkeypatch.setattr(bv, "REPO_ROOT", root)

    hits = bv._find_dangling(delete_root=leaf, needles=[slash, "demo-var-hemelum"])
    assert hits == []
