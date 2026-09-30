"""Grenzen tussen lifecycle-fases Werkbank en Catalogus.

Waarschuwt (of faalt met --fail) bij:
- bestandsnamen met spaties onder content-source/catalogus
- ruwe formats (.cap/.capx/.musicxml/.xml) in de bibliotheek
- kale .mxl in de bibliotheek die geen product-sibling lijkt

Geen VSA-parserlogica.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from catalogus import CATALOGUS_ROOT, REPO_ROOT

RAW_SUFFIXES = frozenset({".cap", ".capx", ".musicxml", ".xml"})
# Sibling-producten eindigen zo; kale .mxl hoort niet als catalogus-bron.
PRODUCT_MXL_MARKERS = (
    ".mscz.mxl",
    ".vsa.mxl",
    ".mvsa.mxl",
)


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _is_product_mxl(name: str) -> bool:
    lower = name.lower()
    return any(lower.endswith(m) for m in PRODUCT_MXL_MARKERS)


def collect_issues(root: Path = CATALOGUS_ROOT) -> list[str]:
    issues: list[str] = []
    if not root.is_dir():
        return issues
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        # Special pages / registers zijn markdown — ok
        if "speciaal" in path.parts:
            continue
        name = path.name
        if " " in name:
            issues.append(
                f"spaties in catalogus-bestandsnaam: {_rel(path)} "
                f"(hoort in werkbank/input of publicatiestam zonder spaties)"
            )
        suffix = path.suffix.lower()
        if suffix in RAW_SUFFIXES:
            issues.append(
                f"ruw formaat in catalogus: {_rel(path)} "
                f"(eerst werkbank: opkuisen / layout, daarna bieb accepteer)"
            )
        if suffix == ".mxl" and not _is_product_mxl(name):
            stem = path.name[: -len(".mxl")]
            parent = path.parent
            if (parent / f"{stem}.vsa").is_file():
                issues.append(
                    f"verouderde sibling-naam (verwacht {stem}.vsa.mxl): {_rel(path)}"
                )
            elif (parent / f"{stem}.mscz").is_file() or (
                parent / f"{stem}.print.mscz"
            ).is_file():
                issues.append(
                    f"verouderde sibling-naam (verwacht {stem}.mscz.mxl): {_rel(path)}"
                )
            elif (parent / f"{stem}.mvsa").is_file():
                issues.append(
                    f"verouderde sibling-naam (verwacht {stem}.mvsa.mxl): {_rel(path)}"
                )
            else:
                issues.append(
                    f"kale .mxl in catalogus (geen product-sibling): {_rel(path)} "
                    f"(canonieke bron is .mscz/.vsa/.mvsa; .mxl is afgeleide)"
                )
    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Controleer grenzen werkbank ↔ catalogus"
    )
    parser.add_argument(
        "--fail",
        action="store_true",
        help="Exit 1 als er problemen zijn (default: alleen melden, exit 0)",
    )
    args = parser.parse_args(argv)
    issues = collect_issues()
    if not issues:
        print("Lifecycle-grenzen: OK (geen spaties/ruwe formats in catalogus).")
        return 0
    print(f"Lifecycle-grenzen: {len(issues)} probleem(en):", flush=True)
    for msg in issues:
        print(f"  - {msg}", flush=True)
    print(
        "\nHandleiding: content-source\\handleiding\\start\\levenscyclus.md",
        flush=True,
    )
    if args.fail:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
