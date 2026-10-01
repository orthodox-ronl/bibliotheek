"""Controleer Coria-``.mxl``-siblings tegen de playback-checklist.

Roept ``mxl validate`` aan (VSA-tooling):

- ``*.vsa.mxl`` → ``--profile mono``
- ``*.mscz.mxl`` / ``*.mvsa.mxl`` → ``--profile satb``

Slaat ``input/`` en ``artefacten_handmatig`` over. Meet alleen bestanden die
er al zijn (ontbrekend = versheidscontrole). Schrijft
``data/mxl-playback-contract-status.json``. Exit 1 bij problemen tenzij
``--warn-only``.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from product_regen import mxl_contract_ok
from sync_vsa_products import folder_is_handmatig

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOT = REPO_ROOT / "content-source" / "catalogus"
STATUS_PATH = REPO_ROOT / "data" / "mxl-playback-contract-status.json"
FIX_PAGE = "/handleiding/start/publicatiecontrole/"
FIX_CMD = r"scripts\products.cmd --kinds mscz,mvsa,vsa --only-invalid"


@dataclass
class Issue:
    kind: str
    file: str
    detail: str


@dataclass
class FileStatus:
    file: str
    profile: str
    ok: bool
    issues: list[Issue]
    fix_cmd: str


def _rel(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def profile_for_coria_mxl(path: Path) -> str | None:
    """Return validate-profile, or None if this is not a known Coria-product."""
    name = path.name.lower()
    if name.endswith(".vsa.mxl"):
        return "mono"
    if name.endswith(".mscz.mxl") or name.endswith(".mvsa.mxl"):
        return "satb"
    return None


def collect_coria_mxl(root: Path) -> list[tuple[Path, str]]:
    out: list[tuple[Path, str]] = []
    if not root.is_dir():
        return out
    for path in sorted(root.rglob("*.mxl")):
        if "input" in path.parts:
            continue
        if folder_is_handmatig(path.parent):
            continue
        profile = profile_for_coria_mxl(path)
        if profile is None:
            continue
        out.append((path, profile))
    return out


def check_one(path: Path, profile: str) -> FileStatus:
    issues: list[Issue] = []
    result = mxl_contract_ok(path, profile=profile)
    if result is None:
        issues.append(
            Issue(
                "mxl_cli_missing",
                _rel(path),
                "mxl validate niet beschikbaar (installeer vsa-tool / pin bumpen)",
            )
        )
    elif result is False:
        issues.append(
            Issue(
                "invalid_mxl",
                _rel(path),
                f"faalt mxl validate --profile {profile} "
                f"(M2/M8, Coria-importer-tags of meta)",
            )
        )
    return FileStatus(
        file=_rel(path),
        profile=profile,
        ok=not issues,
        issues=issues,
        fix_cmd=FIX_CMD,
    )


def collect_statuses(root: Path) -> list[FileStatus]:
    return [check_one(path, profile) for path, profile in collect_coria_mxl(root)]


def write_status_json(statuses: list[FileStatus], path: Path = STATUS_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "fix_page": FIX_PAGE,
        "fix_cmd": FIX_CMD,
        "files": {
            s.file: {
                "profile": s.profile,
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
        f"MXL-playback-contract: {len(statuses) - len(bad)} ok, {len(bad)} probleem "
        f"({STATUS_PATH.relative_to(REPO_ROOT).as_posix()})",
        flush=True,
    )
    for s in bad:
        print(f"  {s.file} [{s.profile}]:", flush=True)
        for issue in s.issues:
            print(f"    - [{issue.kind}] {issue.detail}", flush=True)
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
