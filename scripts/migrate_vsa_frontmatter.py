#!/usr/bin/env python3
"""Migreer catalogus-``.vsa``/``.mvsa``-frontmatter naar het proefschema.

Zie ``docs/specs/vsa-frontmatter.md``. Stappen:

1. Oude sleutels (``identificatie``, ``muziek``, ``genre``, …) → canonieke vorm
2. Nuttige broninfo uit ``herkomst_vsa_demo`` overzetten; dump weg
3. Soort/toon/taal/gelegenheid/arranger uit pad aanvullen waar dat iets toevoegt
4. Ongedocumenteerd/leeg strippen (zelfde regels als ``frontmatter_canoniek``)

Notatie-body blijft onaangeroerd (behalve optioneel migratie-HTML-commentaar).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

from frontmatter_canoniek import (
    ALLOWED_NESTED,
    ALLOWED_TOP,
    FM_RE,
    dump_fm,
    prune,
)

REPO = Path(__file__).resolve().parents[1]
CATALOGUS = REPO / "content-source" / "catalogus"

# feestdag-hints uit zangstuk-/variant-id → gelegenheid-label
GELEGENHEID_HINTS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"geboorte-moeder-gods|geboorte-mg"), "8 sep — Geboorte van de Moeder Gods"),
    (re.compile(r"kruisverheffing"), "14 sep — Kruisverheffing"),
    (re.compile(r"transfiguratie|verheerlijking|thabor"), "6 aug — Verheerlijking op de berg Thabor"),
    (re.compile(r"ontslapen-moeder-gods|ontslaping"), "15 aug — Ontslapen van de Moeder Gods"),
    (re.compile(r"onthoofding-johannes|onthoofding"), "29 aug — Onthoofding Johannes de Doper"),
    (re.compile(r"geboorte-johannes"), "24 jun — Geboorte Johannes de Voorloper"),
    (re.compile(r"tempelgang-moeder-gods"), "21 nov — Tempelgang van de Moeder Gods"),
    (re.compile(r"besnijdenis"), "1 jan — Besnijdenis des Heren"),
    (re.compile(r"nikolaas-van-myra|nicolaas"), "6 dec — Nikolaas van Myra"),
    (re.compile(r"apostel-andreas"), "30 nov — Apostel Andreas"),
    (re.compile(r"maria-magdalena"), "22 jul — Maria Magdalena"),
    (re.compile(r"profeet-elia"), "20 jul — Profeet Elia"),
    (re.compile(r"marina"), "17 jul — Grootmartelares Marina"),
    (re.compile(r"mantel-moeder-gods|blacherna"), "2 jul — Mantel van de Moeder Gods"),
    (re.compile(r"johannes.*shanghai|shanghai"), "2 jul — Johannes van Shanghai"),
    (re.compile(r"icoon-moeder-gods-vladimir|vladimir"), "Icoon Moeder Gods van Vladimir"),
    (re.compile(r"silouan"), "24 sep — Silouan de Athoniet"),
    (re.compile(r"apostel-thaddeos|thaddeos"), "Apostel Thaddeos"),
    (re.compile(r"gregorios-van-utrecht"), "Gregorios van Utrecht"),
]

TOON_RE = re.compile(r"(?:^|-)toon-([1-8])(?:-|$)")
FEESTDAG_RE = re.compile(r'(?m)^feestdag:\s*["\']?([^"\'\n]+)')
SOURCE_RE = re.compile(r'(?m)^source:\s*["\']?([^"\'\n]+)')

BOOKISH = re.compile(
    r"(?i)\b("
    r"liturgikon|meneon|vokn|heiligenjaar|horologion|apostel|"
    r"koormap|jewsewy|rode\s+gebedenboek"
    r")\b"
)
KOORINSTRUCTIE = re.compile(r"(?i)koorinstructie")
COMMENT_DROP = re.compile(
    r"(?m)^\s*<!--\s*(Bronbestand:|Voorheen:|Genre:|Bron: content-source|"
    r"extractie:|stap2_|Bibliotheek-id:|Publicatiestam:).*?-->\s*\n?"
)


def _catalogus_id(path: Path) -> tuple[str, str, str] | None:
    try:
        rel = path.relative_to(CATALOGUS)
    except ValueError:
        return None
    parts = rel.parts
    if len(parts) < 4:
        return None
    return parts[0], parts[1], parts[2]


def _as_bron_map(bron: object) -> dict:
    if isinstance(bron, dict):
        return dict(bron)
    if isinstance(bron, str) and bron.strip():
        return {"uitgangspunt": bron.strip()}
    return {}


def _set_if_empty(d: dict, key: str, value: object) -> None:
    if value is None or value == "" or value == [] or value == {}:
        return
    cur = d.get(key)
    if cur is None or cur == "" or cur == [] or cur == {}:
        d[key] = value


def _merge_bewerking(bron: dict, note: str) -> None:
    note = note.strip()
    if not note:
        return
    cur = (bron.get("bewerking") or "").strip()
    if not cur:
        bron["bewerking"] = note
        return
    if note.lower() in cur.lower():
        return
    bron["bewerking"] = f"{cur}; {note}"


def _sources_from_herkomst(herkomst: object) -> list[str]:
    out: list[str] = []
    if not isinstance(herkomst, dict):
        return out
    for item in herkomst.get("bronnen") or []:
        if not isinstance(item, dict):
            continue
        block = item.get("bron_md_frontmatter") or ""
        for m in SOURCE_RE.finditer(str(block)):
            s = m.group(1).strip().rstrip('"').strip()
            if s and s not in out:
                out.append(s)
        for m in FEESTDAG_RE.finditer(str(block)):
            # feestdag alleen via gelegenheid elders
            _ = m
    return out


def _feestdag_from_herkomst(herkomst: object) -> str | None:
    if not isinstance(herkomst, dict):
        return None
    for item in herkomst.get("bronnen") or []:
        if not isinstance(item, dict):
            continue
        block = str(item.get("bron_md_frontmatter") or "")
        m = FEESTDAG_RE.search(block)
        if m:
            raw = m.group(1).strip().rstrip('"').strip()
            if raw:
                return raw
    return None


def _pick_uitgangspunt(candidates: list[str]) -> str | None:
    if not candidates:
        return None
    books = [c for c in candidates if BOOKISH.search(c) and not KOORINSTRUCTIE.search(c)]
    if books:
        # Prefer longest / most specific (often with page)
        books.sort(key=lambda s: (len(s), s), reverse=True)
        return books[0]
    # Koorinstructie of lokale praktijk mag uitgangspunt zijn als dat de bron is
    return candidates[0]


def _norm_uitgangspunt(s: str) -> str:
    s = s.strip()
    # Gedateerde koorinstructie → stabiele bronlabel
    if KOORINSTRUCTIE.search(s) and re.search(r"(?i)hemelum", s):
        return "Koorinstructie Hemelum"
    if KOORINSTRUCTIE.search(s) and re.search(r"(?i)groningen", s):
        return "Koorinstructie Groningen"
    # Normaliseer veelvoorkomende schrijfwijzen
    repl = [
        (re.compile(r"(?i)^koormap\s+groningen$"), "Koormap Groningen"),
        (re.compile(r"(?i)^groningen$"), "Koormap Groningen"),
        (re.compile(r"(?i)^liturgicon\b"), "Liturgikon"),
        (re.compile(r"(?i)^liturgikon\s*\((p\.[^)]+)\)"), r"Liturgikon, \1"),
        (re.compile(r"(?i)^liturgikon,\s*p\.?\s*"), "Liturgikon, p."),
        (re.compile(r"(?i)^hemelum$"), "Hemelum"),
        (re.compile(r"(?i)^praktijk\s+hemelum$"), "Hemelum"),
        (re.compile(r"(?i)^h\.\s*liturgie\s*-?\s*koormap\s*-?\s*groningen$"), "Koormap Groningen"),
        (re.compile(r"(?i)^praktijk\s+in\s+groningen$"), "Koormap Groningen"),
    ]
    for rx, to in repl:
        s2 = rx.sub(to, s)
        if s2 != s:
            s = s2
    return s


def _uitgangspunt_from_uv(uv: str) -> str | None:
    """Fallback-bron als er geen expliciete bron in metadata stond."""
    if uv.startswith("hemelum"):
        return "Hemelum"
    if uv.startswith("groningen"):
        return "Koormap Groningen"
    if uv.startswith("liturgikon"):
        return "Liturgikon"
    if uv.startswith("meneon"):
        return "Meneon I"
    if uv.startswith("asten"):
        return "Asten"
    if uv.startswith("heiligenjaar"):
        return "Heiligenjaar"
    if uv.startswith("rode-gebedenboek"):
        return "Rode gebedenboek"
    return None


def _arranger_from_uv(uv: str) -> str | None:
    base = uv.split("-")[0] if uv else ""
    mapping = {
        "hemelum": "Hemelum",
        "groningen": "Groningen",
        "asten": "Asten",
        "heiligenjaar": None,
        "liturgikon": None,
        "meneon": None,
        "rode": None,
    }
    if uv.startswith("meneon"):
        return None
    if uv.startswith("hemelum"):
        return "Hemelum"
    if uv.startswith("groningen"):
        return "Groningen"
    return mapping.get(base)


def _taal_from_uv(uv: str) -> str | None:
    if uv.endswith("-ksl") or "-ksl-" in uv:
        return "ksl"
    if uv.endswith("-nl") or "-nl-" in uv:
        return "nl"
    return None


def _toon_from_ids(zangstuk: str, variant: str) -> int | None:
    for blob in (zangstuk, variant):
        m = TOON_RE.search(blob)
        if m:
            return int(m.group(1))
    return None


def _gelegenheid_from_ids(zangstuk: str, variant: str, herkomst: object) -> str | None:
    blob = f"{zangstuk}/{variant}"
    for rx, label in GELEGENHEID_HINTS:
        if rx.search(blob):
            return label
    fee = _feestdag_from_herkomst(herkomst)
    if fee:
        # Alleen feestdag-datum uit yaml → korte label; padhint mist
        return fee
    return None


def _soort_from_zangstuk(zangstuk: str) -> str:
    return zangstuk


def migrate_data(data: dict, path: Path) -> dict:
    out = dict(data)
    ids = _catalogus_id(path)
    zangstuk = variant = uv = ""
    if ids:
        zangstuk, variant, uv = ids

    # --- muziek → plat ---
    muziek = out.pop("muziek", None)
    if isinstance(muziek, dict):
        for k in ("do", "mode", "tempo"):
            if muziek.get(k) is not None:
                _set_if_empty(out, k, muziek[k])

    # --- identificatie ---
    ident = out.pop("identificatie", None)
    if isinstance(ident, dict):
        title = ident.get("title")
        if title:
            _set_if_empty(out, "titel", title)
            part = out.get("partituur") if isinstance(out.get("partituur"), dict) else {}
            part = dict(part)
            _set_if_empty(part, "title", title)
            if ident.get("composer"):
                _set_if_empty(part, "composer", ident["composer"])
            if part:
                out["partituur"] = part
        if ident.get("tone") is not None:
            _set_if_empty(out, "toon", ident["tone"])
        if ident.get("language"):
            _set_if_empty(out, "taal", ident["language"])
        if ident.get("bron"):
            bron = _as_bron_map(out.get("bron"))
            _set_if_empty(bron, "uitgangspunt", _norm_uitgangspunt(str(ident["bron"])))
            out["bron"] = bron

    # --- platte legacy ---
    if "genre" in out:
        _set_if_empty(out, "soort", out.pop("genre"))
    else:
        out.pop("genre", None)
    if "tone" in out:
        _set_if_empty(out, "toon", out.pop("tone"))
    else:
        out.pop("tone", None)
    out.pop("template", None)

    if "title" in out:
        title = out.pop("title")
        if title:
            _set_if_empty(out, "titel", title)
            part = out.get("partituur") if isinstance(out.get("partituur"), dict) else {}
            part = dict(part)
            _set_if_empty(part, "title", title)
            if part:
                out["partituur"] = part

    if "sources" in out:
        sources = out.pop("sources")
        bron = _as_bron_map(out.get("bron"))
        if isinstance(sources, list):
            texts = [str(x).strip() for x in sources if str(x).strip()]
        elif isinstance(sources, str) and sources.strip():
            texts = [sources.strip()]
        else:
            texts = []
        pick = _pick_uitgangspunt(texts)
        if pick:
            _set_if_empty(bron, "uitgangspunt", _norm_uitgangspunt(pick))
        out["bron"] = bron

    # bron als kale string
    if "bron" in out and isinstance(out["bron"], str):
        out["bron"] = {"uitgangspunt": _norm_uitgangspunt(out["bron"])}
    elif isinstance(out.get("bron"), dict):
        bron0 = dict(out["bron"])
        if bron0.get("uitgangspunt"):
            bron0["uitgangspunt"] = _norm_uitgangspunt(str(bron0["uitgangspunt"]))
        # Redundante bewerking weg als uitgangspunt al koorinstructie is
        uit = str(bron0.get("uitgangspunt") or "")
        bew = str(bron0.get("bewerking") or "")
        if KOORINSTRUCTIE.search(uit) and "koorinstructie" in bew.lower():
            bron0.pop("bewerking", None)
        out["bron"] = bron0

    # alias uitgesteld → weg (zoekaliases later)
    out.pop("alias", None)
    out.pop("aliases", None)
    out.pop("based-on", None)
    out.pop("based_on", None)

    # --- herkomst_vsa_demo → bron / gelegenheid ---
    herkomst = out.pop("herkomst_vsa_demo", None)
    src_cands = _sources_from_herkomst(herkomst)
    bron = _as_bron_map(out.get("bron"))
    pick = _pick_uitgangspunt([_norm_uitgangspunt(s) for s in src_cands])
    if pick:
        # Verrijk pagina-info als uitgangspunt nog generiek is
        cur = (bron.get("uitgangspunt") or "").strip()
        if not cur:
            bron["uitgangspunt"] = pick
        elif cur.lower() in {"liturgikon", "hemelum", "koormap groningen"} and len(pick) > len(cur) + 3:
            if BOOKISH.search(pick) or KOORINSTRUCTIE.search(pick):
                bron["uitgangspunt"] = pick
    # Lokale praktijk als bewerking wanneer uitgangspunt een boek is
    arr = _arranger_from_uv(uv) if uv else None
    if arr and bron.get("uitgangspunt"):
        uit = str(bron["uitgangspunt"])
        bew = str(bron.get("bewerking") or "")
        if (
            BOOKISH.search(uit)
            and arr.lower() not in uit.lower()
            and arr.lower() not in bew.lower()
        ):
            _merge_bewerking(bron, f"zetting/praktijk {arr}")
    # Fallback: uitvoeringsvorm als enige bronaanwijzing
    if uv and not (bron.get("uitgangspunt") or "").strip():
        fb = _uitgangspunt_from_uv(uv)
        if fb:
            bron["uitgangspunt"] = fb
    # Opschonen: oude "gebruikt via koorinstructie X" naast zetting/praktijk
    bew = str(bron.get("bewerking") or "")
    if bew:
        parts = [p.strip() for p in bew.split(";") if p.strip()]
        cleaned: list[str] = []
        for part in parts:
            if part.lower().startswith("gebruikt via koorinstructie"):
                continue
            if part not in cleaned:
                cleaned.append(part)
        if cleaned:
            bron["bewerking"] = "; ".join(cleaned)
        else:
            bron.pop("bewerking", None)
    if bron:
        out["bron"] = bron

    # Playback-defaults (Coria / catalogus-conventie) als die nog ontbreken
    _set_if_empty(out, "do", "F4")
    _set_if_empty(out, "mode", "major")
    _set_if_empty(out, "tempo", 130)

    # soort / toon / taal / gelegenheid / partituur.arranger uit pad
    if zangstuk:
        _set_if_empty(out, "soort", _soort_from_zangstuk(zangstuk))
    toon = _toon_from_ids(zangstuk, variant) if ids else None
    if toon is not None:
        _set_if_empty(out, "toon", toon)
    if uv:
        taal = _taal_from_uv(uv)
        if taal:
            _set_if_empty(out, "taal", taal)
        elif "taal" not in out and zangstuk:
            # NL is default voor catalogus-notatie zonder -ksl
            _set_if_empty(out, "taal", "nl")
        arr = _arranger_from_uv(uv)
        if arr:
            part = out.get("partituur") if isinstance(out.get("partituur"), dict) else {}
            part = dict(part)
            _set_if_empty(part, "arranger", arr)
            if part:
                out["partituur"] = part

    gel = _gelegenheid_from_ids(zangstuk, variant, herkomst) if ids else None
    if gel:
        _set_if_empty(out, "gelegenheid", gel)

    # gebruikt-in behouden (lijst)
    gi = out.get("gebruikt-in")
    if isinstance(gi, str) and gi.strip():
        out["gebruikt-in"] = [gi.strip()]
    elif isinstance(gi, list):
        out["gebruikt-in"] = [str(x).strip() for x in gi if str(x).strip()]

    # toon als string "4" → int
    if "toon" in out and not isinstance(out["toon"], int):
        try:
            out["toon"] = int(str(out["toon"]).strip())
        except ValueError:
            pass

    pruned = prune(out, ALLOWED_TOP)
    return pruned if isinstance(pruned, dict) else {}


def migrate_text(text: str, path: Path, *, strip_comments: bool) -> tuple[str, list[str]]:
    notes: list[str] = []
    m = FM_RE.match(text)
    if not m:
        notes.append("geen YAML-frontmatter")
        return text, notes
    raw = m.group(1)
    body = text[m.end() :]
    data = yaml.safe_load(raw) or {}
    if not isinstance(data, dict):
        notes.append("frontmatter is geen mapping — overgeslagen")
        return text, notes

    before_keys = set(data.keys())
    new_data = migrate_data(data, path)
    after_keys = set(new_data.keys())
    removed = sorted(before_keys - after_keys)
    added = sorted(after_keys - before_keys)
    if removed:
        notes.append("weg: " + ", ".join(removed))
    if added:
        notes.append("nieuw/gevuld: " + ", ".join(added))

    if strip_comments:
        new_body, n = COMMENT_DROP.subn("", body)
        if n:
            notes.append(f"migratie-commentaar weg ({n})")
            body = new_body

    if not new_data:
        notes.append("frontmatter leeg na migratie")
        return body.lstrip("\n"), notes

    new_text = dump_fm(new_data) + (body if body.startswith("\n") else body.lstrip("\n"))
    if new_text == text and not notes:
        notes.append("(geen wijzigingen)")
    return new_text, notes


def collect_targets(root: Path) -> list[Path]:
    out: list[Path] = []
    for p in sorted(root.rglob("*")):
        if p.suffix.lower() not in {".vsa", ".mvsa"}:
            continue
        if "artefacten_handmatig" in p.parts:
            continue
        if "input" in p.parts:
            continue
        out.append(p)
    return out


def main(argv: list[str] | None = None) -> int:
    # Zorg dat gebruikt-in in de gate zit (spec)
    if "gebruikt-in" not in ALLOWED_TOP:
        ALLOWED_TOP.add("gebruikt-in")

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "root",
        nargs="?",
        type=Path,
        default=CATALOGUS,
        help="Zoekroot (default: content-source/catalogus)",
    )
    p.add_argument("--dry-run", action="store_true", help="Alleen rapporteren")
    p.add_argument(
        "--keep-migration-comments",
        action="store_true",
        help="Laat Bronbestand:/Voorheen:-HTML-commentaar staan",
    )
    args = p.parse_args(argv)
    root = args.root if args.root.is_absolute() else REPO / args.root
    paths = collect_targets(root)
    changed = 0
    for path in paths:
        text = path.read_text(encoding="utf-8")
        new_text, notes = migrate_text(
            text,
            path,
            strip_comments=not args.keep_migration_comments,
        )
        rel = path.relative_to(REPO).as_posix()
        if new_text != text:
            changed += 1
            print(f"* {rel}")
            for n in notes:
                print(f"    - {n}")
            if not args.dry_run:
                path.write_text(new_text, encoding="utf-8", newline="\n")
        elif notes and notes != ["(geen wijzigingen)"]:
            print(f"= {rel}")
            for n in notes:
                print(f"    - {n}")

    print(
        f"\nKlaar: {changed}/{len(paths)} bestanden "
        f"{'(dry-run)' if args.dry_run else 'geschreven'}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
