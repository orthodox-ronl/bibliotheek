"""Verwijder een catalogus-id (zangstuk, variant of uitvoeringsvorm).

Gebruik::

    bieb verwijder <id> [--dry-run] [--force]

``id``: slash- of stam-vorm (zoals ``bieb hernoem``). Bij ambiguïteit:
slash-vorm typen (``?`` voor uitleg).

Verwijdert de catalogusmap en bijbehorende bladermap-SVG’s. Koormappen
worden **niet** gewist (eigen beheerder); wel gerapporteerd als er
``bieb id=`` / ``alias_van`` of een 1:1-slotmap naar dit id wijst.

Zonder ``--force`` stopt het script als er zulke verwijzingen buiten de
te wissen catalogusmap staan. ``title`` / ``linkTitle`` worden niet
aangepast.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bieb_fs  # noqa: E402
from catalogus import (  # noqa: E402
    AmbiguousRefError,
    REPO_ROOT,
    interactive_disambiguate,
    ref_folder,
    resolve_existing_ref,
    slash_to_stem,
)

_TEXT_SUFFIXES = frozenset(
    {".md", ".vsa", ".mvsa", ".txt", ".yml", ".yaml", ".html", ".toml"}
)
_SKIP_DIR_NAMES = frozenset(
    {".git", "generated", "public", "node_modules", ".hugo_build.lock"}
)
KOORMAPPEN_ROOT = REPO_ROOT / "content-source" / "koormappen"

HELP_VERWIJDER = """\
bieb verwijder — catalogus-id verwijderen

Geef het id (slash- of stam-vorm):

  zangstuk              ektinia
  variant               ektinia/vredes     of  ektinia-vredes
  uitvoeringsvorm       ektinia/vredes/hemelum
                        of  ektinia-vredes-hemelum

Eerst dry-run: toont wat weggaat. Id-register-rijen en werkvoorraad-
doel-id ruimt het script zelf op. Koormap-pagina's niet: die meldt het
met bestand en regelnummer.

  bieb verwijder ektinia/vredes/hemelum --dry-run
  bieb verwijder ektinia/vredes/hemelum
  bieb verwijder ektinia/vredes/hemelum --force

--force: wis de catalogus ook als er nog handmatige refs (koormap e.d.)
zijn; die refs blijven dan staan tot jij ze fixt.
"""


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _print_help_block(text: str) -> None:
    print(flush=True)
    print(text.rstrip(), flush=True)
    print(flush=True)


def _prompt_line(message: str) -> str:
    try:
        return input(message).strip()
    except EOFError:
        return ""


def _prompt_until(message: str, help_text: str) -> str | None:
    while True:
        value = _prompt_line(message)
        if value == "?":
            _print_help_block(help_text)
            continue
        if not value:
            print(
                "Niets ingevuld. Typ een waarde, of ? voor uitleg, "
                "of Enter opnieuw om te stoppen.",
                flush=True,
            )
            again = _prompt_line(message)
            if again == "?":
                _print_help_block(help_text)
                continue
            if not again:
                return None
            return again
        return value


def _resolve_id(raw: str) -> tuple[str, str]:
    try:
        return resolve_existing_ref(raw)
    except AmbiguousRefError as exc:
        chosen = interactive_disambiguate(
            exc, help_text=HELP_VERWIJDER, prefix="verwijder"
        )
        if chosen is None:
            raise ValueError(
                "gestopt: geen id.\n"
                "Oplossing: typ een eenduidig id (slash-vorm) of kies uit de lijst."
            ) from exc
        if isinstance(chosen, tuple) and chosen[0]:
            return chosen
        text = chosen if isinstance(chosen, str) else chosen[1]
        return resolve_existing_ref(text)


def _ids_covered(level: str, slash: str) -> list[str]:
    """Slash-ids die met deze verwijdering verdwijnen (incl. nakomelingen)."""
    root = ref_folder(slash)
    covered = [slash]
    if level == "leaf":
        return covered
    if level == "variant":
        for child in sorted(p for p in root.iterdir() if p.is_dir()):
            covered.append(f"{slash}/{child.name}")
        return covered
    # zangstuk
    for variant in sorted(p for p in root.iterdir() if p.is_dir()):
        vslash = f"{slash}/{variant.name}"
        covered.append(vslash)
        for uv in sorted(p for p in variant.iterdir() if p.is_dir()):
            covered.append(f"{vslash}/{uv.name}")
    return covered


def _needles_for(slash_ids: list[str]) -> list[str]:
    """Zoektermen: slash-id en stam, langste eerst."""
    needles: list[str] = []
    for sid in slash_ids:
        needles.append(sid)
        stem = slash_to_stem(sid)
        if stem != sid:
            needles.append(stem)
    # Uniek, langste eerst (voorkomt dubbele treffers in rapport)
    uniq = sorted(set(needles), key=len, reverse=True)
    return uniq


def _iter_scan_files() -> list[Path]:
    roots = [REPO_ROOT / "content-source", REPO_ROOT / "docs"]
    out: list[Path] = []
    for root in roots:
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if any(part in _SKIP_DIR_NAMES for part in path.parts):
                continue
            if path.suffix.lower() not in _TEXT_SUFFIXES:
                continue
            out.append(path)
    return out


def _find_dangling(
    *,
    delete_root: Path,
    needles: list[str],
) -> list[tuple[Path, int, int | None, str]]:
    """Treffers buiten ``delete_root``: (pad, regel, kolom|None, snippet)."""
    hits: list[tuple[Path, int, int | None, str]] = []
    try:
        delete_resolved = delete_root.resolve()
    except OSError:
        delete_resolved = delete_root
    for path in _iter_scan_files():
        try:
            resolved = path.resolve()
        except OSError:
            resolved = path
        try:
            resolved.relative_to(delete_resolved)
            continue  # binnen te wissen boom
        except ValueError:
            pass
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for i, line in enumerate(text.splitlines(), start=1):
            for needle in needles:
                if needle in line:
                    col = bieb_fs.needle_column(line, *needles)
                    hits.append((path, i, col, line.strip()[:140]))
                    break
    return hits


def _dangling_kind(path: Path) -> str:
    """Soort treffer voor leesbare groepering."""
    rel = _rel(path).replace("\\", "/").lower()
    name = path.name.lower()
    if name == "id-register.md" or rel.endswith("/id-register.md"):
        return "id-register"
    if "werkvoorraad" in name:
        return "werkvoorraad"
    if "koormappen" in path.parts:
        return "koormap"
    if "handleiding" in path.parts:
        return "handleiding"
    if rel.startswith("docs/"):
        return "docs"
    return "overig"


# Soorten die bieb verwijder zelf opruimt (niet blokkeren).
_AUTO_CLEAN_KINDS = frozenset({"id-register", "werkvoorraad"})

# kind → (korte titel, actie voor handmatige rest)
_MANUAL_KIND_INFO: dict[str, tuple[str, str]] = {
    "koormap": (
        "Koormap",
        "pas de shortcode of alias op die pagina aan, of ruim het "
        "slot op (koormap-mappen wist dit script niet).",
    ),
    "handleiding": (
        "Handleiding",
        "pas of verwijder de tekst die dit id noemt.",
    ),
    "docs": (
        "Documentatie (docs)",
        "pas of verwijder de tekst die dit id noemt.",
    ),
    "overig": (
        "Andere tekst",
        "pas of verwijder de treffer in dat bestand.",
    ),
}


def _partition_dangling(
    dangling: list[tuple[Path, int, int | None, str]],
) -> tuple[
    list[tuple[Path, int, int | None, str]],
    list[tuple[Path, int, int | None, str]],
]:
    """Splits in (auto-opschonbaar, handmatig)."""
    auto: list[tuple[Path, int, int | None, str]] = []
    manual: list[tuple[Path, int, int | None, str]] = []
    for hit in dangling:
        if _dangling_kind(hit[0]) in _AUTO_CLEAN_KINDS:
            auto.append(hit)
        else:
            manual.append(hit)
    return auto, manual


def _loci_by_path(
    hits: list[tuple[Path, int, int | None, str]],
) -> dict[str, list[tuple[int, int | None]]]:
    by_path: dict[str, list[tuple[int, int | None]]] = {}
    for path, line, col, _snippet in hits:
        by_path.setdefault(_rel(path), []).append((line, col))
    return by_path


def _format_loci(loci: list[tuple[int, int | None]], *, limit: int = 12) -> str:
    parts = [
        f"regel {ln}" + (f" kolom {c}" if c else "") for ln, c in loci[:limit]
    ]
    if len(loci) > limit:
        parts.append(f"... (+{len(loci) - limit})")
    return ", ".join(parts)


def _format_manual_dangling_report(
    dangling: list[tuple[Path, int, int | None, str]],
) -> list[str]:
    """Handmatige rest (o.a. koormap): bestand + regel/kolom + actie."""
    if not dangling:
        return []

    groups: dict[str, dict[str, list[tuple[int, int | None]]]] = {}
    for path, line, col, _snippet in dangling:
        kind = _dangling_kind(path)
        by_path = groups.setdefault(kind, {})
        by_path.setdefault(_rel(path), []).append((line, col))

    lines: list[str] = [
        f"Nog {len(dangling)} ongeldige verwijzing(en) (handmatig):",
        "",
    ]
    n = 0
    for kind in ("koormap", "handleiding", "docs", "overig"):
        by_path = groups.get(kind)
        if not by_path:
            continue
        title, actie = _MANUAL_KIND_INFO[kind]
        n_hits = sum(len(v) for v in by_path.values())
        n += 1
        lines.append(f"{n}. {title}: {n_hits} treffer(s)")
        for path_rel, loci in sorted(by_path.items()):
            lines.append(f"   Bestand: {path_rel}")
            lines.append(f"   Locaties: {_format_loci(loci)}")
        lines.append(f"   Actie: {actie}")
        lines.append("")
    return lines


def _drop_lines_at(path: Path, line_nos: set[int]) -> int:
    """Verwijder 1-based regelnummers uit bestand. Return aantal gewiste regels."""
    if not line_nos or not path.is_file():
        return 0
    raw_lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    new_lines = [
        ln for i, ln in enumerate(raw_lines, start=1) if i not in line_nos
    ]
    dropped = len(raw_lines) - len(new_lines)
    if dropped:
        bieb_fs.write_text(path, "".join(new_lines))
    return dropped


def _clear_werkvoorraad_doel_id_line(line: str, needles: list[str]) -> str:
    """Maak Doel-id-cel leeg in een werkvoorraad-tabelrij; zet Volgende op doel-id."""
    if not line.lstrip().startswith("|"):
        return line
    # Behoud of de regel met newline eindigde (aanroeper regelt keepends)
    ending = ""
    core = line
    if core.endswith("\r\n"):
        ending = "\r\n"
        core = core[:-2]
    elif core.endswith("\n"):
        ending = "\n"
        core = core[:-1]
    parts = core.split("|")
    # | Input | Doel-id | Koormap | Doelvorm | Stap | Volgende | Notitie |
    if len(parts) < 8:
        return line
    doel_cell = parts[2]
    if not any(n in doel_cell for n in needles):
        return line
    parts[2] = " "
    parts[6] = " doel-id "
    return "|".join(parts) + ending


def _clear_werkvoorraad_doel_ids(
    path: Path,
    line_nos: set[int],
    needles: list[str],
    *,
    dry_run: bool,
) -> int:
    """Leeg doel-id op gegeven regels. Return aantal gewijzigde rijen."""
    if not line_nos or not path.is_file():
        return 0
    text = path.read_text(encoding="utf-8")
    raw_lines = text.splitlines(keepends=True)
    changed = 0
    for i, ln in enumerate(raw_lines):
        lineno = i + 1
        if lineno not in line_nos:
            continue
        new_ln = _clear_werkvoorraad_doel_id_line(ln, needles)
        if new_ln != ln:
            raw_lines[i] = new_ln
            changed += 1
    if changed and not dry_run:
        bieb_fs.write_text(path, "".join(raw_lines))
    return changed


def _report_auto_clean(
    auto_hits: list[tuple[Path, int, int | None, str]],
    *,
    dry_run: bool,
) -> None:
    """Print wis-regels voor Id-register en werkvoorraad (geen schijfschrijven)."""
    by_kind: dict[str, list[tuple[Path, int, int | None, str]]] = {}
    for hit in auto_hits:
        by_kind.setdefault(_dangling_kind(hit[0]), []).append(hit)

    prefix = "would wis" if dry_run else "wis"
    reg_hits = by_kind.get("id-register", [])
    if reg_hits:
        for path_rel, loci in sorted(_loci_by_path(reg_hits).items()):
            print(
                f"  {prefix} ID-REGISTER: {path_rel} ({_format_loci(loci)})",
                flush=True,
            )
    else:
        print("  wis ID-REGISTER: (geen treffers)", flush=True)

    wv_hits = by_kind.get("werkvoorraad", [])
    if wv_hits:
        for path_rel, loci in sorted(_loci_by_path(wv_hits).items()):
            print(
                f"  {prefix} werkvoorraad doel-id: {path_rel} "
                f"({_format_loci(loci)})",
                flush=True,
            )
    else:
        print("  wis werkvoorraad doel-id: (geen treffers)", flush=True)


def _apply_auto_clean(
    auto_hits: list[tuple[Path, int, int | None, str]],
    needles: list[str],
) -> None:
    """Wis Id-register-rijen en leeg werkvoorraad-doel-id op schijf."""
    by_kind: dict[str, list[tuple[Path, int, int | None, str]]] = {}
    for hit in auto_hits:
        by_kind.setdefault(_dangling_kind(hit[0]), []).append(hit)

    for path_rel, loci in sorted(
        _loci_by_path(by_kind.get("id-register", [])).items()
    ):
        path = REPO_ROOT.joinpath(*path_rel.split("/"))
        _drop_lines_at(path, {ln for ln, _c in loci})

    for path_rel, loci in sorted(
        _loci_by_path(by_kind.get("werkvoorraad", [])).items()
    ):
        path = REPO_ROOT.joinpath(*path_rel.split("/"))
        _clear_werkvoorraad_doel_ids(
            path, {ln for ln, _c in loci}, needles, dry_run=False
        )


def _find_koormap_dirs(names: list[str]) -> list[Path]:
    if not KOORMAPPEN_ROOT.is_dir():
        return []
    want = set(names)
    return sorted(
        (
            p
            for p in KOORMAPPEN_ROOT.rglob("*")
            if p.is_dir() and p.name in want
        ),
        key=lambda p: len(p.parts),
        reverse=True,
    )


def _svg_root_for(slash_id: str) -> Path:
    return REPO_ROOT.joinpath(
        "static", "vsa", "bladermap", "catalogus", *slash_id.split("/")
    )


def verwijder(raw: str, *, dry_run: bool, force: bool) -> int:
    level, slash = _resolve_id(raw)
    src = ref_folder(slash)
    if not src.is_dir():
        bieb_fs.print_fail(
            f"bronmap ontbreekt: {_rel(src)}",
            oplossing="controleer het id (slash- of stam-vorm) en probeer opnieuw.",
            stream=sys.stderr,
        )
        return 1

    covered = _ids_covered(level, slash)
    needles = _needles_for(covered)
    dangling = _find_dangling(delete_root=src, needles=needles)
    slot_names = [slash_to_stem(slash)]
    if level == "zangstuk":
        slot_names.append(slash)
    slot_names = list(dict.fromkeys(slot_names))
    koor_dirs = _find_koormap_dirs(slot_names)
    svg = _svg_root_for(slash)

    auto_hits, manual_hits = _partition_dangling(dangling)

    n_files = sum(1 for p in src.rglob("*") if p.is_file())
    print(
        f"=== bieb verwijder [{level}] {slash}"
        + (" (dry-run)" if dry_run else "")
        + (" (--force)" if force else ""),
        flush=True,
    )
    cat_prefix = "would wis" if dry_run else "wis"
    print(
        f"  {cat_prefix} catalogus: {_rel(src)} ({n_files} bestand(en))",
        flush=True,
    )
    if svg.is_dir():
        print(f"  {cat_prefix} SVG: {_rel(svg)}", flush=True)
    else:
        print("  wis SVG: (geen map)", flush=True)

    _report_auto_clean(auto_hits, dry_run=dry_run)

    if koor_dirs:
        print(
            f"  koormap-mappen (blijven staan; zelf opruimen): {len(koor_dirs)}",
            flush=True,
        )
        for d in koor_dirs[:20]:
            print(f"    - {_rel(d)}", flush=True)
        if len(koor_dirs) > 20:
            print(f"    ... en {len(koor_dirs) - 20} meer", flush=True)

    if manual_hits:
        for line in _format_manual_dangling_report(manual_hits):
            print(line, flush=True)
    else:
        print("  ongeldige koormap/docs-verwijzingen: geen", flush=True)

    if manual_hits and not force:
        bieb_fs.print_fail(
            f"wissen gestopt: nog {len(manual_hits)} ongeldige verwijzing(en) "
            "(zie groepen hierboven)",
            oplossing=(
                "pas die bestanden aan (Actie per groep), draai daarna opnieuw "
                "bieb verwijder <id>. Id-register en werkvoorraad-doel-id "
                "worden bij een geslaagde run automatisch meegenomen. "
                "Gebruik --force alleen als je bewust de catalogus wist en "
                "koormap/docs later zelf opruimt."
            ),
            stream=sys.stderr,
        )
        if dry_run:
            print("(dry-run: niets gewist)", flush=True)
        return 1

    if dry_run:
        print("OK: verwijder dry-run (niets gewist)", flush=True)
        return 0

    if auto_hits:
        _apply_auto_clean(auto_hits, needles)

    bieb_fs.rmtree(src)
    print(f"  removed {_rel(src)}", flush=True)
    if svg.is_dir():
        bieb_fs.rmtree(svg)
        print(f"  removed {_rel(svg)}", flush=True)

    print(
        "OK: verwijder klaar. Vervolg: "
        + ("koormap/docs handmatig; " if manual_hits else "")
        + "python scripts\\build_zoek_index.py ; scripts\\check.cmd",
        flush=True,
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="bieb verwijder",
        description=(
            "Verwijder catalogus-id; rapporteer dangling refs / koormap-slots."
        ),
    )
    parser.add_argument("ident", nargs="?", help="Catalogus-id (slash of stam)")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Toon plan en dangling refs zonder te wissen",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Wis ondanks dangling refs buiten de catalogusmap",
    )
    args = parser.parse_args(argv)

    ident = args.ident
    if ident in {"?", "-h", "--help"}:
        _print_help_block(HELP_VERWIJDER)
        return 0 if ident == "?" else 2
    if not ident:
        ident = _prompt_until(
            "Id om te verwijderen (? voor uitleg): ",
            HELP_VERWIJDER,
        )
        if ident is None:
            return 2
    try:
        return verwijder(ident, dry_run=args.dry_run, force=args.force)
    except ValueError as exc:
        print(f"verwijder: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(bieb_fs.run_handler(main, sys.argv[1:], command="verwijder"))
