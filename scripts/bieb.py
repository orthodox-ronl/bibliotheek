"""Multi-command CLI ``bieb`` (zoals ``vsa`` / ``mvsa``).

Subcommando's: ``accepteer``, ``hernoem``.
"""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import bieb_accepteer  # noqa: E402
import bieb_hernoem  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in {"-h", "--help"}:
        print(
            "Gebruik: bieb <subcommando> [args...]\n"
            "\n"
            "  accepteer   partituur/tekstblad opnemen onder bibliotheek-id\n"
            "  hernoem     zangstuk-id hernoemen (map, stam, refs, aliases)\n"
            "\n"
            "Voorbeelden:\n"
            "  bieb accepteer trisagion/8a-nederlands/hemelum pad\\x.mscz --dry-run\n"
            "  bieb hernoem 210-heer-red-uw-volk-en-zegen-uw-erfdeel tropaar --dry-run\n"
        )
        return 0 if argv else 2
    cmd = argv[0]
    if cmd == "accepteer":
        return bieb_accepteer.main(argv[1:])
    if cmd == "hernoem":
        return bieb_hernoem.main(argv[1:])
    print(
        f"Onbekend subcommando: {cmd!r} (probeer: accepteer, hernoem)",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
