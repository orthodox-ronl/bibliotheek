"""Tests voor bieb kopieer (uitvoeringsvorm, dry-run, doelcheck)."""

from __future__ import annotations

from pathlib import Path

import bieb_accepteer as ba
import bieb_kopieer as bk
import catalogus as cat


def _make_leaf(cat_root: Path, slash: str) -> Path:
    leaf = cat_root.joinpath(*slash.split("/"))
    leaf.mkdir(parents=True)
    (leaf.parent.parent / "_index.md").write_text(
        "---\ntitle: Z\nlinkTitle: Z\nautomatische_inhoud: true\n---\n",
        encoding="utf-8",
    )
    (leaf.parent / "_index.md").write_text(
        "---\ntitle: V\nlinkTitle: V\nautomatische_inhoud: true\n---\n",
        encoding="utf-8",
    )
    stem = slash.replace("/", "-")
    (leaf / "index.md").write_text(
        f'---\ntitle: "T"\nlinkTitle: "Hemelum"\n'
        f"publicatiestatus: reviewable\n"
        f"automatische_inhoud: false\n---\n\n"
        f'{{{{< bieb id="{slash}" />}}}}\n',
        encoding="utf-8",
    )
    (leaf / f"{stem}.vsa").write_text(
        "---\ntitel: Testlied\n---\n[/:] a [:]\n", encoding="utf-8"
    )
    return leaf


def test_kopieer_rejects_variant(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "repo"
    cat_root = root / "content-source" / "catalogus"
    _make_leaf(cat_root, "demo/var/hemelum")
    monkeypatch.setattr(cat, "CATALOGUS_ROOT", cat_root)
    monkeypatch.setattr(cat, "REPO_ROOT", root)
    monkeypatch.setattr(bk, "REPO_ROOT", root)
    monkeypatch.setattr(ba, "CATALOGUS_ROOT", cat_root)
    monkeypatch.setattr(ba, "REPO_ROOT", root)

    assert bk.main(["demo/var", "demo/var2", "--dry-run"]) == 2


def test_kopieer_dest_exists(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "repo"
    cat_root = root / "content-source" / "catalogus"
    _make_leaf(cat_root, "demo/var/hemelum")
    _make_leaf(cat_root, "demo/var/groningen")
    monkeypatch.setattr(cat, "CATALOGUS_ROOT", cat_root)
    monkeypatch.setattr(cat, "REPO_ROOT", root)
    monkeypatch.setattr(bk, "REPO_ROOT", root)
    monkeypatch.setattr(ba, "CATALOGUS_ROOT", cat_root)
    monkeypatch.setattr(ba, "REPO_ROOT", root)

    code = bk.kopieer("demo/var/hemelum", "groningen", dry_run=True)
    assert code == 1


def test_kopieer_dry_run_and_write(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "repo"
    cat_root = root / "content-source" / "catalogus"
    src = _make_leaf(cat_root, "demo/var/hemelum")
    monkeypatch.setattr(cat, "CATALOGUS_ROOT", cat_root)
    monkeypatch.setattr(cat, "REPO_ROOT", root)
    monkeypatch.setattr(bk, "REPO_ROOT", root)
    monkeypatch.setattr(ba, "CATALOGUS_ROOT", cat_root)
    monkeypatch.setattr(ba, "REPO_ROOT", root)

    assert bk.kopieer("demo/var/hemelum", "groningen", dry_run=True) == 0
    assert src.is_dir()
    assert not (cat_root / "demo" / "var" / "groningen").exists()

    assert bk.kopieer("demo/var/hemelum", "groningen", dry_run=False) == 0
    dest = cat_root / "demo" / "var" / "groningen"
    assert dest.is_dir()
    assert (dest / "demo-var-groningen.vsa").is_file()
    assert not (dest / "demo-var-hemelum.vsa").exists()
    text = (dest / "index.md").read_text(encoding="utf-8")
    assert 'bieb id="demo/var/groningen"' in text
    assert "Hemelum" not in text or "Groningen" in text
