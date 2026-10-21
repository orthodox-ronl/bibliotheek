"""Bouw pagina-PDF's voor bladermap-index.md (koormap/catalogus).

Leest shortcodes uit de Markdown (bieb / muziek / pdf-pagina), zoekt de
catalogus-product-PDF per uitvoeringsvorm, en plakt die achter elkaar tot
``index.pagina.pdf`` naast het bronbestand (Hugo page resource → Download).

``pdf-pagina`` / ``pdf-bijelkaar`` sturen in v1 de web/print-CSS; bij
samenvoegen worden stukken altijd na elkaar gezet (geen verkleinen).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content-source"
CATALOGUS = CONTENT / "catalogus"

_SC = re.compile(
    r"\{\{<\s*(/?)\s*([a-z0-9_-]+)([^>]*)>\}\}",
    re.IGNORECASE,
)
_ID = re.compile(r'\bid\s*=\s*"([^"]+)"', re.IGNORECASE)
_ONDERDELEN = frozenset(
    {"titel", "title", "muziek", "bron", "copyright", "veld"}
)


def _parse_onderdeel(params: str) -> str | None:
    params = params.replace("/", " ")
    # Positional first token after stripping named attrs roughly:
    # drop id="..." and quoted strings for veld
    stripped = _ID.sub(" ", params)
    stripped = re.sub(r'"[^"]*"', " ", stripped)
    for tok in stripped.split():
        t = tok.strip().lower()
        if t in _ONDERDELEN:
            return t
    return None


def music_ids_from_markdown(text: str) -> list[str]:
    """Volgorde van uitvoeringsvorm-ids die als muziek op de pagina staan."""
    stack: list[str] = []
    pieces: list[str] = []

    for m in _SC.finditer(text):
        closing, name, params = m.group(1), m.group(2).lower(), m.group(3)
        if closing:
            if name == "bieb" and stack:
                stack.pop()
            continue
        if name in {"pdf-pagina", "pagina", "pdf-bijelkaar"}:
            continue
        if name == "muziek":
            if not stack:
                raise ValueError(
                    "shortcode muziek buiten een bieb-blok (geen id-context)"
                )
            pieces.append(stack[-1])
            continue
        if name != "bieb":
            continue

        id_m = _ID.search(params)
        uv_id = id_m.group(1).strip() if id_m else None
        onderdeel = _parse_onderdeel(params)
        self_closing = params.rstrip().endswith("/")

        if not self_closing and uv_id and onderdeel is None:
            # Paired open: {{< bieb id="…" >}}
            stack.append(uv_id)
            continue

        if not uv_id:
            if not stack:
                raise ValueError(
                    f"bieb zonder id en zonder ouder-blok: {m.group(0)!r}"
                )
            uv_id = stack[-1]

        if onderdeel is None:
            onderdeel = "muziek"
        if onderdeel == "muziek":
            pieces.append(uv_id)

    return pieces


def find_product_pdf(uv_id: str) -> Path:
    leaf = CATALOGUS.joinpath(*uv_id.split("/"))
    if not leaf.is_dir():
        raise FileNotFoundError(f"catalogusmap ontbreekt: {leaf}")
    pdfs = sorted(leaf.glob("*.pdf"))
    # Geen geneste *.pagina.pdf hier
    pdfs = [p for p in pdfs if not p.name.endswith(".pagina.pdf")]
    if not pdfs:
        raise FileNotFoundError(f"geen product-PDF in {leaf}")

    def rank(p: Path) -> tuple[int, str]:
        n = p.name.lower()
        if n.endswith(".mscz.pdf"):
            return (0, n)
        if n.endswith(".mvsa.pdf"):
            return (1, n)
        if n.endswith(".vsa.pdf"):
            return (2, n)
        return (3, n)

    pdfs.sort(key=rank)
    return pdfs[0]


def stitch_pdfs(sources: list[Path], dest: Path) -> None:
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError as exc:
        raise RuntimeError(
            "pypdf ontbreekt; installeer met: python -m pip install pypdf"
        ) from exc

    writer = PdfWriter()
    for src in sources:
        writer.append(PdfReader(str(src)))
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".tmp")
    with tmp.open("wb") as fh:
        writer.write(fh)
    tmp.replace(dest)


def build_one(md_path: Path, *, force: bool = False) -> Path | None:
    md_path = md_path.resolve()
    text = md_path.read_text(encoding="utf-8")
    if "bieb" not in text and "muziek" not in text:
        return None
    try:
        ids = music_ids_from_markdown(text)
    except ValueError as exc:
        raise ValueError(f"{md_path}: {exc}") from exc
    if not ids:
        return None

    sources = [find_product_pdf(i) for i in ids]
    # index.md → index.pagina.pdf; andere.md → andere.pagina.pdf
    if md_path.name == "index.md":
        out = md_path.with_name("index.pagina.pdf")
    else:
        out = md_path.with_name(md_path.stem + ".pagina.pdf")

    if out.is_file() and not force:
        newest_src = max(p.stat().st_mtime for p in sources)
        if out.stat().st_mtime >= newest_src and out.stat().st_mtime >= md_path.stat().st_mtime:
            return out

    stitch_pdfs(sources, out)
    return out


def iter_targets(explicit: list[Path], all_koormappen: bool) -> list[Path]:
    if explicit:
        return [p.resolve() for p in explicit]
    if all_koormappen:
        return sorted((CONTENT / "koormappen").rglob("index.md"))
    raise SystemExit("Geef een .md-pad of gebruik --all-koormappen.")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Bouw index.pagina.pdf uit catalogus-product-PDF's."
    )
    ap.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Pad(en) naar bladermap-index.md",
    )
    ap.add_argument(
        "--all-koormappen",
        action="store_true",
        help="Alle index.md onder content-source/koormappen",
    )
    ap.add_argument(
        "--force",
        action="store_true",
        help="Overschrijf ook als de PDF nieuwer lijkt dan de bronnen",
    )
    args = ap.parse_args(argv)

    targets = iter_targets(args.paths, args.all_koormappen)
    written = 0
    skipped = 0
    for md in targets:
        if not md.is_file():
            print(f"OVERGESLAGEN (bestaat niet): {md}", file=sys.stderr)
            skipped += 1
            continue
        try:
            out = build_one(md, force=args.force)
        except (FileNotFoundError, ValueError, RuntimeError) as exc:
            print(f"FOUT: {exc}", file=sys.stderr)
            return 1
        if out is None:
            skipped += 1
            continue
        print(f"OK {out.relative_to(ROOT)} ({md.relative_to(ROOT)})")
        written += 1
    print(f"Klaar: {written} PDF(s), {skipped} overgeslagen.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
