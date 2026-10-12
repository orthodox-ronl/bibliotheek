"""Kopieer een uitvoeringsvorm naar een nieuw catalogus-id.

Gebruik::

    bieb kopieer <bron-id> <nieuw-id> [--dry-run]

Alleen **uitvoeringsvorm** (leaf). Bron en doel: slash- of stam-vorm;
nieuw mag alleen het laatste segment zijn (zelfde ouder). Doelmap mag
nog niet bestaan.

Kopieert bestanden (publicatiestam hernoemd), zet leaf-``index.md`` met
nieuw ``bieb id`` en afgeleide titels, kopieert bladermap-SVG indien
aanwezig. Maakt ontbrekende zangstuk-/variant-``_index.md`` aan.
Geen koormap-slot (handmatig). Geen variant-/zangstuk-kopie.
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
    complete_new_ref,
    derived_leaf_link_title,
    derived_leaf_title,
    interactive_disambiguate,
    parse_id,
    ref_folder,
    resolve_existing_ref,
    slash_to_stem,
)
from bieb_accepteer import ensure_sections  # noqa: E402

HELP_KOPIEER = """\
bieb kopieer — uitvoeringsvorm kopiëren naar nieuw id

Alleen leaf (zangstuk/variant/uitvoeringsvorm). Voorbeelden:

  bieb kopieer ektinia/vredes/hemelum ektinia/vredes/groningen --dry-run
  bieb kopieer ektinia-vredes-hemelum groningen
  bieb kopieer ektinia\\vredes\\hemelum vredes\\groningen
  bieb kopieer tropaar/zondag-toon-1/groningen tropaar/zondag-toon-2/groningen

Nieuw mag kort: alleen uv, variant/uv, variant-uv, of vol pad.
Ambigu? Genummerde voorstellen; Enter = 1.
Doelmap mag nog niet bestaan. Geen automatische koormap-slot.
Na kopiëren: products vernieuwen + check.
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


def _resolve_leaf(raw: str, *, label: str) -> str:
    try:
        level, slash = resolve_existing_ref(raw)
    except AmbiguousRefError as exc:
        chosen = interactive_disambiguate(
            exc, help_text=HELP_KOPIEER, prefix="kopieer"
        )
        if chosen is None:
            raise ValueError(f"gestopt: geen {label}") from exc
        if isinstance(chosen, tuple) and chosen[0]:
            level, slash = chosen
        else:
            text = chosen if isinstance(chosen, str) else chosen[1]
            level, slash = resolve_existing_ref(text)
    if level != "leaf":
        raise ValueError(
            f"{label} moet een uitvoeringsvorm zijn "
            f"(zangstuk/variant/uitvoeringsvorm), kreeg {level} {slash!r}. "
            "Variant-/zangstuk-kopie bestaat nog niet."
        )
    return slash


def _resolve_new_leaf(bron_slash: str, raw: str) -> str:
    try:
        level, slash = complete_new_ref("leaf", bron_slash, raw)
    except AmbiguousRefError as exc:
        chosen = interactive_disambiguate(
            exc, help_text=HELP_KOPIEER, prefix="kopieer"
        )
        if chosen is None:
            raise ValueError("gestopt: geen nieuw id") from exc
        if isinstance(chosen, tuple) and chosen[0]:
            level, slash = chosen
        else:
            text = chosen if isinstance(chosen, str) else chosen[1]
            level, slash = complete_new_ref("leaf", bron_slash, text)
    if level != "leaf":
        raise ValueError(f"nieuw id is geen uitvoeringsvorm: {slash!r}")
    # complete_new_ref hoeft doel niet te laten bestaan; parse ter controle
    parse_id(slash)
    return slash


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


def _leaf_index_text(
    ident: str,
    *,
    status: str,
    artefacten_handmatig: bool,
    source_paths: list[Path],
) -> str:
    title = derived_leaf_title(ident, source_paths=source_paths)
    link = derived_leaf_link_title(ident)
    handmatig = "artefacten_handmatig: true\n" if artefacten_handmatig else ""
    return (
        f"---\ntitle: \"{title}\"\nlinkTitle: \"{link}\"\n"
        f"publicatiestatus: {status}\n"
        f"{handmatig}"
        "automatische_inhoud: false\n---\n\n"
        f"# {title}\n\n"
        f"{{{{< bieb id=\"{ident}\" >}}}}\n"
    )


def _dest_name(name: str, old_stem: str, new_stem: str) -> str:
    if name.startswith(f"{old_stem}-"):
        return f"{new_stem}-{name[len(old_stem) + 1 :]}"
    if name.startswith(f"{old_stem}."):
        return f"{new_stem}{name[len(old_stem) :]}"
    return name


def _svg_root_for(slash_id: str) -> Path:
    return REPO_ROOT.joinpath(
        "static", "vsa", "bladermap", "catalogus", *slash_id.split("/")
    )


def _copy_tree_renaming(
    src: Path,
    dest: Path,
    *,
    old_stem: str,
    new_stem: str,
    dry_run: bool,
) -> int:
    n = 0
    files = sorted(p for p in src.rglob("*") if p.is_file())
    for path in files:
        rel = path.relative_to(src)
        parts = list(rel.parts[:-1]) + [_dest_name(rel.name, old_stem, new_stem)]
        out = dest.joinpath(*parts)
        print(f"  copy {_rel(path)} -> {_rel(out)}", flush=True)
        if not dry_run:
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, out)
        n += 1
    return n


def kopieer(bron_raw: str, nieuw_raw: str, *, dry_run: bool) -> int:
    bron = _resolve_leaf(bron_raw, label="bron")
    nieuw = _resolve_new_leaf(bron, nieuw_raw)
    if bron == nieuw:
        print("bron en nieuw zijn gelijk", file=sys.stderr)
        return 2

    src = ref_folder(bron)
    dest = ref_folder(nieuw)
    if not src.is_dir():
        print(f"bronmap ontbreekt: {_rel(src)}", file=sys.stderr)
        return 1
    if dest.exists():
        print(f"doelmap bestaat al: {_rel(dest)}", file=sys.stderr)
        return 1

    old_stem = slash_to_stem(bron)
    new_stem = slash_to_stem(nieuw)

    index_src = src / "index.md"
    status = "reviewable"
    handmatig = False
    if index_src.is_file():
        try:
            raw_idx = index_src.read_text(encoding="utf-8")
        except OSError:
            raw_idx = ""
        status = _fm_value(raw_idx, "publicatiestatus") or status
        handmatig = (_fm_value(raw_idx, "artefacten_handmatig") or "").lower() in {
            "true",
            "yes",
            "1",
        }

    source_for_title = [
        p
        for p in sorted(src.iterdir())
        if p.is_file() and p.suffix.lower() in {".vsa", ".mvsa"}
    ]

    print(
        f"=== bieb kopieer [leaf] {bron} -> {nieuw}"
        + (" (dry-run)" if dry_run else ""),
        flush=True,
    )

    ensure_sections(nieuw, dry_run=dry_run)

    n = 0
    for path in sorted(p for p in src.rglob("*") if p.is_file()):
        rel = path.relative_to(src)
        if rel.name.lower() == "index.md" and len(rel.parts) == 1:
            out = dest / "index.md"
            text = _leaf_index_text(
                nieuw,
                status=status,
                artefacten_handmatig=handmatig,
                source_paths=source_for_title,
            )
            print(f"  write {_rel(out)} (nieuw bieb id)", flush=True)
            if not dry_run:
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(text, encoding="utf-8", newline="\n")
            n += 1
            continue
        dest_name = _dest_name(rel.name, old_stem, new_stem)
        out = dest.joinpath(*rel.parts[:-1], dest_name)
        print(f"  copy {_rel(path)} -> {_rel(out)}", flush=True)
        if not dry_run:
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, out)
            # Tekstbestanden: stam/id in inhoud bijwerken (colofon, VSA-paden)
            if out.suffix.lower() in {".vsa", ".mvsa", ".md", ".txt"}:
                try:
                    body = out.read_text(encoding="utf-8")
                except (OSError, UnicodeDecodeError):
                    body = ""
                if body and (bron in body or old_stem in body):
                    body = body.replace(bron, nieuw).replace(old_stem, new_stem)
                    # title/linkTitle in gekopieerde niet-index md niet forceren
                    out.write_text(body, encoding="utf-8", newline="\n")
        n += 1

    print(f"  catalogus-bestanden: {n}", flush=True)

    svg_src = _svg_root_for(bron)
    svg_dest = _svg_root_for(nieuw)
    if svg_src.is_dir():
        if svg_dest.exists():
            print(f"FAIL: SVG-doel bestaat al: {_rel(svg_dest)}", file=sys.stderr)
            return 1
        n_svg = _copy_tree_renaming(
            svg_src, svg_dest, old_stem=old_stem, new_stem=new_stem, dry_run=dry_run
        )
        print(f"  SVG-bestanden: {n_svg}", flush=True)
    else:
        print("  SVG: (geen bronmap)", flush=True)

    print("  koormap-slot: niet aangemaakt (handmatig)", flush=True)
    print("OK: kopieer klaar" + (" (dry-run, niets geschreven)" if dry_run else ""))
    if not dry_run:
        print(
            "Vervolg: products vernieuwen; "
            "python scripts\\build_zoek_index.py ; "
            "scripts\\check.cmd. Eventueel koormap-slot met bieb.",
            flush=True,
        )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="bieb kopieer",
        description="Kopieer een uitvoeringsvorm naar een nieuw catalogus-id.",
    )
    parser.add_argument("bron", nargs="?", help="Bron-uitvoeringsvorm (slash of stam)")
    parser.add_argument(
        "nieuw",
        nargs="?",
        help="Nieuw id (slash, stam, of alleen uitvoeringsvorm-segment)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Toon acties zonder te schrijven",
    )
    args = parser.parse_args(argv)

    bron = args.bron
    nieuw = args.nieuw
    if bron in {"?", "-h", "--help"}:
        _print_help_block(HELP_KOPIEER)
        return 0 if bron == "?" else 2
    if not bron:
        bron = _prompt_until("Bron-id (? voor uitleg): ", HELP_KOPIEER)
        if bron is None:
            return 2
    if not nieuw:
        nieuw = _prompt_until("Nieuw id (? voor uitleg): ", HELP_KOPIEER)
        if nieuw is None:
            return 2
    try:
        return kopieer(bron, nieuw, dry_run=args.dry_run)
    except ValueError as exc:
        print(f"kopieer: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
