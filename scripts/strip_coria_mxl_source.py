"""Strip ``identification/source`` uit alle catalogus-Coria-``.mxl``.

Coria faalt op ``<source>`` samen met ``<encoding>`` (``translation failed``).
Brontekst blijft in ``miscellaneous-field name="bron"``.

Na afloop: ``scripts\\fingerprint_coria_mxl.py`` (of ``check``) opnieuw.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from check_mxl_playback_contract import collect_coria_mxl, has_coria_source_encoding_clash
from coria_mxl import load_score_xml, strip_identification_source, write_mxl

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOT = REPO_ROOT / "content-source" / "catalogus"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "root",
        nargs="?",
        type=Path,
        default=DEFAULT_ROOT,
        help="Zoekroot (default: content-source/catalogus)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Alleen tonen welke bestanden source+encoding hebben",
    )
    args = parser.parse_args(argv)
    root = args.root if args.root.is_absolute() else REPO_ROOT / args.root

    touched = 0
    scanned = 0
    for path, _profile in collect_coria_mxl(root):
        scanned += 1
        if not has_coria_source_encoding_clash(path):
            continue
        rel = path.relative_to(REPO_ROOT).as_posix()
        if args.dry_run:
            print(f"  would-strip {rel}", flush=True)
            touched += 1
            continue
        root_xml = load_score_xml(path)
        n = strip_identification_source(root_xml)
        if n:
            write_mxl(path, root_xml)
            print(f"  stripped {rel}", flush=True)
            touched += 1
    print(
        f"Coria-source-strip: {touched} bijgewerkt van {scanned} Coria-.mxl",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
