"""Multi-command CLI ``bieb`` (zoals ``vsa`` / ``mvsa``).

Subcommando's (NL canoniek): ``accepteer``, ``hernoem``, ``verwijder``,
``kopieer``. Engelse aliassen: ``accept``, ``rename``, ``delete``, ``copy``.
"""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import bieb_fs  # noqa: E402

# Canonieke NL-naam → module. Engelse aliassen staan in ``_ALIASES``.
# Modules worden pas geladen bij het gekozen subcommando (zodat een kapotte
# ``hernoem`` niet ``verwijder`` blokkeert).
_COMMAND_MODULES: dict[str, str] = {
    "accepteer": "bieb_accepteer",
    "hernoem": "bieb_hernoem",
    "verwijder": "bieb_verwijder",
    "kopieer": "bieb_kopieer",
}
_ALIASES: dict[str, str] = {
    "accept": "accepteer",
    "rename": "hernoem",
    "delete": "verwijder",
    "copy": "kopieer",
}

# Compat: tests patchten ``_COMMANDS``; houd die dict bij na lazy load.
_COMMANDS: dict[str, object] = {}


def resolve_subcommand(name: str) -> str | None:
    """NL-naam of Engelse alias → canonieke subcommando-naam, of ``None``."""
    key = name.strip().lower()
    if key in _COMMAND_MODULES:
        return key
    return _ALIASES.get(key)


def _load_handler(canonical: str):
    if canonical in _COMMANDS:
        return _COMMANDS[canonical]
    mod_name = _COMMAND_MODULES[canonical]
    try:
        module = __import__(mod_name)
    except ImportError as exc:
        print(
            f"FAIL: bieb kan module {mod_name!r} niet laden: {exc}\n"
            "Oplossing: zorg dat alle bestanden onder scripts\\ bij dezelfde "
            "versie horen (niet half gekopieerd tussen mappen). "
            "Werk scripts\\catalogus.py en de bieb_*.py bij vanuit één checkout, "
            "of vraag na.",
            file=sys.stderr,
        )
        raise SystemExit(1) from None
    handler = module.main
    _COMMANDS[canonical] = handler
    return handler


_BIEB_EPILOG = """\
Engelse aliassen: accept, rename, delete, copy.

Geen gedeelde top-level opties: elke subcommando heeft eigen flags
(standaard o.a. --dry-run uit). Hulp per subcommando: bieb <naam> -h

Voorbeelden:
  bieb accepteer trisagion/8a-nederlands/hemelum pad\\x.mscz --dry-run
  bieb hernoem ektinia/vredes ektinia/litanie --dry-run
  bieb verwijder ektinia/vredes/hemelum --dry-run
  bieb kopieer ektinia/vredes/hemelum groningen --dry-run

Handleiding: content-source\\handleiding\\scripts\\bieb-*.md
"""


def build_root_parser():
    """Top-level help: subcommando's + epilog (zelfde stijl als ``bieb hernoem -h``)."""
    from cli_help import make_parser

    p = make_parser(
        prog="bieb",
        description=(
            "Catalogus-CLI: partituur/tekstblad opnemen, hernoemen, "
            "verwijderen of kopiëren onder content-source\\catalogus."
        ),
        epilog=_BIEB_EPILOG,
    )
    sub = p.add_subparsers(
        title="subcommando's",
        dest="command",
        metavar="{accepteer,hernoem,verwijder,kopieer}",
        required=True,
    )
    sub.add_parser(
        "accepteer",
        aliases=["accept"],
        help="partituur/tekstblad opnemen onder catalogus-id",
    )
    sub.add_parser(
        "hernoem",
        aliases=["rename"],
        help="catalogus-id hernoemen (zangstuk/variant/uitvoeringsvorm)",
    )
    sub.add_parser(
        "verwijder",
        aliases=["delete"],
        help="catalogus-id wissen (dangling refs rapporteren)",
    )
    sub.add_parser(
        "kopieer",
        aliases=["copy"],
        help="uitvoeringsvorm kopiëren naar nieuw id",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in {"-h", "--help"}:
        build_root_parser().print_help()
        return 0 if argv else 2
    canonical = resolve_subcommand(argv[0])
    if canonical is None:
        print(
            f"Onbekend subcommando: {argv[0]!r} "
            "(probeer: accepteer, hernoem, verwijder, kopieer "
            "of accept, rename, delete, copy)",
            file=sys.stderr,
        )
        build_root_parser().print_help()
        return 2
    try:
        handler = _load_handler(canonical)
    except SystemExit as exc:
        code = exc.code
        return int(code) if isinstance(code, int) else 1
    return bieb_fs.run_handler(handler, argv[1:], command=canonical)


if __name__ == "__main__":
    raise SystemExit(main())
