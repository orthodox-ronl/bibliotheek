"""Maak Coria-``.vsa.mxl`` + A4-``.vsa.pdf`` bij bibliotheek-``.vsa``.

Siblings: ``{stam}.vsa.mxl`` (Coria / Oefenen) en ``{stam}.vsa.pdf``
(Downloaden / Printen). MXL: ``vsa musicxml --musicxml-profile playback``
na tijdelijke syllabify. PDF: tijdelijke Markdown met ``::: vsa-notatie``
via ``vsa pdf`` (Chrome/Edge). Beide krijgen ``vsa-source-sha256``.

Slaat mappen met ``artefacten_handmatig: true`` over. CI genereert niet —
alleen ``check_vsa_products``; vernieuw lokaal met ``scripts\\vsa-products.cmd``.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from coria_mxl import load_score_xml, process_existing_mxl, require_no_spaces, write_mxl
from product_meta import (
    FIELD_SOURCE_KIND,
    FIELD_SOURCE_SHA,
    GENERATOR_VSA,
    GENERATOR_VSA_PDF,
    SOURCE_KIND_VSA,
    read_mxl_stamp,
    read_pdf_stamp,
    source_sha256,
    stamp_mxl_source,
    stamp_pdf,
    utc_now_iso,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOT = REPO_ROOT / "content-source" / "bibliotheek"


def _fm_bool(text: str, key: str) -> bool:
    in_fm = False
    prefix = f"{key.lower()}:"
    for line in text.splitlines():
        if line.strip() == "---":
            if not in_fm:
                in_fm = True
                continue
            break
        if in_fm and line.lower().startswith(prefix):
            val = line.split(":", 1)[1].strip().strip("\"'").lower()
            return val in {"true", "1", "yes"}
    return False


def folder_is_handmatig(folder: Path) -> bool:
    index = folder / "index.md"
    if not index.is_file():
        return False
    try:
        return _fm_bool(index.read_text(encoding="utf-8"), "artefacten_handmatig")
    except OSError:
        return False


def product_path_for_vsa(vsa: Path) -> Path:
    """``naam.vsa`` -> ``naam.vsa.mxl``."""
    return vsa.with_suffix(".vsa.mxl")


def product_pdf_for_vsa(vsa: Path) -> Path:
    """``naam.vsa`` -> ``naam.vsa.pdf``."""
    return vsa.with_suffix(".vsa.pdf")


def collect_vsa(root: Path) -> list[Path]:
    out: list[Path] = []
    if not root.is_dir():
        return out
    for path in sorted(root.rglob("*.vsa")):
        if path.name.lower().endswith(".syl.vsa"):
            continue
        if "input" in path.parts:
            continue
        if folder_is_handmatig(path.parent):
            continue
        require_no_spaces(path)
        out.append(path)
    return out


@dataclass
class PlaybackVsaSource:
    path: Path
    _temp: Path | None = None

    def cleanup(self) -> None:
        if self._temp is not None and self._temp.is_file():
            self._temp.unlink(missing_ok=True)


def playback_vsa_for_export(canonical: Path) -> PlaybackVsaSource:
    """Syllabify ongescoopte tekst voor Coria; canonieke bron blijft ongewijzigd."""
    try:
        from vsa.syllabify import syllabify_vsa_source
    except ImportError:
        return PlaybackVsaSource(path=canonical)

    text = canonical.read_text(encoding="utf-8")
    result = syllabify_vsa_source(text)
    if not result.changed:
        return PlaybackVsaSource(path=canonical)
    handle, tmp_name = tempfile.mkstemp(suffix=".vsa", prefix="vsa-coria-")
    tmp_path = Path(tmp_name)
    try:
        with open(handle, "w", encoding="utf-8", closefd=True) as fh:
            fh.write(result.text)
    except OSError:
        tmp_path.unlink(missing_ok=True)
        raise
    return PlaybackVsaSource(path=tmp_path, _temp=tmp_path)


def _stamp_ok_mxl(mxl: Path, source_hash: str) -> bool:
    if not mxl.is_file():
        return False
    stamp = read_mxl_stamp(mxl)
    kind = stamp.get(FIELD_SOURCE_KIND, "")
    if kind and kind != SOURCE_KIND_VSA:
        return stamp.get(FIELD_SOURCE_SHA, "") == source_hash
    return stamp.get(FIELD_SOURCE_SHA, "") == source_hash


def _stamp_ok_pdf(pdf: Path, source_hash: str) -> bool:
    if not pdf.is_file():
        return False
    stamp = read_pdf_stamp(pdf)
    if stamp.get(FIELD_SOURCE_KIND) != SOURCE_KIND_VSA:
        return False
    return stamp.get(FIELD_SOURCE_SHA, "") == source_hash


def is_stale(vsa: Path, mxl: Path) -> bool:
    """True als MXL ontbreekt of verouderd is (compat voor callers)."""
    return not _stamp_ok_mxl(mxl, source_sha256(vsa))


def is_stale_pair(vsa: Path) -> tuple[bool, bool]:
    """``(need_mxl, need_pdf)``."""
    digest = source_sha256(vsa)
    return (
        not _stamp_ok_mxl(product_path_for_vsa(vsa), digest),
        not _stamp_ok_pdf(product_pdf_for_vsa(vsa), digest),
    )


def _run_vsa_musicxml(vsa: Path, mxl: Path) -> None:
    cmd = [
        sys.executable,
        "-m",
        "vsa.cli",
        "musicxml",
        "--musicxml-profile",
        "playback",
        str(vsa),
        str(mxl),
    ]
    subprocess.check_call(cmd, cwd=str(REPO_ROOT))


def _run_vsa_pdf(vsa: Path, pdf: Path) -> None:
    """A4-PDF via tijdelijke Markdown + ``vsa pdf`` (site-SVG-look, printbaar)."""
    body = vsa.read_text(encoding="utf-8").rstrip() + "\n"
    title = vsa.stem.replace("-", " ")
    md_text = f"# {title}\n\n::: vsa-notatie\n{body}:::\n"
    handle, tmp_name = tempfile.mkstemp(suffix=".md", prefix="vsa-pdf-")
    tmp_path = Path(tmp_name)
    try:
        with open(handle, "w", encoding="utf-8", closefd=True) as fh:
            fh.write(md_text)
        cmd = [
            sys.executable,
            "-m",
            "vsa.cli",
            "pdf",
            str(tmp_path),
            "-o",
            str(pdf),
            "--content-root",
            str(REPO_ROOT / "content-source"),
        ]
        proc = subprocess.run(cmd, cwd=str(REPO_ROOT), check=False)
        if proc.returncode != 0:
            raise RuntimeError(f"vsa pdf faalde (exit {proc.returncode})")
    finally:
        tmp_path.unlink(missing_ok=True)
    if not pdf.is_file():
        raise RuntimeError(f"PDF ontbreekt na vsa pdf: {pdf}")


def sync_one(
    vsa: Path,
    *,
    dry_run: bool,
    do_mxl: bool = True,
    do_pdf: bool = True,
) -> None:
    rel = vsa.relative_to(REPO_ROOT)
    source_hash = source_sha256(vsa)
    generated_at = utc_now_iso()
    mxl = product_path_for_vsa(vsa)
    pdf = product_pdf_for_vsa(vsa)
    if do_mxl:
        print(f"  MXL  {rel} -> {mxl.name}", flush=True)
    if do_pdf:
        print(f"  PDF  {rel} -> {pdf.name}", flush=True)
    if dry_run:
        return
    if do_mxl:
        require_no_spaces(mxl)
        playback = playback_vsa_for_export(vsa)
        try:
            _run_vsa_musicxml(playback.path, mxl)
        finally:
            playback.cleanup()
        process_existing_mxl(mxl)
        root = load_score_xml(mxl)
        stamp_mxl_source(
            root,
            source_hash=source_hash,
            source_kind=SOURCE_KIND_VSA,
            generated_at=generated_at,
            generator=GENERATOR_VSA,
        )
        write_mxl(mxl, root)
        legacy = vsa.with_suffix(".mxl")
        if legacy.is_file() and legacy.resolve() != mxl.resolve():
            stamp = read_mxl_stamp(legacy)
            if stamp.get(FIELD_SOURCE_KIND, SOURCE_KIND_VSA) in {"", SOURCE_KIND_VSA}:
                print(f"  remove legacy {legacy.name}", flush=True)
                legacy.unlink()
    if do_pdf:
        require_no_spaces(pdf)
        _run_vsa_pdf(vsa, pdf)
        stamp_pdf(
            pdf,
            source_hash=source_hash,
            source_kind=SOURCE_KIND_VSA,
            generated_at=generated_at,
            generator=GENERATOR_VSA_PDF,
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Exporteer stale Coria-.mxl en A4-.vsa.pdf vanuit bibliotheek-.vsa."
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
        help="Ook exporteren als producten al bij de bron passen",
    )
    args = parser.parse_args()
    root = args.root if args.root.is_absolute() else REPO_ROOT / args.root
    vsas = collect_vsa(root)
    todo: list[tuple[Path, bool, bool]] = []
    for vsa in vsas:
        need_mxl, need_pdf = is_stale_pair(vsa)
        if args.force:
            need_mxl, need_pdf = True, True
        if need_mxl or need_pdf:
            todo.append((vsa, need_mxl, need_pdf))
    if not todo:
        print(f"VSA-producten up-to-date ({len(vsas)} .vsa)", flush=True)
        return 0
    print(f"VSA-producten bijwerken: {len(todo)} van {len(vsas)}", flush=True)
    failed = 0
    for vsa, need_mxl, need_pdf in todo:
        print(f"== {vsa.relative_to(REPO_ROOT)}", flush=True)
        try:
            sync_one(
                vsa,
                dry_run=args.dry_run,
                do_mxl=need_mxl,
                do_pdf=need_pdf,
            )
        except Exception as exc:  # noqa: BLE001
            print(f"  FAILED {exc}", flush=True)
            failed += 1
    if failed:
        print(f"{failed} mislukt van {len(todo)}", flush=True)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
