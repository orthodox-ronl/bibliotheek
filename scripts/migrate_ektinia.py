"""Consolideer litanie-zangstukken onder ``ektinia`` (eenmalige migratie).

Zie ``content-source/handleiding/start/zangstuk-soorten.md`` besluiten 1–2.

Gebruik::

    python scripts\\migrate_ektinia.py --dry-run
    python scripts\\migrate_ektinia.py
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from catalogus import CATALOGUS_ROOT, REPO_ROOT  # noqa: E402
from bieb_hernoem import (  # noqa: E402
    _SKIP_DIR_NAMES,
    _TEXT_SUFFIXES,
    _insert_aliases,
    _rel,
)

# oud zangstuk-id -> (variant-id, weight, title, linkTitle)
# 22 deelt variant ``vragend`` met 16 (alleen aliases + refs).
_MOVES: list[tuple[str, str, int, str, str]] = [
    ("1-vredeslitanie", "vrede", 100, "Vredeslitanie", "Vrede"),
    ("3-eerste-kleine-litanie", "kleine", 300, "Kleine litanie", "Kleine"),
    ("11-dringende-litanie", "dringend", 1100, "Dringende litanie", "Dringend"),
    ("12-ontslapenen-litanie", "ontslapenen", 1200, "Ontslapenen-litanie", "Ontslapenen"),
    ("13-catechumenen-litanie", "catechumenen", 1300, "Catechumenen-litanie", "Catechumenen"),
    ("14-gelovigen-litanie", "gelovigen", 1400, "Gelovigen-litanie", "Gelovigen"),
    ("16-vragende-litanie", "vragend", 1600, "Vragende litanie", "Vragend"),
]

_ALIAS_ONLY = ("22-vragende-litanie", "vragend")


def _rewrite_paths(text: str) -> str:
    """Vervang bibliotheek-ids en publicatiestammen (niet koormap-slotnamen).

    Alleen ``{oud}/default/…`` en ``{oud}-default-…`` -> ektinia-variant.
    Koormap-mappen zoals ``koormappen/.../1-vredeslitanie/`` blijven staan.
    """
    replacements: list[tuple[str, str]] = []
    for old, variant, *_ in _MOVES:
        replacements.append((f"{old}/default/", f"ektinia/{variant}/"))
        replacements.append((f"{old}-default-", f"ektinia-{variant}-"))
    old22, variant = _ALIAS_ONLY
    replacements.append((f"{old22}/default/", f"ektinia/{variant}/"))
    replacements.append((f"{old22}-default-", f"ektinia-{variant}-"))
    replacements.sort(key=lambda t: len(t[0]), reverse=True)
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def _set_frontmatter_fields(text: str, fields: dict[str, str | int]) -> str:
    if not text.startswith("---"):
        fm = "".join(f"{k}: {fields[k]!r}\n".replace("'", '"') for k in fields)
        # simpler yaml
        lines = []
        for k, v in fields.items():
            if isinstance(v, int):
                lines.append(f"{k}: {v}")
            else:
                lines.append(f'{k}: "{v}"')
        return "---\n" + "\n".join(lines) + "\n---\n\n" + text
    end = text.find("\n---", 3)
    if end < 0:
        return text
    fm = text[4:end]
    body = text[end + len("\n---") :]
    for key, value in fields.items():
        pat = re.compile(rf"(?m)^{re.escape(key)}:\s*.*$")
        if isinstance(value, int):
            line = f"{key}: {value}"
        else:
            line = f'{key}: "{value}"'
        if pat.search(fm):
            fm = pat.sub(line, fm)
        else:
            fm = fm.rstrip() + "\n" + line + "\n"
    return f"---\n{fm.rstrip()}\n---{body}"


def _rename_files_in_dir(directory: Path, old_prefix: str, new_prefix: str, *, dry_run: bool) -> int:
    n = 0
    files = sorted(
        (p for p in directory.rglob("*") if p.is_file() and p.name.startswith(old_prefix)),
        key=lambda p: len(p.parts),
        reverse=True,
    )
    for path in files:
        dest = path.with_name(new_prefix + path.name[len(old_prefix) :])
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
                raise SystemExit(f"kon niet hernoemen: {_rel(path)}") from last_err
        n += 1
    return n


def _add_aliases_to_tree(variant_dir: Path, old_zangstuk: str, *, dry_run: bool) -> int:
    """Aliases voor oude zangstuk-URL’s (inclusief /default/)."""
    n = 0
    indexes = list(variant_dir.rglob("_index.md")) + list(variant_dir.rglob("index.md"))
    for index in indexes:
        try:
            rel = index.parent.resolve().relative_to(variant_dir.resolve())
        except ValueError:
            continue
        rel_s = "" if str(rel) in {".", ""} else rel.as_posix().rstrip("/")
        # variant root ≈ oud/default; uitvoeringsvorm ≈ oud/default/<uv>
        if not rel_s:
            alias_paths = [
                f"/catalogus/{old_zangstuk}/",
                f"/catalogus/{old_zangstuk}/default/",
            ]
        else:
            alias_paths = [
                f"/catalogus/{old_zangstuk}/default/{rel_s}/",
            ]
        text = index.read_text(encoding="utf-8")
        new_text = _insert_aliases(text, alias_paths)
        if new_text == text:
            continue
        for a in alias_paths:
            print(f"  alias {_rel(index)} <- {a}", flush=True)
        if not dry_run:
            index.write_text(new_text, encoding="utf-8", newline="\n")
        n += 1
    return n


def migrate(*, dry_run: bool) -> int:
    dest_root = CATALOGUS_ROOT / "ektinia"
    if dest_root.exists() and any(dest_root.iterdir()):
        print(f"doel bestaat al en is niet leeg: {_rel(dest_root)}", file=sys.stderr)
        return 1

    print("=== migrate litanieen -> ektinia" + (" (dry-run)" if dry_run else ""))

    if not dry_run:
        dest_root.mkdir(parents=True, exist_ok=True)
        index = dest_root / "_index.md"
        index.write_text(
            "---\n"
            'title: "Ektinia"\n'
            'linkTitle: "Ektinia"\n'
            "nav_sort: weight\n"
            "publicatiestatus: concept\n"
            "automatische_inhoud: true\n"
            "weight: 100\n"
            "---\n\n"
            "Liturgische familie van de ektinia’s (litanieën). "
            "Varianten = soort ektinia. Zoeken: synoniem *litanie* -> *ektinia*. "
            "Zie handleiding *Zangstuk-soorten*.\n",
            encoding="utf-8",
            newline="\n",
        )
        print(f"  write {_rel(index)}", flush=True)

    for old, variant, weight, title, link_title in _MOVES:
        src = CATALOGUS_ROOT / old
        src_variant = src / "default"
        dest_variant = dest_root / variant
        if not src_variant.is_dir():
            print(f"bron ontbreekt: {_rel(src_variant)}", file=sys.stderr)
            return 1
        print(f"  move {_rel(src_variant)} -> {_rel(dest_variant)}", flush=True)
        if not dry_run:
            if dest_variant.exists():
                raise SystemExit(f"variant bestaat al: {_rel(dest_variant)}")
            shutil.move(str(src_variant), str(dest_variant))
            # Update variant _index titles/weight
            v_index = dest_variant / "_index.md"
            if v_index.is_file():
                text = v_index.read_text(encoding="utf-8")
                text = _set_frontmatter_fields(
                    text,
                    {
                        "title": title,
                        "linkTitle": link_title,
                        "weight": weight,
                    },
                )
                v_index.write_text(text, encoding="utf-8", newline="\n")
            # Stam: {old}-default- -> ektinia-{variant}-
            _rename_files_in_dir(
                dest_variant,
                f"{old}-default-",
                f"ektinia-{variant}-",
                dry_run=False,
            )
            # Verwijder lege oude zangstuk-map (nog _index.md)
            old_index = src / "_index.md"
            if old_index.is_file():
                old_index.unlink()
            if src.is_dir() and not any(src.iterdir()):
                src.rmdir()
                print(f"  remove {_rel(src)}", flush=True)
            elif src.is_dir():
                shutil.rmtree(src)
                print(f"  remove tree {_rel(src)}", flush=True)

    # 22: inhoud weg (zelfde werk als 16); aliases later op vragend
    old22, variant22 = _ALIAS_ONLY
    src22 = CATALOGUS_ROOT / old22
    print(f"  drop duplicate {old22} (-> ektinia/{variant22})", flush=True)
    if not dry_run and src22.is_dir():
        shutil.rmtree(src22)
        print(f"  remove tree {_rel(src22)}", flush=True)

    # Bladermap-SVG (indien aanwezig)
    svg_root = REPO_ROOT / "static" / "vsa" / "bladermap" / "catalogus"
    for old, variant, *_ in _MOVES:
        svg_src = svg_root / old
        if not svg_src.is_dir():
            continue
        svg_dest = svg_root / "ektinia" / variant
        print(f"  move {_rel(svg_src)} -> {_rel(svg_dest)}", flush=True)
        if not dry_run:
            svg_dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(svg_src), str(svg_dest))
            _rename_files_in_dir(
                svg_dest,
                f"{old}-default-",
                f"ektinia-{variant}-",
                dry_run=False,
            )

    # Globale tekst-rewrite (vóór aliases, zodat oude URL’s niet herschreven worden)
    skip_rewrite = {
        Path(__file__).resolve(),
        (REPO_ROOT / "content-source" / "handleiding" / "start" / "zangstuk-soorten.md").resolve(),
    }
    n_files = 0
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in _SKIP_DIR_NAMES for part in path.parts):
            continue
        if path.suffix.lower() not in _TEXT_SUFFIXES:
            continue
        if path.resolve() in skip_rewrite:
            continue
        try:
            raw = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        updated = _rewrite_paths(raw)
        if updated == raw:
            continue
        n_files += 1
        print(f"  rewrite {_rel(path)}", flush=True)
        if not dry_run:
            path.write_text(updated, encoding="utf-8", newline="\n")
    print(f"  tekstbestanden bijgewerkt: {n_files}", flush=True)

    # Hugo-aliases ná rewrite (oude URL’s moeten letterlijk blijven)
    if not dry_run:
        for old, variant, *_ in _MOVES:
            dest_variant = dest_root / variant
            if dest_variant.is_dir():
                _add_aliases_to_tree(dest_variant, old, dry_run=False)
        vragend = dest_root / variant22
        if vragend.is_dir():
            _add_aliases_to_tree(vragend, old22, dry_run=False)

    print("OK: ektinia-migratie klaar" + (" (dry-run)" if dry_run else ""))
    if not dry_run:
        print(
            "Vervolg: python scripts\\build_zoek_index.py ; "
            "scripts\\check.cmd (SVG/fingerprints/Hugo)."
        )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Consolideer litanieën onder ektinia.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    return migrate(dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
