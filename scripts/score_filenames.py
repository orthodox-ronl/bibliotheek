"""Publicatie-bestandsnamen voor conversies (geen spaties).

Print-``.mscz``: buiten layout / mscz-products / publicatiecontrole.
"""

from __future__ import annotations

import re
from pathlib import Path

_UNSAFE = re.compile(r"[^a-zA-Z0-9_-]+")
PRINT_MSCZ_SUFFIX = ".print.mscz"
TEKSTBLAD_MD_SUFFIX = ".tekstblad.md"
# Ketting / verkeerde siblings:
# - twee notatie-extensies + nog iets (….mvsa.mscz.mp3) of bladreeks
#   (….mscz.mscz-1.svg);
# - kaal ….mscz.mscz;
# - Score-IR/from-ir horen alleen bij .mvsa, niet bij .mscz/.vsa.
_CHAINED_PRODUCT = re.compile(
    r"(?i)"
    r"(?:"
    r"(?:\.(?:m?vsa|mscz)){2}(?:\.|-)"
    r"|\.mscz\.mscz$"
    r"|\.(?:mscz|vsa)\.(?:score-ir\.json|from-ir\.musicxml)$"
    r")"
)


def require_no_spaces(path: Path) -> None:
    if " " in path.name:
        raise SystemExit(f"bestandsnaam mag geen spaties hebben: {path.name}")


def is_print_mscz(path: Path | str) -> bool:
    name = path.name if isinstance(path, Path) else Path(path).name
    return name.lower().endswith(PRINT_MSCZ_SUFFIX) or ".print." in name.lower()


def is_tekstblad_md(path: Path | str) -> bool:
    name = path.name if isinstance(path, Path) else Path(path).name
    return name.lower().endswith(TEKSTBLAD_MD_SUFFIX)


def is_derived_mscz(path: Path | str) -> bool:
    """True voor ``{stam}.vsa.mscz`` / ``.mvsa.mscz`` / ``.mscz.mscz``.

    Dat is een afgeleide (of ketting), geen canonieke basispartituur-``.mscz``.
    Bulk-productruns moeten die overslaan; een expliciet CLI-bestandspad mag
    wél als bron.
    """
    name = path.name if isinstance(path, Path) else Path(path).name
    lower = name.lower()
    if not lower.endswith(".mscz"):
        return False
    if is_print_mscz(name):
        return False
    base = lower[: -len(".mscz")]
    return base.endswith((".vsa", ".mvsa", ".mscz"))


def is_chained_product_name(name: str) -> bool:
    """True voor ketting-afgeleiden zoals ``{stam}.mvsa.mscz.mp3``."""
    return _CHAINED_PRODUCT.search(name) is not None


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
