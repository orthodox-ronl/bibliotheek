"""Wis alle gegenereerde (regenereerbare) bestanden uit catalogus en koormappen.

Bedoeld voor een schone start: daarna maakt ``products`` / ``pdf`` alles opnieuw.

Wat telt als gegenereerd, is dezelfde definitie als bij ``seed-repo``
(``seed_repo.is_notation_derived_product`` e.d.): een bestandsnaam met een
bronextensie (``.vsa`` / ``.mvsa`` / ``.mscz``) en daarachter nog een extensie
(``{stam}.vsa.svg``, ``{stam}.mvsa.mp3``, ``{stam}.vsa.products-meta.json`` …),
plus ``index.md.pdf`` / ``index.md.translit-*.pdf``.

Blijft altijd staan:

- bronnen (``.vsa``, ``.mvsa``, ``.mscz``, ``.md``, losse ``.svg`` / ``.mxl``),
  ``{stam}.print.mscz``, ``{stam}.mscz.mvsa`` (import-bewerkvorm);
- alles in map ``formules``;
- 'handmatige' mappen: ``index.md`` met ``manueel: true`` (of ``manual``), en
  mappen met een ``*.tekstblad.md`` (tekstbladen, zoals dialoog-met-diaken).

Standaard alleen melden (dry-run). Echt wissen: ``--apply``.
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

REPO_ROOT = SCRIPT_DIR.parent
DEFAULT_ROOTS = (
    REPO_ROOT / "content-source" / "catalogus",
    REPO_ROOT / "content-source" / "koormappen",
)
PROTECTED_DIR_NAMES = frozenset({"formules"})


def is_generated_name(name: str) -> bool:
    """True als ``name`` een regenereerbaar product is (nooit een bron)."""
    from seed_repo import _INDEX_MD_PDF, _PRODUCTS_META, is_notation_derived_product

    return bool(
        _INDEX_MD_PDF.match(name)
        or _PRODUCTS_META.search(name)
        or is_notation_derived_product(name)
    )


def protected_reason(folder: Path, *, root: Path) -> str | None:
    """Waarom deze map niet aangeraakt wordt (of ``None``)."""
    try:
        parts = folder.resolve().relative_to(root.resolve()).parts
    except ValueError:
        parts = folder.parts
    if any(p in PROTECTED_DIR_NAMES for p in parts):
        return "formules"
    from sync_vsa_products import folder_is_handmatig

    if folder_is_handmatig(folder):
        return "handmatig (index.md: manueel)"
    if any(folder.glob("*.tekstblad.md")):
        return "handmatig (tekstblad)"
    return None


def find_generated(root: Path) -> tuple[list[Path], dict[Path, str]]:
    """(te wissen bestanden, beschermde mappen met reden) onder ``root``."""
    files: list[Path] = []
    protected: dict[Path, str] = {}
    if root.is_file():
        reason = protected_reason(root.parent, root=root.parent)
        if reason:
            protected[root.parent] = reason
        elif is_generated_name(root.name):
            files.append(root)
        return files, protected
    if not root.is_dir():
        return files, protected
    folders = [root] + sorted(p for p in root.rglob("*") if p.is_dir())
    for folder in folders:
        entries = [p for p in sorted(folder.iterdir()) if p.is_file()]
        hits = [p for p in entries if is_generated_name(p.name)]
        if not hits:
            continue
        reason = protected_reason(folder, root=root)
        if reason:
            protected[folder] = reason
            continue
        files.extend(hits)
    return files, protected


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def _kind(path: Path) -> str:
    """Korte groepsnaam voor de samenvatting, bijv. ``.vsa.svg``."""
    name = path.name
    if name.lower().startswith("index.md"):
        return "index.md.*"
    lower = name.lower()
    for marker in (".vsa.", ".mvsa.", ".mscz."):
        i = lower.find(marker)
        if i >= 0:
            return name[i:]
    return "overig"


def main(argv: list[str] | None = None) -> int:
    from cli_help import make_parser
    from input_paths import InputPathError, resolve_user_path

    parser = make_parser(
        prog="wis-producten",
        description=(
            "Wis alle gegenereerde bestanden (products, pdf, meta) uit catalogus "
            "en koormappen, zodat alles opnieuw gegenereerd kan worden. "
            "Bronnen, formules en handmatige mappen blijven staan. "
            "Standaard dry-run; echt wissen: --apply."
        ),
    )
    parser.add_argument(
        "root",
        nargs="*",
        help=(
            "Map(pen) of bestand(en) (standaard: catalogus én koormappen). "
            "Korte paden: t.o.v. content-source, catalogus of koormappen."
        ),
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Bestanden echt verwijderen (zonder deze vlag alleen tonen)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Alleen tonen, niets wissen (standaardgedrag; expliciete vlag)",
    )
    args = parser.parse_args(argv)

    if args.dry_run and args.apply:
        print("FAIL: gebruik --dry-run of --apply, niet beide.", file=sys.stderr)
        return 1

    roots: list[Path] = []
    try:
        for raw in args.root or [str(p) for p in DEFAULT_ROOTS]:
            roots.append(resolve_user_path(raw, repo_root=REPO_ROOT))
    except InputPathError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        print(
            "Oplossing: geef een bestaande map of bestand, of laat het "
            "standaardpad staan.",
            file=sys.stderr,
        )
        return 1

    hits: list[Path] = []
    protected: dict[Path, str] = {}
    for root in roots:
        f, p = find_generated(root)
        hits.extend(f)
        protected.update(p)

    mode = "VERWIJDER" if args.apply else "dry-run"
    print(f"=== wis-producten ({mode}) - {len(hits)} bestand(en)", flush=True)
    kinds = Counter(_kind(p) for p in hits)
    for kind, n in sorted(kinds.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"  {n:5d}  {kind}", flush=True)
    if protected:
        print(f"Niet aangeraakt ({len(protected)} map(pen)):", flush=True)
        for folder, reason in sorted(protected.items()):
            print(f"  {_rel(folder)}  [{reason}]", flush=True)

    if args.apply:
        for path in hits:
            path.unlink()
        print(
            f"OK: {len(hits)} bestand(en) verwijderd. Opnieuw genereren: "
            "scripts\\products.cmd (en scripts\\pdf.cmd).",
            flush=True,
        )
        print(
            "Let op: bestanden die niet in git zitten (bijv. index.md.pdf) komen "
            "alleen terug door opnieuw te genereren.",
            flush=True,
        )
    elif hits:
        print(
            f"OK: {len(hits)} bestand(en) zouden verdwijnen "
            "(opnieuw met --apply om te wissen)",
            flush=True,
        )
    else:
        print("OK: niets te wissen", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
