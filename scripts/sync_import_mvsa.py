"""Maak/vernieuw sibling ``{stam}.mscz.mvsa`` bij een basispartituur-``.mscz``.

Roept tooling aan: ``mscz import`` (via MuseScore → temp-``.mxl`` → ``.mvsa``).
Zet comment-stamps ``vsa-partituur-sha256``. Dit is een **bewerk-/importvorm**,
geen site-product: standaard alleen bestaande siblings vernieuwen; nieuwe
aanmaken met een expliciet ``.mscz``-pad of ``--create``.

CI genereert niet — alleen ``check_import_mvsa`` op bestaande paren; vernieuw
lokaal met ``scripts\\import-mvsa.cmd``.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

from product_meta import (
    FIELD_SOURCE_KIND,
    GENERATOR_IMPORT_MVSA,
    SOURCE_KIND_PARTITUUR,
    partituur_sha256,
    read_mvsa_stamp,
    stamp_mvsa_partituur,
    stamp_sha_from_dict,
    utc_now_iso,
)
from sync_mscz_products import DEFAULT_ROOT, collect_mscz, is_print_mscz
from sync_vsa_products import folder_is_handmatig

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PITCH = "a-g"


def _running_in_ci() -> bool:
    return os.environ.get("CI", "").strip().lower() in {"1", "true", "yes"}


def product_mvsa_for_mscz(mscz: Path) -> Path:
    """``naam.mscz`` → ``naam.mscz.mvsa``."""
    return mscz.with_suffix(".mscz.mvsa")


def mscz_for_import_mvsa(mvsa: Path) -> Path:
    """``naam.mscz.mvsa`` → ``naam.mscz``."""
    name = mvsa.name
    if name.lower().endswith(".mscz.mvsa"):
        return mvsa.with_name(name[: -len(".mvsa")])
    return mvsa.with_suffix(".mscz")


def is_import_mvsa(path: Path) -> bool:
    return path.name.lower().endswith(".mscz.mvsa")


def collect_import_mvsa(root: Path) -> list[Path]:
    """Bestaande import-siblings onder ``root`` (geen eis dat elke .mscz er een heeft)."""
    out: list[Path] = []
    if not root.is_dir():
        return out
    for path in sorted(root.rglob("*.mscz.mvsa")):
        if not path.is_file():
            continue
        if "input" in path.parts:
            continue
        if folder_is_handmatig(path.parent):
            continue
        if " " in path.name:
            raise SystemExit(f"bestandsnaam mag geen spaties hebben: {path.name}")
        out.append(path)
    return out


def _stamp_ok(mvsa: Path, digest: str) -> bool:
    if not mvsa.is_file():
        return False
    stamp = read_mvsa_stamp(mvsa)
    if stamp.get(FIELD_SOURCE_KIND, SOURCE_KIND_PARTITUUR) not in {
        "",
        SOURCE_KIND_PARTITUUR,
    }:
        return False
    return stamp_sha_from_dict(stamp) == digest


def is_stale(mscz: Path, mvsa: Path | None = None) -> bool:
    target = mvsa if mvsa is not None else product_mvsa_for_mscz(mscz)
    return not _stamp_ok(target, partituur_sha256(mscz))


def _run_mscz_import(mscz: Path, mvsa: Path, *, pitch: str) -> None:
    cmd = [
        "mscz",
        "import",
        str(mscz),
        "--pitch",
        pitch,
        "-o",
        str(mvsa),
    ]
    subprocess.check_call(cmd, cwd=str(REPO_ROOT))


def sync_one(mscz: Path, *, pitch: str, dry_run: bool) -> None:
    mvsa = product_mvsa_for_mscz(mscz)
    rel = mscz.relative_to(REPO_ROOT)
    print(f"  MVSA {rel} -> {mvsa.name}", flush=True)
    if dry_run:
        return
    if " " in mvsa.name:
        raise SystemExit(f"bestandsnaam mag geen spaties hebben: {mvsa.name}")
    _run_mscz_import(mscz, mvsa, pitch=pitch)
    if not mvsa.is_file():
        raise RuntimeError(f".mvsa ontbreekt na mscz import: {mvsa}")
    stamp_mvsa_partituur(
        mvsa,
        partituur_hash=partituur_sha256(mscz),
        generated_at=utc_now_iso(),
        generator=GENERATOR_IMPORT_MVSA,
    )


def _resolve_targets(
    root: Path,
    *,
    create: bool,
    policy,
) -> list[Path]:
    """Lijst basispartituur-``.mscz`` die (opnieuw) geïmporteerd moeten worden."""
    from product_regen import need_regen

    if root.is_file():
        path = root
        if is_print_mscz(path):
            raise SystemExit(f"print-.mscz niet voor import-mvsa: {path.name}")
        if path.suffix.lower() != ".mscz":
            raise SystemExit(f"verwacht .mscz-bestand, kreeg: {path.name}")
        if folder_is_handmatig(path.parent):
            raise SystemExit(
                f"map heeft artefacten_handmatig; sla over: {path.parent}"
            )
        return [path]

    if create:
        msczs = collect_mscz(root)
        todo: list[Path] = []
        for m in msczs:
            mvsa = product_mvsa_for_mscz(m)
            exists = mvsa.is_file()
            stamp_ok = _stamp_ok(mvsa, partituur_sha256(m)) if exists else False
            if need_regen(
                policy,
                exists=exists,
                stamp_ok=stamp_ok,
                contract_ok=None,
            ):
                todo.append(m)
        return todo

    # Standaard: alleen bestaande siblings vernieuwen.
    todo = []
    for mvsa in collect_import_mvsa(root):
        mscz = mscz_for_import_mvsa(mvsa)
        if not mscz.is_file():
            continue
        if is_print_mscz(mscz) or folder_is_handmatig(mscz.parent):
            continue
        exists = True
        stamp_ok = _stamp_ok(mvsa, partituur_sha256(mscz))
        if need_regen(
            policy,
            exists=exists,
            stamp_ok=stamp_ok,
            contract_ok=None,
        ):
            todo.append(mscz)
    return todo


def main(argv: list[str] | None = None) -> int:
    from product_regen import add_regen_arguments, policy_from_args

    parser = argparse.ArgumentParser(
        description=(
            "Importeer basispartituur-.mscz naar sibling .mscz.mvsa "
            "(bewerkvorm; standaard alleen bestaande siblings)."
        )
    )
    parser.add_argument(
        "root",
        nargs="?",
        type=Path,
        default=DEFAULT_ROOT,
        help="Zoekroot of één .mscz (default: content-source/bibliotheek)",
    )
    add_regen_arguments(parser)
    parser.add_argument(
        "--create",
        action="store_true",
        help=(
            "Maak ontbrekende .mscz.mvsa voor alle basispartituur-.mscz "
            "onder de zoekroot (standaard: alleen bestaande siblings)"
        ),
    )
    parser.add_argument(
        "--pitch",
        choices=["doremi", "a-g", "abc", "vsa"],
        default=DEFAULT_PITCH,
        help=f"Spelling voor mscz import (default: {DEFAULT_PITCH})",
    )
    args = parser.parse_args(argv)
    policy = policy_from_args(args)
    root = args.root if args.root.is_absolute() else REPO_ROOT / args.root
    todo = _resolve_targets(root, create=args.create, policy=policy)
    if not todo:
        existing = (
            1
            if root.is_file()
            else len(collect_import_mvsa(root if root.is_dir() else root.parent))
        )
        print(
            f"Import-.mvsa up-to-date ({existing} bestaande sibling(s))",
            flush=True,
        )
        return 0

    from vsa.musescore_cli import find_musescore

    if find_musescore() is None:
        print(
            f"{len(todo)} stale/missende .mscz.mvsa t.o.v. .mscz; MuseScore ontbreekt.",
            flush=True,
        )
        if _running_in_ci():
            print("CI: sla lokale MuseScore-import over.", flush=True)
            return 0
        print(r"Installeer MuseScore 4 of: scripts\import-mvsa.cmd", flush=True)
        for mscz in todo:
            print(f"  - {mscz.name} -> {product_mvsa_for_mscz(mscz).name}", flush=True)
        return 1

    print(f"Import-.mvsa bijwerken: {len(todo)}", flush=True)
    failed = 0
    for mscz in todo:
        print(f"== {mscz.relative_to(REPO_ROOT)}", flush=True)
        try:
            sync_one(mscz, pitch=args.pitch, dry_run=args.dry_run)
        except Exception as exc:  # noqa: BLE001
            print(f"  FAILED {exc}", flush=True)
            failed += 1
    if failed:
        print(f"{failed} mislukt van {len(todo)}", flush=True)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
