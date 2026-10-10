"""Controleer catalogus-titelcontract (docs/catalogus-titels.md).

``data/uitvoeringsvorm-link-titles.yaml`` moet gelijk zijn aan
``UITVOERINGSVORM_LINK_TITLES`` in catalogus.py zodat Hugo en Python
dezelfde uitvoeringsvorm-labels gebruiken.

Handmatige leaf-``title`` / ``linkTitle`` in frontmatter worden niet meer
geëist of gecontroleerd — Hugo en de zoekindex leiden af uit pad/id (bron).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from catalogus import REPO_ROOT, UITVOERINGSVORM_LINK_TITLES  # noqa: E402

DATA_PATH = REPO_ROOT / "data" / "uitvoeringsvorm-link-titles.yaml"


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _load_data_labels() -> dict[str, str]:
    try:
        import yaml
    except ImportError:
        return {}
    if not DATA_PATH.is_file():
        return {}
    raw = yaml.safe_load(DATA_PATH.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        return {}
    return {str(k): str(v) for k, v in raw.items()}


def find_issues() -> list[str]:
    issues: list[str] = []
    data = _load_data_labels()
    if not data:
        issues.append(
            f"{_rel(DATA_PATH)}: ontbreekt of leeg "
            "(spiegel van UITVOERINGSVORM_LINK_TITLES)."
        )
        return issues
    py_keys = set(UITVOERINGSVORM_LINK_TITLES)
    data_keys = set(data)
    for key in sorted(py_keys - data_keys):
        issues.append(
            f"{_rel(DATA_PATH)}: mist sleutel {key!r} "
            f"(Python heeft {UITVOERINGSVORM_LINK_TITLES[key]!r})"
        )
    for key in sorted(data_keys - py_keys):
        issues.append(
            f"{_rel(DATA_PATH)}: extra sleutel {key!r} "
            "(niet in catalogus.UITVOERINGSVORM_LINK_TITLES)"
        )
    for key in sorted(py_keys & data_keys):
        if data[key] != UITVOERINGSVORM_LINK_TITLES[key]:
            issues.append(
                f"{_rel(DATA_PATH)}: {key!r} is {data[key]!r}, "
                f"Python heeft {UITVOERINGSVORM_LINK_TITLES[key]!r}"
            )
    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Controleer catalogus-titelcontract (UV-labels data)."
    )
    parser.add_argument(
        "--fail",
        action="store_true",
        help="Exit 1 bij problemen (standaard: waarschuwen, exit 0)",
    )
    args = parser.parse_args(argv)
    issues = find_issues()
    if not issues:
        print("catalogus-titels: OK")
        return 0
    print(f"catalogus-titels: {len(issues)} probleem(en)")
    for line in issues:
        print(f"  {line}")
    if args.fail:
        return 1
    print("(geen --fail: exit 0; CI/check --strict gebruikt --fail)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
