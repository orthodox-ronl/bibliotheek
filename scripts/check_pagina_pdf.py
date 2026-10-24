"""Controleer bladermap-``index.pagina.pdf`` (Download/Print pagina).

Geen catalogus-sibling: zelfde selectie als ``pagina-pdf`` (``pagina_pdf_job``).
Schrijft ``data/pagina-pdf-status.json``. Exit 1 bij problemen tenzij
``--warn-only``. ``--fail`` is voor CI / ``check --strict``.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from pagina_pdf import (
    ROOT,
    PaginaPdfJob,
    iter_bladermap_index_md,
    pagina_pdf_job,
)

REPO_ROOT = ROOT
STATUS_PATH = REPO_ROOT / "data" / "pagina-pdf-status.json"
FIX_PAGE = "/handleiding/scripts/pagina-pdf/"


@dataclass
class Issue:
    kind: str  # missing_pdf | stale_pdf | parse_error
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
    try:
        rel = md.parent.relative_to(REPO_ROOT / "content-source")
    except ValueError:
        return md.parent.as_posix()
    return rel.as_posix()


def _fix_cmd(md: Path) -> str:
    try:
        rel = md.relative_to(REPO_ROOT)
    except ValueError:
        rel = md
    return rf"scripts\pagina-pdf.cmd {rel.as_posix().replace('/', '\\')}"


def check_job(job: PaginaPdfJob) -> FolderStatus:
    issues: list[Issue] = []
    out = job.out_path
    if not out.is_file():
        issues.append(
            Issue(
                "missing_pdf",
                _rel(out),
                "index.pagina.pdf ontbreekt (Download/Print pagina)",
            )
        )
    else:
        dep_mtimes = [
            p.stat().st_mtime for p in job.deps if p.is_file()
        ]
        if dep_mtimes and out.stat().st_mtime < max(dep_mtimes):
            issues.append(
                Issue(
                    "stale_pdf",
                    _rel(out),
                    "index.pagina.pdf is ouder dan Markdown of notatiebron",
                )
            )
    return FolderStatus(
        dir=_bladermap_key(job.md_path),
        source=_rel(job.md_path),
        ok=not issues,
        issues=issues,
        fix_cmd=_fix_cmd(job.md_path),
    )


def check_parse_error(md: Path, detail: str) -> FolderStatus:
    return FolderStatus(
        dir=_bladermap_key(md),
        source=_rel(md),
        ok=False,
        issues=[
            Issue(
                "parse_error",
                _rel(md),
                f"pagina-pdf kan de Markdown niet lezen: {detail}",
            )
        ],
        fix_cmd=_fix_cmd(md),
    )


def collect_statuses() -> list[FolderStatus]:
    statuses: list[FolderStatus] = []
    for md in iter_bladermap_index_md():
        text = md.read_text(encoding="utf-8")
        try:
            job = pagina_pdf_job(md)
        except ValueError as exc:
            if "bieb" in text or "muziek" in text:
                statuses.append(check_parse_error(md, str(exc)))
            continue
        if job is None:
            continue
        statuses.append(check_job(job))
    return sorted(statuses, key=lambda s: s.dir)


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
            "Controleer index.pagina.pdf bij koormap-/catalogusbladen "
            "(zelfde selectie als pagina-pdf)."
        )
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
    statuses = collect_statuses()
    write_status_json(statuses)
    bad = [s for s in statuses if not s.ok]
    n_ok = len(statuses) - len(bad)
    print(
        f"Pagina-PDF: {n_ok} ok, {len(bad)} probleem "
        f"({STATUS_PATH.relative_to(REPO_ROOT).as_posix()})",
        flush=True,
    )
    for s in bad:
        print(f"  {s.dir}:", flush=True)
        for issue in s.issues:
            print(
                f"    - [{issue.kind}] {issue.file}: {issue.detail}",
                flush=True,
            )
        print(f"    fix: {s.fix_cmd}", flush=True)
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
