"""Controleer bibliotheek-bronnen vs sibling preview-``.mp3``.

Elke canonieke ``.mvsa``, basispartituur-``.mscz`` en ``.vsa`` (zelfde
scope als de Coria-MXL-sporen) moet een passende ``.mp3`` hebben met
herkomststempel. Orphan-``.mp3`` zonder bron faalt ook.

Schrijft ``data/audio-product-status.json``. Exit 1 bij problemen tenzij
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
    FIELD_SOURCE_KIND,
    FIELD_SOURCE_SHA,
    SOURCE_KIND_MVSA,
    SOURCE_KIND_PARTITUUR,
    SOURCE_KIND_VSA,
    partituur_sha256,
    read_audio_stamp,
    source_sha256,
    stamp_sha_from_dict,
)
from sync_audio_products import (
    DEFAULT_ROOT,
    AudioJob,
    collect_audio_jobs,
)
from sync_import_mvsa import is_import_mvsa
from sync_mscz_products import is_print_mscz
from sync_vsa_products import folder_is_handmatig

REPO_ROOT = Path(__file__).resolve().parents[1]
STATUS_PATH = REPO_ROOT / "data" / "audio-product-status.json"
FIX_PAGE = "/handleiding/scripts/audio-products/"


@dataclass
class Issue:
    kind: str
    file: str
    detail: str


@dataclass
class FolderStatus:
    dir: str
    source: str
    product: str
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


def _source_for_mp3(mp3: Path) -> AudioJob | None:
    """Leid bron af uit ``{stam}.{bron-ext}.mp3``."""
    name = mp3.name
    lower = name.lower()
    if lower.endswith(".mvsa.mp3"):
        source = mp3.with_name(name[: -len(".mp3")])
        if source.is_file() and not is_import_mvsa(source):
            return AudioJob(source, SOURCE_KIND_MVSA)
        return None
    if lower.endswith(".mscz.mp3"):
        source = mp3.with_name(name[: -len(".mp3")])
        if source.is_file() and not is_print_mscz(source):
            return AudioJob(source, SOURCE_KIND_PARTITUUR)
        return None
    if lower.endswith(".vsa.mp3"):
        source = mp3.with_name(name[: -len(".mp3")])
        if source.is_file() and not source.name.lower().endswith(".syl.vsa"):
            return AudioJob(source, SOURCE_KIND_VSA)
        return None
    return None


def collect_existing_mp3(root: Path) -> list[Path]:
    out: list[Path] = []
    if not root.is_dir():
        return out
    for path in sorted(root.rglob("*.mp3")):
        if not path.is_file():
            continue
        if "input" in path.parts:
            continue
        if folder_is_handmatig(path.parent):
            continue
        lower = path.name.lower()
        if not (
            lower.endswith(".mvsa.mp3")
            or lower.endswith(".mscz.mp3")
            or lower.endswith(".vsa.mp3")
        ):
            continue
        out.append(path)
    return out


def check_one(job: AudioJob) -> FolderStatus:
    issues: list[Issue] = []
    mp3 = job.product
    fix = r"scripts\audio-products.cmd"
    digest = (
        partituur_sha256(job.source)
        if job.kind == SOURCE_KIND_PARTITUUR
        else source_sha256(job.source)
    )

    if not mp3.is_file():
        issues.append(
            Issue(
                "missing_mp3",
                _rel(mp3),
                "Preview-.mp3 ontbreekt naast de bron (Beluisteren)",
            )
        )
        return FolderStatus(
            dir=_bladermap_key(job.source),
            source=_rel(job.source),
            product=_rel(mp3),
            ok=False,
            issues=issues,
            fix_cmd=fix,
        )

    stamp = read_audio_stamp(mp3)
    kind = stamp.get(FIELD_SOURCE_KIND, "")
    if job.kind == SOURCE_KIND_PARTITUUR:
        got = stamp_sha_from_dict(stamp)
        if not got:
            issues.append(
                Issue(
                    "unstamped_mp3",
                    _rel(mp3),
                    "MP3 mist vsa-partituur-sha256 (opnieuw audio-products)",
                )
            )
        elif kind and kind != SOURCE_KIND_PARTITUUR:
            issues.append(
                Issue(
                    "wrong_kind",
                    _rel(mp3),
                    f"MP3 source-kind is {kind!r}, verwacht {SOURCE_KIND_PARTITUUR!r}",
                )
            )
        elif got != digest:
            when = stamp.get(FIELD_GENERATED_AT, "?")
            issues.append(
                Issue(
                    "stale_mp3",
                    _rel(mp3),
                    f"MP3-partituur-hash wijkt af (gegenereerd {when}); .mscz is gewijzigd",
                )
            )
    else:
        got = stamp.get(FIELD_SOURCE_SHA, "")
        if not got:
            issues.append(
                Issue(
                    "unstamped_mp3",
                    _rel(mp3),
                    "MP3 mist vsa-source-sha256 (opnieuw audio-products)",
                )
            )
        elif kind and kind != job.kind:
            issues.append(
                Issue(
                    "wrong_kind",
                    _rel(mp3),
                    f"MP3 source-kind is {kind!r}, verwacht {job.kind!r}",
                )
            )
        elif got != digest:
            when = stamp.get(FIELD_GENERATED_AT, "?")
            issues.append(
                Issue(
                    "stale_mp3",
                    _rel(mp3),
                    f"MP3-source-hash wijkt af (gegenereerd {when}); bron is gewijzigd",
                )
            )

    return FolderStatus(
        dir=_bladermap_key(job.source),
        source=_rel(job.source),
        product=_rel(mp3),
        ok=not issues,
        issues=issues,
        fix_cmd=fix,
    )


def check_orphan(mp3: Path) -> FolderStatus:
    return FolderStatus(
        dir=_bladermap_key(mp3),
        source="",
        product=_rel(mp3),
        ok=False,
        issues=[
            Issue(
                "orphan_mp3",
                _rel(mp3),
                "MP3 zonder passende bron (.mvsa / .mscz / .vsa); verwijder of herstel bron",
            )
        ],
        fix_cmd=r"scripts\audio-products.cmd",
    )


def collect_statuses(root: Path) -> list[FolderStatus]:
    statuses: list[FolderStatus] = []
    seen_products: set[Path] = set()
    for job in collect_audio_jobs(root):
        statuses.append(check_one(job))
        seen_products.add(job.product.resolve())
    for mp3 in collect_existing_mp3(root):
        if mp3.resolve() in seen_products:
            continue
        job = _source_for_mp3(mp3)
        if job is None:
            statuses.append(check_orphan(mp3))
    return statuses


def write_status_json(statuses: list[FolderStatus], path: Path = STATUS_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "fix_page": FIX_PAGE,
        "policy": "require_all_sources",
        "folders": {
            f"{s.dir}|{Path(s.product).name if s.product else 'missing'}": {
                "source": s.source,
                "product": s.product,
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
        f"Audio-producten: {len(statuses) - len(bad)} ok, {len(bad)} probleem "
        f"({STATUS_PATH.relative_to(REPO_ROOT).as_posix()})",
        flush=True,
    )
    for s in bad:
        label = s.dir or s.product
        print(f"  {label}:", flush=True)
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
