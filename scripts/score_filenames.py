"""Publicatie-bestandsnamen voor conversies (geen spaties).

Print-``.mscz``: buiten layout / mscz-products / publicatiecontrole.
"""

from __future__ import annotations

import re
from pathlib import Path

_UNSAFE = re.compile(r"[^a-zA-Z0-9_-]+")
PRINT_MSCZ_SUFFIX = ".print.mscz"
TEKSTBLAD_MD_SUFFIX = ".tekstblad.md"


def require_no_spaces(path: Path) -> None:
    if " " in path.name:
        raise SystemExit(f"bestandsnaam mag geen spaties hebben: {path.name}")


def is_print_mscz(path: Path | str) -> bool:
    name = path.name if isinstance(path, Path) else Path(path).name
    return name.lower().endswith(PRINT_MSCZ_SUFFIX) or ".print." in name.lower()


def is_tekstblad_md(path: Path | str) -> bool:
    name = path.name if isinstance(path, Path) else Path(path).name
    return name.lower().endswith(TEKSTBLAD_MD_SUFFIX)


def is_vsa_source(path: Path | str) -> bool:
    """Canonieke bibliotheek-``.vsa`` (geen ``.syl.vsa``-sidecar)."""
    name = path.name if isinstance(path, Path) else Path(path).name
    lower = name.lower()
    if not lower.endswith(".vsa"):
        return False
    return not lower.endswith(".syl.vsa")


def published_stem(name: str) -> str:
    stem = Path(name).stem.replace(" - ", "-").replace(" ", "-")
    stem = _UNSAFE.sub("-", stem)
    stem = re.sub(r"-{2,}", "-", stem).strip("-")
    if not stem:
        raise SystemExit(f"geen geldige stam uit {name!r}")
    return stem


def published_path(path: Path) -> Path:
    return path.with_name(published_stem(path.name) + path.suffix)
