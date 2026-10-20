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
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from product_kind import (
    DEFAULT_ROOT,
    REPO_ROOT,
    ProductSlot,
    catalog_eligible,
    main_for_kind,
    require_no_spaces_name,
)
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
from product_regen import RegenPolicy, list_source_paths
from sync_mscz_products import collect_mscz, is_print_mscz
from sync_vsa_products import folder_is_handmatig

DEFAULT_PITCH = "a-g"


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
    for path in list_source_paths(root, pattern="*.mscz.mvsa"):
        if not path.is_file():
            continue
        name = path.name.lower()
        if not name.endswith(".mscz.mvsa"):
            continue
        if not catalog_eligible(path, folder_is_handmatig=folder_is_handmatig):
            continue
        require_no_spaces_name(path)
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
    require_no_spaces_name(mvsa)
    _run_mscz_import(mscz, mvsa, pitch=pitch)
    if not mvsa.is_file():
        raise RuntimeError(f".mvsa ontbreekt na mscz import: {mvsa}")
    stamp_mvsa_partituur(
        mvsa,
        partituur_hash=partituur_sha256(mscz),
        generated_at=utc_now_iso(),
        generator=GENERATOR_IMPORT_MVSA,
    )


def collect_import_sources(root: Path, *, create: bool) -> list[Path]:
    """Basispartituur-``.mscz`` die in aanmerking komen voor import-``.mvsa``."""
    if root.is_file():
        path = root
        if is_print_mscz(path):
            return []
        if path.suffix.lower() != ".mscz":
            return []
        if folder_is_handmatig(path.parent):
            return []
        return [path]

    if create:
        return collect_mscz(root)

    # Standaard: alleen .mscz met bestaande import-sibling.
    out: list[Path] = []
    for mvsa in collect_import_mvsa(root):
        mscz = mscz_for_import_mvsa(mvsa)
        if not mscz.is_file():
            continue
        if is_print_mscz(mscz) or folder_is_handmatig(mscz.parent):
            continue
        out.append(mscz)
    return out


@dataclass
class ImportKind:
    id: str = "import"
    label: str = "Import-.mvsa"
    source_noun: str = " .mscz"
    fix_cmd: str = r"scripts\import-mvsa.cmd"
    create: bool = False
    pitch: str = DEFAULT_PITCH

    def collect(self, root: Path) -> list[Path]:
        return collect_import_sources(root, create=self.create)

    def slots_for(self, source: Path, policy: RegenPolicy) -> list[ProductSlot]:
        del policy
        mvsa = product_mvsa_for_mscz(source)
        exists = mvsa.is_file()
        # Zonder --create: ontbrekende sibling komt niet in collect.
        # Met --create of expliciet .mscz-pad: missing telt mee via need_regen.
        stamp_ok = _stamp_ok(mvsa, partituur_sha256(source)) if exists else False
        return [
            ProductSlot(
                path=mvsa,
                exists=exists,
                stamp_ok=stamp_ok,
                contract_ok=None,
                needs_musescore=True,
            )
        ]

    def sync(self, source: Path, *, need: Sequence[bool], dry_run: bool) -> None:
        if need and need[0]:
            sync_one(source, pitch=self.pitch, dry_run=dry_run)


KIND = ImportKind()


def main(argv: list[str] | None = None) -> int:
    def add_extra(parser: argparse.ArgumentParser) -> None:
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

    def after_parse(args: argparse.Namespace) -> None:
        KIND.create = bool(args.create)
        KIND.pitch = str(args.pitch)

    return main_for_kind(
        KIND,
        argv,
        description=(
            "Importeer basispartituur-.mscz naar sibling .mscz.mvsa "
            "(bewerkvorm; standaard alleen bestaande siblings)."
        ),
        default_root=DEFAULT_ROOT,
        add_extra=add_extra,
        after_parse=after_parse,
    )


if __name__ == "__main__":
    raise SystemExit(main())
