"""Zet of controleer bibliotheek-id in basispartituur-``.mscz``-colofon.

Verwacht id = pad ``zangstuk/variant/uitvoeringsvorm`` onder
``content-source\\catalogus``. Schrijven gebeurt via tooling-layoutprofiel
``partituur`` (zelfde als ``layout.cmd``). CI / ``--check-only`` schrijft niet.
Colofonregel blijft ``Bibliotheek-id:`` (VSA-tooling-contract).
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import zipfile
from pathlib import Path

from sync_mscz_products import collect_mscz, is_print_mscz
from sync_vsa_products import folder_is_handmatig

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOT = REPO_ROOT / "content-source" / "catalogus"
_BIB_ID_LABEL = "Bibliotheek-id:"
_ID_PART = re.compile(r"^[a-z0-9_-]+$")
FIX_PAGE = "/handleiding/partituur/3-standaard-mscz/"


def _running_in_ci() -> bool:
    return os.environ.get("CI", "").strip().lower() in {"1", "true", "yes"}


def _rel(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def id_from_catalogus_path(path: Path) -> str | None:
    """``content-source/catalogus/<zangstuk>/<variant>/<uitvoeringsvorm>/…``.

    De repo-root heet ook ``bibliotheek``; pad-sniffing in tooling grijpt die
    eerst. Hier zoeken we daarom expliciet onder ``content-source/catalogus``.
    """
    parts = Path(path).resolve().parts
    for i, part in enumerate(parts):
        if part != "catalogus":
            continue
        if i == 0 or parts[i - 1] != "content-source":
            continue
        if i + 3 >= len(parts):
            return None
        segs = parts[i + 1 : i + 4]
        if all(_ID_PART.fullmatch(s) for s in segs):
            return "/".join(segs)
        return None
    return None


def _read_mscx(path: Path) -> str:
    with zipfile.ZipFile(path, "r") as zin:
        name = next((n for n in zin.namelist() if n.lower().endswith(".mscx")), None)
        if name is None:
            raise KeyError(f"geen .mscx in {path}")
        return zin.read(name).decode("utf-8")


def bibliotheek_id_status(path: Path, expected: str) -> tuple[bool, str]:
    """Of het colofon de regel ``Bibliotheek-id: <expected>`` heeft."""
    expected = (expected or "").strip()
    if not expected:
        return False, "geen verwacht bibliotheek-id"
    try:
        mscx = _read_mscx(path)
    except (OSError, zipfile.BadZipFile, FileNotFoundError, KeyError) as exc:
        return False, f"kan .mscz niet lezen: {exc}"
    loose = re.compile(
        rf"{re.escape(_BIB_ID_LABEL)}\s*{re.escape(expected)}",
        re.I,
    )
    if loose.search(mscx):
        return True, "ok"
    return False, "colofon mist Bibliotheek-id-regel"


def collect_basispartituren(root: Path) -> list[tuple[Path, str]]:
    """(``.mscz``, expected id) onder de bibliotheekboom."""
    out: list[tuple[Path, str]] = []
    for mscz in collect_mscz(root):
        if is_print_mscz(mscz):
            continue
        if folder_is_handmatig(mscz.parent):
            continue
        ident = id_from_catalogus_path(mscz)
        if not ident:
            continue
        out.append((mscz, ident))
    out.sort(key=lambda item: item[1])
    return out


def _strict_exit() -> bool:
    ref = (
        os.environ.get("GITHUB_REF", "")
        or os.environ.get("GITHUB_REF_NAME", "")
        or ""
    )
    if ref in {"main", "refs/heads/main"}:
        return True
    if os.environ.get("BIBLIOTHEEK_ID_STRICT", "").strip().lower() in {
        "1",
        "true",
        "yes",
    }:
        return True
    if os.environ.get("PIPELINE_STRICT", "").strip():
        return True
    return False


def _fix(mscz: Path, expected: str) -> None:
    from vsa.mscz_layout import MsczPartituurError, apply_mscz_layout_profile

    try:
        apply_mscz_layout_profile(
            mscz,
            layout="partituur",
            bibliotheek_id=expected,
        )
    except MsczPartituurError as exc:
        raise SystemExit(f"{mscz}: ERROR: {exc}") from exc


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "root",
        nargs="?",
        type=Path,
        default=DEFAULT_ROOT,
        help="Zoekroot (default: content-source/catalogus)",
    )
    p.add_argument(
        "--check-only",
        action="store_true",
        help="Niet herschrijven; alleen controleren",
    )
    p.add_argument(
        "--fail",
        action="store_true",
        help="Exit 1 bij problemen (naast main/strict)",
    )
    p.add_argument(
        "--warn-only",
        action="store_true",
        help="Altijd exit 0",
    )
    args = p.parse_args(argv)
    root = args.root if args.root.is_absolute() else REPO_ROOT / args.root
    items = collect_basispartituren(root)
    write = not args.check_only and not _running_in_ci()

    fixed = 0
    bad: list[tuple[Path, str, str]] = []
    for mscz, expected in items:
        ok, detail = bibliotheek_id_status(mscz, expected)
        if ok:
            continue
        if write:
            print(f"fix {_rel(mscz)} -> {expected}", flush=True)
            _fix(mscz, expected)
            ok2, detail2 = bibliotheek_id_status(mscz, expected)
            if ok2:
                fixed += 1
                continue
            bad.append((mscz, expected, detail2))
        else:
            bad.append((mscz, expected, detail))

    print(
        f"Bibliotheek-id: {len(items) - len(bad)} ok, {fixed} hersteld, "
        f"{len(bad)} probleem",
        flush=True,
    )
    for mscz, expected, detail in bad:
        print(f"  [{expected}] {_rel(mscz)}: {detail}", flush=True)
        print(
            f"    Fix: scripts\\layout.cmd \"{_rel(mscz)}\" --id {expected}",
            flush=True,
        )
        print(f"    Zie: {FIX_PAGE}", flush=True)

    if not bad or args.warn_only:
        return 0
    if args.fail or _strict_exit():
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
