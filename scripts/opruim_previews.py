"""Verwijder op gh-pages de proefsites van takken die niet meer bestaan.

Alleen voor CI (``.github/workflows/pages.yml``, na een publicatie van
``development``). Een map in de wortel van gh-pages telt alleen als
proefsite wanneer die map het bestand ``.branch-preview`` bevat. Dat bestand
noemt de tak. Mappen zonder dat bestand blijven altijd staan, dus de echte
site en ``preview/`` worden nooit geraakt.
"""

from __future__ import annotations

import argparse
import subprocess
import sys

MARKER = ".branch-preview"


def git(*args: str, stdin: str | None = None) -> str:
    return subprocess.run(
        ["git", *args],
        input=stdin,
        check=True,
        capture_output=True,
        encoding="utf-8",
    ).stdout


def live_branches(remote: str) -> set[str]:
    out = git("ls-remote", "--heads", remote)
    return {line.split("refs/heads/", 1)[1] for line in out.splitlines()}


def stale_previews(commit: str, branches: set[str]) -> dict[str, str]:
    """``{map: tak}`` voor proefsites waarvan de tak weg is."""
    stale: dict[str, str] = {}
    for line in git("ls-tree", commit).splitlines():
        meta, name = line.split("\t", 1)
        if meta.split()[1] != "tree":
            continue
        if not git("ls-tree", commit, f"{name}/{MARKER}").strip():
            continue
        branch = git("cat-file", "-p", f"{commit}:{name}/{MARKER}").strip()
        if branch and branch not in branches:
            stale[name] = branch
    return stale


def commit_without(commit: str, names: set[str]) -> str:
    """Nieuwe commit bovenop ``commit`` zonder de mappen ``names``."""
    keep = [
        line
        for line in git("ls-tree", commit).splitlines()
        if line.split("\t", 1)[1] not in names
    ]
    tree = git("mktree", "--missing", stdin="".join(f"{x}\n" for x in keep))
    message = "chore(pages): proefsites van verwijderde takken opgeruimd"
    return git("commit-tree", tree.strip(), "-p", commit, "-m", message).strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--remote", default="origin")
    args = parser.parse_args(argv)

    branches = live_branches(args.remote)
    if "development" not in branches:
        print("ERROR  takkenlijst onbetrouwbaar; niets verwijderd", file=sys.stderr)
        return 1
    git("fetch", "--depth", "1", args.remote, "gh-pages")
    head = git("rev-parse", "FETCH_HEAD").strip()
    stale = stale_previews(head, branches)
    if not stale:
        print("Geen proefsites om op te ruimen.")
        return 0
    for name, branch in sorted(stale.items()):
        print(f"Opruimen: {name}/ (tak {branch} bestaat niet meer)")
    new = commit_without(head, set(stale))
    git("push", args.remote, f"{new}:refs/heads/gh-pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
