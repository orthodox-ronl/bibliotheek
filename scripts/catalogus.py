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


def slash_to_stem(slash_id: str) -> str:
    """``a/b/c`` → ``a-b-c`` (ook voor 1 of 2 segmenten)."""
    return slash_id.strip().strip("/").replace("/", "-")


def ref_folder(slash_id: str) -> Path:
    """Catalogusmap voor zangstuk, variant of leaf (slash-vorm)."""
    parts = slash_id.strip().strip("/").split("/")
    if not parts or parts == [""]:
        raise ValueError(f"leeg id {slash_id!r}")
    for part in parts:
        if not _ID_PART.fullmatch(part):
            raise ValueError(f"ongeldig id-segment {part!r} in {slash_id!r}")
    if len(parts) > 3:
        raise ValueError(f"verwacht max 3 segmenten, kreeg {slash_id!r}")
    return CATALOGUS_ROOT.joinpath(*parts)


class AmbiguousRefError(ValueError):
    """Dash-vorm kan op meer dan één niveau slaan; vraag slash-vorm."""

    def __init__(self, value: str, options: list[tuple[str, str]]) -> None:
        self.value = value
        self.options = options
        opts = ", ".join(f"{lvl} {sid}" for lvl, sid in options)
        super().__init__(
            f"id {value!r} is ambigu ({opts}). "
            "Gebruik de slash-vorm, bijv. zangstuk/variant of "
            "zangstuk/variant/uitvoeringsvorm."
        )


def resolve_existing_ref(value: str) -> tuple[str, str]:
    """Bestaand catalogus-id → ``(niveau, slash-id)``.

    Niveau: ``zangstuk`` | ``variant`` | ``leaf``.
    Accepteert slash-vorm of publicatiestam/dash-vorm.
    """
    raw = value.strip().strip("/")
    if not raw:
        raise ValueError("leeg id")
    if "/" in raw:
        parts = raw.split("/")
        for part in parts:
            if not _ID_PART.fullmatch(part):
                raise ValueError(f"ongeldig id-segment {part!r} in {raw!r}")
        if len(parts) == 1:
            level, slash = "zangstuk", parts[0]
        elif len(parts) == 2:
            level, slash = "variant", raw
        elif len(parts) == 3:
            level, slash = "leaf", raw
        else:
            raise ValueError(f"verwacht max 3 segmenten, kreeg {raw!r}")
        if not ref_folder(slash).is_dir():
            raise ValueError(f"catalogusmap ontbreekt: {ref_folder(slash)}")
        return level, slash

    if not _ID_PART.fullmatch(raw):
        raise ValueError(f"ongeldig id {raw!r}")

    candidates: list[tuple[str, str]] = []
    if (CATALOGUS_ROOT / raw).is_dir():
        candidates.append(("zangstuk", raw))

    leaf = id_from_publication_stem(raw)
    if leaf and folder(leaf).is_dir():
        candidates.append(("leaf", leaf))

    for zangstuk in _known_zangstuk_ids():
        prefix = f"{zangstuk}-"
        if not raw.startswith(prefix):
            continue
        variant = raw[len(prefix) :]
        if not variant or not _ID_PART.fullmatch(variant):
            continue
        vdir = CATALOGUS_ROOT / zangstuk / variant
        if vdir.is_dir():
            candidates.append(("variant", f"{zangstuk}/{variant}"))

    # Uniek per slash-id
    by_slash: dict[str, str] = {}
    for level, slash in candidates:
        by_slash.setdefault(slash, level)
    unique = [(lvl, sid) for sid, lvl in by_slash.items()]
    # Preferentie als zangstuk-map én iets anders: zangstuk wint alleen
    # als raw exact die map is (al zo). Bij meerdere slash-ids → ambigu.
    if not unique:
        raise ValueError(
            f"onbekend id {raw!r}. Gebruik slash-vorm "
            "(zangstuk, zangstuk/variant of "
            "zangstuk/variant/uitvoeringsvorm)."
        )
    if len(unique) > 1:
        raise AmbiguousRefError(raw, unique)
    return unique[0]


def complete_new_ref(old_level: str, old_slash: str, new_raw: str) -> tuple[str, str]:
    """Nieuw id op hetzelfde niveau als ``old`` (slash of kortere vorm).

    Kortere vorm: alleen het laatste segment, bijv. oud
    ``ektinia/vredes/hemelum`` + nieuw ``groningen`` →
    ``ektinia/vredes/groningen``.
    """
    raw = new_raw.strip().strip("/")
    if not raw:
        raise ValueError("leeg nieuw id")
    old_parts = old_slash.split("/")
    if "/" in raw:
        parts = raw.split("/")
    else:
        if not _ID_PART.fullmatch(raw):
            raise ValueError(f"ongeldig id {raw!r}")
        # Volledige dash-stam op hetzelfde niveau?
        if old_level == "zangstuk":
            parts = [raw]
        elif old_level == "variant":
            # ``z-v`` of alleen ``v``
            if raw.count("-") >= 1:
                try:
                    level, slash = resolve_existing_ref(raw)
                except (ValueError, AmbiguousRefError):
                    level, slash = "", ""
                if level == "variant":
                    return level, slash
                # Nieuw (bestaat nog niet): split zangstuk-prefix
                for zangstuk in _known_zangstuk_ids():
                    prefix = f"{zangstuk}-"
                    if raw.startswith(prefix):
                        variant = raw[len(prefix) :]
                        if variant and _ID_PART.fullmatch(variant):
                            return "variant", f"{zangstuk}/{variant}"
                parts = old_parts[:-1] + [raw]
            else:
                parts = old_parts[:-1] + [raw]
        else:  # leaf
            leaf = id_from_publication_stem(raw)
            if leaf:
                return "leaf", leaf
            for zangstuk in _known_zangstuk_ids():
                prefix = f"{zangstuk}-"
                if not raw.startswith(prefix):
                    continue
                rest = raw[len(prefix) :]
                for variant in _known_variant_ids(zangstuk):
                    vprefix = f"{variant}-"
                    if rest.startswith(vprefix):
                        uv = rest[len(vprefix) :]
                        if uv and _ID_PART.fullmatch(uv):
                            return "leaf", f"{zangstuk}/{variant}/{uv}"
            if "-" in raw:
                raise ValueError(
                    f"kon dash-vorm {raw!r} niet splitsen; "
                    "gebruik slash-vorm zangstuk/variant/uitvoeringsvorm"
                )
            parts = old_parts[:-1] + [raw]

    for part in parts:
        if not _ID_PART.fullmatch(part):
            raise ValueError(f"ongeldig id-segment {part!r} in {raw!r}")
    if len(parts) > 3:
        raise ValueError(f"verwacht max 3 segmenten, kreeg {raw!r}")

    if old_level == "zangstuk":
        if len(parts) != 1:
            raise ValueError(
                f"oud is zangstuk-id; nieuw moet één segment zijn, kreeg {raw!r}"
            )
        return "zangstuk", parts[0]
    if old_level == "variant":
        if len(parts) == 1:
            parts = [old_parts[0], parts[0]]
        if len(parts) != 2:
            raise ValueError(
                f"oud is variant; nieuw moet zangstuk/variant zijn, kreeg {raw!r}"
            )
        return "variant", "/".join(parts)
    # leaf
    if len(parts) == 1:
        parts = [old_parts[0], old_parts[1], parts[0]]
    if len(parts) == 2:
        raise ValueError(
            f"oud is uitvoeringsvorm; nieuw moet drie segmenten hebben "
            f"(of alleen de nieuwe uitvoeringsvorm), kreeg {raw!r}"
        )
    if len(parts) != 3:
        raise ValueError(f"ongeldig nieuw leaf-id {raw!r}")
    return "leaf", "/".join(parts)


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


def words_title(slug: str) -> str:
    """``johannes-de-theoloog`` → ``Johannes De Theoloog``."""
    parts: list[str] = []
    for w in slug.replace("-", " ").split():
        if not w:
            continue
        parts.append(w[:1].upper() + w[1:])
    return " ".join(parts)


def section_title(slug: str) -> str:
    """Titel/linkTitle voor zangstuk- of variant-sectie uit mapnaam."""
    if slug == "default":
        return "Standaard"
    return words_title(slug)


def derived_leaf_link_title(ident: str) -> str:
    """Leaf-linkTitle uit uitvoeringsvorm-id."""
    _z, _v, uv = parse_id(ident)
    return uitvoeringsvorm_link_title(uv)


def title_hint_from_source(path: Path) -> str | None:
    """Optionele paginatitel uit VSA/mvsa-frontmatter (``titel:`` / ``soort:``)."""
    if path.suffix.lower() not in {".vsa", ".mvsa"}:
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    if not text.lstrip().startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    fm = parts[1]
    titel = None
    soort = None
    for line in fm.splitlines():
        stripped = line.strip()
        low = stripped.lower()
        if low.startswith("titel:"):
            titel = stripped.split(":", 1)[1].strip().strip("\"'")
        elif low.startswith("soort:") and soort is None:
            soort = stripped.split(":", 1)[1].strip().strip("\"'")
    if not titel:
        return None
    if soort:
        s = soort.replace("-", " ")
        s = s[:1].upper() + s[1:] if s else s
        if not titel.lower().startswith(s.lower()):
            return f"{s} — {titel}"
    return titel


def derived_leaf_title_from_id(ident: str) -> str:
    """Leaf-title uitsluitend uit id: ``Kondak Variant (Hemelum)``."""
    zangstuk, variant, uv = parse_id(ident)
    return (
        f"{section_title(zangstuk)} {section_title(variant)} "
        f"({uitvoeringsvorm_link_title(uv)})"
    )


def derived_leaf_title(
    ident: str,
    *,
    source_paths: list[Path] | None = None,
    leaf_dir: Path | None = None,
) -> str:
    """Leaf-title: bron (VSA/mvsa) als die er is, anders uit id.

    ``source_paths`` = bestanden bij accepteer; ``leaf_dir`` = catalogusmap
    (zoek/bouw). Brontitel krijgt het uitvoeringsvorm-label tussen haakjes
    als dat er nog niet in staat.
    """
    paths: list[Path] = []
    if source_paths:
        paths.extend(source_paths)
    if leaf_dir is not None and leaf_dir.is_dir():
        paths.extend(sorted(leaf_dir.glob("*.vsa")))
        paths.extend(sorted(leaf_dir.glob("*.mvsa")))
    _z, _v, uv = parse_id(ident)
    uv_label = uitvoeringsvorm_link_title(uv)
    for path in paths:
        hint = title_hint_from_source(path)
        if not hint:
            continue
        if uv_label.lower() not in hint.lower():
            return f"{hint} ({uv_label})"
        return hint
    return derived_leaf_title_from_id(ident)


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
