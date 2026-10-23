"""Controleer bibliotheek-``.mvsa`` vs MXL/PDF/SVG/Score-IR/from-ir.

Slaat import-siblings ``*.mscz.mvsa`` over. Schrijft
``data/mvsa-product-status.json``. Exit 1 bij problemen tenzij ``--warn-only``.
"""

from __future__ import annotations

import argparse
import json
import os
from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path

from product_meta import (
    FIELD_GENERATED_AT,
    FIELD_SOURCE_KIND,
    FIELD_SOURCE_SHA,
    SOURCE_KIND_MVSA,
    read_from_ir_musicxml_stamp,
    read_mxl_stamp,
    read_pdf_stamp,
    read_score_ir_stamp,
    read_svg_stamp,
    source_sha256,
)
from sync_mvsa_products import (
    DEFAULT_ROOT,
    _stamp_ok_from_ir,
    collect_mvsa,
    product_from_ir_musicxml_for_mvsa,
    product_mxl_for_mvsa,
    product_pdf_for_mvsa,
    product_score_ir_for_mvsa,
    product_svg_for_mvsa,
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


def _check_stamped_product(
    issues: list[Issue],
    *,
    path: Path,
    digest: str,
    missing_kind: str,
    missing_detail: str,
    unstamped_kind: str,
    stale_kind: str,
    label: str,
    read_stamp: Callable[[Path], dict[str, str]],
) -> None:
    if not path.is_file():
        issues.append(Issue(missing_kind, _rel(path), missing_detail))
        return
    stamp = read_stamp(path)
    kind = stamp.get(FIELD_SOURCE_KIND, "")
    got = stamp.get(FIELD_SOURCE_SHA, "")
    if not got:
        issues.append(
            Issue(
                unstamped_kind,
                _rel(path),
                f"{label} mist vsa-source-sha256 (opnieuw mvsa-products)",
            )
        )
    elif kind and kind != SOURCE_KIND_MVSA:
        issues.append(
            Issue(
                "wrong_kind",
                _rel(path),
                f"{label} source-kind is {kind!r}, verwacht {SOURCE_KIND_MVSA!r}",
            )
        )
    elif got != digest:
        when = stamp.get(FIELD_GENERATED_AT, "?")
        issues.append(
            Issue(
                stale_kind,
                _rel(path),
                f"{label}-source-hash wijkt af (gegenereerd {when}); .mvsa is gewijzigd",
            )
        )


def check_one(mvsa: Path) -> FolderStatus:
    issues: list[Issue] = []
    digest = source_sha256(mvsa)
    fix = r"scripts\mvsa-products.cmd"

    _check_stamped_product(
        issues,
        path=product_mxl_for_mvsa(mvsa),
        digest=digest,
        missing_kind="missing_mxl",
        missing_detail="Coria-.mvsa.mxl ontbreekt naast de .mvsa",
        unstamped_kind="unstamped_mxl",
        stale_kind="stale_mxl",
        label="MXL",
        read_stamp=read_mxl_stamp,
    )
    _check_stamped_product(
        issues,
        path=product_pdf_for_mvsa(mvsa),
        digest=digest,
        missing_kind="missing_pdf",
        missing_detail="PDF ontbreekt naast de .mvsa",
        unstamped_kind="unstamped_pdf",
        stale_kind="stale_pdf",
        label="PDF",
        read_stamp=read_pdf_stamp,
    )
    _check_stamped_product(
        issues,
        path=product_score_ir_for_mvsa(mvsa),
        digest=digest,
        missing_kind="missing_score_ir",
        missing_detail="Score-IR (.mvsa.score-ir.json) ontbreekt naast de .mvsa",
        unstamped_kind="unstamped_score_ir",
        stale_kind="stale_score_ir",
        label="Score-IR",
        read_stamp=read_score_ir_stamp,
    )
    from_ir = product_from_ir_musicxml_for_mvsa(mvsa)
    _check_stamped_product(
        issues,
        path=from_ir,
        digest=digest,
        missing_kind="missing_from_ir",
        missing_detail="OSMD-MusicXML (.mvsa.from-ir.musicxml) ontbreekt naast de .mvsa",
        unstamped_kind="unstamped_from_ir",
        stale_kind="stale_from_ir",
        label="from-ir MusicXML",
        read_stamp=read_from_ir_musicxml_stamp,
    )
    # Scherm: OSMD via from-ir. .mvsa.svg is fallback — niet verplicht als
    # from-ir met geldige herkomststempel aanwezig is (o.a. multipagina-stukken).
    svg = product_svg_for_mvsa(mvsa)
    if _stamp_ok_from_ir(from_ir, digest):
        if svg.is_file():
            _check_stamped_product(
                issues,
                path=svg,
                digest=digest,
                missing_kind="missing_svg",
                missing_detail="Koormap-SVG ontbreekt naast de .mvsa",
                unstamped_kind="unstamped_svg",
                stale_kind="stale_svg",
                label="SVG",
                read_stamp=read_svg_stamp,
            )
    else:
        _check_stamped_product(
            issues,
            path=svg,
            digest=digest,
            missing_kind="missing_svg",
            missing_detail=(
                "Koormap-SVG ontbreekt naast de .mvsa "
                "(en geen bruikbare .from-ir.musicxml voor OSMD)"
            ),
            unstamped_kind="unstamped_svg",
            stale_kind="stale_svg",
            label="SVG",
            read_stamp=read_svg_stamp,
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
        help="Zoekroot (default: content-source/catalogus)",
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
