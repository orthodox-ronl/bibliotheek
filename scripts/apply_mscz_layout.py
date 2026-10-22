"""Dunne wrapper: basispartituur-layout via VSA-tooling (geen fork).

Roept ``vsa.mscz_layout.apply_mscz_layout_profile`` (profiel ``partituur``)
aan met een expliciete bibliotheek-id. Bij ``.mxl``-invoer eerst
``mxl mscz`` (MuseScore), daarna het layoutprofiel met id.

Invoer: één ``.mscz``/``.mxl`` **of** een map (recursief die extensies).
``-o`` alleen bij precies één bronbestand. Weigert ``*.print.mscz``.
Geen PDF/Coria — dat is ``mscz-products``.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from batch_guard import add_yes_argument, confirm_batch, run_timed_batch
from coria_mxl import require_no_spaces
from input_paths import InputPathError, collect_cli_sources, reject_multi_with_output
from sync_mscz_products import is_print_mscz

REPO_ROOT = Path(__file__).resolve().parents[1]
_LAYOUT_SUFFIXES = (".mscz", ".mxl")
_BATCH_KIND = "layout"


def _resolve_id(explicit: str | None, path: Path) -> str | None:
    """Expliciete ``--id`` wint; anders pad onder ``content-source/catalogus``."""
    from vsa.bibliotheek_id import normalize_bibliotheek_id

    from ensure_bibliotheek_id import id_from_catalogus_path

    if explicit is not None:
        return normalize_bibliotheek_id(explicit)
    return id_from_catalogus_path(path)


def _mxl_to_mscz(src: Path, out: Path) -> None:
    cmd = ["mxl", "mscz", str(src), "-o", str(out)]
    proc = subprocess.run(cmd, cwd=REPO_ROOT)
    if proc.returncode != 0:
        raise SystemExit(proc.returncode or 1)


def _apply_layout(
    mscz: Path,
    bibliotheek_id: str | None,
    *,
    bron: str | None = None,
) -> None:
    from vsa.mscz_layout import MsczPartituurError, apply_mscz_layout_profile

    if bron is None:
        from vsa_bron import bron_uitgangspunt_near

        bron = bron_uitgangspunt_near(mscz)

    try:
        apply_mscz_layout_profile(
            mscz,
            layout="partituur",
            bibliotheek_id=bibliotheek_id,
            bron=bron,
        )
    except MsczPartituurError as exc:
        raise SystemExit(f"{mscz}: ERROR: {exc}") from exc


def _layout_one(
    src: Path,
    *,
    output: Path | None,
    explicit_id: str | None,
    bron: str | None,
) -> int:
    require_no_spaces(src)
    if is_print_mscz(src):
        print(
            f"Geweigerd: print-vel ({src.name}). Geen layout op *.print.mscz.",
            file=sys.stderr,
        )
        return 1

    suffix = src.suffix.lower()
    if suffix == ".mxl":
        if output is None:
            print(
                "Bij .mxl-invoer is -o/--output naar een .mscz verplicht.",
                file=sys.stderr,
            )
            return 2
        out = output if output.is_absolute() else REPO_ROOT / output
        if out.suffix.lower() != ".mscz":
            out = out.with_suffix(".mscz")
        require_no_spaces(out)
        out.parent.mkdir(parents=True, exist_ok=True)
        _mxl_to_mscz(src, out)
        bib = _resolve_id(explicit_id, out)
        _apply_layout(out, bib, bron=bron)
        id_note = f" bibliotheek-id={bib}" if bib else ""
        bron_note = f" bron={bron!r}" if bron else ""
        print(f"ok {out.as_posix()}{id_note}{bron_note}")
        return 0

    if suffix != ".mscz":
        print(f"Verwacht .mscz of .mxl; kreeg {suffix!r}", file=sys.stderr)
        return 2

    if output is not None:
        out = output if output.is_absolute() else REPO_ROOT / output
        if out.suffix.lower() != ".mscz":
            out = out.with_suffix(".mscz")
        require_no_spaces(out)
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, out)
        target = out
    else:
        target = src

    bib = _resolve_id(explicit_id, target)
    _apply_layout(target, bib, bron=bron)
    id_note = f" bibliotheek-id={bib}" if bib else ""
    bron_note = f" bron={bron!r}" if bron else ""
    print(f"ok {target.as_posix()}{id_note}{bron_note}")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "path",
        type=Path,
        help=".mscz/.mxl-bestand of map (recursief .mscz/.mxl)",
    )
    p.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Doel-.mscz (alleen bij precies één bron; verplicht bij .mxl)",
    )
    p.add_argument(
        "--id",
        default=None,
        help="Bibliotheek-id zangstuk/variant/uitvoeringsvorm",
    )
    p.add_argument(
        "--bron",
        default=None,
        help="Bronvermelding → MuseScore meta source + colofon (default: "
        "bron.uitgangspunt uit sibling .vsa/.mvsa indien aanwezig)",
    )
    add_yes_argument(p)
    args = p.parse_args(argv)

    root = args.path if args.path.is_absolute() else REPO_ROOT / args.path
    try:
        sources = collect_cli_sources(root, suffixes=_LAYOUT_SUFFIXES)
        reject_multi_with_output(sources, args.output)
    except InputPathError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    # Map-scan: sla print-velden over (expliciet één *.print.mscz blijft weigering).
    if root.is_dir():
        filtered = [s for s in sources if not is_print_mscz(s)]
        if not filtered:
            print(
                f"Geen passende .mscz/.mxl (na filter *.print.mscz): {root}",
                file=sys.stderr,
            )
            return 2
        sources = filtered

    if len(sources) > 1 and args.id is not None:
        print(
            "--id is alleen zinvol bij precies één bronbestand.",
            file=sys.stderr,
        )
        return 2

    n_mxl = sum(1 for s in sources if s.suffix.lower() == ".mxl")
    n_mscz = len(sources) - n_mxl
    details = [
        f"{len(sources)} bestand(en): {n_mscz}× .mscz, {n_mxl}× .mxl",
        (
            "Actie: layout in-place (.mscz) / via -o (.mxl bij één bron)"
            if len(sources) == 1
            else "Actie: layout in-place per .mscz; .mxl in batch vereist apart -o (skip/fout)"
        ),
    ]
    if n_mxl and len(sources) > 1:
        details.append(
            "Let op: .mxl in een map-batch faalt zonder per-bestand -o; "
            "layout die eerst los of converteer naar .mscz."
        )
    if not confirm_batch(
        _BATCH_KIND,
        n=len(sources),
        headline=str(root),
        details=details,
        yes=args.yes,
    ):
        return 2

    single = len(sources) == 1

    def _one(src: Path) -> int:
        return _layout_one(
            src,
            output=args.output if single else None,
            explicit_id=args.id if single else None,
            bron=args.bron,
        )

    ok, failed, _skipped = run_timed_batch(
        _BATCH_KIND,
        sources,
        _one,
        label=lambda p: p.as_posix(),
    )
    if len(sources) > 1:
        print(f"Klaar: {ok} ok, {failed} mislukt.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
