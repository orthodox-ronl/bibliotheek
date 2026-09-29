"""Dunne wrapper: basispartituur-layout via VSA-tooling (geen fork).

Roept ``vsa.mscz_layout.apply_mscz_layout_profile`` (profiel ``partituur``)
aan met een expliciete bibliotheek-id. Bij ``.mxl``-invoer eerst
``mxl mscz`` (MuseScore), daarna het layoutprofiel met id.

Weigert ``*.print.mscz``. Geen PDF/Coria — dat is ``mscz-products``.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from coria_mxl import require_no_spaces
from sync_mscz_products import is_print_mscz

REPO_ROOT = Path(__file__).resolve().parents[1]


def _resolve_id(explicit: str | None, path: Path) -> str | None:
    """Expliciete ``--id`` wint; anders pad onder ``content-source/bibliotheek``."""
    from vsa.bibliotheek_id import normalize_bibliotheek_id

    from ensure_bibliotheek_id import id_from_bibliotheek_path

    if explicit is not None:
        return normalize_bibliotheek_id(explicit)
    return id_from_bibliotheek_path(path)


def _mxl_to_mscz(src: Path, out: Path) -> None:
    cmd = ["mxl", "mscz", str(src), "-o", str(out)]
    proc = subprocess.run(cmd, cwd=REPO_ROOT)
    if proc.returncode != 0:
        raise SystemExit(proc.returncode or 1)


def _apply_layout(mscz: Path, bibliotheek_id: str | None) -> None:
    from vsa.mscz_layout import MsczPartituurError, apply_mscz_layout_profile

    try:
        apply_mscz_layout_profile(
            mscz,
            layout="partituur",
            bibliotheek_id=bibliotheek_id,
        )
    except MsczPartituurError as exc:
        raise SystemExit(f"{mscz}: ERROR: {exc}") from exc


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("path", type=Path, help=".mscz of .mxl bronbestand")
    p.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Doel-.mscz (verplicht bij .mxl; bij .mscz optioneel kopie)",
    )
    p.add_argument(
        "--id",
        default=None,
        help="Bibliotheek-id zangstuk/variant/uitvoeringsvorm",
    )
    args = p.parse_args(argv)

    src = args.path if args.path.is_absolute() else REPO_ROOT / args.path
    if not src.is_file():
        print(f"Bestand niet gevonden: {src}", file=sys.stderr)
        return 1
    require_no_spaces(src)
    if is_print_mscz(src):
        print(
            f"Geweigerd: print-vel ({src.name}). Geen layout op *.print.mscz.",
            file=sys.stderr,
        )
        return 1

    suffix = src.suffix.lower()
    if suffix == ".mxl":
        if args.output is None:
            print(
                "Bij .mxl-invoer is -o/--output naar een .mscz verplicht.",
                file=sys.stderr,
            )
            return 2
        out = args.output if args.output.is_absolute() else REPO_ROOT / args.output
        if out.suffix.lower() != ".mscz":
            out = out.with_suffix(".mscz")
        require_no_spaces(out)
        out.parent.mkdir(parents=True, exist_ok=True)
        _mxl_to_mscz(src, out)
        bib = _resolve_id(args.id, out)
        _apply_layout(out, bib)
        id_note = f" bibliotheek-id={bib}" if bib else ""
        print(f"ok {out.as_posix()}{id_note}")
        return 0

    if suffix != ".mscz":
        print(f"Verwacht .mscz of .mxl; kreeg {suffix!r}", file=sys.stderr)
        return 2

    if args.output is not None:
        out = args.output if args.output.is_absolute() else REPO_ROOT / args.output
        if out.suffix.lower() != ".mscz":
            out = out.with_suffix(".mscz")
        require_no_spaces(out)
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, out)
        target = out
    else:
        target = src

    bib = _resolve_id(args.id, target)
    _apply_layout(target, bib)
    id_note = f" bibliotheek-id={bib}" if bib else ""
    print(f"ok {target.as_posix()}{id_note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
