"""Translit-SVG siblings naast ``.vsa`` / ``.mvsa`` (§5a vorm A).

Bestandsnamen (gelijk aan VSA-tooling ``derived_svg_output_path``):

- ``{bron}.translit-nls.svg`` — hulpregel Latijn (ksl→nls)
- ``{bron}.translit-ksl.svg`` — hulpregel Cyrillisch (nl→ksl)

Welke modi: puur ksl → nls; puur nl → ksl; hybride (beide schriften) →
beide. Geen Latin/Cyrillisch in de bron → geen translit-SVG.

Aanroep: na kale ``vsa``/``mvsa products`` vanuit sync; niet via OSMG.
"""

from __future__ import annotations

import sys
from pathlib import Path

from cli_style import check_call, detail
from product_kind import REPO_ROOT
from product_meta import (
    GENERATOR_MVSA,
    GENERATOR_VSA_PDF,
    SOURCE_KIND_MVSA,
    SOURCE_KIND_VSA,
    source_sha256,
    stamp_svg,
    utc_now_iso,
)
from street_meta import write_products_meta

MODUS_NLS = "nls"
MODUS_KSL = "ksl"
META_KEY_NLS = "svg-translit-nls"
META_KEY_KSL = "svg-translit-ksl"

_META_KEYS = {
    MODUS_NLS: META_KEY_NLS,
    MODUS_KSL: META_KEY_KSL,
}


def product_translit_svg(source: Path, modus: str) -> Path:
    """``lied.vsa`` + ``nls`` → ``lied.vsa.translit-nls.svg``."""
    m = (modus or "").casefold()
    if m not in {MODUS_NLS, MODUS_KSL}:
        raise ValueError(f"onbekende translit-modus {modus!r} (nls|ksl)")
    return source.with_name(f"{source.name}.translit-{m}.svg")


def meta_key_for_modus(modus: str) -> str:
    m = (modus or "").casefold()
    if m not in _META_KEYS:
        raise ValueError(f"onbekende translit-modus {modus!r}")
    return _META_KEYS[m]


def read_source_body(source: Path) -> str:
    """Tekst voor schriftdetectie (``.vsa``: body zonder YAML-frontmatter)."""
    raw = source.read_text(encoding="utf-8")
    if source.suffix.lower() != ".vsa":
        return raw
    try:
        from vsa.yaml_frontmatter import parse_vsa_frontmatter

        _meta, body = parse_vsa_frontmatter(raw)
        return body
    except Exception:
        return raw


def translit_modi_for_text(text: str) -> tuple[str, ...]:
    """Welke ``--translit-modus``-SVG’s bij deze brontekst horen (§5a)."""
    from vsa.transliterate import has_cyrillic, has_latin_letter

    cyr = has_cyrillic(text)
    lat = has_latin_letter(text)
    if cyr and lat:
        return (MODUS_NLS, MODUS_KSL)
    if cyr:
        return (MODUS_NLS,)
    if lat:
        return (MODUS_KSL,)
    return ()


def translit_modi_for_source(source: Path) -> tuple[str, ...]:
    if source.suffix.lower() not in {".vsa", ".mvsa"}:
        return ()
    try:
        text = read_source_body(source)
    except OSError:
        return ()
    return translit_modi_for_text(text)


def page_translit_modi(sources: list[Path] | tuple[Path, ...]) -> tuple[str, ...]:
    """Unie van modi over notatiebronnen op één blad (§5a)."""
    needed: set[str] = set()
    for source in sources:
        needed.update(translit_modi_for_source(source))
    return tuple(m for m in (MODUS_NLS, MODUS_KSL) if m in needed)


def pagina_translit_pdf_path(md_path: Path, modus: str) -> Path:
    """``index.md`` + ``nls`` → ``index.md.translit-nls.pdf``."""
    m = (modus or "").casefold()
    if m not in {MODUS_NLS, MODUS_KSL}:
        raise ValueError(f"onbekende translit-modus {modus!r}")
    return md_path.with_name(f"{md_path.name}.translit-{m}.pdf")


def _cli_for_source(source: Path) -> list[str]:
    suf = source.suffix.lower()
    if suf == ".vsa":
        return [sys.executable, "-m", "vsa.cli", "svg"]
    if suf == ".mvsa":
        return [sys.executable, "-m", "vsa.cli_mvsa", "svg"]
    raise ValueError(
        f"translit-SVG alleen voor .vsa/.mvsa, niet {source.suffix!r}"
    )


def _source_kind_and_generator(source: Path) -> tuple[str, str]:
    if source.suffix.lower() == ".mvsa":
        return SOURCE_KIND_MVSA, GENERATOR_MVSA
    return SOURCE_KIND_VSA, GENERATOR_VSA_PDF


def export_one_translit_svg(source: Path, modus: str) -> Path:
    """Roep tooling ``svg --translit-modus`` aan; retourneer bestemming."""
    dest = product_translit_svg(source, modus)
    cmd = [
        *_cli_for_source(source),
        str(source),
        "--translit-modus",
        (modus or "").casefold(),
        "-o",
        str(dest),
    ]
    check_call(cmd, cwd=str(REPO_ROOT))
    if not dest.is_file():
        raise RuntimeError(f"translit-SVG ontbreekt na export: {dest}")
    return dest


def translit_svgs_fresh(source: Path, digest: str | None = None) -> bool:
    """True als alle verwachte translit-SVG’s bestaan en stamp/meta klopt."""
    from street_meta import stamp_ok_or_meta

    modi = translit_modi_for_source(source)
    if not modi:
        return True
    digest = digest or source_sha256(source)
    kind, _gen = _source_kind_and_generator(source)
    for modus in modi:
        path = product_translit_svg(source, modus)
        meta_key = meta_key_for_modus(modus)
        stamp_ok = _stamp_ok_translit_svg(path, digest, source_kind=kind)
        if not stamp_ok_or_meta(
            source,
            required_keys={meta_key},
            stamp_ok=stamp_ok,
        ):
            return False
    return True


def _stamp_ok_translit_svg(
    svg: Path, source_hash: str, *, source_kind: str
) -> bool:
    from product_meta import FIELD_SOURCE_KIND, FIELD_SOURCE_SHA, read_svg_stamp

    if not svg.is_file():
        return False
    stamp = read_svg_stamp(svg)
    kind = stamp.get(FIELD_SOURCE_KIND, source_kind)
    if kind not in {"", source_kind}:
        return False
    return stamp.get(FIELD_SOURCE_SHA, "") == source_hash


def sync_translit_svgs(
    source: Path,
    *,
    dry_run: bool = False,
    force: bool = False,
) -> dict[str, Path]:
    """Bouw ontbrekende/stale translit-SVG’s; merge products-meta.

    ``force``: altijd opnieuw exporteren (bijv. na kale bron-SVG-export).
    Retourneert meta-key → pad voor geschreven (of al verse) bestanden.
    """
    modi = translit_modi_for_source(source)
    if not modi:
        return {}

    digest = source_sha256(source)
    generated_at = utc_now_iso()
    kind, generator = _source_kind_and_generator(source)
    written: dict[str, Path] = {}

    try:
        rel = source.relative_to(REPO_ROOT)
    except ValueError:
        rel = source

    for modus in modi:
        dest = product_translit_svg(source, modus)
        meta_key = meta_key_for_modus(modus)
        fresh = _stamp_ok_translit_svg(dest, digest, source_kind=kind)
        if fresh and not force:
            written[meta_key] = dest
            continue
        detail(f"  EXP  {rel} -> {dest.name} (--translit-modus {modus})")
        if dry_run:
            written[meta_key] = dest
            continue
        export_one_translit_svg(source, modus)
        stamp_svg(
            dest,
            source_hash=digest,
            source_kind=kind,
            generated_at=generated_at,
            generator=generator,
        )
        written[meta_key] = dest

    if written and not dry_run:
        write_products_meta(source, written, merge=True)
    return written
