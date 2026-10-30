"""Maak sibling preview-``.mp3`` bij bibliotheek-``.mvsa`` / ``.mscz`` / ``.vsa``.

Per brontype een eigen product: ``{stam}.mvsa.mp3``, ``{stam}.mscz.mp3``,
``{stam}.vsa.mp3``. Straat-puur: ``mvsa mp3`` / ``mscz mp3`` / ``vsa audio``
(MuseScore). Bij ``.vsa`` eerst tijdelijk syllabifyen (zelfde als
``products --kinds vsa`` / Coria-``.vsa.mxl``), zodat preview-audio dezelfde
lettergreep-notatie krijgt. Zet herkomststempel in ID3
(``vsa-source-sha256`` of ``vsa-partituur-sha256``).

Slaat ``input/``, ``manueel/manual``, import-``.mscz.mvsa``,
``.print.mscz`` en afgeleide ``*.vsa.mscz`` / ``*.mvsa.mscz`` over
(tenzij je zo'n bestand expliciet als CLI-pad doorgeeft). CI genereert
niet — alleen ``check_audio_products`` (bestaande siblings); vernieuw
lokaal met ``scripts\\products.cmd --kinds audio``.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from cli_style import check_call, detail
from coria_mxl import require_no_spaces
from product_kind import (
    DEFAULT_ROOT,
    REPO_ROOT,
    ProductSlot,
    catalog_eligible,
    main_for_kind,
)
from product_meta import (
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
from product_regen import RegenPolicy, list_source_paths
from score_filenames import is_derived_mscz
from sync_import_mvsa import is_import_mvsa
from sync_mscz_products import is_print_mscz
from sync_vsa_products import folder_is_handmatig, playback_vsa_for_export


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


def collect_audio_jobs(root: Path) -> list[AudioJob]:
    """Alle bronnen die preview-audio mogen krijgen.

    Map-scan slaat afgeleide ``*.vsa.mscz`` / ``*.mvsa.mscz`` over.
    Expliciet CLI-bestandspad (ook met meerdere extensies) mag wél.
    """
    jobs: list[AudioJob] = []
    explicit = root.is_file()
    for path in list_source_paths(root, pattern="*"):
        if not path.is_file():
            continue
        if not catalog_eligible(path, folder_is_handmatig=folder_is_handmatig):
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
            if not explicit and is_derived_mscz(path):
                continue
            require_no_spaces(path)
            jobs.append(AudioJob(path, SOURCE_KIND_PARTITUUR))
        elif suffix == ".vsa":
            if name.endswith(".syl.vsa"):
                continue
            require_no_spaces(path)
            jobs.append(AudioJob(path, SOURCE_KIND_VSA))
    return jobs


def _job_for(source: Path) -> AudioJob:
    suf = source.suffix.lower()
    if suf == ".mvsa":
        return AudioJob(source, SOURCE_KIND_MVSA)
    if suf == ".mscz":
        return AudioJob(source, SOURCE_KIND_PARTITUUR)
    return AudioJob(source, SOURCE_KIND_VSA)


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


def _audio_cli_cmd(job: AudioJob, mp3: Path) -> list[str]:
    """Canonieke street-CLI per brontype (``vsa audio`` weigert .mscz/.mvsa)."""
    if job.kind == SOURCE_KIND_PARTITUUR:
        return ["mscz", "mp3", str(job.source), "-o", str(mp3)]
    if job.kind == SOURCE_KIND_MVSA:
        return ["mvsa", "mp3", str(job.source), "-o", str(mp3)]
    return ["vsa", "audio", str(job.source), str(mp3), "--format", "mp3"]


def _run_audio(job: AudioJob, mp3: Path) -> None:
    check_call(_audio_cli_cmd(job, mp3), cwd=str(REPO_ROOT))


def sync_one(job: AudioJob, *, dry_run: bool) -> None:
    rel = job.source.relative_to(REPO_ROOT)
    mp3 = job.product
    detail(f"  MP3  {rel} -> {mp3.name}")
    if dry_run:
        return
    require_no_spaces(mp3)
    if job.kind == SOURCE_KIND_VSA:
        playback = playback_vsa_for_export(job.source)
        try:
            _run_audio(AudioJob(playback.path, SOURCE_KIND_VSA), mp3)
        finally:
            playback.cleanup()
    else:
        _run_audio(job, mp3)
    if not mp3.is_file():
        raise RuntimeError(f"MP3 ontbreekt na audio-export: {mp3}")
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


class AudioKind:
    id = "audio"
    label = "Audio-producten"
    source_noun = " bronnen"
    fix_cmd = r"scripts\products.cmd --kinds audio"

    def collect(self, root: Path) -> list[Path]:
        return [job.source for job in collect_audio_jobs(root)]

    def slots_for(self, source: Path, policy: RegenPolicy) -> list[ProductSlot]:
        del policy
        job = _job_for(source)
        exists = job.product.is_file()
        stamp_ok = _stamp_ok(job) if exists else False
        return [
            ProductSlot(
                path=job.product,
                exists=exists,
                stamp_ok=stamp_ok,
                contract_ok=None,
                needs_musescore=True,
            )
        ]

    def sync(self, source: Path, *, need: Sequence[bool], dry_run: bool) -> None:
        if need and need[0]:
            sync_one(_job_for(source), dry_run=dry_run)


KIND = AudioKind()


def main(argv: list[str] | None = None) -> int:
    return main_for_kind(
        KIND,
        argv,
        description="Exporteer stale preview-.mp3 vanuit bibliotheek-bronnen.",
        default_root=DEFAULT_ROOT,
    )


if __name__ == "__main__":
    raise SystemExit(main())
