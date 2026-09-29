"""Maak sibling preview-``.mp3`` bij bibliotheek-``.mvsa`` / ``.mscz`` / ``.vsa``.

Per brontype een eigen product: ``{stam}.mvsa.mp3``, ``{stam}.mscz.mp3``,
``{stam}.vsa.mp3``. Roept ``vsa audio`` aan (MuseScore). Bij ``.vsa`` eerst
tijdelijk syllabifyen (zelfde als ``vsa-products`` / Coria-``.vsa.mxl``),
zodat preview-audio dezelfde lettergreep-notatie krijgt. Zet herkomststempel
in ID3 (``vsa-source-sha256`` of ``vsa-partituur-sha256``).

Slaat ``input/``, ``artefacten_handmatig``, import-``.mscz.mvsa`` en
``.print.mscz`` over. CI genereert niet — alleen ``check_audio_products``
(bestaande siblings); vernieuw lokaal met ``scripts\\audio-products.cmd``.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from coria_mxl import require_no_spaces
from product_meta import (
    FIELD_PARTITUUR_SHA,
    FIELD_SOURCE_KIND,
    FIELD_SOURCE_SHA,
    GENERATOR_AUDIO,
    SOURCE_KIND_MVSA,
    SOURCE_KIND_PARTITUUR,
    SOURCE_KIND_VSA,
    partituur_sha256,
    read_audio_stamp,
    source_sha256,
    stamp_audio,
    stamp_sha_from_dict,
    utc_now_iso,
)
from sync_import_mvsa import is_import_mvsa
from sync_mscz_products import is_print_mscz
from sync_vsa_products import folder_is_handmatig, playback_vsa_for_export

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOT = REPO_ROOT / "content-source" / "bibliotheek"


@dataclass(frozen=True)
class AudioJob:
    source: Path
    kind: str  # mvsa | partituur | vsa

    @property
    def product(self) -> Path:
        if self.kind == SOURCE_KIND_MVSA:
            return self.source.with_suffix(".mvsa.mp3")
        if self.kind == SOURCE_KIND_PARTITUUR:
            return self.source.with_suffix(".mscz.mp3")
        return self.source.with_suffix(".vsa.mp3")


def _running_in_ci() -> bool:
    return os.environ.get("CI", "").strip().lower() in {"1", "true", "yes"}


def collect_audio_jobs(root: Path) -> list[AudioJob]:
    """Alle bronnen die preview-audio mogen krijgen."""
    jobs: list[AudioJob] = []
    if not root.is_dir():
        return jobs
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if "input" in path.parts:
            continue
        if folder_is_handmatig(path.parent):
            continue
        suffix = path.suffix.lower()
        name = path.name.lower()
        if suffix == ".mvsa":
            if is_import_mvsa(path):
                continue
            require_no_spaces(path)
            jobs.append(AudioJob(path, SOURCE_KIND_MVSA))
        elif suffix == ".mscz":
            if is_print_mscz(path):
                continue
            require_no_spaces(path)
            jobs.append(AudioJob(path, SOURCE_KIND_PARTITUUR))
        elif suffix == ".vsa":
            if name.endswith(".syl.vsa"):
                continue
            require_no_spaces(path)
            jobs.append(AudioJob(path, SOURCE_KIND_VSA))
    return jobs


def _digest_for(job: AudioJob) -> str:
    if job.kind == SOURCE_KIND_PARTITUUR:
        return partituur_sha256(job.source)
    return source_sha256(job.source)


def _stamp_ok(job: AudioJob) -> bool:
    mp3 = job.product
    if not mp3.is_file():
        return False
    stamp = read_audio_stamp(mp3)
    digest = _digest_for(job)
    kind = stamp.get(FIELD_SOURCE_KIND, "")
    if kind and kind != job.kind:
        return False
    if job.kind == SOURCE_KIND_PARTITUUR:
        return stamp_sha_from_dict(stamp) == digest
    return stamp.get(FIELD_SOURCE_SHA, "") == digest


def is_stale(job: AudioJob) -> bool:
    return not _stamp_ok(job)


def _run_vsa_audio(source: Path, mp3: Path) -> None:
    cmd = ["vsa", "audio", str(source), str(mp3), "--format", "mp3"]
    subprocess.check_call(cmd, cwd=str(REPO_ROOT))


def sync_one(job: AudioJob, *, dry_run: bool) -> None:
    rel = job.source.relative_to(REPO_ROOT)
    mp3 = job.product
    print(f"  MP3  {rel} -> {mp3.name}", flush=True)
    if dry_run:
        return
    require_no_spaces(mp3)
    if job.kind == SOURCE_KIND_VSA:
        playback = playback_vsa_for_export(job.source)
        try:
            _run_vsa_audio(playback.path, mp3)
        finally:
            playback.cleanup()
    else:
        _run_vsa_audio(job.source, mp3)
    if not mp3.is_file():
        raise RuntimeError(f"MP3 ontbreekt na vsa audio: {mp3}")
    generated_at = utc_now_iso()
    digest = _digest_for(job)
    if job.kind == SOURCE_KIND_PARTITUUR:
        stamp_audio(
            mp3,
            partituur_hash=digest,
            source_kind=SOURCE_KIND_PARTITUUR,
            generated_at=generated_at,
            generator=GENERATOR_AUDIO,
        )
    else:
        stamp_audio(
            mp3,
            source_hash=digest,
            source_kind=job.kind,
            generated_at=generated_at,
            generator=GENERATOR_AUDIO,
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Exporteer stale preview-.mp3 vanuit bibliotheek-bronnen."
    )
    parser.add_argument(
        "root",
        nargs="?",
        type=Path,
        default=DEFAULT_ROOT,
        help="Zoekroot (default: content-source/bibliotheek)",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Ook exporteren als het mp3 al bij de bron past",
    )
    args = parser.parse_args(argv)
    root = args.root if args.root.is_absolute() else REPO_ROOT / args.root
    jobs = collect_audio_jobs(root)
    todo = [j for j in jobs if args.force or is_stale(j)]
    if not todo:
        print(f"Audio-producten up-to-date ({len(jobs)} bronnen)", flush=True)
        return 0

    from vsa.musescore_cli import find_musescore

    if find_musescore() is None:
        print(
            f"{len(todo)} stale .mp3; MuseScore ontbreekt.",
            flush=True,
        )
        if _running_in_ci():
            print("CI: sla audio-export over (check only).", flush=True)
            return 0
        print(r"Installeer MuseScore 4 of: scripts\audio-products.cmd", flush=True)
        for job in todo:
            print(f"  - {job.source.name} -> {job.product.name}", flush=True)
        return 1

    print(f"Audio-producten bijwerken: {len(todo)} van {len(jobs)}", flush=True)
    failed = 0
    for job in todo:
        print(f"== {job.source.relative_to(REPO_ROOT)}", flush=True)
        try:
            sync_one(job, dry_run=args.dry_run)
        except Exception as exc:  # noqa: BLE001
            print(f"  FAILED {exc}", flush=True)
            failed += 1
    if failed:
        print(f"{failed} mislukt van {len(todo)}", flush=True)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
