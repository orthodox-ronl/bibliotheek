"""Controleer basispartituur-``.mscz`` vs sibling PDF/MXL (partituur-sha256).

Doelvorm: ``{stam}.mscz.pdf`` / ``{stam}.mscz.mxl``. Legacy ``{stam}.pdf`` /
``{stam}.mxl`` (en ``.partituur.*``) nog toegestaan tot migratie.

Schrijft ``data/mscz-product-status.json``. Exit 1 bij problemen tenzij
``--warn-only``.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from product_meta import (
    FIELD_GENERATED_AT,
    partituur_sha256,
    read_mxl_stamp,
    read_pdf_stamp,
    stamp_sha_from_dict,
)
from sync_mscz_products import (
    DEFAULT_ROOT,
    collect_mscz,
    legacy_mxl_for_mscz,
    legacy_pdf_for_mscz,
    product_mxl_for_mscz,
    product_pdf_for_mscz,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
STATUS_PATH = REPO_ROOT / "data" / "mscz-product-status.json"
FIX_PAGE = "/handleiding/partituur/5-pdf-en-coria/"


@dataclass
class Issue:
    kind: str
    file: str
    detail: str


@dataclass
class FolderStatus:
    dir: str
    mscz: str
    ok: bool
    issues: list[Issue]
    fix_cmd: str


def _rel(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _bladermap_key(mscz: Path) -> str:
    rel = mscz.parent.relative_to(REPO_ROOT / "content-source")
    return rel.as_posix()


def _resolve_product(canonical: Path, *legacy: Path) -> Path | None:
    if canonical.is_file():
        return canonical
    for path in legacy:
        if path.is_file():
            return path
    return None


def check_one(mscz: Path) -> FolderStatus:
    issues: list[Issue] = []
    digest = partituur_sha256(mscz)
    fix = r"scripts\mscz-products.cmd"

    pdf_canon = product_pdf_for_mscz(mscz)
    pdf = _resolve_product(
        pdf_canon,
        legacy_pdf_for_mscz(mscz),
        mscz.with_suffix(".partituur.pdf"),
    )
    if pdf is None:
        issues.append(
            Issue(
                "missing_pdf",
                _rel(pdf_canon),
                "PDF ontbreekt naast de basispartituur-.mscz",
            )
        )
    else:
        stamp = read_pdf_stamp(pdf)
        got = stamp_sha_from_dict(stamp)
        if not got:
            issues.append(
                Issue(
                    "unstamped_pdf",
                    _rel(pdf),
                    "PDF heeft geen VSAPartituurSHA256-metadata (opnieuw genereren)",
                )
            )
        elif got != digest:
            when = stamp.get(FIELD_GENERATED_AT, "?")
            issues.append(
                Issue(
                    "stale_pdf",
                    _rel(pdf),
                    f"PDF-partituur-hash wijkt af (gegenereerd {when}); "
                    f"basispartituur is gewijzigd",
                )
            )

    mxl_canon = product_mxl_for_mscz(mscz)
    mxl = _resolve_product(
        mxl_canon,
        legacy_mxl_for_mscz(mscz),
        mscz.with_suffix(".partituur.mxl"),
    )
    if mxl is None:
        issues.append(
            Issue(
                "missing_mxl",
                _rel(mxl_canon),
                "Coria-.mxl ontbreekt naast de basispartituur-.mscz",
            )
        )
    else:
        stamp = read_mxl_stamp(mxl)
        got = stamp_sha_from_dict(stamp)
        if not got:
            issues.append(
                Issue(
                    "unstamped_mxl",
                    _rel(mxl),
                    "MXL heeft geen vsa-partituur-sha256 (opnieuw genereren)",
                )
            )
        elif got != digest:
            when = stamp.get(FIELD_GENERATED_AT, "?")
            issues.append(
                Issue(
                    "stale_mxl",
                    _rel(mxl),
                    f"MXL-partituur-hash wijkt af (gegenereerd {when}); "
                    f"basispartituur is gewijzigd",
                )
            )

    return FolderStatus(
        dir=_bladermap_key(mscz),
        mscz=_rel(mscz),
        ok=not issues,
        issues=issues,
        fix_cmd=fix,
    )


def collect_statuses(root: Path) -> list[FolderStatus]:
    by_dir: dict[str, FolderStatus] = {}
    for mscz in collect_mscz(root):
        status = check_one(mscz)
        prev = by_dir.get(status.dir)
        if prev is None:
            by_dir[status.dir] = status
            continue
        merged = list(prev.issues) + list(status.issues)
        by_dir[status.dir] = FolderStatus(
            dir=status.dir,
            mscz=prev.mscz + "; " + status.mscz,
            ok=not merged,
            issues=merged,
            fix_cmd=status.fix_cmd,
        )
    return sorted(by_dir.values(), key=lambda s: s.dir)


def write_status_json(statuses: list[FolderStatus], path: Path = STATUS_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "fix_page": FIX_PAGE,
        "folders": {
            s.dir: {
                "mscz": s.mscz,
                "ok": s.ok,
                "fix_cmd": s.fix_cmd,
                "issues": [asdict(i) for i in s.issues],
            }
            for s in statuses
        },
    }
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "root",
        nargs="?",
        type=Path,
        default=DEFAULT_ROOT,
        help="Zoekroot (default: content-source/bibliotheek)",
    )
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="Schrijf status-JSON maar exit altijd 0",
    )
    parser.add_argument(
        "--fail",
        action="store_true",
        help="Non-zero bij problemen (CI / --strict)",
    )
    args = parser.parse_args()
    root = args.root if args.root.is_absolute() else REPO_ROOT / args.root
    statuses = collect_statuses(root)
    write_status_json(statuses)
    bad = [s for s in statuses if not s.ok]
    print(
        f"MSCZ-producten: {len(statuses) - len(bad)} ok, {len(bad)} probleem "
        f"({STATUS_PATH.relative_to(REPO_ROOT).as_posix()})",
        flush=True,
    )
    for s in bad:
        print(f"  {s.dir}:", flush=True)
        for issue in s.issues:
            print(f"    - [{issue.kind}] {issue.file}: {issue.detail}", flush=True)
        print(f"    Fix: {s.fix_cmd}", flush=True)
        print(f"    Zie: {FIX_PAGE}", flush=True)

    if not bad:
        return 0
    if args.warn_only:
        return 0
    if args.fail:
        return 1
    ref = (
        os.environ.get("GITHUB_REF", "")
        or os.environ.get("GITHUB_REF_NAME", "")
        or ""
    )
    if ref in {"main", "refs/heads/main"}:
        return 1
    if os.environ.get("BIBLIOTHEEK_PRODUCTS_STRICT", "").strip().lower() in {
        "1",
        "true",
        "yes",
    }:
        return 1
    if os.environ.get("GITHUB_ACTIONS", "").strip().lower() == "true":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
