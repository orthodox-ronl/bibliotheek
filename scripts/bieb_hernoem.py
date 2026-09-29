"""Hernoem een zangstuk-id (map + stam + verwijzingen + Hugo-aliases).

Gebruik::

    bieb hernoem tropaar tropaar [--dry-run]

Verplaatst ``content-source/bibliotheek/<oud>`` → ``<nieuw>``, hernoemt
bestanden waarvan de naam met ``{oud}-`` begint, werkt tekstverwijzingen
bij (``bieb id``, ``alias_van``, colofon, docs), verplaatst bladermap-SVG,
en zet Hugo-``aliases`` op elke verhuisde pagina voor de oude URL.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bibliotheek import BIBLIOTHEEK_ROOT, REPO_ROOT, _ID_PART  # noqa: E402

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


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _validate_zangstuk(name: str) -> str:
    name = name.strip().strip("/")
    if "/" in name:
        raise ValueError(f"verwacht alleen zangstuk-id (geen slash), kreeg {name!r}")
    if not _ID_PART.fullmatch(name):
        raise ValueError(f"ongeldig zangstuk-id {name!r}")
    return name


def _insert_aliases(text: str, alias_paths: list[str]) -> str:
    """Voeg aliases toe aan YAML-frontmatter (of maak frontmatter)."""
    aliases_block = "aliases:\n" + "".join(f'  - "{p}"\n' for p in alias_paths)
    if not text.startswith("---"):
        return f"---\n{aliases_block}---\n\n{text}"
    end = text.find("\n---", 3)
    if end < 0:
        return text
    fm = text[4:end]
    body = text[end + len("\n---") :]
    # Bestaande aliases: voeg regels toe.
    if re.search(r"(?m)^aliases:\s*$", fm):
        lines = fm.splitlines(keepends=True)
        out: list[str] = []
        i = 0
        while i < len(lines):
            out.append(lines[i])
            if re.match(r"^aliases:\s*$", lines[i]):
                i += 1
                existing: list[str] = []
                while i < len(lines) and (
                    lines[i].startswith("  -") or lines[i].startswith("\t-")
                ):
                    existing.append(lines[i].strip().lstrip("-").strip().strip("\"'"))
                    out.append(lines[i])
                    i += 1
                for p in alias_paths:
                    if p not in existing:
                        out.append(f'  - "{p}"\n')
                continue
            i += 1
        fm = "".join(out)
    else:
        fm = fm.rstrip() + "\n" + aliases_block
    return f"---\n{fm.rstrip()}\n---{body}"


def _rewrite_text(text: str, old: str, new: str) -> str:
    """Vervang id/stam-voorvoegsels; langere stam-vorm eerst."""
    # Pad/id: tropaar/... of alleen tropaar als segment
    text = text.replace(f"{old}/", f"{new}/")
    text = text.replace(f"{old}-", f"{new}-")
    # Losse token (mapnaam in docs): word boundary-achtig
    text = re.sub(rf"(?<![a-z0-9_-]){re.escape(old)}(?![a-z0-9_-])", new, text)
    return text


def _iter_repo_text_files() -> list[Path]:
    out: list[Path] = []
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in _SKIP_DIR_NAMES for part in path.parts):
            continue
        if path.suffix.lower() not in _TEXT_SUFFIXES:
            continue
        # binary-ish large json under static/zoek regenerated anyway — still ok
        out.append(path)
    return out


def _rename_stem_files(root: Path, old: str, new: str, *, dry_run: bool) -> int:
    """Hernoem bestanden die met ``{old}-`` beginnen (diepste eerst)."""
    n = 0
    files = sorted(
        (p for p in root.rglob("*") if p.is_file() and p.name.startswith(f"{old}-")),
        key=lambda p: len(p.parts),
        reverse=True,
    )
    for path in files:
        dest = path.with_name(f"{new}-{path.name[len(old) + 1 :]}")
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
                    f"kon niet hernoemen (bestand vergrendeld?): {_rel(path)} -> {dest.name}"
                ) from last_err
        n += 1
    return n


def _add_page_aliases(zangstuk_dir: Path, old: str, new: str, *, dry_run: bool) -> int:
    """Zet Hugo-aliases voor oude URL’s op _index.md / index.md onder nieuw pad."""
    n = 0
    indexes = list(zangstuk_dir.rglob("_index.md")) + list(zangstuk_dir.rglob("index.md"))
    for index in indexes:
        try:
            rel = index.parent.resolve().relative_to(zangstuk_dir.resolve())
        except ValueError:
            continue
        rel_s = "" if str(rel) in {".", ""} else rel.as_posix().rstrip("/")
        old_url = (
            f"/bibliotheek/{old}/"
            if not rel_s
            else f"/bibliotheek/{old}/{rel_s}/"
        )
        text = index.read_text(encoding="utf-8")
        new_text = _insert_aliases(text, [old_url])
        if new_text == text:
            continue
        print(f"  alias {_rel(index)} <- {old_url}", flush=True)
        if not dry_run:
            index.write_text(new_text, encoding="utf-8", newline="\n")
        n += 1
    return n


def hernoem_zangstuk(old: str, new: str, *, dry_run: bool) -> int:
    old = _validate_zangstuk(old)
    new = _validate_zangstuk(new)
    if old == new:
        print("oud en nieuw zijn gelijk", file=sys.stderr)
        return 2

    src = BIBLIOTHEEK_ROOT / old
    dest = BIBLIOTHEEK_ROOT / new
    if not src.is_dir():
        print(f"bronmap ontbreekt: {_rel(src)}", file=sys.stderr)
        return 1
    if dest.exists():
        print(f"doelmap bestaat al: {_rel(dest)}", file=sys.stderr)
        return 1

    print(f"=== bieb hernoem {old} -> {new}" + (" (dry-run)" if dry_run else ""))
    print(f"  move {_rel(src)} -> {_rel(dest)}", flush=True)
    if not dry_run:
        shutil.move(str(src), str(dest))
        zangstuk_dir = dest
    else:
        zangstuk_dir = src  # dry-run: werk op bron voor listing

    # Stam-bestanden (in bibliotheek-map)
    n_stem = _rename_stem_files(zangstuk_dir if not dry_run else src, old, new, dry_run=dry_run)
    print(f"  stam-bestanden: {n_stem}", flush=True)

    # Bladermap-SVG
    svg_src = REPO_ROOT / "static" / "vsa" / "bladermap" / "bibliotheek" / old
    svg_dest = REPO_ROOT / "static" / "vsa" / "bladermap" / "bibliotheek" / new
    if svg_src.is_dir():
        print(f"  move {_rel(svg_src)} -> {_rel(svg_dest)}", flush=True)
        if not dry_run:
            svg_dest.parent.mkdir(parents=True, exist_ok=True)
            if svg_dest.exists():
                raise SystemExit(f"SVG-doel bestaat al: {_rel(svg_dest)}")
            shutil.move(str(svg_src), str(svg_dest))
            _rename_stem_files(svg_dest, old, new, dry_run=False)
        else:
            _rename_stem_files(svg_src, old, new, dry_run=True)

    # Tekstverwijzingen in de hele repo (na mapverplaatsing: nieuw pad)
    n_files = 0
    n_hits = 0
    for path in _iter_repo_text_files():
        # Skip dit script zelf voor de voorbeelden? Nee — docs moeten mee.
        try:
            raw = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if old not in raw:
            continue
        updated = _rewrite_text(raw, old, new)
        if updated == raw:
            continue
        n_files += 1
        n_hits += raw.count(old)
        print(f"  rewrite {_rel(path)}", flush=True)
        if not dry_run:
            path.write_text(updated, encoding="utf-8", newline="\n")
    print(f"  tekstbestanden bijgewerkt: {n_files} (~{n_hits} treffers)", flush=True)

    # Hugo-aliases op verhuisde pagina's
    alias_root = dest if not dry_run else src
    # Na rewrite heten aliases-doelen al /bibliotheek/new/… — we willen OUDE urls.
    # Dus aliases toevoegen met old-naam, onafhankelijk van rewrite.
    n_alias = _add_page_aliases(alias_root, old, new, dry_run=dry_run)
    print(f"  hugo-aliases: {n_alias}", flush=True)

    print("OK: hernoem klaar" + (" (dry-run, niets geschreven)" if dry_run else ""))
    if not dry_run:
        print(
            "Vervolg: python scripts\\build_zoek_index.py ; "
            "scripts\\check.cmd (SVG/fingerprints/Hugo)."
        )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="bieb hernoem",
        description="Hernoem een zangstuk-id (map, stam, refs, aliases).",
    )
    parser.add_argument("oud", help="Huidig zangstuk-id (mapnaam)")
    parser.add_argument("nieuw", help="Nieuw zangstuk-id")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Toon acties zonder te schrijven",
    )
    args = parser.parse_args(argv)
    try:
        return hernoem_zangstuk(args.oud, args.nieuw, dry_run=args.dry_run)
    except ValueError as exc:
        print(f"hernoem: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
