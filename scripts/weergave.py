"""Weergave (vsa of partituur) op blad-PDF's: welke stukken zijn wisselbaar.

Zelfde regels als ``layouts/partials/bieb-score.html``
(docs/specs/schermpartituur.md §2.1): beslissend zijn de schermplaatjes die
in de catalogusmap staan.
"""

from __future__ import annotations

import itertools
import re
from dataclasses import dataclass
from pathlib import Path

VSA = "vsa"
PARTITUUR = "partituur"
WEERGAVEN = (VSA, PARTITUUR)
# Meer wisselbare stukken op één blad: eerst opnieuw overleggen (2^n PDF's).
MAX_WISSELBAAR = 4

VARIANT_GLOB = "index.md.weergave-*.pdf"
_FRONT = re.compile(r"\A﻿?---\r?\n(.*?)\r?\n---", re.S)
_VELD = re.compile(r"(?m)^weergave:[ \t]*[\"']?([A-Za-z]+)[\"']?[ \t]*(?:#.*)?$")


def soort_van_svg(name: str) -> str | None:
    """``vsa`` / ``partituur`` voor een schermplaatje, anders ``None``."""
    n = name.lower()
    if "@" in n or ".translit" in n:
        return None
    if n.endswith(".vsa.svg") and ".vsa.mvsa." not in n:
        return VSA
    if n.endswith((".mvsa.svg", ".mscz.svg")):
        return PARTITUUR
    return None


def _rang(source: Path) -> tuple[int, str]:
    n = source.name.lower()
    if n.endswith(".mvsa") and not n.endswith((".vsa.mvsa", ".mscz.mvsa")):
        return (0, n)
    if n.endswith(".mvsa"):
        return (1, n)
    return (2, n)


def bronnen_per_weergave(leaf: Path) -> dict[str, Path]:
    """Per aanwezige weergave de bron waarvan het schermplaatje komt."""
    found: dict[str, list[Path]] = {}
    for svg in leaf.glob("*.svg"):
        soort = soort_van_svg(svg.name)
        source = svg.with_name(svg.name[: -len(".svg")])
        if soort and source.is_file():
            found.setdefault(soort, []).append(source)
    return {soort: min(paths, key=_rang) for soort, paths in found.items()}


def blad_weergave(leaf: Path) -> str | None:
    """``weergave:`` uit de frontmatter van de blad-``index.md``."""
    index = leaf / "index.md"
    if not index.is_file():
        return None
    front = _FRONT.match(index.read_text(encoding="utf-8"))
    if not front:
        return None
    m = _VELD.search(front.group(1))
    return controleer(m.group(1), str(index)) if m else None


def controleer(value: str, waar: str) -> str:
    v = value.strip().lower()
    if v not in WEERGAVEN:
        raise ValueError(
            f"{waar}: weergave={value!r} onbekend. Oplossing: kies vsa of partituur."
        )
    return v


@dataclass(frozen=True)
class Wisselbaar:
    """Eén wisselbaar muziekstuk op een blad (documentvolgorde)."""

    standaard: str
    bronnen: dict[str, Path]
    leaf: Path


def wisselbaar(leaf: Path, gevraagd: str | None) -> Wisselbaar | None:
    if not leaf.is_dir():
        return None
    bronnen = bronnen_per_weergave(leaf)
    if len(bronnen) < 2:
        return None
    return Wisselbaar(gevraagd or blad_weergave(leaf) or VSA, bronnen, leaf)


def code(keuzes: list[str]) -> str:
    """``['vsa', 'partituur']`` → ``'vp'`` (zelfde letters als de website)."""
    return "".join(k[0] for k in keuzes)


def andere_combinaties(stukken: list[Wisselbaar]) -> list[list[str]]:
    """Alle keuzes behalve de standaard; leeg boven de grens."""
    if not stukken or len(stukken) > MAX_WISSELBAAR:
        return []
    standaard = tuple(s.standaard for s in stukken)
    return [
        list(c)
        for c in itertools.product(WEERGAVEN, repeat=len(stukken))
        if c != standaard
    ]


def variant_pad(md_path: Path, keuzes: list[str]) -> Path:
    return md_path.with_name(f"{md_path.name}.weergave-{code(keuzes)}.pdf")
