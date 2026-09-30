"""Bladermap-SVG uit bibliotheek-``.vsa`` (geen versheidscontrole/stamp).

``--svg``: schrijft plaatjes naar ``static/vsa/bladermap/`` voor elke
canonieke ``.vsa`` in een bladermap **zonder** basispartituur-``.mscz``
(``.print.mscz`` blokkeert niet). Geen publicatiecontrole: SVG is een
site-plaatje, geen sha-stampproduct. Commit ze mee of laat check/build/CI
ze vernieuwen vóór Hugo.

Zonder flags: legacy strip van auto-widgets in bladermap-``index.md``
(pagina’s met ``bieb`` of ``automatische_inhoud: false`` blijven onaangeroerd).
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from score_filenames import is_print_mscz, is_vsa_source

REPO = Path(__file__).resolve().parents[1]
CONTENT = REPO / "content-source"
CATALOGUS = CONTENT / "catalogus"
SVG_ROOT = REPO / "static" / "vsa" / "bladermap"

RE_BIEB = re.compile(r"\{\{<\s*bieb\b", re.I)
AUTO_FALSE_RE = re.compile(
    r"^automatische_inhoud:\s*(false|0|nee|no)\s*$", re.I | re.M
)
LOCAL_INCLUDE_RE = re.compile(
    r'^\s*:::\s*include\s+(?:svg|coria|mxl)\s+"[^"]+".*:::\s*$', re.I
)
SCORE_OPEN_RE = re.compile(r"^\s*\{\{<\s*score-actions\b", re.I)
SCORE_CLOSE_RE = re.compile(r"^\s*\{\{<\s*/score-actions\s*>\}\}\s*$", re.I)
PDF_SHEET_RE = re.compile(r"^\s*\{\{<\s*pdf-sheet\b.*>\}\}\s*$", re.I)
STUB_COMMENT_RE = re.compile(
    r"^\s*<!--\s*(?::::include|score-actions|pdf-sheet)\b.*?-->\s*$",
    re.I,
)


def _split_frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---"):
        return "", text
    rest = text[3:]
    end = rest.find("\n---")
    if end < 0:
        return "", text
    fm = rest[:end].strip("\n")
    body = rest[end + 4 :].lstrip("\n")
    return fm, body


def _strip_widgets(body: str) -> str:
    kept: list[str] = []
    skipping_score = False
    for line in body.splitlines():
        if skipping_score:
            if SCORE_CLOSE_RE.match(line):
                skipping_score = False
            continue
        if LOCAL_INCLUDE_RE.match(line):
            continue
        if SCORE_OPEN_RE.match(line):
            skipping_score = True
            continue
        if PDF_SHEET_RE.match(line):
            continue
        if STUB_COMMENT_RE.match(line):
            continue
        kept.append(line)
    text = "\n".join(kept)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return f"{text}\n" if text else ""


def _iter_indexes() -> list[Path]:
    if not CATALOGUS.is_dir():
        return []
    return sorted(CATALOGUS.rglob("index.md"))


def strip_indexes(*, dry_run: bool, verbose: bool) -> int:
    changed = 0
    skipped = 0
    for path in _iter_indexes():
        raw = path.read_text(encoding="utf-8")
        fm, body = _split_frontmatter(raw)
        if not fm:
            skipped += 1
            continue
        if AUTO_FALSE_RE.search(fm):
            skipped += 1
            continue
        if RE_BIEB.search(body):
            skipped += 1
            continue
        new_body = _strip_widgets(body)
        new = f"---\n{fm}\n---\n"
        if new_body:
            new += f"\n{new_body}"
        if new.replace("\r\n", "\n") == raw.replace("\r\n", "\n"):
            continue
        rel = path.relative_to(REPO).as_posix()
        if dry_run:
            print(f"would strip {rel}", flush=True)
        else:
            path.write_text(new, encoding="utf-8", newline="\n")
            if verbose:
                print(f"stripped {rel}", flush=True)
        changed += 1
    print(
        f"oefenhoek-index: {changed} gestript, {skipped} overgeslagen",
        flush=True,
    )
    return 0


def _render_one_vsa(src: Path, dest: Path) -> None:
    from vsa.include_vsa import prepare_vsa_body
    from vsa.markdown_newline_policy import preserve_vsa_source_newlines
    from vsa.parser import Parser
    from vsa.svg_renderer import SVGRenderer

    text = src.read_text(encoding="utf-8")
    body, _ = prepare_vsa_body(text, src)
    document = Parser(preserve_vsa_source_newlines(body)).parse()
    svg = SVGRenderer().render_document(document)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(svg, encoding="utf-8")


def _bladermap_folders() -> list[Path]:
    if not CATALOGUS.is_dir():
        return []
    out: list[Path] = []
    for folder in sorted(CATALOGUS.rglob("*")):
        if not folder.is_dir():
            continue
        if "input" in folder.parts:
            continue
        if not (folder / "index.md").is_file():
            continue
        out.append(folder)
    return out


def render_svgs(*, verbose: bool) -> int:
    from vsa.errors import VSAError
    from vsa.include_vsa import IncludeVsaError

    if SVG_ROOT.exists():
        for old in SVG_ROOT.rglob("*.svg"):
            old.unlink()

    written = 0
    errors: list[str] = []
    for folder in _bladermap_folders():
        msczs = [
            p
            for p in folder.glob("*.mscz")
            if not is_print_mscz(p)
        ]
        if msczs:
            continue
        for vsa in sorted(folder.glob("*.vsa")):
            if not is_vsa_source(vsa):
                continue
            rel = vsa.relative_to(CONTENT).with_suffix(".svg")
            dest = SVG_ROOT / rel
            try:
                _render_one_vsa(vsa, dest)
            except IncludeVsaError as exc:
                errors.append(
                    f"{vsa.relative_to(REPO).as_posix()}: {exc.message_nl}"
                )
                continue
            except VSAError as exc:
                errors.append(f"{vsa.relative_to(REPO).as_posix()}: {exc}")
                continue
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{vsa.relative_to(REPO).as_posix()}: {exc}")
                continue
            written += 1
            if verbose:
                print(f"svg {rel.as_posix()}", flush=True)
    if errors:
        for line in errors:
            print(f"FAIL: {line}", flush=True)
        print(
            f"bladermap-svg: {written} ok, {len(errors)} fout(en)",
            flush=True,
        )
        return 1
    print(f"bladermap-svg: {written} bestand(en)", flush=True)
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument(
        "--svg",
        action="store_true",
        help="Schrijf SVG van catalogus-.vsa naar static/vsa/bladermap/",
    )
    p.add_argument(
        "--verbose",
        action="store_true",
        help="Toon elk bestand (standaard alleen een samenvatting)",
    )
    args = p.parse_args(argv)
    if args.svg:
        return render_svgs(verbose=args.verbose)
    return strip_indexes(dry_run=args.dry_run, verbose=args.verbose)


if __name__ == "__main__":
    raise SystemExit(main())
