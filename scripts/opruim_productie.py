"""Verwijder van de echte site de bestanden die niet meer in de publicatie zitten.

Alleen voor CI (``.github/workflows/pages.yml``, na een publicatie van
``main``). De publicatiestap voegt alleen toe; oude bestanden blijven anders
staan. Opgeruimd wordt uitsluitend binnen de mappen die de nieuwe publicatie
zelf ook heeft. ``preview/``, proefsites van takken en bestanden in de wortel
van ``gh-pages`` blijven altijd staan.
"""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path

from opruim_previews import MARKER, git

PROTECTED = frozenset({"preview"})


def prunable_dirs(commit: str, site: Path) -> set[str]:
    out = set()
    for child in site.iterdir():
        if not child.is_dir() or child.name in PROTECTED:
            continue
        if git("ls-tree", commit, f"{child.name}/{MARKER}").strip():
            continue
        out.add(child.name)
    return out


def stale_files(commit: str, site: Path) -> list[str]:
    dirs = prunable_dirs(commit, site)
    published = {p.relative_to(site).as_posix() for p in site.rglob("*") if p.is_file()}
    listed = git("ls-tree", "-r", "-z", "--name-only", commit).split("\0")
    return [
        path
        for path in listed
        if "/" in path and path.split("/", 1)[0] in dirs and path not in published
    ]


def commit_without_files(commit: str, paths: list[str]) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        os.environ["GIT_INDEX_FILE"] = str(Path(tmp) / "index")
        try:
            git("read-tree", commit)
            git(
                "update-index",
                "-z",
                "--force-remove",
                "--stdin",
                stdin="".join(f"{p}\0" for p in paths),
            )
            tree = git("write-tree", "--missing-ok").strip()
        finally:
            del os.environ["GIT_INDEX_FILE"]
    message = "chore(pages): bestanden die niet meer in de site horen verwijderd"
    return git("commit-tree", tree, "-p", commit, "-m", message).strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("site", type=Path, help="Map met de nieuwe publicatie")
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    site: Path = args.site
    if not (site / "index.html").is_file() or not (site / "catalogus").is_dir():
        print(f"ERROR  {site} lijkt geen volledige site; niets verwijderd", file=sys.stderr)
        return 1
    git("fetch", "--depth", "1", args.remote, "gh-pages")
    head = git("rev-parse", "FETCH_HEAD").strip()
    stale = stale_files(head, site)
    pdfs = sum(1 for p in stale if p.endswith(".pdf"))
    print(f"{len(stale)} verouderde bestand(en), waarvan {pdfs} PDF.")
    if args.dry_run or not stale:
        return 0
    new = commit_without_files(head, stale)
    git("push", args.remote, f"{new}:refs/heads/gh-pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
