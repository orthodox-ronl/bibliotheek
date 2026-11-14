"""Stage of commit gewijzigde bronnen (of met ``--all``: repo minus afgeleiden).

Afgeleiden (``.vsa.svg``, ``.mvsa.mxl``, product-status-JSON, …) blijven
lokaal staan. Zie handleiding ``commit`` / ``stage`` en
``docs/publicatiecontrole.md``.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

from cli_style import error, info, ok
from products_changed import _norm_rel, resolve_base_ref
from score_filenames import (
    is_chained_product_name,
    is_derived_mscz,
    is_print_mscz,
    is_tekstblad_md,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTENT = "content-source"
CATALOGUS = f"{CONTENT}/catalogus"
KOORMAPPEN = f"{CONTENT}/koormappen"
SCOPE_ROOTS = (CATALOGUS, KOORMAPPEN)

# Vlag ↔ kind-tag. ``.tekstblad.md`` valt onder tekstblad én md;
# ``.print.mscz`` / ``.syl.vsa`` onder mscz / vsa.
KIND_FLAGS = ("vsa", "mvsa", "mscz", "md", "tekstblad")

# data/*.json die check/products/fingerprints schrijven (niet handmatig).
_DATA_PRODUCT_JSON = frozenset(
    {
        "check-fixlist.json",
        "coria-fp.json",
        "coria-public-base.json",
    }
)
_STATUS_JSON = re.compile(r"(?i)-status\.json$")
_PDF_R2_JSON = re.compile(r"(?i)^pdf-r2-.*\.json$")
_PAGE_SVG = re.compile(r"(?i)\.(?:vsa|mvsa|mscz)-\d+\.svg$")
_PRODUCTS_META = re.compile(r"(?i)\.products-meta\.json$")
_TEKSTBLAD_PRODUCT = re.compile(
    r"(?i)(?:\.tekstblad\.pdf$|\.tekstblad\.scherm\.html$|"
    r"(?:tekstblad-)?block-\d+\.svg$)"
)
_INDEX_MD_PDF = re.compile(r"(?i)^index\.md(?:\.translit-[a-z0-9_-]+)?\.pdf$")


def in_scope(rel: str) -> bool:
    rel_n = _norm_rel(rel)
    return any(rel_n == root or rel_n.startswith(f"{root}/") for root in SCOPE_ROOTS)


def source_kinds(name: str) -> frozenset[str] | None:
    """Welke ``--``-soorten dit bronbestand dekt, of None als geen bron."""
    lower = Path(name).name.lower()

    if is_tekstblad_md(lower):
        return frozenset({"tekstblad", "md"})

    if lower.endswith(".md"):
        return frozenset({"md"})

    if is_print_mscz(lower):
        return frozenset({"mscz"})

    if lower.endswith(".syl.vsa"):
        return frozenset({"vsa"})

    if lower.endswith(".vsa"):
        # Alleen kale ``{stam}.vsa`` (geen ``….iets.vsa`` behalve syl hierboven).
        stem = lower[: -len(".vsa")]
        if "." in Path(stem).name:
            return None
        return frozenset({"vsa"})

    if lower.endswith(".mvsa"):
        stem = lower[: -len(".mvsa")]
        if stem.endswith(".vsa") or stem.endswith(".mscz"):
            return None
        return frozenset({"mvsa"})

    if lower.endswith(".mscz"):
        if is_derived_mscz(lower):
            return None
        return frozenset({"mscz"})

    return None


def is_commit_source(rel: str) -> frozenset[str] | None:
    if not in_scope(rel):
        return None
    return source_kinds(Path(_norm_rel(rel)).name)


def is_product_artifact(rel: str) -> bool:
    """True voor afgeleiden en JSON/status die uit producten/check komen."""
    rel_n = _norm_rel(rel)
    name = Path(rel_n).name
    lower = name.lower()

    if _INDEX_MD_PDF.match(lower):
        return True
    if _PRODUCTS_META.search(lower):
        return True
    if _TEKSTBLAD_PRODUCT.search(lower):
        return True
    if _PAGE_SVG.search(lower):
        return True

    if rel_n == "static/zoek/index.json":
        return True

    if rel_n.startswith("data/") and "/" not in rel_n[5:]:
        if lower in _DATA_PRODUCT_JSON:
            return True
        if _STATUS_JSON.search(lower):
            return True
        if _PDF_R2_JSON.match(lower):
            return True

    # Canonieke bronnen / print / tekstblad-md zijn geen artefact.
    if source_kinds(name) is not None:
        return False
    if is_tekstblad_md(name) or is_print_mscz(name):
        return False

    if is_chained_product_name(name):
        return True
    if is_derived_mscz(name):
        return True
    for marker in (".vsa.", ".mvsa.", ".mscz."):
        if marker in lower:
            return True
    return False


def git_changed_paths(
    repo: Path,
    *,
    base: str = "HEAD",
    scoped: bool,
) -> list[str]:
    """Gewijzigde/nieuwe/verwijderde paden; ``scoped`` = alleen catalogus+koormappen."""
    names: set[str] = set()
    pathspecs = list(SCOPE_ROOTS) if scoped else []

    def _add_lines(stdout: str) -> None:
        for line in stdout.splitlines():
            rel = _norm_rel(line)
            if not rel:
                continue
            if scoped and not in_scope(rel):
                continue
            names.add(rel)

    resolved = resolve_base_ref(repo, base)
    diff_cmd = [
        "git",
        "diff",
        "--name-only",
        "--diff-filter=ACDMRT",
        resolved,
    ]
    if pathspecs:
        diff_cmd.extend(["--", *pathspecs])
    diff = subprocess.run(
        diff_cmd,
        cwd=str(repo),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if diff.returncode != 0:
        err = (diff.stderr or diff.stdout or "").strip() or f"exit {diff.returncode}"
        raise SystemExit(f"git diff mislukt ({resolved}): {err}")
    _add_lines(diff.stdout)

    other_cmd = ["git", "ls-files", "--others", "--exclude-standard"]
    if pathspecs:
        other_cmd.extend(["--", *pathspecs])
    other = subprocess.run(
        other_cmd,
        cwd=str(repo),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if other.returncode != 0:
        err = (other.stderr or other.stdout or "").strip() or f"exit {other.returncode}"
        raise SystemExit(f"git ls-files mislukt: {err}")
    _add_lines(other.stdout)

    return sorted(names)


def git_changed_scoped(repo: Path, *, base: str = "HEAD") -> list[str]:
    """Gewijzigde paden onder catalogus + koormappen."""
    return git_changed_paths(repo, base=base, scoped=True)


def select_sources(
    relpaths: list[str],
    *,
    wanted: frozenset[str] | None,
) -> list[str]:
    """Filter git-paden tot bronnen; ``wanted`` None = alle bronsoorten."""
    out: list[str] = []
    for rel in relpaths:
        kinds = is_commit_source(rel)
        if kinds is None:
            continue
        if wanted is not None and kinds.isdisjoint(wanted):
            continue
        out.append(_norm_rel(rel))
    return out


def select_all_non_artifacts(relpaths: list[str]) -> list[str]:
    """Alles behalve afgeleiden / product-JSON / status-JSON."""
    return [_norm_rel(rel) for rel in relpaths if not is_product_artifact(rel)]


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=str(repo),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def stage_paths(
    repo: Path,
    paths: list[str],
    *,
    dry_run: bool,
    label: str = "Bronnen",
) -> int:
    if not paths:
        info(f"Niets te stagen (geen gewijzigde {label.lower()} in selectie).")
        return 0

    info(f"{label} ({len(paths)}):")
    for rel in paths:
        info(f"  {rel}")

    if dry_run:
        info("Dry-run: geen git add.")
        return 0

    add = _git(repo, "add", "--", *paths)
    if add.returncode != 0:
        error((add.stderr or add.stdout or "git add mislukt").strip())
        return 1
    ok(f"Gestaged: {len(paths)} pad(en).")
    return 0


def commit_paths(
    repo: Path,
    paths: list[str],
    *,
    message: str | None,
    dry_run: bool,
    label: str = "Bronnen",
) -> int:
    if not paths:
        info(f"Niets te committen (geen gewijzigde {label.lower()} in selectie).")
        return 0

    info(f"{label} ({len(paths)}):")
    for rel in paths:
        info(f"  {rel}")

    if dry_run:
        info("Dry-run: geen git add/commit.")
        return 0

    add = _git(repo, "add", "--", *paths)
    if add.returncode != 0:
        error((add.stderr or add.stdout or "git add mislukt").strip())
        return 1

    cmd = ["commit", "--"]
    if message is not None:
        cmd = ["commit", "-m", message, "--"]
    cmd.extend(paths)
    proc = _git(repo, *cmd)
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip() or f"exit {proc.returncode}"
        # Niets gestaged na add (bijv. alleen whitespace die git negeert)
        if "nothing to commit" in err.lower() or "no changes added" in err.lower():
            info("Niets te committen (git zag geen inhoudelijke wijziging).")
            return 0
        error(err)
        return 1

    out = (proc.stdout or "").strip()
    if out:
        ok(out.splitlines()[0])
    else:
        ok(f"Commit klaar ({len(paths)} pad(en)).")
    return 0


def build_parser(*, mode: str = "commit") -> argparse.ArgumentParser:
    if mode == "stage":
        description = (
            "Stage gewijzigde bronbestanden onder content-source\\catalogus "
            "en content-source\\koormappen; sla afgeleiden over. "
            "Met --all: hele repo minus afgeleiden/product-JSON."
        )
        epilog = (
            "Voorbeelden:\n"
            "  scripts\\stage.cmd\n"
            "  scripts\\stage.cmd --vsa\n"
            "  scripts\\stage.cmd --mscz --mvsa\n"
            "  scripts\\stage.cmd --all\n"
            "  scripts\\stage.cmd --md --dry-run\n"
        )
        dry_help = "Toon welke paden gestaged zouden worden; geen git add."
    else:
        description = (
            "Commit gewijzigde bronbestanden onder content-source\\catalogus "
            "en content-source\\koormappen; sla afgeleiden over. "
            "Met --all: hele repo minus afgeleiden/product-JSON."
        )
        epilog = (
            "Voorbeelden:\n"
            "  scripts\\commit.cmd -m \"wip: koormaptekst\"\n"
            "  scripts\\commit.cmd --vsa -m \"wip: vsa\"\n"
            "  scripts\\commit.cmd --mscz --mvsa -m \"wip: partituur\"\n"
            "  scripts\\commit.cmd --all -m \"wip: scripts en bronnen\"\n"
            "  scripts\\commit.cmd --md --dry-run\n"
        )
        dry_help = "Toon welke paden mee zouden gaan; geen add/commit."

    from cli_help import CliHelpFormatter

    p = argparse.ArgumentParser(
        description=description,
        epilog=epilog,
        formatter_class=CliHelpFormatter,
    )
    for kind in KIND_FLAGS:
        p.add_argument(
            f"--{kind}",
            action="store_true",
            help=(
                {
                    "vsa": "Alleen .vsa / .syl.vsa",
                    "mvsa": "Alleen canonieke .mvsa (geen .vsa.mvsa / .mscz.mvsa)",
                    "mscz": "Alleen basis-.mscz / .print.mscz",
                    "md": "Alleen Markdown (index.md, tekstblad, ...)",
                    "tekstblad": "Alleen .tekstblad.md",
                }[kind]
            ),
        )
    p.add_argument(
        "--all",
        action="store_true",
        help=(
            "Hele repo: bronnen plus overige niet-afgeleide bestanden "
            "(scripts, layouts, …). Geen product-JSON/status. "
            "Niet combineren met --vsa/--mvsa/--mscz/--md/--tekstblad."
        ),
    )
    if mode == "commit":
        p.add_argument(
            "-m",
            "--message",
            help="Commitbericht (zonder -m opent git de editor).",
        )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help=dry_help,
    )
    p.add_argument(
        "--base",
        default="HEAD",
        help="Git-referentie voor 'gewijzigd' (default: HEAD).",
    )
    return p


def main(argv: list[str] | None = None, *, mode: str = "commit") -> int:
    if mode not in {"commit", "stage"}:
        raise ValueError(f"onbekende mode: {mode!r}")
    args = build_parser(mode=mode).parse_args(argv)
    selected = frozenset(k for k in KIND_FLAGS if getattr(args, k))
    if args.all and selected:
        error(
            "--all mag niet samen met --vsa / --mvsa / --mscz / --md / --tekstblad."
        )
        return 2

    wanted: frozenset[str] | None = selected if selected else None

    try:
        rels = git_changed_paths(
            REPO_ROOT,
            base=args.base,
            scoped=not args.all,
        )
    except SystemExit as exc:
        error(str(exc))
        return 1

    if args.all:
        paths = select_all_non_artifacts(rels)
        label = "Bestanden"
    else:
        paths = select_sources(rels, wanted=wanted)
        label = "Bronnen"

    if mode == "stage":
        return stage_paths(
            REPO_ROOT,
            paths,
            dry_run=args.dry_run,
            label=label,
        )
    return commit_paths(
        REPO_ROOT,
        paths,
        message=args.message,
        dry_run=args.dry_run,
        label=label,
    )


if __name__ == "__main__":
    sys.exit(main())
