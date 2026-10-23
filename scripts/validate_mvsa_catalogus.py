"""``mvsa validate`` op catalogusbronnen; sla import-``.mscz.mvsa`` over.

Import-siblings zijn bewerkvorm naast ``.mscz``, geen canonieke catalogus-``.mvsa``.
Zij mogen ``check`` / Pages niet blokkeren (en kunnen nieuwere tokens gebruiken
dan de float-pin op VSA-tooling ``main``).
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def collect_canonical_mvsa(root: Path) -> list[Path]:
    out: list[Path] = []
    for path in sorted(root.rglob("*.mvsa")):
        if not path.is_file():
            continue
        if path.name.lower().endswith(".mscz.mvsa"):
            continue
        out.append(path)
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "root",
        nargs="?",
        type=Path,
        default=REPO_ROOT / "content-source" / "catalogus",
        help="Map of bestand (default: content-source/catalogus)",
    )
    args = parser.parse_args(argv)
    root = args.root if args.root.is_absolute() else REPO_ROOT / args.root
    if not root.exists():
        print(f"FAIL: pad bestaat niet: {root}", file=sys.stderr)
        return 1

    if root.is_file():
        if root.name.lower().endswith(".mscz.mvsa"):
            print(f"SKIP import-sibling: {root}")
            return 0
        files = [root]
    else:
        files = collect_canonical_mvsa(root)

    if not files:
        print("Geen canonieke .mvsa onder", root)
        return 0

    # Eén aanroep per bestand: mvsa validate op een map zou *.mscz.mvsa meenemen.
    failed = 0
    for path in files:
        print(f"=== mvsa validate {path.relative_to(REPO_ROOT)} ===", flush=True)
        rc = subprocess.call(["mvsa", "validate", str(path)], cwd=str(REPO_ROOT))
        if rc != 0:
            failed += 1
    if failed:
        print(f"ERROR: {failed} mvsa-bestand(en) ongeldig", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
