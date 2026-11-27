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


def _write_status() -> int:
    from check_report import print_check_findings
    from gebreken import (
        STATUS_PATH,
        collect_gebreken_statuses,
        write_gebreken_status_json,
    )
    from input_paths import rel_for_log
    from gebreken import REPO_ROOT

    statuses, n_leaves = collect_gebreken_statuses()
    write_gebreken_status_json(statuses)
    bad_leaves = {s.dir.removesuffix(" (pdf)") for s in statuses}
    print_check_findings(
        headline=(
            f"Gebreken-stempels: {n_leaves - len(bad_leaves)} ok, "
            f"{len(bad_leaves)} probleem "
            f"({rel_for_log(STATUS_PATH, repo_root=REPO_ROOT)})"
        ),
        what="Controle: of SVG-stempel/PDF-watermark bij de gebreken-markering passen",
        bad=statuses,
        fix_page=None,
    )
    return 1 if statuses else 0


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
    parser.add_argument(
        "--write-status",
        action="store_true",
        help=(
            "Schrijf data/gebreken-status.json (voor check-fixlist/fix) en "
            "toon de afwerkbare stempel-/watermerkproblemen; exit 1 bij problemen."
        ),
    )
    args = parser.parse_args(argv)
    if args.write_status:
        return _write_status()
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
