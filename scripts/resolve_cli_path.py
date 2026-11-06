"""Print één opgelost CLI-pad (voor ``.cmd``-wrappers zoals validate).

Gebruik::

    python scripts\\resolve_cli_path.py [pad]

Zonder pad: ``content-source/catalogus``. Exit 1 + stderr bij ontbrekend pad.
Stdout: absoluut pad (één regel), geschikt voor ``vsa validate``.
"""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from input_paths import InputPathError, resolve_user_path  # noqa: E402

REPO_ROOT = _SCRIPTS.parent
_DEFAULT = "content-source/catalogus"


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    raw = args[0] if args else _DEFAULT
    try:
        path = resolve_user_path(raw, repo_root=REPO_ROOT)
    except InputPathError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        print(
            "Oplossing: geef een bestaande map of bronbestand "
            "(kort: t.o.v. content-source, catalogus of koormappen).",
            file=sys.stderr,
        )
        return 1
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
