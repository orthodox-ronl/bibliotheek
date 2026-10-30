"""Tekstblad-producten: scherm-HTML (+ SVG) uit ``::: vsa-notatie``.

Product-PDF is afgebouwd (blad = ``index.md.pdf`` via ``scripts\\pdf.cmd``).
Scherm: body van ``.tekstblad.md``; blokken ``::: vsa-notatie`` worden
vervangen door sibling-SVG’s in ``{stam}.tekstblad.scherm.html``
(``products --kinds tekstblad``).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Sequence

from cli_style import detail, run_checked
from product_kind import (
    DEFAULT_ROOT,
    REPO_ROOT,
    ProductSlot,
    catalog_eligible,
    main_for_kind,
    require_no_spaces_name,
)
from product_meta import (
    FIELD_GENERATED_AT,
    FIELD_GENERATOR,
    FIELD_SOURCE_KIND,
    FIELD_SOURCE_SHA,
    GENERATOR_TEKSTBLAD,
    SOURCE_KIND_TEKSTBLAD,
    read_pdf_stamp,
    source_sha256,
    stamp_pdf,
    stamp_svg,
    utc_now_iso,
)
from product_regen import RegenPolicy, list_source_paths
from sync_vsa_products import folder_is_handmatig

_VSA_NOTATIE_OPEN = re.compile(r":::[\t ]*vsa-notatie\b", re.IGNORECASE)
_FRONTMATTER = re.compile(r"^---\r?\n.*?\r?\n---\r?\n?", re.DOTALL)
_HTML_STAMP_STRIP = re.compile(
    r"<!--\s*vsa-(?:source-sha256|source-kind|generated-at|generator):\s*[^>]*-->\s*",
    re.IGNORECASE,
)
_HTML_STAMP_READ = re.compile(
    r"<!--\s*(vsa-source-sha256|vsa-source-kind|vsa-generated-at|vsa-generator):\s*([^>]*?)-->",
    re.IGNORECASE,
)


def is_tekstblad_md(path: Path) -> bool:
    return path.name.lower().endswith(".tekstblad.md")


def product_pdf_for_md(md: Path) -> Path:
    """``naam.tekstblad.md`` → ``naam.tekstblad.pdf``."""
    return md.with_suffix(".pdf")


def scherm_html_for_md(md: Path) -> Path:
    """``naam.tekstblad.md`` → ``naam.tekstblad.scherm.html``."""
    return md.with_name(md.name[: -len(".md")] + ".scherm.html")


def has_vsa_notatie(md: Path) -> bool:
    try:
        text = md.read_text(encoding="utf-8")
    except OSError:
        return False
    return bool(_VSA_NOTATIE_OPEN.search(text))


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


def read_html_stamp(path: Path) -> dict[str, str]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return {}
    out: dict[str, str] = {}
    for m in _HTML_STAMP_READ.finditer(text):
        key, value = m.group(1).lower(), m.group(2).strip()
        if value:
            out[key] = value
    return out


def _stamp_ok_scherm(html: Path, source_hash: str) -> bool:
    if not html.is_file():
        return False
    stamp = read_html_stamp(html)
    return (
        stamp.get(FIELD_SOURCE_SHA) == source_hash
        and stamp.get(FIELD_SOURCE_KIND) == SOURCE_KIND_TEKSTBLAD
    )


def _block_svg_glob(md: Path) -> str:
    """Prefix van door ``prepare_markdown_document`` gekozen block-SVG-namen."""
    stem = md.name[: -len(".md")] if md.name.lower().endswith(".md") else md.stem
    safe = re.sub(r"[^a-z0-9_-]+", "-", stem.lower()).strip("-") or "vsa"
    return f"{safe}-block-*.svg"


def _remove_old_block_svgs(md: Path) -> None:
    for path in md.parent.glob(_block_svg_glob(md)):
        path.unlink(missing_ok=True)


def sync_one(md: Path, *, dry_run: bool) -> None:
    """Optioneel: schrijf sibling product-PDF (niet meer via products-slots)."""
    pdf = product_pdf_for_md(md)
    rel = md.relative_to(REPO_ROOT)
    detail(f"  PDF  {rel} -> {pdf.name}")
    if dry_run:
        return
    cmd = [
        sys.executable,
        "-m",
        "vsa.cli_md",
        "pdf",
        str(md),
        "-o",
        str(pdf),
        "--content-root",
        str(REPO_ROOT / "content-source"),
    ]
    proc = run_checked(cmd, cwd=str(REPO_ROOT))
    if proc.returncode != 0:
        raise RuntimeError(f"markdown pdf faalde (exit {proc.returncode})")
    if not pdf.is_file():
        raise RuntimeError(f"PDF ontbreekt na markdown pdf: {pdf}")
    stamp_pdf(
        pdf,
        source_hash=source_sha256(md),
        source_kind=SOURCE_KIND_TEKSTBLAD,
        generated_at=utc_now_iso(),
        generator=GENERATOR_TEKSTBLAD,
    )


def sync_tekstblad_scherm(md: Path, *, dry_run: bool) -> None:
    """Schrijf ``.tekstblad.scherm.html`` + block-SVG’s voor schermweergave."""
    from vsa.markdown_builder import prepare_markdown_document

    html_path = scherm_html_for_md(md)
    rel = md.relative_to(REPO_ROOT)
    detail(f"  scherm  {rel} -> {html_path.name}")
    if dry_run:
        return

    digest = source_sha256(md)
    generated_at = utc_now_iso()
    _remove_old_block_svgs(md)

    rewritten, svg_paths = prepare_markdown_document(
        md,
        content_root=md.parent,
        assets_dir=md.parent,
        # Token: Hugo vervangt door RelPermalink van de catalogus-leaf
        # (relatief ./… breekt op koormappen).
        assets_url_prefix="__TEKSTBLAD_ASSET__",
        output_mode="img",
    )
    body = _FRONTMATTER.sub("", rewritten, count=1)
    body = _HTML_STAMP_STRIP.sub("", body).lstrip("\n")
    body = re.sub(
        r'<img class="vsa-notation"([^>]*)>',
        r'<div class="vsa-container"><img class="vsa-notation"\1></div>',
        body,
    )
    stamp_block = "\n".join(
        [
            f"<!-- {FIELD_SOURCE_SHA}: {digest} -->",
            f"<!-- {FIELD_SOURCE_KIND}: {SOURCE_KIND_TEKSTBLAD} -->",
            f"<!-- {FIELD_GENERATED_AT}: {generated_at} -->",
            f"<!-- {FIELD_GENERATOR}: {GENERATOR_TEKSTBLAD} -->",
            "",
        ]
    )
    html_path.write_text(stamp_block + body, encoding="utf-8", newline="\n")

    for svg in svg_paths:
        if svg.is_file():
            stamp_svg(
                svg,
                generated_at=generated_at,
                source_hash=digest,
                source_kind=SOURCE_KIND_TEKSTBLAD,
                generator=GENERATOR_TEKSTBLAD,
            )


class TekstbladKind:
    id = "tekstblad"
    label = "Tekstblad-producten"
    source_noun = " .tekstblad.md"
    fix_cmd = r"scripts\products.cmd --kinds tekstblad"

    def collect(self, root: Path) -> list[Path]:
        return collect_tekstblad(root)

    def slots_for(self, source: Path, policy: RegenPolicy) -> list[ProductSlot]:
        del policy
        if not has_vsa_notatie(source):
            return []
        html = scherm_html_for_md(source)
        digest = source_sha256(source)
        return [
            ProductSlot(
                path=html,
                exists=html.is_file(),
                stamp_ok=_stamp_ok_scherm(html, digest),
            )
        ]

    def sync(self, source: Path, *, need: Sequence[bool], dry_run: bool) -> None:
        if not any(need):
            return
        sync_tekstblad_scherm(source, dry_run=dry_run)


KIND = TekstbladKind()


def main(argv: list[str] | None = None) -> int:
    return main_for_kind(
        KIND,
        argv,
        description=(
            "Tekstblad-scherm: SVG’s voor ::: vsa-notatie in .scherm.html. "
            "Pagina-PDF: scripts\\pdf.cmd."
        ),
        default_root=DEFAULT_ROOT,
    )


if __name__ == "__main__":
    raise SystemExit(main())
