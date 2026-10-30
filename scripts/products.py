"""Orchestrator: bibliotheek-producten genereren per kind + regeneratie-condities.

Zie ``scripts\\products.cmd`` en handleiding Publicatiecontrole.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from cli_style import add_verbose_argument, error, error_block, info, set_verbose
from product_kind import KindFailure, collect_failures
from product_regen import (
    KIND_HELP,
    KIND_ORDER,
    add_regen_arguments,
    policy_from_args,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOT = REPO_ROOT / "content-source" / "catalogus"


def _parse_kinds(raw: str) -> list[str]:
    text = (raw or "all").strip().lower()
    if text in {"all", "*"}:
        return list(KIND_ORDER)
    parts = [p.strip().lower() for p in text.replace(";", ",").split(",") if p.strip()]
    if not parts:
        raise SystemExit("--kinds mag niet leeg zijn (gebruik all of een lijst)")
    unknown = [p for p in parts if p not in KIND_ORDER]
    if unknown:
        known = ", ".join(KIND_ORDER)
        raise SystemExit(f"Onbekend kind: {', '.join(unknown)}. Bekend: {known}, all")
    # Stabiele volgorde zoals KIND_ORDER
    return [k for k in KIND_ORDER if k in parts]


def _print_products_summary(
    *,
    kind_failures: dict[str, list[KindFailure]],
    kind_exit: dict[str, int],
) -> None:
    failed_kinds = [k for k, code in kind_exit.items() if code != 0]
    if not failed_kinds:
        info("\nOK: products klaar")
        return

    error("")
    error("=== Samenvatting products ===")
    error(f"{len(failed_kinds)} kind(s) mislukt: {', '.join(failed_kinds)}")
    for kind in failed_kinds:
        rows = kind_failures.get(kind) or []
        if not rows:
            error(f"\n{kind}: exit {kind_exit[kind]} (geen per-bestanddetails)")
            error(
                "  Oplossing: draai opnieuw met --verbose of alleen "
                f"--kinds {kind} om de fout te zien."
            )
            continue
        error(f"\n{kind} ({len(rows)}):")
        for fail in rows:
            error(f"  - {fail.path}")
            error(f"    {fail.reason}")
            error(f"    {fail.solution}")
    error("")
    error(
        "Oplossing: herstel de items hierboven (vaak: bestand sluiten of "
        "bronfout), daarna opnieuw: scripts\\products.cmd … "
        "(eventueel --kinds …). Meer detail: voeg --verbose toe."
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Genereer bibliotheek-afgeleiden onder een map (recursief) of "
            "voor één bronbestand. Default: ontbrekend, verouderd (stamp) of "
            "contract-ongeldig. Ontbreekt het brontype voor een kind "
            "(bijv. geen .mscz bij een .mvsa-pad), dan wordt dat kind "
            "overgeslagen — dat is geen fout."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "kinds (default: all — inclusief audio en lyrics):\n"
            + "\n".join(f"  {k:10} {KIND_HELP[k]}" for k in KIND_ORDER)
            + "\n  all         alle kinds\n"
            "\n"
            "--kinds beperkt welke sporen draaien (focus / uitsluiten).\n"
            "Het vertelt niet dat andere brontypen 'ontbreken': die\n"
            "sporen slaan vanzelf over als er geen passende bron is.\n"
            "\n"
            "voorbeelden:\n"
            "  python scripts/products.py\n"
            "  python scripts/products.py pad/naar/lied.mvsa\n"
            "  python scripts/products.py content-source/catalogus/trisagion "
            "--kinds mscz,audio\n"
            "  python scripts/products.py --kinds all --dry-run\n"
            "  python scripts/products.py --only-invalid --kinds mscz,mvsa,vsa\n"
            "  python scripts/products.py --verbose\n"
        ),
    )
    parser.add_argument(
        "root",
        nargs="?",
        type=Path,
        default=DEFAULT_ROOT,
        help="Catalogusmap of één bronbestand (default: content-source/catalogus)",
    )
    parser.add_argument(
        "--kinds",
        default="all",
        metavar="LIST",
        help=(
            "Focus: alleen deze kinds (komma-lijst) of 'all' (default). "
            "Gebruik om werk uit te sluiten, niet omdat andere bronnen "
            "ontbreken."
        ),
    )
    add_regen_arguments(parser)
    add_verbose_argument(parser)
    from batch_guard import add_yes_argument

    add_yes_argument(parser)
    args = parser.parse_args(argv)

    try:
        kinds = _parse_kinds(args.kinds)
        policy = policy_from_args(args)
    except SystemExit as exc:
        if exc.code not in (0, None):
            print(exc, file=sys.stderr)
            return 2
        raise

    set_verbose(bool(args.verbose))
    root = args.root if args.root.is_absolute() else REPO_ROOT / args.root
    if not root.exists():
        error(f"Root niet gevonden: {root}")
        error(
            "Oplossing: geef een bestaande map of bronbestand onder "
            "content-source\\catalogus."
        )
        return 1

    # Zelfde flags doorgeven aan sync_*-mains (minus --kinds).
    forward: list[str] = [str(root)]
    if args.dry_run:
        forward.append("--dry-run")
    if args.force:
        forward.append("--force")
    if args.only_missing:
        forward.append("--only-missing")
    if args.only_stale:
        forward.append("--only-stale")
    if args.only_invalid:
        forward.append("--only-invalid")
    if args.reasons:
        forward.extend(["--reasons", args.reasons])
    if args.verbose:
        forward.append("--verbose")

    # Bevestiging per kind op de echte todo-lijst (korte runs stil;
    # 100+: dubbele vraag). -y/--yes: stil doorgeven aan kind-sporen.
    if args.yes:
        forward.append("-y")
        forward.append("--already-confirmed")

    info(
        f"=== products: kinds={','.join(kinds)} "
        f"reasons={','.join(policy.active_reasons())} "
        f"root={root} ===",
    )

    # Dunne mains blijven (CLI-compat); elk delegeert naar product_kind.run_kind.
    runners = {
        "vsa": "sync_vsa_products",
        "mscz": "sync_mscz_products",
        "tekstblad": "sync_tekstblad_products",
        "mvsa": "sync_mvsa_products",
        "import": "sync_import_mvsa",
        "audio": "sync_audio_products",
        "lyrics": "sync_lyrics_products",
    }

    kind_exit: dict[str, int] = {}
    kind_failures: dict[str, list[KindFailure]] = {}

    for kind in kinds:
        mod_name = runners[kind]
        info(f"\n--- {kind} ({KIND_HELP[kind]}) ---")
        mod = __import__(mod_name)
        rows: list[KindFailure] = []
        with collect_failures(rows):
            code = mod.main(forward)
        kind_exit[kind] = 0 if code in (0, None) else int(code)
        kind_failures[kind] = rows

    failed = sum(1 for c in kind_exit.values() if c != 0)
    if failed:
        _print_products_summary(kind_failures=kind_failures, kind_exit=kind_exit)
        return 1

    # Zoekindex hangt af van lyrics, status en audio-paden — altijd vernieuwen
    # na een geslaagde products-run (ook --only-stale), behalve dry-run.
    if not args.dry_run:
        info("\n--- zoekindex (static/zoek/index.json) ---")
        from build_zoek_index import main as build_zoek_main

        zoek_code = build_zoek_main([])
        if zoek_code not in (0, None):
            error_block(
                [
                    f"FAILED zoekindex exit={zoek_code}",
                    "Oplossing: controleer de fout hierboven; daarna "
                    "python scripts\\build_zoek_index.py opnieuw.",
                ]
            )
            return 1

    info("\nOK: products klaar")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
