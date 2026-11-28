"""Proef opruim_productie.py op een echte, tijdelijke git-repository."""

from __future__ import annotations

from pathlib import Path

import opruim_previews
import opruim_productie as op

git = opruim_previews.git


def _write(root: Path, rel: str, text: str = "x") -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_alleen_verouderde_bestanden_van_de_echte_site(
    tmp_path: Path, monkeypatch
) -> None:
    remote = tmp_path / "remote.git"
    work = tmp_path / "work"
    site = tmp_path / "site"
    work.mkdir()
    monkeypatch.chdir(work)
    for var in ("GIT_AUTHOR_NAME", "GIT_COMMITTER_NAME"):
        monkeypatch.setenv(var, "test")
    for var in ("GIT_AUTHOR_EMAIL", "GIT_COMMITTER_EMAIL"):
        monkeypatch.setenv(var, "test@example.org")
    git("init", "-q", "--bare", str(remote))
    git("init", "-q")
    git("remote", "add", "origin", str(remote))
    blijft = [
        ".nojekyll",
        "index.html",
        "catalogus/a/index.html",
        "catalogus/Mattheüs blad/index.html",
        "preview/catalogus/a/index.md.pdf",
        "tak/.branch-preview",
        "tak/oud.pdf",
        "onbekend/oud.pdf",
    ]
    for rel in [*blijft, "catalogus/a/index.md.pdf", "catalogus/weg/index.html"]:
        _write(work, rel)
    git("add", "-A")
    git("commit", "-q", "-m", "pages")
    git("push", "-q", "origin", "HEAD:refs/heads/gh-pages")
    for rel in ("index.html", "catalogus/a/index.html", "catalogus/Mattheüs blad/index.html"):
        _write(site, rel)

    assert op.main([str(site)]) == 0

    git("fetch", "-q", "origin", "gh-pages")
    names = git("ls-tree", "-r", "-z", "--name-only", "FETCH_HEAD").split("\0")
    assert sorted(n for n in names if n) == sorted(blijft)


def test_onvolledige_site_verwijdert_niets(tmp_path: Path) -> None:
    assert op.main([str(tmp_path)]) == 1
