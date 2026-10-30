"""Afwerklijst uit check: tonen (--dry-run) of uitvoeren (fix_cmd per regel).

Met ``--check`` eerst ``check --strict`` (lijst vernieuwen); problemen
(exit 1) zijn verwacht. Harde check-fout (validate/tooling) stopt fix.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

from batch_guard import add_yes_argument, confirm_batch
from check_fixlist import (
    FIXLIST_PATH,
    FixItem,
    load_fixlist,
    print_fixlist,
    save_fixlist,
    write_fixlist,
)
from cli_style import add_verbose_argument, error, info, set_verbose

REPO_ROOT = Path(__file__).resolve().parents[1]
CHECK_CMD = REPO_ROOT / "scripts" / "check.cmd"


def _fixlist_mtime() -> float:
    try:
        return FIXLIST_PATH.stat().st_mtime
    except OSError:
        return 0.0


def _run_check_strict(*, verbose: bool) -> int:
    """Run check --strict. Return process exit code."""
    cmd = ["cmd", "/c", str(CHECK_CMD), "--strict"]
    info("=== fix: check --strict (fixlist vernieuwen) ===")
    proc = subprocess.run(
        cmd,
        cwd=str(REPO_ROOT),
        check=False,
    )
    if verbose:
        info(f"check --strict exit={proc.returncode}")
    return int(proc.returncode)


def _check_failed_before_fixlist(code: int, *, mtime_before: float) -> bool:
    """True als check stopte vóór een verse fixlist (validate/tooling/…).

    Exit 0/1 mét nieuwere fixlist = ok (0 groen, 1 productproblemen).
    Exit ≥2, of fixlist niet vernieuwd → niet afwerken.
    """
    if code >= 2:
        return True
    return _fixlist_mtime() <= mtime_before


def _refresh_fixlist_from_status() -> list[FixItem]:
    items = write_fixlist()
    info(
        f"Fixlist vernieuwd: {len(items)} item(s) → "
        f"{FIXLIST_PATH.relative_to(REPO_ROOT).as_posix()}"
    )
    return items


def _run_fix_cmd(fix_cmd: str, *, verbose: bool) -> int:
    proc = subprocess.run(
        ["cmd", "/c", fix_cmd],
        cwd=str(REPO_ROOT),
        check=False,
    )
    if verbose:
        info(f"exit={proc.returncode} ← {fix_cmd}")
    return int(proc.returncode)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Toon of werk de check-fixlist af (één fix_cmd per regel). "
            "Met --check eerst check --strict."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "voorbeelden:\n"
            "  python scripts/fix.py --dry-run\n"
            "  python scripts/fix.py --check --dry-run\n"
            "  python scripts/fix.py --check\n"
            "  python scripts/fix.py -y\n"
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Toon de lijst; voer geen fix_cmd uit.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Eerst check --strict (lijst opnieuw bouwen), daarna tonen/afwerken.",
    )
    add_verbose_argument(parser)
    add_yes_argument(parser)
    args = parser.parse_args(argv)
    set_verbose(bool(args.verbose))

    if args.check:
        mtime_before = _fixlist_mtime()
        code = _run_check_strict(verbose=bool(args.verbose))
        if _check_failed_before_fixlist(code, mtime_before=mtime_before):
            error(
                f"check --strict leverde geen verse fixlist "
                f"(exit {code}). Geen afwerken. "
                "Herstel validate/tooling eerst, of draai check opnieuw."
            )
            return 2
        # check.cmd schreef al; opnieuw aggregaten dekt race/handmatige status.
        items = _refresh_fixlist_from_status()
    else:
        if not FIXLIST_PATH.is_file():
            error(
                "Geen fixlist gevonden (data\\check-fixlist.json). "
                "Oplossing: scripts\\check.cmd of scripts\\fix.cmd --check"
            )
            return 2
        items = load_fixlist()

    if args.dry_run:
        print_fixlist(items)
        info("\nOK: dry-run (niets gefixt)")
        return 0

    if not items:
        info("Fixlist leeg — niets te doen.")
        return 0

    if not confirm_batch(
        "fix",
        n=len(items),
        headline=f"{len(items)} auto-fix(es) uit check-fixlist",
        details=[
            f"Bestand: {FIXLIST_PATH.relative_to(REPO_ROOT).as_posix()}",
            "Elke regel = één fix_cmd (zoals check voorstelt).",
        ],
        yes=bool(args.yes),
    ):
        return 2

    remaining = list(items)
    fixed = 0
    failed = 0

    for item in list(items):
        info(f"\n>>> {item.summary}")
        info(f"    {item.fix_cmd}")
        t0 = time.perf_counter()
        code = _run_fix_cmd(item.fix_cmd, verbose=bool(args.verbose))
        elapsed = time.perf_counter() - t0
        if code == 0:
            fixed += 1
            remaining = [x for x in remaining if x.id != item.id]
            save_fixlist(remaining)
            info(
                f"    OK ({elapsed:.1f}s) — geschrapt "
                f"({len(remaining)} rest)"
            )
        else:
            failed += 1
            error(f"    FAILED exit={code} — blijft op de lijst")

    info(f"\n=== fix klaar: {fixed} ok, {failed} mislukt, "
         f"{len(remaining)} rest ===")
    if failed:
        error(
            "Oplossing: bekijk de fout hierboven; daarna "
            "scripts\\fix.cmd opnieuw (of --dry-run)."
        )
        return 1
    info("OK: fixlist leeg" if not remaining else "OK: fix afgerond")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
