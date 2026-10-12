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
    """Invoer kan op meer dan één catalogus-id slaan; vraag eenduidige vorm."""

    def __init__(self, value: str, options: list[tuple[str, str]]) -> None:
        self.value = value
        self.options = options
        opts = ", ".join(f"{lvl} {sid}" for lvl, sid in options)
        super().__init__(
            f"id {value!r} is ambigu ({opts}). "
            "Kies een eenduidige vorm, bijv. zangstuk/variant of "
            "zangstuk/variant/uitvoeringsvorm "
            "(of content-source\\catalogus\\…)."
        )


def interactive_disambiguate(
    exc: AmbiguousRefError,
    *,
    help_text: str,
    prefix: str = "",
) -> tuple[str, str] | str | None:
    """Genummerde voorstellen bij ambiguïteit.

    Terugkeerwaarde:

    - ``(niveau, slash-id)`` bij nummer of Enter (Enter = eerste voorstel)
    - ``str`` bij zelf getypte eenduidige vorm (caller resolved opnieuw)
    - ``None`` als de gebruiker stopt (twee keer leeg / EOF)

    ``?`` toont ``help_text``.
    """
    label = f"{prefix}: " if prefix else ""
    print(f"{label}{exc}", flush=True)
    for i, (_lvl, sid) in enumerate(exc.options, 1):
        print(f"  {i}. {sid}", flush=True)
    print(
        "Typ nummer of eenduidige vorm (Enter = 1, ? voor uitleg).",
        flush=True,
    )
    prompt = "Keuze: "
    while True:
        try:
            value = input(prompt).strip()
        except EOFError:
            return None
        if value == "?":
            print(flush=True)
            print(help_text.rstrip(), flush=True)
            print(flush=True)
            continue
        if not value:
            return exc.options[0]
        if value.isdigit():
            idx = int(value)
            if 1 <= idx <= len(exc.options):
                return exc.options[idx - 1]
            print(
                f"Kies een nummer van 1 t/m {len(exc.options)}.",
                flush=True,
            )
            continue
        return value


def normalize_ref_input(value: str) -> str:
    """Normaliseer gebruikersinvoer naar relatieve catalogus-ref of stam.

    - trim + quotes weg
    - ``\\`` → ``/``
    - strip repo-root en ``content-source/catalogus/``
    - bestaande map onder catalogus → slash-id (1–3 segmenten)
    """
    s = value.strip().strip('"').strip("'")
    if not s:
        return ""
    s = s.replace("\\", "/")

    # Absoluut pad of bestaand pad t.o.v. repo → resolve waar mogelijk
    candidate = Path(s)
    resolved: Path | None = None
    if candidate.is_absolute():
        try:
            resolved = candidate.resolve()
        except OSError:
            resolved = None
    else:
        under_repo = (REPO_ROOT / s).resolve()
        if under_repo.exists():
            resolved = under_repo
        else:
            under_cat = (CATALOGUS_ROOT / s).resolve()
            if under_cat.exists():
                resolved = under_cat

    if resolved is not None:
        try:
            rel = resolved.relative_to(CATALOGUS_ROOT.resolve())
        except ValueError:
            rel = None
        if rel is not None and rel.parts:
            parts = list(rel.parts[:3])
            if all(_ID_PART.fullmatch(p) for p in parts):
                return "/".join(parts)

    repo_posix = REPO_ROOT.resolve().as_posix().rstrip("/")
    if s.lower().startswith(repo_posix.lower() + "/"):
        s = s[len(repo_posix) + 1 :]

    lower = s.lower()
    for prefix in (
        "content-source/catalogus/",
        "./content-source/catalogus/",
        "content-source/catalogus",
    ):
        if lower.startswith(prefix):
            s = s[len(prefix) :].lstrip("/")
            break

    return s.strip().strip("/")


def _dedupe_ref_candidates(
    candidates: list[tuple[str, str]],
) -> list[tuple[str, str]]:
    by_slash: dict[str, str] = {}
    for level, slash in candidates:
        by_slash.setdefault(slash, level)
    return [(lvl, sid) for sid, lvl in by_slash.items()]


def _leaf_matches_variant_uv(variant: str, uv: str) -> list[tuple[str, str]]:
    """Alle leaves ``*/{variant}/{uv}`` die bestaan."""
    if not _ID_PART.fullmatch(variant) or not _ID_PART.fullmatch(uv):
        return []
    out: list[tuple[str, str]] = []
    for zangstuk in _known_zangstuk_ids():
        if (CATALOGUS_ROOT / zangstuk / variant / uv).is_dir():
            out.append(("leaf", f"{zangstuk}/{variant}/{uv}"))
    return out


def _leaf_matches_uv_only(uv: str) -> list[tuple[str, str]]:
    """Alle leaves ``*/*/{uv}`` die bestaan."""
    if not _ID_PART.fullmatch(uv):
        return []
    out: list[tuple[str, str]] = []
    for zangstuk in _known_zangstuk_ids():
        for variant in _known_variant_ids(zangstuk):
            if (CATALOGUS_ROOT / zangstuk / variant / uv).is_dir():
                out.append(("leaf", f"{zangstuk}/{variant}/{uv}"))
    return out


def _leaf_matches_variant_uv_dash(raw: str) -> list[tuple[str, str]]:
    """Dash-vorm ``{variant}-{uv}`` als unieke/suffix-match over zangstukken."""
    if not _ID_PART.fullmatch(raw) or "-" not in raw:
        return []
    out: list[tuple[str, str]] = []
    for zangstuk in _known_zangstuk_ids():
        for variant in _known_variant_ids(zangstuk):
            prefix = f"{variant}-"
            if not raw.startswith(prefix):
                continue
            uv = raw[len(prefix) :]
            if uv and _ID_PART.fullmatch(uv):
                if (CATALOGUS_ROOT / zangstuk / variant / uv).is_dir():
                    out.append(("leaf", f"{zangstuk}/{variant}/{uv}"))
    return out


def resolve_existing_ref(value: str) -> tuple[str, str]:
    """Bestaand catalogus-id → ``(niveau, slash-id)``.

    Niveau: ``zangstuk`` | ``variant`` | ``leaf``.

    Accepteert o.a.:

    - slash-vorm ``zangstuk/variant/uv`` (ook met ``\\``)
    - ``content-source/catalogus/…`` of pad t.o.v. repo-root
    - publicatiestam ``zangstuk-variant-uv``
    - unieke suffix ``variant/uv`` of ``variant-uv``
    - unieke uitvoeringsvorm alleen (``uv``) als die nergens anders voorkomt
    """
    raw = normalize_ref_input(value)
    if not raw:
        raise ValueError("leeg id")

    if "/" in raw:
        parts = raw.split("/")
        for part in parts:
            if not _ID_PART.fullmatch(part):
                raise ValueError(f"ongeldig id-segment {part!r} in {raw!r}")
        if len(parts) > 3:
            raise ValueError(f"verwacht max 3 segmenten, kreeg {raw!r}")

        if len(parts) == 3:
            slash = "/".join(parts)
            if not ref_folder(slash).is_dir():
                raise ValueError(f"catalogusmap ontbreekt: {ref_folder(slash)}")
            return "leaf", slash

        if len(parts) == 2:
            # Exact zangstuk/variant?
            if ref_folder(raw).is_dir():
                return "variant", raw
            # Anders: unieke leaf-suffix variant/uv
            matches = _dedupe_ref_candidates(
                _leaf_matches_variant_uv(parts[0], parts[1])
            )
            if not matches:
                raise ValueError(
                    f"catalogusmap ontbreekt voor {raw!r} "
                    "(geen zangstuk/variant en geen unieke variant/uv)"
                )
            if len(matches) > 1:
                raise AmbiguousRefError(raw, matches)
            return matches[0]

        # Één segment via slash-normalisatie → zelfde als stam zonder streepjes
        raw = parts[0]

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

    unique = _dedupe_ref_candidates(candidates)
    if not unique:
        # Geen zangstuk-/stam-treffer: probeer unieke suffix variant-uv
        dash_hits = _dedupe_ref_candidates(_leaf_matches_variant_uv_dash(raw))
        if len(dash_hits) == 1:
            return dash_hits[0]
        if len(dash_hits) > 1:
            raise AmbiguousRefError(raw, dash_hits)
        # Laatste kans: unieke uitvoeringsvorm-naam alleen
        uv_hits = _dedupe_ref_candidates(_leaf_matches_uv_only(raw))
        if len(uv_hits) == 1:
            return uv_hits[0]
        if len(uv_hits) > 1:
            raise AmbiguousRefError(raw, uv_hits)
        raise ValueError(
            f"onbekend id {raw!r}. Gebruik slash-vorm "
            "(zangstuk, zangstuk/variant of "
            "zangstuk/variant/uitvoeringsvorm) of "
            "content-source\\catalogus\\…."
        )
    if len(unique) > 1:
        raise AmbiguousRefError(raw, unique)
    return unique[0]


def _complete_from_parts(
    old_level: str,
    old_parts: list[str],
    parts: list[str],
    raw: str,
) -> tuple[str, str]:
    """Slash-segmenten → nieuw id op ``old_level`` (korter mag t.o.v. bron)."""
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
            return "variant", f"{old_parts[0]}/{parts[0]}"
        if len(parts) == 2:
            return "variant", "/".join(parts)
        raise ValueError(
            f"oud is variant; nieuw moet zangstuk/variant zijn "
            f"(of alleen de nieuwe variant), kreeg {raw!r}"
        )

    # leaf: 1 = alleen uv; 2 = variant/uv t.o.v. oud zangstuk; 3 = volledig
    if len(parts) == 1:
        return "leaf", f"{old_parts[0]}/{old_parts[1]}/{parts[0]}"
    if len(parts) == 2:
        return "leaf", f"{old_parts[0]}/{parts[0]}/{parts[1]}"
    if len(parts) == 3:
        return "leaf", "/".join(parts)
    raise ValueError(f"ongeldig nieuw leaf-id {raw!r}")


def complete_new_ref(old_level: str, old_slash: str, new_raw: str) -> tuple[str, str]:
    """Nieuw id op hetzelfde niveau als ``old`` (slash, pad of kortere vorm).

    Kortere vormen t.o.v. de bron:

    - alleen ``{uv}`` (ook met streepjes, bijv. ``hemelum-ksl``)
    - ``{variant}/{uv}`` of ``{variant}\\{uv}``
    - ``{variant}-{uv}`` onder hetzelfde zangstuk (bestaande variant-prefix)
    - volledig pad / publicatiestam (zelfde normalisatie als src)
    """
    raw = normalize_ref_input(new_raw)
    if not raw:
        raise ValueError("leeg nieuw id")
    old_parts = old_slash.split("/")

    if "/" in raw:
        return _complete_from_parts(old_level, old_parts, raw.split("/"), raw)

    if not _ID_PART.fullmatch(raw):
        raise ValueError(f"ongeldig id {raw!r}")

    if old_level == "zangstuk":
        return "zangstuk", raw

    if old_level == "variant":
        for zangstuk in _known_zangstuk_ids():
            prefix = f"{zangstuk}-"
            if raw.startswith(prefix):
                variant = raw[len(prefix) :]
                if variant and _ID_PART.fullmatch(variant):
                    return "variant", f"{zangstuk}/{variant}"
        # Alleen nieuwe variant-naam (mag streepjes bevatten)
        return "variant", f"{old_parts[0]}/{raw}"

    # leaf — eerst relatief ``variant-uv`` onder het zangstuk van de bron
    # (vóór stam-heuristiek, die anders bv. 15c-kastorski-groningen
    # als nieuw zangstuk 15c/… kan lezen)
    zangstuk = old_parts[0]
    rel_hits: list[tuple[str, str]] = []
    for variant in _known_variant_ids(zangstuk):
        vprefix = f"{variant}-"
        if not raw.startswith(vprefix):
            continue
        uv = raw[len(vprefix) :]
        if uv and _ID_PART.fullmatch(uv):
            rel_hits.append(("leaf", f"{zangstuk}/{variant}/{uv}"))
    unique = _dedupe_ref_candidates(rel_hits)
    if len(unique) == 1:
        return unique[0]
    if len(unique) > 1:
        raise AmbiguousRefError(raw, unique)

    # Volledige publicatiestam of bekend zangstuk-prefix
    leaf = id_from_publication_stem(raw)
    if leaf:
        return "leaf", leaf
    for zs in _known_zangstuk_ids():
        prefix = f"{zs}-"
        if not raw.startswith(prefix):
            continue
        rest = raw[len(prefix) :]
        for variant in _known_variant_ids(zs):
            vprefix = f"{variant}-"
            if rest.startswith(vprefix):
                uv = rest[len(vprefix) :]
                if uv and _ID_PART.fullmatch(uv):
                    return "leaf", f"{zs}/{variant}/{uv}"

    # Korte vorm: hele string = nieuwe uitvoeringsvorm (ook met streepjes)
    return "leaf", f"{old_parts[0]}/{old_parts[1]}/{raw}"


# Leesbare linkTitle voor bekende uitvoeringsvorm-ids (navigatie / broodkruimels).
UITVOERINGSVORM_LINK_TITLES: dict[str, str] = {
    "hemelum": "Hemelum",
    "hemelum-ksl": "Hemelum (ksl)",
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
