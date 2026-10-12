"""Hernoem een catalogus-id (zangstuk, variant of uitvoeringsvorm).

Gebruik::

    bieb hernoem <oud> <nieuw> [--dry-run]

``oud`` / ``nieuw``: slash-vorm (``ektinia``, ``ektinia/vredes``,
``ektinia/vredes/hemelum``) of dash-/stam-vorm (``ektinia-vredes``,
``ektinia-vredes-hemelum``). Bij ambiguïteit: slash-vorm typen
(``?`` voor uitleg).

Verplaatst de catalogusmap, hernoemt publicatiestam-bestanden, verplaatst
bladermap-SVG’s, hernoemt 1:1-koormap-mappen (mapnaam = oude id/stam),
en werkt veilige id-verwijzingen bij. Frontmatter ``title`` / ``linkTitle``
worden niet aangepast (afgeleid bij de bouw; zie docs/catalogus-titels.md).
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from catalogus import (  # noqa: E402
    AmbiguousRefError,
    REPO_ROOT,
    complete_new_ref,
    ref_folder,
    resolve_existing_ref,
    slash_to_stem,
)

_TEXT_SUFFIXES = frozenset(
    {
        ".md",
        ".vsa",
        ".mvsa",
        ".txt",
        ".json",
        ".yml",
        ".yaml",
        ".html",
        ".cmd",
        ".py",
        ".toml",
    }
)
_SKIP_DIR_NAMES = frozenset(
    {
        ".git",
        "generated",
        "public",
        "node_modules",
        ".hugo_build.lock",
    }
)
KOORMAPPEN_ROOT = REPO_ROOT / "content-source" / "koormappen"
_TITLE_FM_RE = re.compile(r"^(title|linkTitle)\s*:", re.IGNORECASE)

HELP_HERNOEM = """\
bieb hernoem — catalogus-id hernoemen

Geef het oude en nieuwe id. Vorm (beide kanten):

  zangstuk              ektinia
  variant               ektinia/vredes     of  ektinia-vredes
  uitvoeringsvorm       ektinia/vredes/hemelum
                        of  ektinia-vredes-hemelum

Alleen het laatste stuk mag ook als nieuw id (zelfde ouder):
  bieb hernoem ektinia/vredes/hemelum groningen

Dash-vorm ambigu? Typ de slash-vorm. Doelmap mag nog niet bestaan.

Voorbeelden:
  bieb hernoem ektinia litanie --dry-run
  bieb hernoem ektinia/vredes ektinia/vredeslitanie
  bieb hernoem ektinia-vredes-hemelum ektinia-vredes-groningen
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


def _resolve_old(raw: str) -> tuple[str, str]:
    try:
        return resolve_existing_ref(raw)
    except AmbiguousRefError as exc:
        print(f"hernoem: {exc}", flush=True)
        value = _prompt_until(
            "Slash-vorm van het oude id (? voor uitleg): ",
            HELP_HERNOEM,
        )
        if value is None:
            raise ValueError("gestopt: geen oud id") from exc
        return resolve_existing_ref(value)


def _resolve_new(old_level: str, old_slash: str, raw: str) -> tuple[str, str]:
    try:
        return complete_new_ref(old_level, old_slash, raw)
    except AmbiguousRefError as exc:
        print(f"hernoem: {exc}", flush=True)
        value = _prompt_until(
            "Slash-vorm van het nieuwe id (? voor uitleg): ",
            HELP_HERNOEM,
        )
        if value is None:
            raise ValueError("gestopt: geen nieuw id") from exc
        return complete_new_ref(old_level, old_slash, value)


def _rewrite_text(
    text: str,
    old_slash: str,
    new_slash: str,
    *,
    level: str,
) -> tuple[str, list[str]]:
    """Veilige id/stam-vervanging; twijfelregels als lijst (niet herschreven)."""
    old_stem = slash_to_stem(old_slash)
    new_stem = slash_to_stem(new_slash)
    doubtful: list[str] = []

    def _safe_line(line: str) -> str:
        if _TITLE_FM_RE.match(line.strip()):
            return line
        out = line
        if old_slash in out:
            out = out.replace(old_slash, new_slash)
        if old_stem != old_slash and old_stem in out:
            out = out.replace(old_stem, new_stem)
        if level == "zangstuk":
            out = re.sub(
                rf"(?<![a-z0-9_-]){re.escape(old_slash)}(?![a-z0-9_-])",
                new_slash,
                out,
            )
        return out

    lines_out: list[str] = []
    for line in text.splitlines(keepends=True):
        stripped = line.rstrip("\n\r")
        newline = line[len(stripped) :]
        if _TITLE_FM_RE.match(stripped.strip()):
            # Titels niet herschrijven (bouw leidt af); wel melden in dry-run.
            if old_slash in stripped or (
                old_stem != old_slash and old_stem in stripped
            ):
                doubtful.append(stripped.strip()[:120])
            lines_out.append(line)
            continue
        updated = _safe_line(stripped)
        lines_out.append(updated + newline)
    return "".join(lines_out), doubtful


def _iter_repo_text_files() -> list[Path]:
    """Tekst met id-refs: catalogus, koormappen, handleiding, docs.

    Geen ``data/*-status.json`` / ``static/zoek`` (worden opnieuw gebouwd).
    """
    roots = [
        REPO_ROOT / "content-source",
        REPO_ROOT / "docs",
    ]
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


def _rename_stem_files(root: Path, old_stem: str, new_stem: str, *, dry_run: bool) -> int:
    """Hernoem bestanden die met ``{old_stem}-`` beginnen of exact stem+ext zijn."""
    n = 0
    files = sorted(
        (
            p
            for p in root.rglob("*")
            if p.is_file()
            and (
                p.name.startswith(f"{old_stem}-")
                or p.name.startswith(f"{old_stem}.")
            )
        ),
        key=lambda p: len(p.parts),
        reverse=True,
    )
    for path in files:
        name = path.name
        if name.startswith(f"{old_stem}-"):
            dest_name = f"{new_stem}-{name[len(old_stem) + 1 :]}"
        else:
            dest_name = f"{new_stem}{name[len(old_stem) :]}"
        dest = path.with_name(dest_name)
        print(f"  rename {_rel(path)} -> {dest.name}", flush=True)
        if not dry_run:
            if dest.exists():
                raise SystemExit(f"doel bestaat al: {_rel(dest)}")
            last_err: OSError | None = None
            for attempt in range(8):
                try:
                    path.rename(dest)
                    last_err = None
                    break
                except PermissionError as exc:
                    last_err = exc
                    time.sleep(0.4 * (attempt + 1))
            if last_err is not None:
                raise SystemExit(
                    f"kon niet hernoemen (bestand vergrendeld?): "
                    f"{_rel(path)} -> {dest.name}"
                ) from last_err
        n += 1
    return n


def _rename_koormap_slots(names: list[str], new_name: str, *, dry_run: bool) -> int:
    """Hernoem koormap-mappen waarvan de naam in ``names`` zit → ``new_name``."""
    if not KOORMAPPEN_ROOT.is_dir():
        return 0
    want = set(names)
    slots = sorted(
        (
            p
            for p in KOORMAPPEN_ROOT.rglob("*")
            if p.is_dir() and p.name in want
        ),
        key=lambda p: len(p.parts),
        reverse=True,
    )
    n = 0
    for src in slots:
        dest = src.with_name(new_name)
        print(f"  move {_rel(src)} -> {_rel(dest)}", flush=True)
        if dest.exists():
            raise SystemExit(f"koormap-doel bestaat al: {_rel(dest)}")
        if not dry_run:
            shutil.move(str(src), str(dest))
        n += 1
    return n


def _svg_root_for(slash_id: str) -> Path:
    return REPO_ROOT.joinpath(
        "static", "vsa", "bladermap", "catalogus", *slash_id.split("/")
    )


def hernoem(old_raw: str, new_raw: str, *, dry_run: bool) -> int:
    old_level, old_slash = _resolve_old(old_raw)
    new_level, new_slash = _resolve_new(old_level, old_slash, new_raw)
    if new_level != old_level:
        print(
            f"hernoem: niveau verschilt ({old_level} → {new_level})",
            file=sys.stderr,
        )
        return 2
    if old_slash == new_slash:
        print("oud en nieuw zijn gelijk", file=sys.stderr)
        return 2

    src = ref_folder(old_slash)
    dest = ref_folder(new_slash)
    if not src.is_dir():
        print(f"bronmap ontbreekt: {_rel(src)}", file=sys.stderr)
        return 1
    if dest.exists():
        print(f"doelmap bestaat al: {_rel(dest)}", file=sys.stderr)
        return 1

    # Zelfde ouder bij variant/leaf-hernoem binnen één parent-rename
    if old_level != "zangstuk":
        if src.parent != dest.parent and src.parent.resolve() != dest.parent.resolve():
            # Ouder mag mee veranderen alleen als die al bestaat (verhuis naar
            # ander zangstuk/variant) — dan moet dest.parent bestaan.
            if not dest.parent.is_dir():
                print(
                    f"doel-ouder ontbreekt: {_rel(dest.parent)} "
                    "(maak die eerst, of hernoem in stappen)",
                    file=sys.stderr,
                )
                return 1

    old_stem = slash_to_stem(old_slash)
    new_stem = slash_to_stem(new_slash)

    print(
        f"=== bieb hernoem [{old_level}] {old_slash} -> {new_slash}"
        + (" (dry-run)" if dry_run else ""),
        flush=True,
    )
    print(f"  move {_rel(src)} -> {_rel(dest)}", flush=True)
    if not dry_run:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dest))
        work_dir = dest
    else:
        work_dir = src

    n_stem = _rename_stem_files(work_dir, old_stem, new_stem, dry_run=dry_run)
    print(f"  stam-bestanden: {n_stem}", flush=True)

    svg_src = _svg_root_for(old_slash)
    svg_dest = _svg_root_for(new_slash)
    if svg_src.is_dir():
        print(f"  move {_rel(svg_src)} -> {_rel(svg_dest)}", flush=True)
        if not dry_run:
            svg_dest.parent.mkdir(parents=True, exist_ok=True)
            if svg_dest.exists():
                raise SystemExit(f"SVG-doel bestaat al: {_rel(svg_dest)}")
            shutil.move(str(svg_src), str(svg_dest))
            _rename_stem_files(svg_dest, old_stem, new_stem, dry_run=False)
        else:
            _rename_stem_files(svg_src, old_stem, new_stem, dry_run=True)

    # Koormap: mapnamen gelijk aan slash-laatste segment (zangstuk) of stam
    slot_names = [old_stem]
    if old_level == "zangstuk":
        slot_names.append(old_slash)
    slot_names = list(dict.fromkeys(slot_names))
    new_slot = new_stem if old_level != "zangstuk" else new_slash
    # Bij zangstuk: map heet ektinia → litanie (niet ektinia-… stam)
    if old_level == "zangstuk":
        n_koor = _rename_koormap_slots([old_slash], new_slash, dry_run=dry_run)
    else:
        n_koor = _rename_koormap_slots(slot_names, new_slot, dry_run=dry_run)
    print(f"  koormap-slots: {n_koor}", flush=True)

    n_files = 0
    n_hits = 0
    all_doubt: list[tuple[str, str]] = []
    for path in _iter_repo_text_files():
        try:
            raw = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if old_slash not in raw and old_stem not in raw:
            continue
        updated, doubt = _rewrite_text(
            raw, old_slash, new_slash, level=old_level
        )
        for d in doubt:
            all_doubt.append((_rel(path), d))
        if updated == raw:
            continue
        n_files += 1
        n_hits += raw.count(old_slash) + (
            raw.count(old_stem) if old_stem != old_slash else 0
        )
        print(f"  rewrite {_rel(path)}", flush=True)
        if not dry_run:
            path.write_text(updated, encoding="utf-8", newline="\n")
    print(f"  tekstbestanden bijgewerkt: {n_files} (~{n_hits} treffers)", flush=True)

    if all_doubt:
        print(
            f"  twijfelgevallen (niet herschreven): {len(all_doubt)}",
            flush=True,
        )
        for rel, snippet in all_doubt[:40]:
            print(f"    ? {rel}: {snippet}", flush=True)
        if len(all_doubt) > 40:
            print(f"    … en {len(all_doubt) - 40} meer", flush=True)

    print("OK: hernoem klaar" + (" (dry-run, niets geschreven)" if dry_run else ""))
    if not dry_run:
        print(
            "Vervolg: products vernieuwen waar nodig; "
            "python scripts\\build_zoek_index.py ; "
            "scripts\\check.cmd (SVG/fingerprints/Hugo)."
        )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="bieb hernoem",
        description=(
            "Hernoem catalogus-id (zangstuk/variant/uitvoeringsvorm): "
            "map, stam, refs, koormap-slots. Titels niet aanpassen."
        ),
    )
    parser.add_argument(
        "oud",
        nargs="?",
        help="Huidig id (slash- of stam-vorm)",
    )
    parser.add_argument(
        "nieuw",
        nargs="?",
        help="Nieuw id (slash-, stam-vorm, of alleen laatste segment)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Toon acties zonder te schrijven",
    )
    args = parser.parse_args(argv)

    oud = args.oud
    nieuw = args.nieuw
    if oud in {None, "?", "-h", "--help"} and nieuw is None:
        _print_help_block(HELP_HERNOEM)
        return 0 if oud == "?" else 2
    if not oud or not nieuw:
        if not oud:
            oud = _prompt_until("Oud id (? voor uitleg): ", HELP_HERNOEM)
            if oud is None:
                return 2
        if not nieuw:
            nieuw = _prompt_until("Nieuw id (? voor uitleg): ", HELP_HERNOEM)
            if nieuw is None:
                return 2
    try:
        return hernoem(oud, nieuw, dry_run=args.dry_run)
    except ValueError as exc:
        print(f"hernoem: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
