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
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
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

Eerst dry-run: toont wat weggaat en welke verwijzingen (dangling) er
nog zijn in koormappen/docs. Koormap-pagina's wist het script niet.

  bieb verwijder ektinia/vredes/hemelum --dry-run
  bieb verwijder ektinia/vredes/hemelum
  bieb verwijder ektinia/vredes/hemelum --force

--force: wis ondanks dangling refs (refs blijven staan tot jij ze fixt).
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
            raise ValueError("gestopt: geen id") from exc
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
) -> list[tuple[Path, int, str]]:
    """Treffers buiten ``delete_root``: (pad, regel, snippet)."""
    hits: list[tuple[Path, int, str]] = []
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
                    hits.append((path, i, line.strip()[:140]))
                    break
    return hits


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
        print(f"bronmap ontbreekt: {_rel(src)}", file=sys.stderr)
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

    n_files = sum(1 for p in src.rglob("*") if p.is_file())
    print(
        f"=== bieb verwijder [{level}] {slash}"
        + (" (dry-run)" if dry_run else "")
        + (" (--force)" if force else ""),
        flush=True,
    )
    print(f"  wis catalogus: {_rel(src)} ({n_files} bestand(en))", flush=True)
    if svg.is_dir():
        print(f"  wis SVG: {_rel(svg)}", flush=True)
    else:
        print("  wis SVG: (geen map)", flush=True)

    if koor_dirs:
        print(
            f"  koormap-mappen (blijven staan; zelf opruimen): {len(koor_dirs)}",
            flush=True,
        )
        for d in koor_dirs[:20]:
            print(f"    - {_rel(d)}", flush=True)
        if len(koor_dirs) > 20:
            print(f"    … en {len(koor_dirs) - 20} meer", flush=True)

    if dangling:
        print(f"  dangling refs: {len(dangling)}", flush=True)
        for path, line, snippet in dangling[:50]:
            print(f"    {_rel(path)}:{line}: {snippet}", flush=True)
        if len(dangling) > 50:
            print(f"    … en {len(dangling) - 50} meer", flush=True)
    else:
        print("  dangling refs: geen", flush=True)

    if dangling and not force:
        print(
            "STOP: er zijn nog verwijzingen buiten de catalogusmap. "
            "Pas die aan, of gebruik --force om toch te wissen "
            "(dangling blijft dan staan).",
            file=sys.stderr,
        )
        if dry_run:
            print("(dry-run: niets gewist)", flush=True)
        return 1

    if dry_run:
        print("OK: verwijder dry-run (niets gewist)", flush=True)
        return 0

    shutil.rmtree(src)
    print(f"  removed {_rel(src)}", flush=True)
    if svg.is_dir():
        shutil.rmtree(svg)
        print(f"  removed {_rel(svg)}", flush=True)

    print(
        "OK: verwijder klaar. Vervolg: dangling/koormap handmatig; "
        "python scripts\\build_zoek_index.py ; scripts\\check.cmd",
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
    raise SystemExit(main())
