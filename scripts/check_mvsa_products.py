"""Controleer bibliotheek-``.mvsa`` vs sibling ``.mvsa.mxl`` / ``.mvsa.pdf``.

Slaat import-siblings ``*.mscz.mvsa`` over. Schrijft
``data/mvsa-product-status.json``. Exit 1 bij problemen tenzij ``--warn-only``.
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
    FIELD_SOURCE_KIND,
    FIELD_SOURCE_SHA,
    SOURCE_KIND_MVSA,
    read_mxl_stamp,
    read_pdf_stamp,
    source_sha256,
)
from sync_mvsa_products import (
    DEFAULT_ROOT,
    collect_mvsa,
    product_mxl_for_mvsa,
    product_pdf_for_mvsa,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
STATUS_PATH = REPO_ROOT / "data" / "mvsa-product-status.json"
FIX_PAGE = "/handleiding/scripts/mvsa-products/"


@dataclass
class Issue:
    kind: str
    file: str
    detail: str


@dataclass
class FolderStatus:
    dir: str
    source: str
    ok: bool
    issues: list[Issue]
    fix_cmd: str


def _rel(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _bladermap_key(path: Path) -> str:
    rel = path.parent.relative_to(REPO_ROOT / "content-source")
    return rel.as_posix()


def check_one(mvsa: Path) -> FolderStatus:
    issues: list[Issue] = []
    digest = source_sha256(mvsa)
    fix = r"scripts\mvsa-products.cmd"

    mxl = product_mxl_for_mvsa(mvsa)
    if not mxl.is_file():
        issues.append(
            Issue(
                "missing_mxl",
                _rel(mxl),
                "Coria-.mvsa.mxl ontbreekt naast de .mvsa",
            )
        )
    else:
        stamp = read_mxl_stamp(mxl)
        kind = stamp.get(FIELD_SOURCE_KIND, "")
        got = stamp.get(FIELD_SOURCE_SHA, "")
        if not got:
            issues.append(
                Issue(
                    "unstamped_mxl",
                    _rel(mxl),
                    "MXL mist vsa-source-sha256 (opnieuw mvsa-products)",
                )
            )
        elif kind and kind != SOURCE_KIND_MVSA:
            issues.append(
                Issue(
                    "wrong_kind",
                    _rel(mxl),
                    f"MXL source-kind is {kind!r}, verwacht {SOURCE_KIND_MVSA!r}",
                )
            )
        elif got != digest:
            when = stamp.get(FIELD_GENERATED_AT, "?")
            issues.append(
                Issue(
                    "stale_mxl",
                    _rel(mxl),
                    f"MXL-source-hash wijkt af (gegenereerd {when}); .mvsa is gewijzigd",
                )
            )

    pdf = product_pdf_for_mvsa(mvsa)
    if not pdf.is_file():
        issues.append(
            Issue(
                "missing_pdf",
                _rel(pdf),
                "PDF ontbreekt naast de .mvsa",
            )
        )
    else:
        stamp = read_pdf_stamp(pdf)
        kind = stamp.get(FIELD_SOURCE_KIND, "")
        got = stamp.get(FIELD_SOURCE_SHA, "")
        if not got:
            issues.append(
                Issue(
                    "unstamped_pdf",
                    _rel(pdf),
                    "PDF mist vsa-source-sha256 (opnieuw mvsa-products)",
                )
            )
        elif kind and kind != SOURCE_KIND_MVSA:
            issues.append(
                Issue(
                    "wrong_kind",
                    _rel(pdf),
                    f"PDF source-kind is {kind!r}, verwacht {SOURCE_KIND_MVSA!r}",
                )
            )
        elif got != digest:
            when = stamp.get(FIELD_GENERATED_AT, "?")
            issues.append(
                Issue(
                    "stale_pdf",
                    _rel(pdf),
                    f"PDF-source-hash wijkt af (gegenereerd {when}); .mvsa is gewijzigd",
                )
            )

    return FolderStatus(
        dir=_bladermap_key(mvsa),
        source=_rel(mvsa),
        ok=not issues,
        issues=issues,
        fix_cmd=fix,
    )


def collect_statuses(root: Path) -> list[FolderStatus]:
    return [check_one(mvsa) for mvsa in collect_mvsa(root)]


def write_status_json(statuses: list[FolderStatus], path: Path = STATUS_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "fix_page": FIX_PAGE,
        "folders": {
            s.dir: {
                "source": s.source,
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
        f"MVSA-producten: {len(statuses) - len(bad)} ok, {len(bad)} probleem "
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
