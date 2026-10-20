"""Orchestrator: bibliotheek-producten genereren per kind + regeneratie-condities.

Zie ``scripts\\products.cmd`` en handleiding Publicatiecontrole.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

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
    args = parser.parse_args(argv)

    try:
        kinds = _parse_kinds(args.kinds)
        policy = policy_from_args(args)
    except SystemExit as exc:
        if exc.code not in (0, None):
            print(exc, file=sys.stderr)
            return 2
        raise

    root = args.root if args.root.is_absolute() else REPO_ROOT / args.root
    if not root.exists():
        print(f"Root niet gevonden: {root}", file=sys.stderr)
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

    print(
        f"=== products: kinds={','.join(kinds)} "
        f"reasons={','.join(policy.active_reasons())} "
        f"root={root} ===",
        flush=True,
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

    failed = 0
    for kind in kinds:
        mod_name = runners[kind]
        print(f"\n--- {kind} ({KIND_HELP[kind]}) ---", flush=True)
        mod = __import__(mod_name)
        code = mod.main(forward)
        if code not in (0, None):
            failed += 1
            print(f"FAILED kind={kind} exit={code}", flush=True)

    if failed:
        print(f"\nproducts: {failed} kind(s) mislukt", flush=True)
        return 1

    # Zoekindex hangt af van lyrics, status en audio-paden — altijd vernieuwen
    # na een geslaagde products-run (ook --only-stale), behalve dry-run.
    if not args.dry_run:
        print("\n--- zoekindex (static/zoek/index.json) ---", flush=True)
        from build_zoek_index import main as build_zoek_main

        zoek_code = build_zoek_main([])
        if zoek_code not in (0, None):
            print(f"FAILED zoekindex exit={zoek_code}", flush=True)
            return 1

    print("\nOK: products klaar", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
