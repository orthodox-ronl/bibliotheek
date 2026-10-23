"""Tekstblad-producten (historisch: sibling ``{stam}.tekstblad.pdf``).

Sinds product-pdf-afbouw + pagina-pdf uit ``.tekstblad.md`` is de
product-PDF **niet meer verplicht**. Blad print/download:
``index.pagina.pdf`` via ``scripts\\pagina-pdf.cmd``. Scherm: body van de
``.tekstblad.md`` in ``bieb``.

Dit script blijft als no-op / optioneel herstelpad: ``sync_one`` kan nog
een PDF schrijven als je het handmatig aanroept; ``TekstbladKind`` heeft
geen sync-slots meer, dus ``tekstblad-products`` doet standaard niets.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Sequence

from product_kind import (
    DEFAULT_ROOT,
    REPO_ROOT,
    ProductSlot,
    catalog_eligible,
    main_for_kind,
    require_no_spaces_name,
)
from product_meta import (
    FIELD_SOURCE_KIND,
    FIELD_SOURCE_SHA,
    GENERATOR_TEKSTBLAD,
    SOURCE_KIND_TEKSTBLAD,
    read_pdf_stamp,
    source_sha256,
    stamp_pdf,
    utc_now_iso,
)
from product_regen import RegenPolicy, list_source_paths
from sync_vsa_products import folder_is_handmatig


def is_tekstblad_md(path: Path) -> bool:
    return path.name.lower().endswith(".tekstblad.md")


def product_pdf_for_md(md: Path) -> Path:
    """``naam.tekstblad.md`` → ``naam.tekstblad.pdf``."""
    return md.with_suffix(".pdf")


def collect_tekstblad(root: Path) -> list[Path]:
    out: list[Path] = []
    for path in list_source_paths(root, pattern="*"):
        if not path.is_file() or not is_tekstblad_md(path):
            continue
        if not catalog_eligible(path, folder_is_handmatig=folder_is_handmatig):
            continue
        require_no_spaces_name(path)
        out.append(path)
    return out


def is_stale(md: Path, pdf: Path) -> bool:
    if not pdf.is_file():
        return True
    stamp = read_pdf_stamp(pdf)
    if stamp.get(FIELD_SOURCE_KIND) != SOURCE_KIND_TEKSTBLAD:
        return True
    if stamp.get(FIELD_SOURCE_SHA) != source_sha256(md):
        return True
    return False


def sync_one(md: Path, *, dry_run: bool) -> None:
    """Optioneel: schrijf sibling product-PDF (niet meer via products-slots)."""
    pdf = product_pdf_for_md(md)
    rel = md.relative_to(REPO_ROOT)
    print(f"  PDF  {rel} -> {pdf.name}", flush=True)
    if dry_run:
        return
    cmd = [
        sys.executable,
        "-m",
        "vsa.cli",
        "pdf",
        str(md),
        "-o",
        str(pdf),
        "--content-root",
        str(REPO_ROOT / "content-source"),
    ]
    proc = subprocess.run(cmd, cwd=str(REPO_ROOT), check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"vsa pdf faalde (exit {proc.returncode})")
    if not pdf.is_file():
        raise RuntimeError(f"PDF ontbreekt na vsa pdf: {pdf}")
    stamp_pdf(
        pdf,
        source_hash=source_sha256(md),
        source_kind=SOURCE_KIND_TEKSTBLAD,
        generated_at=utc_now_iso(),
        generator=GENERATOR_TEKSTBLAD,
    )


class TekstbladKind:
    id = "tekstblad"
    label = "Tekstblad-producten"
    source_noun = " .tekstblad.md"
    fix_cmd = r"scripts\pagina-pdf.cmd"

    def collect(self, root: Path) -> list[Path]:
        return collect_tekstblad(root)

    def slots_for(self, source: Path, policy: RegenPolicy) -> list[ProductSlot]:
        del source, policy
        # Geen verplichte product-PDF meer (pagina-pdf rendert uit .md).
        return []

    def sync(self, source: Path, *, need: Sequence[bool], dry_run: bool) -> None:
        del source, need, dry_run


KIND = TekstbladKind()


def main(argv: list[str] | None = None) -> int:
    return main_for_kind(
        KIND,
        argv,
        description=(
            "Tekstblad: geen verplichte product-PDF meer. "
            "Pagina: scripts\\pagina-pdf.cmd op de catalogus-leaf."
        ),
        default_root=DEFAULT_ROOT,
    )


if __name__ == "__main__":
    raise SystemExit(main())
