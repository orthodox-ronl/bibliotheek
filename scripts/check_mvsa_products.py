"""Controleer bibliotheek-``.mvsa`` vs MXL/SVG/Score-IR/from-ir.

Product-``.mvsa.pdf`` niet meer verplicht. Slaat import-siblings
``*.mscz.mvsa`` over. Schrijft ``data/mvsa-product-status.json``.
De JSON-sleutel is het bronpad (niet de bladermap): twee ``.mvsa``
in dezelfde leaf overschrijven elkaar anders, en ``check-fixlist``
ziet het falende bestand dan niet.
Exit 1 bij problemen tenzij ``--warn-only``.
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
    read_score_ir_stamp,
    read_svg_stamp,
    source_sha256,
)
from street_meta import issues_from_meta_or
from fix_cmds import products_fix_cmd
from sync_mvsa_products import (
    DEFAULT_ROOT,
    _MVSA_META_KEYS,
    _stamp_ok_from_ir,
    collect_mvsa,
    product_from_ir_musicxml_for_mvsa,
    product_mxl_for_mvsa,
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
    from input_paths import rel_for_log

    return rel_for_log(path, repo_root=REPO_ROOT)


def _bladermap_key(path: Path) -> str:
    from input_paths import rel_for_log

    return rel_for_log(path.parent, repo_root=REPO_ROOT)


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
                f"{label} mist vsa-source-sha256 (opnieuw products --kinds mvsa)",
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


def _stamp_issues(mvsa: Path, digest: str) -> list[Issue]:
    issues: list[Issue] = []
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
    return issues


def _append_sectie_issues(
    issues: list[Issue],
    mvsa: Path,
    digest: str,
    refs: dict[str, set[str]],
) -> None:
    """Sectie-producten alleen als ergens ``bieb id=\"…@sectie\"`` staat."""
    from catalogus_sectie import (
        product_from_ir_for_sectie,
        product_svg_for_sectie,
    )
    from ensure_bibliotheek_id import id_from_catalogus_path

    bib = id_from_catalogus_path(mvsa)
    if not bib:
        return
    for sectie in sorted(refs.get(bib, ())):
        _check_stamped_product(
            issues,
            path=product_svg_for_sectie(mvsa, sectie),
            digest=digest,
            missing_kind="missing_sectie_svg",
            missing_detail=(
                f"Sectie-SVG (.mvsa@{sectie}.svg) ontbreekt "
                f"(gerefereerd in bieb-id)"
            ),
            unstamped_kind="unstamped_sectie_svg",
            stale_kind="stale_sectie_svg",
            label=f"SVG @{sectie}",
            read_stamp=read_svg_stamp,
        )
        _check_stamped_product(
            issues,
            path=product_from_ir_for_sectie(mvsa, sectie),
            digest=digest,
            missing_kind="missing_sectie_from_ir",
            missing_detail=(
                f"Sectie from-ir (.mvsa@{sectie}.from-ir.musicxml) "
                f"ontbreekt (gerefereerd in bieb-id)"
            ),
            unstamped_kind="unstamped_sectie_from_ir",
            stale_kind="stale_sectie_from_ir",
            label=f"from-ir @{sectie}",
            read_stamp=read_from_ir_musicxml_stamp,
        )


def check_one(
    mvsa: Path, *, sectie_refs: dict[str, set[str]] | None = None
) -> FolderStatus:
    digest = source_sha256(mvsa)
    fix = products_fix_cmd("mvsa", mvsa)
    refs = sectie_refs if sectie_refs is not None else {}

    # Sectie-SVG/from-ir staan niet in products-meta-keys; altijd apart
    # controleren — ook als meta voor mxl/score-ir/from-ir «ok» is.
    issues = issues_from_meta_or(
        mvsa,
        required_keys=set(_MVSA_META_KEYS),
        rel=_rel,
        stamp_issues=lambda: _stamp_issues(mvsa, digest),
        issue_cls=Issue,
    )
    _append_sectie_issues(issues, mvsa, digest, refs)
    return FolderStatus(
        dir=_bladermap_key(mvsa),
        source=_rel(mvsa),
        ok=not issues,
        issues=issues,
        fix_cmd=fix,
    )


def collect_statuses(root: Path) -> list[FolderStatus]:
    from catalogus_sectie import collect_sectie_refs

    refs = collect_sectie_refs(REPO_ROOT / "content-source")
    return [check_one(mvsa, sectie_refs=refs) for mvsa in collect_mvsa(root)]


def write_status_json(statuses: list[FolderStatus], path: Path = STATUS_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "fix_page": FIX_PAGE,
        "folders": {
            # Sleutel = bronpad. Map-pad als sleutel liet een tweede .mvsa
            # in dezelfde leaf de falende status overschrijven (fixlist leeg).
            (s.source or s.dir): {
                "source": s.source,
                "dir": s.dir,
                "ok": s.ok,
                "fix_cmd": s.fix_cmd,
                "issues": [asdict(i) for i in s.issues],
            }
            for s in statuses
        },
    }
    from cli_style import atomic_write_json

    atomic_write_json(path, payload, ensure_ascii=False)


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
    from check_report import print_check_findings

    print_check_findings(
        headline=(
            f"MVSA-producten: {len(statuses) - len(bad)} ok, {len(bad)} probleem "
            f"({_rel(STATUS_PATH)})"
        ),
        what="Controle: of .mvsa-afgeleiden (mxl/svg/…) bij de bron passen",
        bad=bad,
        fix_page=FIX_PAGE,
    )

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
