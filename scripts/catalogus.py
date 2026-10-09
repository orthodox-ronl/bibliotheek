"""Catalogus-root: catalogus-id (zangstuk/variant/uitvoeringsvorm) <-> pad.

Id: ``zangstuk/variant/uitvoeringsvorm`` (``[a-z0-9_-]+``, drie lagen).
Publicatiestam: ``zangstuk-variant-uitvoeringsvorm``.
Colofon in ``.mscz`` blijft de tooling-regel ``Bibliotheek-id:``.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CATALOGUS_ROOT = REPO_ROOT / "content-source" / "catalogus"
_ID_PART = re.compile(r"^[a-z0-9_-]+$")


def parse_id(value: str) -> tuple[str, str, str]:
    parts = value.strip().strip("/").split("/")
    if len(parts) != 3:
        raise ValueError(
            f"verwacht zangstuk/variant/uitvoeringsvorm, kreeg {value!r}"
        )
    for part in parts:
        if not _ID_PART.fullmatch(part):
            raise ValueError(f"ongeldig id-segment {part!r} in {value!r}")
    return parts[0], parts[1], parts[2]


def parse_variant_id(value: str) -> tuple[str, str]:
    parts = value.strip().strip("/").split("/")
    if len(parts) != 2:
        raise ValueError(f"verwacht zangstuk/variant, kreeg {value!r}")
    for part in parts:
        if not _ID_PART.fullmatch(part):
            raise ValueError(f"ongeldig id-segment {part!r} in {value!r}")
    return parts[0], parts[1]


def folder(value: str) -> Path:
    zangstuk, variant, uitvoeringsvorm = parse_id(value)
    return CATALOGUS_ROOT / zangstuk / variant / uitvoeringsvorm


def variant_folder(value: str) -> Path:
    zangstuk, variant = parse_variant_id(value)
    return CATALOGUS_ROOT / zangstuk / variant


def stem(value: str) -> str:
    zangstuk, variant, uitvoeringsvorm = parse_id(value)
    return f"{zangstuk}-{variant}-{uitvoeringsvorm}"


# Leesbare linkTitle voor bekende uitvoeringsvorm-ids (navigatie / broodkruimels).
UITVOERINGSVORM_LINK_TITLES: dict[str, str] = {
    "hemelum": "Hemelum",
    "hemelum-ksl": "Hemelum (ksl)",
    "hemelum-nl": "Hemelum (nl)",
    "hemelum-ksl-trlat": "Hemelum (ksl/trlat)",
    "liturgikon": "Liturgikon",
    "liturgikon-ksl": "Liturgikon (ksl)",
    "heiligenjaar": "Heiligenjaar",
    "groningen": "Groningen",
    "groningen-ksl": "Groningen (ksl)",
    "meneon-1": "Meneon I",
    "meneon-i-den-haag": "Meneon I Den Haag",
    "vokn-25": "VOKN-25",
    "default": "Standaard",
    "asten": "Asten",
    "rode-gebedenboek": "Rode gebedenboek",
}

_PUBLICATION_SUFFIXES = (
    ".tekstblad.md",
    ".print.mscz",
    ".mscz.mvsa",
    ".mscz",
    ".mvsa",
    ".vsa",
    ".pdf",
    ".mxl",
    ".md",
)


def uitvoeringsvorm_link_title(uitvoeringsvorm: str) -> str:
    """Korte navigatienaam voor een uitvoeringsvorm-id."""
    known = UITVOERINGSVORM_LINK_TITLES.get(uitvoeringsvorm)
    if known:
        return known
    parts = uitvoeringsvorm.split("-")
    return "-".join(p[:1].upper() + p[1:] if p else p for p in parts)


def publication_stem_from_filename(name: str) -> str:
    """Bestandsnaam → publicatiestam (zonder score-/product-suffix)."""
    lower = name.lower()
    for suf in _PUBLICATION_SUFFIXES:
        if lower.endswith(suf):
            return name[: -len(suf)]
    return Path(name).stem


def _known_zangstuk_ids() -> list[str]:
    if not CATALOGUS_ROOT.is_dir():
        return []
    return sorted(
        (
            p.name
            for p in CATALOGUS_ROOT.iterdir()
            if p.is_dir() and _ID_PART.fullmatch(p.name)
        ),
        key=len,
        reverse=True,
    )


def _known_variant_ids(zangstuk: str) -> list[str]:
    root = CATALOGUS_ROOT / zangstuk
    if not root.is_dir():
        return []
    return sorted(
        (
            p.name
            for p in root.iterdir()
            if p.is_dir() and _ID_PART.fullmatch(p.name)
        ),
        key=len,
        reverse=True,
    )


def id_from_publication_stem(stam: str) -> str | None:
    """Leid ``zangstuk/variant/uitvoeringsvorm`` af uit publicatiestam.

    Gebruikt bestaande catalogusmappen (langste match) zodat ids met streepjes
    in meerdere lagen eenduidig blijven. Geen unieke match → ``None``.
    """
    stam = stam.strip().lower().strip("-")
    if not stam or "/" in stam:
        return None

    for zangstuk in _known_zangstuk_ids():
        prefix = f"{zangstuk}-"
        if not stam.startswith(prefix):
            continue
        rest = stam[len(prefix) :]
        if not rest:
            continue
        for variant in _known_variant_ids(zangstuk):
            vprefix = f"{variant}-"
            if not rest.startswith(vprefix):
                continue
            uv = rest[len(vprefix) :]
            if uv and _ID_PART.fullmatch(uv):
                return f"{zangstuk}/{variant}/{uv}"
        # Nieuw variant-id: rest = ``{variant}-{uv}`` met bekende uv-suffix.
        for uv in sorted(UITVOERINGSVORM_LINK_TITLES, key=len, reverse=True):
            usuf = f"-{uv}"
            if rest.endswith(usuf):
                variant = rest[: -len(usuf)]
                if variant and _ID_PART.fullmatch(variant):
                    return f"{zangstuk}/{variant}/{uv}"

    # Volledig nieuw zangstuk: probeer ``{zangstuk}-{variant}-{uv}`` via uv-suffix.
    for uv in sorted(UITVOERINGSVORM_LINK_TITLES, key=len, reverse=True):
        usuf = f"-{uv}"
        if not stam.endswith(usuf):
            continue
        left = stam[: -len(usuf)]
        for zangstuk in _known_zangstuk_ids():
            prefix = f"{zangstuk}-"
            if left.startswith(prefix):
                variant = left[len(prefix) :]
                if variant and _ID_PART.fullmatch(variant):
                    return f"{zangstuk}/{variant}/{uv}"
        # Geen bekend zangstuk: één streepje-splitsing (zangstuk-variant).
        if "-" in left:
            zangstuk, variant = left.split("-", 1)
            if (
                zangstuk
                and variant
                and _ID_PART.fullmatch(zangstuk)
                and _ID_PART.fullmatch(variant)
            ):
                return f"{zangstuk}/{variant}/{uv}"
    return None


def is_generic_leaf_title(title: str, zangstuk: str) -> bool:
    """True als leaf-title alleen het zangstuk-id nabootst (te kaal voor zoeken)."""
    t = (title or "").strip().strip("\"'").lower()
    if not t:
        return True
    z = zangstuk.strip().lower()
    return t in {z, z.replace("-", " ")}


def id_from_path(path: Path) -> str | None:
    try:
        rel = path.resolve().relative_to(CATALOGUS_ROOT.resolve())
    except ValueError:
        return None
    parts = rel.parts
    if len(parts) < 3:
        return None
    candidate = "/".join(parts[:3])
    try:
        parse_id(candidate)
    except ValueError:
        return None
    return candidate


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


def alias_van_of(variant_id: str) -> str | None:
    index = variant_folder(variant_id) / "_index.md"
    if not index.is_file():
        return None
    raw = _fm_value(index.read_text(encoding="utf-8"), "alias_van")
    return raw or None


def under_alias_variant(path: Path) -> bool:
    try:
        rel = path.resolve().relative_to(CATALOGUS_ROOT.resolve())
    except ValueError:
        return False
    if len(rel.parts) < 2:
        return False
    try:
        return bool(alias_van_of(f"{rel.parts[0]}/{rel.parts[1]}"))
    except ValueError:
        return False


def resolve_id(value: str) -> str:
    """Herschrijf via variant-alias, anders ongewijzigd."""
    zangstuk, variant, uitvoeringsvorm = parse_id(value)
    target = alias_van_of(f"{zangstuk}/{variant}")
    if not target:
        return value
    tz, tv = parse_variant_id(target)
    return f"{tz}/{tv}/{uitvoeringsvorm}"


def leaf_folders() -> list[tuple[str, Path]]:
    found: list[tuple[str, Path]] = []
    if not CATALOGUS_ROOT.is_dir():
        return found
    for index in CATALOGUS_ROOT.rglob("index.md"):
        ident = id_from_path(index.parent)
        if not ident:
            continue
        if under_alias_variant(index.parent):
            continue
        found.append((ident, index.parent))
    return sorted(found, key=lambda item: item[0])
