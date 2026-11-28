"""Proef opruim_previews.py op een echte, tijdelijke git-repository."""

from __future__ import annotations

from pathlib import Path

import opruim_previews as op


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_alleen_gemarkeerde_mappen_zonder_tak_verdwijnen(
    tmp_path: Path, monkeypatch
) -> None:
    remote = tmp_path / "remote.git"
    work = tmp_path / "work"
    work.mkdir()
    monkeypatch.chdir(work)
    for var in ("GIT_AUTHOR_NAME", "GIT_COMMITTER_NAME"):
        monkeypatch.setenv(var, "test")
    for var in ("GIT_AUTHOR_EMAIL", "GIT_COMMITTER_EMAIL"):
        monkeypatch.setenv(var, "test@example.org")
    op.git("init", "-q", "--bare", str(remote))
    op.git("init", "-q")
    op.git("remote", "add", "origin", str(remote))
    _write(work, "catalogus/index.html", "echt")
    _write(work, "preview/index.html", "preview")
    _write(work, "oud/.branch-preview", "fix/oud\n")
    _write(work, "bezig/.branch-preview", "feat/bezig\n")
    op.git("add", "-A")
    op.git("commit", "-q", "-m", "pages")
    op.git("push", "-q", "origin", "HEAD:refs/heads/gh-pages")
    op.git("push", "-q", "origin", "HEAD:refs/heads/development")
    op.git("push", "-q", "origin", "HEAD:refs/heads/feat/bezig")

    assert op.main([]) == 0

    op.git("fetch", "-q", "origin", "gh-pages")
    names = op.git("ls-tree", "--name-only", "FETCH_HEAD").split()
    assert names == ["bezig", "catalogus", "preview"]
