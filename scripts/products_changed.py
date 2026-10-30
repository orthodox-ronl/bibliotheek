"""Alleen producten/pdf voor git-gewijzigde bronnen onder content-source.

Doel: kleine, snelle runs (geen hele catalogus-scan met invalid) zodat
volgende commits ook klein blijven.

Default: working tree + index t.o.v. HEAD; condities ``missing,stale``
(geen ``invalid`` — dat is de dure mxl-validate-scan).
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from cli_style import add_verbose_argument, error, info, set_verbose
from product_regen import KIND_ORDER

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTENT = "content-source"
KOORMAPPEN = f"{CONTENT}/koormappen"


@dataclass(frozen=True)
class ProductJob:
    path: Path
    kinds: tuple[str, ...]


@dataclass(frozen=True)
class Plan:
    products: list[ProductJob]
    pdfs: list[Path]
    ignored: list[str]


def _norm_rel(raw: str) -> str:
    text = raw.strip().strip('"').replace("\\", "/")
    while text.startswith("./"):
        text = text[2:]
    return text


def _git_ok(repo: Path, *args: str) -> bool:
    proc = subprocess.run(
        ["git", *args],
        cwd=str(repo),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return proc.returncode == 0


def resolve_base_ref(repo: Path, base: str) -> str:
    """Kies een bestaande git-ref; bij ``main`` ook ``origin/main`` proberen."""
    raw = (base or "HEAD").strip() or "HEAD"
    if raw.upper() == "HEAD":
        return "HEAD"
    if _git_ok(repo, "rev-parse", "--verify", "--quiet", f"{raw}^{{commit}}"):
        return raw
    if "/" not in raw:
        remote = f"origin/{raw}"
        if _git_ok(repo, "rev-parse", "--verify", "--quiet", f"{remote}^{{commit}}"):
            return remote
    raise SystemExit(
        f"Git-referentie niet gevonden: {raw}. "
        "Oplossing: gebruik HEAD, main, origin/main, of een commit-hash."
    )


def git_changed_relpaths(repo: Path, *, base: str = "HEAD") -> list[str]:
    """Gewijzigde paden onder content-source (t.o.v. base + untracked)."""
    names: set[str] = set()

    def _add_lines(stdout: str) -> None:
        for line in stdout.splitlines():
            rel = _norm_rel(line)
            if not rel or not rel.startswith(f"{CONTENT}/"):
                continue
            names.add(rel)

    resolved = resolve_base_ref(repo, base)
    diff = subprocess.run(
        [
            "git",
            "diff",
            "--name-only",
            "--diff-filter=ACMR",
            resolved,
            "--",
            CONTENT,
        ],
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

    # Untracked (niet in diff t.o.v. base)
    other = subprocess.run(
        [
            "git",
            "ls-files",
            "--others",
            "--exclude-standard",
            "--",
            CONTENT,
        ],
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


def kinds_for_source(rel: str) -> tuple[str, ...] | None:
    """Kinds voor een content-source-relpad, of None als geen productbron."""
    name = Path(rel).name.lower()
    if name.endswith(".tekstblad.md"):
        return ("tekstblad",)
    if name.endswith(".mscz.mvsa"):
        return ("import",)
    if name.endswith(".mvsa"):
        return ("mvsa", "audio", "lyrics")
    if name.endswith(".vsa"):
        return ("vsa", "audio", "lyrics")
    if name.endswith(".mscz"):
        if (
            name.endswith(".vsa.mscz")
            or name.endswith(".mvsa.mscz")
            or name.endswith(".print.mscz")
        ):
            return None
        return ("mscz", "audio", "lyrics")
    return None


def is_koormap_index(rel: str) -> bool:
    rel_n = _norm_rel(rel)
    if not rel_n.startswith(f"{KOORMAPPEN}/"):
        return False
    return Path(rel_n).name.lower() == "index.md"


def build_plan(relpaths: list[str], *, repo: Path = REPO_ROOT) -> Plan:
    products: list[ProductJob] = []
    pdfs: list[Path] = []
    ignored: list[str] = []
    seen_prod: set[Path] = set()
    seen_pdf: set[Path] = set()

    for rel in relpaths:
        rel_n = _norm_rel(rel)
        path = repo / Path(*rel_n.split("/"))
        if is_koormap_index(rel_n):
            if path not in seen_pdf:
                seen_pdf.add(path)
                pdfs.append(path)
            continue
        kinds = kinds_for_source(rel_n)
        if kinds is None:
            ignored.append(rel_n)
            continue
        if path in seen_prod:
            continue
        seen_prod.add(path)
        # Stabiele kind-volgorde
        ordered = tuple(k for k in KIND_ORDER if k in kinds)
        products.append(ProductJob(path=path, kinds=ordered))

    return Plan(products=products, pdfs=pdfs, ignored=ignored)


def _print_plan(plan: Plan, *, dry_run: bool, base: str) -> None:
    label = "dry-run" if dry_run else "plan"
    info(f"=== products-changed ({label}, base={base}) ===")
    if not plan.products and not plan.pdfs:
        info("Geen productbronnen of koormap-index.md in de git-wijzigingen.")
        if plan.ignored:
            info(
                f"(Overgeslagen niet-bron: {len(plan.ignored)} pad(en) "
                "onder content-source.)"
            )
        if base.upper() == "HEAD":
            info(
                "Tip: wijzigingen al gecommit? Probeer "
                "--since-development --dry-run (feature → development) "
                "of --since-main --dry-run (richting productie)."
            )
        return
    if plan.products:
        info(f"products ({len(plan.products)}):")
        for job in plan.products:
            try:
                show = job.path.relative_to(REPO_ROOT)
            except ValueError:
                show = job.path
            info(f"  {show}  --kinds {','.join(job.kinds)}")
    if plan.pdfs:
        info(f"pdf ({len(plan.pdfs)}):")
        for path in plan.pdfs:
            try:
                show = path.relative_to(REPO_ROOT)
            except ValueError:
                show = path
            info(f"  {show}")
    if plan.ignored and dry_run:
        info(f"overgeslagen ({len(plan.ignored)}), bijv.:")
        for rel in plan.ignored[:8]:
            info(f"  {rel}")
        if len(plan.ignored) > 8:
            info(f"  … +{len(plan.ignored) - 8} meer")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Genereer alleen producten (en koormap-pdf) voor git-gewijzigde "
            "bronnen onder content-source. Condities: missing+stale "
            "(geen invalid)."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "voorbeelden:\n"
            "  python scripts/products_changed.py --dry-run\n"
            "  python scripts/products_changed.py\n"
            "  python scripts/products_changed.py --since-main --dry-run\n"
            "  python scripts/products_changed.py --since-development --dry-run\n"
            "  python scripts/products_changed.py --base origin/main\n"
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Toon wat zou draaien; schrijf niets.",
    )
    parser.add_argument(
        "--base",
        default=None,
        metavar="REF",
        help=(
            "Git-referentie voor diff (default: HEAD). "
            "Zie ook --since-main / --since-development."
        ),
    )
    parser.add_argument(
        "--since-main",
        action="store_true",
        help="Zelfde als --base main (of origin/main als main ontbreekt).",
    )
    parser.add_argument(
        "--since-development",
        "--since-dev",
        action="store_true",
        help=(
            "Zelfde als --base development (of origin/development). "
            "Voor feature-branches die op development landen."
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Doorgeven aan products/pdf (regenereer altijd).",
    )
    add_verbose_argument(parser)
    from batch_guard import add_yes_argument

    add_yes_argument(parser)
    args = parser.parse_args(argv)
    set_verbose(bool(args.verbose))

    since_flags = sum(
        [bool(args.since_main), bool(args.since_development), args.base is not None]
    )
    if since_flags > 1:
        error(
            "Gebruik hoogstens één van --since-main, --since-development "
            "of --base."
        )
        return 2
    if args.since_main:
        base_arg = "main"
    elif args.since_development:
        base_arg = "development"
    else:
        base_arg = args.base or "HEAD"

    try:
        resolved = resolve_base_ref(REPO_ROOT, base_arg)
        rels = git_changed_relpaths(REPO_ROOT, base=resolved)
    except SystemExit as exc:
        if exc.code not in (0, None):
            print(exc, file=sys.stderr)
            return 2
        raise

    plan = build_plan(rels, repo=REPO_ROOT)
    _print_plan(plan, dry_run=bool(args.dry_run), base=resolved)

    if not plan.products and not plan.pdfs:
        return 0

    if args.dry_run:
        info("\nOK: dry-run (niets geschreven)")
        return 0

    import products as products_mod

    failed = 0
    for job in plan.products:
        if not job.path.exists():
            error(f"Bron ontbreekt (verwijderd?): {job.path}")
            failed += 1
            continue
        forward = [
            str(job.path),
            "--kinds",
            ",".join(job.kinds),
            "--reasons",
            "missing,stale",
            "--skip-post",
            "-y",
        ]
        if args.force:
            forward.append("--force")
        if args.verbose:
            forward.append("--verbose")
        info(f"\n>>> products {' '.join(forward)}")
        code = products_mod.main(forward)
        if code not in (0, None):
            failed += 1

    if plan.pdfs:
        import index_md_pdf as pdf_mod

        for path in plan.pdfs:
            if not path.exists():
                error(f"index.md ontbreekt: {path}")
                failed += 1
                continue
            forward = [str(path)]
            if args.force:
                forward.append("--force")
            info(f"\n>>> pdf {' '.join(forward)}")
            code = pdf_mod.main(forward)
            if code not in (0, None):
                failed += 1

    if failed:
        error(f"\nFAILED: {failed} taak(en) mislukt")
        return 1

    if plan.products:
        info("\n--- zoekindex (static/zoek/index.json) ---")
        from build_zoek_index import main as build_zoek_main

        zoek_code = build_zoek_main([])
        if zoek_code not in (0, None):
            error(f"FAILED zoekindex exit={zoek_code}")
            return 1

        info("\n--- Coria-fingerprints ---")
        import fingerprint_coria_mxl as fp_mod

        fp_code = fp_mod.main()
        if fp_code not in (0, None):
            error(f"FAILED fingerprints exit={fp_code}")
            return 1

    info("\nOK: products-changed klaar")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
