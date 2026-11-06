"""Verwijder ketting-afgeleiden in de catalogus (product-van-product).

Geldig is één product naast een bron, bijvoorbeeld::

    {stam}.mvsa.mp3
    {stam}.mvsa.mscz
    {stam}.mvsa.score-ir.json
    {stam}.vsa.svg
    {stam}.mscz.mvsa
    {stam}.mscz-1.svg

Ongeldig (ketting / verkeerde sibling) — die verwijdert dit script::

    {stam}.mvsa.mscz.mp3
    {stam}.mscz.mscz
    {stam}.mscz.mscz.mp3
    {stam}.mscz.score-ir.json
    {stam}.mscz.from-ir.musicxml
    {stam}.mscz.mvsa.mp3

Standaard alleen melden (dry-run). Echt wissen: ``--apply``.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from score_filenames import is_chained_product_name  # noqa: E402

REPO_ROOT = SCRIPT_DIR.parent
DEFAULT_ROOT = REPO_ROOT / "content-source" / "catalogus"


def find_chained_products(root: Path) -> list[Path]:
    """Alle ketting-bestanden onder ``root`` (bestand of map)."""
    if root.is_file():
        return [root] if is_chained_product_name(root.name) else []
    if not root.is_dir():
        return []
    out: list[Path] = []
    for path in root.rglob("*"):
        if path.is_file() and is_chained_product_name(path.name):
            out.append(path)
    return sorted(out)


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cleanup-chained-products",
        description=(
            "Verwijdert ketting-afgeleiden zoals "
            "{stam}.mvsa.mscz.mp3 of {stam}.vsa.mscz.mscz. "
            "Laat geldige enkele producten staan ({stam}.mvsa.mscz, "
            "{stam}.mvsa.mp3, {stam}.mscz.mvsa, …)."
        ),
    )
    parser.add_argument(
        "root",
        nargs="?",
        default=str(DEFAULT_ROOT),
        help=(
            "Catalogusmap of één bestand "
            f"(standaard: {DEFAULT_ROOT.relative_to(REPO_ROOT).as_posix()})"
        ),
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Bestanden echt verwijderen (zonder deze vlag alleen tonen)",
    )
    args = parser.parse_args(argv)

    root = Path(args.root)
    if not root.is_absolute():
        root = (REPO_ROOT / root).resolve()
    else:
        root = root.resolve()

    if not root.exists():
        print(f"FAIL: pad bestaat niet: {_rel(root)}", file=sys.stderr)
        print(
            "Oplossing: geef een bestaande catalogusmap of laat het "
            "standaardpad staan.",
            file=sys.stderr,
        )
        return 1

    hits = find_chained_products(root)
    mode = "VERWIJDER" if args.apply else "dry-run"
    print(
        f"=== cleanup-chained-products ({mode}) - {len(hits)} bestand(en)",
        flush=True,
    )
    for path in hits:
        print(f"  {_rel(path)}", flush=True)
        if args.apply:
            path.unlink()

    if not hits:
        print("OK: geen ketting-afgeleiden gevonden", flush=True)
        return 0
    if args.apply:
        print(f"OK: {len(hits)} bestand(en) verwijderd", flush=True)
    else:
        print(
            f"OK: {len(hits)} bestand(en) zouden verdwijnen "
            "(opnieuw met --apply om te wissen)",
            flush=True,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
