"""Scherm-SVG voor ``::: vsa``-blokken in ``index.md`` (koormappen, catalogus).

Hugo kent zulke blokken niet. Dit script tekent elk blok met ``vsa svg``
(dezelfde omzetting als ``pdf.cmd`` voor de blad-PDF) naar
``static/vsa/blok/<md5 van de blokinhoud>.svg``. De layout
``partials/content-met-vsa.html`` zet het plaatje op de plaats van het blok.

De plaatjes staan niet in git: ``serve``, ``build``, ``check`` en CI maken ze
vlak voor Hugo opnieuw. Een fout in een blok stopt de bouw.
"""

from __future__ import annotations

import hashlib
import shutil
import sys
import tempfile
from pathlib import Path

from index_md_pdf import _INLINE_VSA_FENCE, export_inline_vsa_svg

REPO = Path(__file__).resolve().parents[1]
CONTENT = REPO / "content-source"
OUT = REPO / "static" / "vsa" / "blok"


def block_key(body: str) -> str:
    """Zelfde sleutel als in ``content-met-vsa.html``."""
    return hashlib.md5(body.strip().encode("utf-8")).hexdigest()


def collect_blocks(content: Path) -> dict[str, tuple[Path, str]]:
    blocks: dict[str, tuple[Path, str]] = {}
    for section in ("koormappen", "catalogus"):
        for index in sorted((content / section).rglob("index.md")):
            text = index.read_text(encoding="utf-8-sig").replace("\r", "")
            for match in _INLINE_VSA_FENCE.finditer(text):
                body = match.group(1).strip()
                if body:
                    blocks[block_key(body)] = (index, body)
    return blocks


def main() -> int:
    blocks = collect_blocks(CONTENT)
    shutil.rmtree(OUT, ignore_errors=True)
    OUT.mkdir(parents=True)
    failed = 0
    for key, (index, body) in blocks.items():
        with tempfile.TemporaryDirectory() as tmp:
            try:
                pages = export_inline_vsa_svg(body, Path(tmp) / f"{key}.svg")
            except Exception as exc:  # noqa: BLE001 - meld welk bestand
                where = index.relative_to(REPO).as_posix()
                print(f"ERROR  ::: vsa-blok in {where}: {exc}", file=sys.stderr)
                failed += 1
                continue
            for page in pages:
                shutil.copyfile(page, OUT / page.name)
    print(f"::: vsa-blokken: {len(blocks) - failed} van {len(blocks)} getekend")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
