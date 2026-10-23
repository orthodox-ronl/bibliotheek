"""Controleer bibliotheek-``.tekstblad.md`` (geen verplichte product-PDF).

Product-``.tekstblad.pdf`` is afgebouwd: scherm en ``index.pagina.pdf``
komen uit de ``.tekstblad.md``. Schrijft
``data/tekstblad-product-status.json`` (altijd ok zolang de bron bestaat).
Exit 1 bij problemen tenzij ``--warn-only``. ``--fail`` is voor
CI / ``check --strict`` (zelfde CLI als de andere product-checks).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from sync_tekstblad_products import DEFAULT_ROOT, collect_tekstblad

REPO_ROOT = Path(__file__).resolve().parents[1]
STATUS_PATH = REPO_ROOT / "data" / "tekstblad-product-status.json"
FIX_PAGE = "/handleiding/werktrajecten/tekstblad/"


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


def _bladermap_key(md: Path) -> str:
    rel = md.parent.relative_to(REPO_ROOT / "content-source")
    return rel.as_posix()


def check_one(md: Path) -> FolderStatus:
    return FolderStatus(
        dir=_bladermap_key(md),
        source=_rel(md),
        ok=True,
        issues=[],
        fix_cmd=r"scripts\pagina-pdf.cmd",
    )


def collect_statuses(root: Path) -> list[FolderStatus]:
    by_dir: dict[str, FolderStatus] = {}
    for md in collect_tekstblad(root):
        status = check_one(md)
        prev = by_dir.get(status.dir)
        if prev is None:
            by_dir[status.dir] = status
            continue
        by_dir[status.dir] = FolderStatus(
            dir=status.dir,
            source=prev.source + "; " + status.source,
            ok=True,
            issues=[],
            fix_cmd=status.fix_cmd,
        )
    return sorted(by_dir.values(), key=lambda s: s.dir)


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
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Controleer .tekstblad.md in de catalogus "
            "(geen product-PDF-eis meer)."
        )
    )
    parser.add_argument(
        "root",
        nargs="?",
        type=Path,
        default=DEFAULT_ROOT,
        help="Catalogusmap (default: content-source/catalogus)",
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
    args = parser.parse_args(argv)
    root = args.root if args.root.is_absolute() else REPO_ROOT / args.root
    if not root.exists():
        print(f"FAIL: pad bestaat niet: {root}", file=sys.stderr)
        return 1
    statuses = collect_statuses(root)
    write_status_json(statuses)
    bad = [s for s in statuses if not s.ok]
    n_ok = len(statuses) - len(bad)
    print(
        f"Tekstblad: {n_ok} ok, {len(bad)} probleem ({STATUS_PATH.relative_to(REPO_ROOT).as_posix()})",
        flush=True,
    )
    for s in bad:
        print(f"  {s.dir}:", flush=True)
        for issue in s.issues:
            print(f"    - [{issue.kind}] {issue.file}: {issue.detail}", flush=True)
    if not bad:
        return 0
    if args.warn_only or os.environ.get("TEKSTBLAD_CHECK_WARN_ONLY") == "1":
        return 0
    if args.fail:
        return 1
    # Zonder --fail: lokaal waarschuwen; CI / main streng.
    ref = (
        os.environ.get("GITHUB_REF", "")
        or os.environ.get("GITHUB_REF_NAME", "")
        or ""
    )
    if ref in {"main", "refs/heads/main"}:
        return 1
    if os.environ.get("GITHUB_ACTIONS", "").strip().lower() == "true":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
