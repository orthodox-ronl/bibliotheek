"""Bestand-of-map-invoer voor bibliotheek-CLI's.

**Afspraak** (spiegel VSA-tooling ``vsa.input_paths``): een ``path``-argument
is óf één bronbestand met de juiste extensie, óf een map waarvan (standaard
recursief) alle passende bestanden worden verzameld.

Enkelvoudige uitvoerpaden (``-o`` / ``--output``) alleen bij precies één bron.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from pathlib import Path


class InputPathError(ValueError):
    """Pad ontbreekt, is geen bestand/map, of past niet bij de extensies."""


def normalize_suffixes(suffixes: Sequence[str]) -> frozenset[str]:
    """Normaliseer tot lowercase extensies met leidende punt (``.mvsa``).

    Samengestelde vormen mogen: ``.tekstblad.md``.
    """
    out: set[str] = set()
    for raw in suffixes:
        s = str(raw).strip().lower()
        if not s:
            continue
        if not s.startswith("."):
            s = f".{s}"
        out.add(s)
    if not out:
        raise InputPathError("minstens één bestands-extensie vereist")
    return frozenset(out)


def _name_matches(path: Path, allowed: frozenset[str]) -> bool:
    """True als de bestandsnaam eindigt op een toegestane (compound) suffix."""
    name = path.name.lower()
    return any(name.endswith(suf) for suf in allowed)


def collect_input_files(
    path: Path | str,
    *,
    suffixes: Sequence[str],
    recursive: bool = True,
    names: Sequence[str] | None = None,
) -> list[Path]:
    """Verzamel bronbestanden: één file of (recursief) een map.

    Parameters
    ----------
    path:
        Bestaand bestand of bestaande map.
    suffixes:
        Toegestane extensies (``.mvsa``, ``tekstblad.md``, …). Case-insensitive.
        Matching via ``name.endswith(suffix)`` (ook samengestelde suffixes).
    recursive:
        Bij een map: ``rglob`` (True) of alleen directe kinderen (False).
    names:
        Optioneel: alleen deze basenames (case-insensitive), bv. ``index.md``.

    Returns
    -------
    list[Path]
        Gesorteerde lijst. Mag leeg zijn als de map geen matches heeft.

    Raises
    ------
    InputPathError
        Pad bestaat niet; is geen file/dir; of is een file met verkeerde
        extensie / naam.
    """
    p = Path(path)
    allowed = normalize_suffixes(suffixes)
    name_set = (
        frozenset(n.strip().lower() for n in names if str(n).strip())
        if names is not None
        else None
    )
    if names is not None and not name_set:
        raise InputPathError("names mag niet leeg zijn als het is opgegeven")

    if not p.exists():
        raise InputPathError(f"Pad niet gevonden: {p}")

    def _ok(candidate: Path) -> bool:
        if not candidate.is_file():
            return False
        if not _name_matches(candidate, allowed):
            return False
        if name_set is not None and candidate.name.lower() not in name_set:
            return False
        return True

    if p.is_file():
        if not _name_matches(p, allowed):
            want = ", ".join(sorted(allowed))
            raise InputPathError(
                f"Verwacht bestand met extensie {want}; kreeg: {p.name}"
            )
        if name_set is not None and p.name.lower() not in name_set:
            want = ", ".join(sorted(name_set))
            raise InputPathError(
                f"Verwacht bestandsnaam {want}; kreeg: {p.name}"
            )
        return [p]
    if p.is_dir():
        if recursive:
            candidates: Iterable[Path] = p.rglob("*")
        else:
            candidates = p.iterdir()
        return sorted(c for c in candidates if _ok(c))
    raise InputPathError(f"Geen bestand of map: {p}")


def collect_cli_sources(
    path: Path | str,
    *,
    suffixes: Sequence[str],
    recursive: bool = True,
    names: Sequence[str] | None = None,
) -> list[Path]:
    """Zoals :func:`collect_input_files`, maar lege map → :exc:`InputPathError`."""
    files = collect_input_files(
        path, suffixes=suffixes, recursive=recursive, names=names
    )
    if not files:
        raise InputPathError(f"Geen passende bestanden gevonden: {path}")
    return files


def reject_multi_with_output(
    files: Sequence[Path],
    output: Path | str | None,
    *,
    flag: str = "-o/--output",
) -> None:
    """Weiger enkelvoudig uitvoerpad bij meer dan één bronbestand."""
    if output is not None and len(files) > 1:
        raise InputPathError(
            f"{flag} is alleen toegestaan bij precies één bronbestand "
            f"(nu {len(files)} bestanden)"
        )
