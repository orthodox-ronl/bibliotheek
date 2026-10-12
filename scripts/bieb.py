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

import bieb_accepteer  # noqa: E402
import bieb_hernoem  # noqa: E402
import bieb_kopieer  # noqa: E402
import bieb_verwijder  # noqa: E402

# Canonieke NL-naam → handler. Engelse aliassen staan in ``_ALIASES``.
_COMMANDS: dict[str, object] = {
    "accepteer": bieb_accepteer.main,
    "hernoem": bieb_hernoem.main,
    "verwijder": bieb_verwijder.main,
    "kopieer": bieb_kopieer.main,
}
_ALIASES: dict[str, str] = {
    "accept": "accepteer",
    "rename": "hernoem",
    "delete": "verwijder",
    "copy": "kopieer",
}


def resolve_subcommand(name: str) -> str | None:
    """NL-naam of Engelse alias → canonieke subcommando-naam, of ``None``."""
    key = name.strip().lower()
    if key in _COMMANDS:
        return key
    return _ALIASES.get(key)


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in {"-h", "--help"}:
        print(
            "Gebruik: bieb <subcommando> [args...]\n"
            "\n"
            "  accepteer   partituur/tekstblad opnemen onder catalogus-id\n"
            "  hernoem     catalogus-id hernoemen (zangstuk/variant/uitvoeringsvorm)\n"
            "  verwijder   catalogus-id wissen (dangling refs rapporteren)\n"
            "  kopieer     uitvoeringsvorm kopiëren naar nieuw id\n"
            "\n"
            "Engelse aliassen: accept, rename, delete, copy.\n"
            "\n"
            "Voorbeelden:\n"
            "  bieb accepteer trisagion/8a-nederlands/hemelum pad\\x.mscz --dry-run\n"
            "  bieb hernoem ektinia/vredes ektinia/litanie --dry-run\n"
            "  bieb verwijder ektinia/vredes/hemelum --dry-run\n"
            "  bieb kopieer ektinia/vredes/hemelum groningen --dry-run\n"
        )
        return 0 if argv else 2
    canonical = resolve_subcommand(argv[0])
    if canonical is None:
        print(
            f"Onbekend subcommando: {argv[0]!r} "
            "(probeer: accepteer, hernoem, verwijder, kopieer "
            "of accept, rename, delete, copy)",
            file=sys.stderr,
        )
        return 2
    handler = _COMMANDS[canonical]
    return int(handler(argv[1:]))  # type: ignore[operator]


if __name__ == "__main__":
    raise SystemExit(main())
