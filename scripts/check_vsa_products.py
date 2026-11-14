"""Controleer ``.vsa`` vs siblings ``.vsa.svg`` (+ optioneel ``.vsa.mvsa``).

Geen verplichte Coria-``.vsa.mxl`` meer: playback-MXL hoort bij de
afgeleide ``.vsa.mvsa`` (dan ``check_mvsa_products`` / Coria-contract).
Templatekeuze T1: geen default → geen eis op ``.vsa.mvsa``; ongeldige
``formule:`` of andere harde T1-fout → issue. Product-``.vsa.pdf`` niet
verplicht. Schrijft ``data/vsa-product-status.json``. Slaat
``manueel/manual`` over. Exit 1 bij problemen tenzij ``--warn-only``.
"""

from __future__ import annotations

import argparse
import os
from dataclasses import asdict, dataclass
from pathlib import Path

from product_meta import (
    FIELD_GENERATED_AT,
    FIELD_SOURCE_KIND,
    FIELD_SOURCE_SHA,
    SOURCE_KIND_VSA,
    read_svg_stamp,
    source_sha256,
)
from fix_cmds import products_fix_cmd
from street_meta import issues_from_meta_or
from sync_vsa_products import (
    DEFAULT_ROOT,
    classify_vsa_mvsa_template,
    collect_vsa,
    product_mvsa_for_vsa,
    product_svg_for_vsa,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
STATUS_PATH = REPO_ROOT / "data" / "vsa-product-status.json"
FIX_PAGE = "/handleiding/vsa/1-vsa-schrijven/"


@dataclass
class Issue:
    kind: str  # missing_svg | stale_svg | missing_mvsa | template_error | ...
    file: str
    detail: str


@dataclass
class FolderStatus:
    dir: str
    vsa: str
    ok: bool
    issues: list[Issue]
    fix_cmd: str


def _rel(path: Path) -> str:
    from input_paths import rel_for_log

    return rel_for_log(path, repo_root=REPO_ROOT)


def _bladermap_key(vsa: Path) -> str:
    from input_paths import rel_for_log

    return rel_for_log(vsa.parent, repo_root=REPO_ROOT)


def _stamp_issues_svg(vsa: Path, src_hash: str) -> list[Issue]:
    issues: list[Issue] = []
    svg = product_svg_for_vsa(vsa)
    if not svg.is_file():
        issues.append(
            Issue(
                "missing_svg",
                _rel(svg),
                "Muziek-.vsa.svg ontbreekt naast de bibliotheek-.vsa (scherm)",
            )
        )
        return issues
    stamp = read_svg_stamp(svg)
    kind = stamp.get(FIELD_SOURCE_KIND, "")
    got = stamp.get(FIELD_SOURCE_SHA, "")
    if not got:
        issues.append(
            Issue(
                "unstamped_svg",
                _rel(svg),
                "SVG mist vsa-source-sha256 (opnieuw products --kinds vsa)",
            )
        )
    elif kind and kind != SOURCE_KIND_VSA:
        issues.append(
            Issue(
                "wrong_kind_svg",
                _rel(svg),
                f"SVG source-kind is {kind!r}, verwacht {SOURCE_KIND_VSA!r}",
            )
        )
    elif got != src_hash:
        when = stamp.get(FIELD_GENERATED_AT, "?")
        issues.append(
            Issue(
                "stale_svg",
                _rel(svg),
                f"SVG-source-hash wijkt af (gegenereerd {when}); .vsa is gewijzigd",
            )
        )
    return issues


def _stamp_issues_mvsa(vsa: Path) -> list[Issue]:
    mvsa = product_mvsa_for_vsa(vsa)
    if mvsa.is_file():
        return []
    return [
        Issue(
            "missing_mvsa",
            _rel(mvsa),
            "Schets-.vsa.mvsa ontbreekt naast de bibliotheek-.vsa "
            "(products --kinds vsa; T1)",
        )
    ]


def _template_decision(
    vsa: Path,
) -> tuple[str, list[Issue]]:
    """``ok`` | ``soft_skip`` | ``hard`` + eventuele template-issues."""
    try:
        decision, _tpl = classify_vsa_mvsa_template(vsa)
    except Exception as exc:  # noqa: BLE001 — T1 harde fout als check-issue
        return "hard", [
            Issue(
                "template_error",
                _rel(vsa),
                f"Geen geldige formule-template (T1): {exc}",
            )
        ]
    return decision, []


def check_one(vsa: Path) -> FolderStatus:
    src_hash = source_sha256(vsa)
    fix = products_fix_cmd("vsa", vsa)
    decision, template_issues = _template_decision(vsa)
    # soft_skip: alleen svg. hard (T1-fout): svg + template-issue, geen
    # aparte missing_mvsa. ok: svg + .vsa.mvsa.
    required: set[str] = {"svg"}
    if decision == "ok":
        required.add("mvsa")

    def _stamps() -> list[Issue]:
        out = _stamp_issues_svg(vsa, src_hash)
        if "mvsa" in required:
            out.extend(_stamp_issues_mvsa(vsa))
        return out

    issues = list(template_issues)
    issues.extend(
        issues_from_meta_or(
            vsa,
            required_keys=required,
            rel=_rel,
            stamp_issues=_stamps,
            issue_cls=Issue,
        )
    )
    return FolderStatus(
        dir=_bladermap_key(vsa),
        vsa=_rel(vsa),
        ok=not issues,
        issues=issues,
        fix_cmd=fix,
    )


def collect_statuses(root: Path) -> list[FolderStatus]:
    by_dir: dict[str, FolderStatus] = {}
    for vsa in collect_vsa(root):
        status = check_one(vsa)
        prev = by_dir.get(status.dir)
        if prev is None:
            by_dir[status.dir] = status
            continue
        merged_issues = list(prev.issues) + list(status.issues)
        by_dir[status.dir] = FolderStatus(
            dir=status.dir,
            vsa=prev.vsa + "; " + status.vsa,
            ok=not merged_issues,
            issues=merged_issues,
            fix_cmd=status.fix_cmd,
        )
    return sorted(by_dir.values(), key=lambda s: s.dir)


def write_status_json(statuses: list[FolderStatus], path: Path = STATUS_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "fix_page": FIX_PAGE,
        "folders": {
            s.dir: {
                "vsa": s.vsa,
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
            f"VSA-producten: {len(statuses) - len(bad)} ok, {len(bad)} probleem "
            f"({_rel(STATUS_PATH)})"
        ),
        what="Controle: of .vsa-afgeleiden (svg / .vsa.mvsa) bij de bron passen",
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
    # CI (Pages) en lokale check --strict zetten --fail; default lokaal: warn.
    if os.environ.get("GITHUB_ACTIONS", "").strip().lower() == "true":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
