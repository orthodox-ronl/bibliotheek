"""Bibliotheek-root: bibliotheek-id <-> pad.

Id: ``zangstuk/variant/uitvoeringsvorm`` (``[a-z0-9_-]+``, drie lagen).
Publicatiestam: ``zangstuk-variant-uitvoeringsvorm``.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BIBLIOTHEEK_ROOT = REPO_ROOT / "content-source" / "bibliotheek"
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
    return BIBLIOTHEEK_ROOT / zangstuk / variant / uitvoeringsvorm


def variant_folder(value: str) -> Path:
    zangstuk, variant = parse_variant_id(value)
    return BIBLIOTHEEK_ROOT / zangstuk / variant


def stem(value: str) -> str:
    zangstuk, variant, uitvoeringsvorm = parse_id(value)
    return f"{zangstuk}-{variant}-{uitvoeringsvorm}"


def id_from_path(path: Path) -> str | None:
    try:
        rel = path.resolve().relative_to(BIBLIOTHEEK_ROOT.resolve())
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
        rel = path.resolve().relative_to(BIBLIOTHEEK_ROOT.resolve())
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
    if not BIBLIOTHEEK_ROOT.is_dir():
        return found
    for index in BIBLIOTHEEK_ROOT.rglob("index.md"):
        ident = id_from_path(index.parent)
        if not ident:
            continue
        if under_alias_variant(index.parent):
            continue
        found.append((ident, index.parent))
    return sorted(found, key=lambda item: item[0])
