"""Controleer leaf-frontmatter: titel niet te generiek, linkTitle leesbaar.

``bieb accepteer`` zet ``title`` op een volledige leesbare titel en
``linkTitle`` op het uitvoeringsvorm-label (Hemelum, Liturgikon, …).
Kale titels als alleen ``kondak`` maken zoektreffers onbruikbaar.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from catalogus import (  # noqa: E402
    REPO_ROOT,
    is_generic_leaf_title,
    leaf_folders,
    parse_id,
    uitvoeringsvorm_link_title,
)


def _fm_value(text: str, key: str) -> str | None:
    in_fm = False
    prefix = f"{key.lower()}:"
    for line in text.splitlines():
        if line.strip() == "---":
            if not in_fm:
                in_fm = True
                continue
            break
        if in_fm and line.lower().startswith(prefix):
            return line.split(":", 1)[1].strip().strip("\"'")
    return None


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def find_issues() -> list[str]:
    issues: list[str] = []
    for ident, folder in leaf_folders():
        index = folder / "index.md"
        if not index.is_file():
            continue
        try:
            text = index.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        zangstuk, _variant, uv = parse_id(ident)
        title = _fm_value(text, "title") or ""
        link = _fm_value(text, "linkTitle") or ""
        if is_generic_leaf_title(title, zangstuk):
            issues.append(
                f"{_rel(index)}: title {title!r} is te generiek "
                f"(alleen zangstuk-id). Zet een volledige titel "
                f"(zie handleiding catalogus-titels / bieb accepteer --title)."
            )
        expect_link = uitvoeringsvorm_link_title(uv)
        if link and link.lower() == uv.lower() and link != expect_link:
            issues.append(
                f"{_rel(index)}: linkTitle {link!r} hoort "
                f"{expect_link!r} te zijn (leesbaar uitvoeringsvorm-label)."
            )
        if link and is_generic_leaf_title(link, zangstuk):
            issues.append(
                f"{_rel(index)}: linkTitle {link!r} is te generiek; "
                f"gebruik het uitvoeringsvorm-label ({expect_link!r})."
            )
    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Controleer catalogus-leaf title/linkTitle."
    )
    parser.add_argument(
        "--fail",
        action="store_true",
        help="exit 1 bij problemen (default: alleen waarschuwen)",
    )
    args = parser.parse_args(argv)
    issues = find_issues()
    if not issues:
        print("catalogus-leaf-titles: OK")
        return 0
    print(f"catalogus-leaf-titles: {len(issues)} probleem(en)")
    for line in issues:
        print(f"  {line}")
    if args.fail:
        return 1
    print("(waarschuwing — zonder --fail geen exit 1)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
