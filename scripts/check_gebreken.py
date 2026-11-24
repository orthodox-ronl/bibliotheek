"""Controleer gebreken-markering op catalogus-leaves.

Hard: ``publicatiestatus: productie`` samen met ``gebreken: true``.
Waarschuwing: markering aan maar SVG/PDF zonder stempel (of omgekeerd).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gebreken import find_gebreken_issues  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Controleer gebreken-frontmatter versus stempels op SVG/PDF "
            "en weiger productie+gebreken."
        )
    )
    parser.add_argument(
        "--fail",
        action="store_true",
        help="Exit 1 bij fouten of waarschuwingen (CI/check --strict)",
    )
    parser.add_argument(
        "--fail-errors-only",
        action="store_true",
        help="Exit 1 alleen bij harde fouten (productie+gebreken)",
    )
    args = parser.parse_args(argv)
    errors, warnings = find_gebreken_issues()
    if not errors and not warnings:
        print("gebreken: OK")
        return 0
    print(
        f"gebreken: {len(errors)} fout(en), {len(warnings)} waarschuwing(en)"
    )
    for line in errors:
        print(f"  FOUT: {line}")
    for line in warnings:
        print(f"  waarschuwing: {line}")
    if args.fail_errors_only:
        return 1 if errors else 0
    if args.fail:
        return 1 if (errors or warnings) else 0
    if errors:
        # Zonder --fail: harde fouten toch exit 1 (productie+gebreken)
        return 1
    print("(geen --fail: waarschuwingen exit 0; CI/check --strict gebruikt --fail)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
