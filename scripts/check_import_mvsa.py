"""Importcontrole: bestaande ``{stam}.mscz.mvsa`` vs basispartituur-``.mscz``.

Controleert **alleen bestaande** import-siblings (niet elke ``.mscz``
hoeft een ``.mscz.mvsa`` te hebben — bewerkvorm, geen site-product).

Schrijft ``data/import-mvsa-status.json``. Exit 1 bij problemen tenzij
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
    read_mvsa_stamp,
    stamp_sha_from_dict,
)
from sync_import_mvsa import collect_import_mvsa, mscz_for_import_mvsa
from sync_mscz_products import DEFAULT_ROOT

REPO_ROOT = Path(__file__).resolve().parents[1]
STATUS_PATH = REPO_ROOT / "data" / "import-mvsa-status.json"
FIX_PAGE = "/handleiding/scripts/import-mvsa/"


@dataclass
class Issue:
    kind: str  # missing_mscz | stale_mvsa | unstamped_mvsa
    file: str
    detail: str


@dataclass
class PairStatus:
    dir: str
    mscz: str
    mvsa: str
    ok: bool
    issues: list[Issue]
    fix_cmd: str


def _rel(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _bladermap_key(path: Path) -> str:
    try:
        rel = path.parent.relative_to(REPO_ROOT / "content-source")
        return rel.as_posix()
    except ValueError:
        return _rel(path.parent)


def check_one(mvsa: Path) -> PairStatus:
    issues: list[Issue] = []
    fix = r"scripts\import-mvsa.cmd"
    mscz = mscz_for_import_mvsa(mvsa)

    if not mscz.is_file():
        issues.append(
            Issue(
                "missing_mscz",
                _rel(mscz),
                "basispartituur-.mscz ontbreekt naast de import-.mscz.mvsa",
            )
        )
        return PairStatus(
            dir=_bladermap_key(mvsa),
            mscz=_rel(mscz),
            mvsa=_rel(mvsa),
            ok=False,
            issues=issues,
            fix_cmd=fix,
        )

    digest = partituur_sha256(mscz)
    stamp = read_mvsa_stamp(mvsa)
    got = stamp_sha_from_dict(stamp)
    if not got:
        issues.append(
            Issue(
                "unstamped_mvsa",
                _rel(mvsa),
                "import-.mvsa mist vsa-partituur-sha256 (opnieuw import-mvsa)",
            )
        )
    elif got != digest:
        when = stamp.get(FIELD_GENERATED_AT, "?")
        issues.append(
            Issue(
                "stale_mvsa",
                _rel(mvsa),
                f"import-.mvsa-partituur-hash wijkt af (gegenereerd {when}); "
                f"basispartituur is gewijzigd",
            )
        )

    return PairStatus(
        dir=_bladermap_key(mvsa),
        mscz=_rel(mscz),
        mvsa=_rel(mvsa),
        ok=not issues,
        issues=issues,
        fix_cmd=fix,
    )


def collect_statuses(root: Path) -> list[PairStatus]:
    return [check_one(mvsa) for mvsa in collect_import_mvsa(root)]


def write_status_json(statuses: list[PairStatus], path: Path = STATUS_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "fix_page": FIX_PAGE,
        "pairs": {
            s.mvsa: {
                "dir": s.dir,
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
        f"Import-.mvsa: {len(statuses) - len(bad)} ok, {len(bad)} probleem "
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
