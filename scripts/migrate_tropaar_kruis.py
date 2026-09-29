"""Verplaats ``210-…`` en ``220-…`` onder ``tropaar`` (eenmalige migratie).

Zie ``content-source/handleiding/start/zangstuk-soorten.md`` besluit 3.

Doel::

    tropaar/heer-red-uw-volk/{liturgikon,rode-gebedenboek}/…
    tropaar/uw-heilig-kruis/{groningen,hemelum,…}/…

Gebruik::

    python scripts\\migrate_tropaar_kruis.py --dry-run
    python scripts\\migrate_tropaar_kruis.py
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bibliotheek import BIBLIOTHEEK_ROOT, REPO_ROOT  # noqa: E402
from bieb_hernoem import _SKIP_DIR_NAMES, _TEXT_SUFFIXES, _insert_aliases, _rel  # noqa: E402

# (oud-zangstuk, nieuwe-variant-id, weight, title, linkTitle)
_MOVES: list[tuple[str, str, int, str, str]] = [
    (
        "210-heer-red-uw-volk-en-zegen-uw-erfdeel",
        "heer-red-uw-volk",
        210,
        "Heer, red Uw volk en zegen Uw erfdeel",
        "Heer red Uw volk",
    ),
    (
        "220-uw-heilig-kruis",
        "uw-heilig-kruis",
        220,
        "Uw Heilig Kruis",
        "Uw Heilig Kruis",
    ),
]


def _rename_files_in_dir(
    directory: Path, old_prefix: str, new_prefix: str, *, dry_run: bool
) -> int:
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


def _set_frontmatter_fields(text: str, fields: dict[str, str | int | bool]) -> str:
    if not text.startswith("---"):
        lines = []
        for k, v in fields.items():
            if isinstance(v, bool):
                lines.append(f"{k}: {'true' if v else 'false'}")
            elif isinstance(v, int):
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
        if isinstance(value, bool):
            line = f"{key}: {'true' if value else 'false'}"
        elif isinstance(value, int):
            line = f"{key}: {value}"
        else:
            line = f'{key}: "{value}"'
        if pat.search(fm):
            fm = pat.sub(line, fm)
        else:
            fm = fm.rstrip() + "\n" + line + "\n"
    # Verwijder alias_van (echte inhoud i.p.v. alleen alias)
    fm = re.sub(r"(?m)^alias_van:\s*.*\n?", "", fm)
    return f"---\n{fm.rstrip()}\n---{body}"


def _add_aliases_to_tree(variant_dir: Path, old_zangstuk: str, *, dry_run: bool) -> int:
    n = 0
    indexes = list(variant_dir.rglob("_index.md")) + list(variant_dir.rglob("index.md"))
    for index in indexes:
        try:
            rel = index.parent.resolve().relative_to(variant_dir.resolve())
        except ValueError:
            continue
        rel_s = "" if str(rel) in {".", ""} else rel.as_posix().rstrip("/")
        if not rel_s:
            alias_paths = [
                f"/bibliotheek/{old_zangstuk}/",
                f"/bibliotheek/{old_zangstuk}/default/",
            ]
        else:
            alias_paths = [f"/bibliotheek/{old_zangstuk}/default/{rel_s}/"]
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


def _rewrite_paths(text: str) -> str:
    """Alleen ``{oud}/default/`` en ``{oud}-default-`` (koormap-slotnamen blijven)."""
    replacements: list[tuple[str, str]] = []
    for old, variant, *_ in _MOVES:
        replacements.append((f"{old}/default/", f"tropaar/{variant}/"))
        replacements.append((f"{old}-default-", f"tropaar-{variant}-"))
    replacements.sort(key=lambda t: len(t[0]), reverse=True)
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def migrate(*, dry_run: bool) -> int:
    tropaar = BIBLIOTHEEK_ROOT / "tropaar"
    if not tropaar.is_dir():
        print(f"tropaar ontbreekt: {_rel(tropaar)}", file=sys.stderr)
        return 1

    print("=== migrate 210/220 -> tropaar" + (" (dry-run)" if dry_run else ""))

    for old, variant, weight, title, link_title in _MOVES:
        src = BIBLIOTHEEK_ROOT / old
        src_default = src / "default"
        dest_variant = tropaar / variant
        if not src_default.is_dir():
            print(f"bron ontbreekt: {_rel(src_default)}", file=sys.stderr)
            return 1

        print(f"  merge {_rel(src_default)} -> {_rel(dest_variant)}", flush=True)
        if dry_run:
            continue

        dest_variant.mkdir(parents=True, exist_ok=True)

        # Verplaats elke uitvoeringsvorm-map
        for child in sorted(src_default.iterdir()):
            if not child.is_dir():
                continue
            target = dest_variant / child.name
            if target.exists():
                raise SystemExit(f"uitvoeringsvorm bestaat al: {_rel(target)}")
            print(f"  move {_rel(child)} -> {_rel(target)}", flush=True)
            shutil.move(str(child), str(target))
            _rename_files_in_dir(
                target,
                f"{old}-default-",
                f"tropaar-{variant}-",
                dry_run=False,
            )

        # Variant-_index: herschrijf of maak
        v_index = dest_variant / "_index.md"
        if v_index.is_file():
            text = v_index.read_text(encoding="utf-8")
        else:
            text = "---\n---\n"
        text = _set_frontmatter_fields(
            text,
            {
                "title": title,
                "linkTitle": link_title,
                "weight": weight,
                "nav_sort": "weight",
                "publicatiestatus": "concept",
                "automatische_inhoud": True,
            },
        )
        v_index.write_text(text, encoding="utf-8", newline="\n")
        print(f"  write {_rel(v_index)}", flush=True)

        # Oude zangstuk-map weg
        if src.is_dir():
            shutil.rmtree(src)
            print(f"  remove tree {_rel(src)}", flush=True)

    # Bladermap-SVG
    svg_root = REPO_ROOT / "static" / "vsa" / "bladermap" / "bibliotheek"
    for old, variant, *_ in _MOVES:
        svg_src = svg_root / old
        if not svg_src.is_dir():
            continue
        svg_dest = svg_root / "tropaar" / variant
        print(f"  move {_rel(svg_src)} -> {_rel(svg_dest)}", flush=True)
        if not dry_run:
            svg_dest.parent.mkdir(parents=True, exist_ok=True)
            if svg_src.name == "default" or (svg_src / "default").is_dir():
                # structuur oud/default/uv of oud/uv
                default = svg_src / "default"
                if default.is_dir():
                    for child in default.iterdir():
                        target = svg_dest / child.name
                        shutil.move(str(child), str(target))
                        _rename_files_in_dir(
                            target,
                            f"{old}-default-",
                            f"tropaar-{variant}-",
                            dry_run=False,
                        )
                    shutil.rmtree(svg_src)
                else:
                    shutil.move(str(svg_src), str(svg_dest))
                    _rename_files_in_dir(
                        svg_dest,
                        f"{old}-default-",
                        f"tropaar-{variant}-",
                        dry_run=False,
                    )
            else:
                shutil.move(str(svg_src), str(svg_dest))
                _rename_files_in_dir(
                    svg_dest,
                    f"{old}-default-",
                    f"tropaar-{variant}-",
                    dry_run=False,
                )

    skip_rewrite = {
        Path(__file__).resolve(),
        (
            REPO_ROOT
            / "content-source"
            / "handleiding"
            / "start"
            / "zangstuk-soorten.md"
        ).resolve(),
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

    if not dry_run:
        for old, variant, *_ in _MOVES:
            dest_variant = tropaar / variant
            if dest_variant.is_dir():
                _add_aliases_to_tree(dest_variant, old, dry_run=False)

    print("OK: tropaar-kruis-migratie klaar" + (" (dry-run)" if dry_run else ""))
    if not dry_run:
        print(
            "Vervolg: python scripts\\build_zoek_index.py ; "
            "scripts\\vsa-products.cmd / audio / lyrics indien nodig."
        )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verplaats 210/220-kruisstukken onder tropaar."
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    return migrate(dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
