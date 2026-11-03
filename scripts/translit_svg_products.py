"""Translit-siblings naast ``.vsa`` / ``.mvsa`` (§5a).

SVG (vorm A), namen gelijk aan VSA-tooling ``derived_svg_output_path``:

- ``{bron}.translit-nls.svg`` — hulpregel Latijn (ksl→nls)
- ``{bron}.translit-ksl.svg`` — hulpregel Cyrillisch (nl→ksl)

Coria-MXL (alleen ``.mvsa``): ``{bron}.translit.mxl`` via
``mvsa mxl --translit-as-parts`` (extra Nls-/Ksl-parts; één bestand).
Kale ``{bron}.mxl`` blijft zonder hulp-parts.

Welke modi/SVG’s: puur ksl → nls; puur nl → ksl; hybride → beide.
Geen Latin/Cyrillisch → geen translit-producten. Translit-MXL volgt
dezelfde voorwaarde (er is iets te translitereren).

Aanroep: na kale SVG-export vanuit sync (``vsa svg`` / ``mvsa``-straat);
niet via OSMG.
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
MODUS_BEIDE = "beide"
META_KEY_NLS = "svg-translit-nls"
META_KEY_KSL = "svg-translit-ksl"
META_KEY_MXL = "mxl-translit"

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


def product_translit_mxl(source: Path) -> Path:
    """``lied.mvsa`` → ``lied.mvsa.translit.mxl`` (Coria + hulp-parts)."""
    return source.with_name(f"{source.name}.translit.mxl")


def expects_translit_mxl(source: Path) -> bool:
    """True als deze bron een Coria-translit-``.mxl`` hoort te krijgen.

    Alleen ``.mvsa`` (tooling ``--translit-as-parts``); en alleen als er
    Latin/Cyrillisch in de bron zit.
    """
    if source.suffix.lower() != ".mvsa":
        return False
    return bool(translit_modi_for_source(source))


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


def page_needs_beide_pdf(sources: list[Path] | tuple[Path, ...]) -> bool:
    """True als het blad zowel Nls- als Ksl-translit nodig heeft (gemengd blad)."""
    modi = page_translit_modi(sources)
    return MODUS_NLS in modi and MODUS_KSL in modi


def beide_modus_for_source(source: Path) -> str | None:
    """Welke enkelvoudige translit-SVG past bij «beide knoppen» voor deze bron.

    Zelfde keuze als het scherm: Ksl-bron → nls; Nls-bron → ksl; hybride → nls.
    ``None`` = kale SVG.
    """
    modi = translit_modi_for_source(source)
    if MODUS_NLS in modi:
        return MODUS_NLS
    if MODUS_KSL in modi:
        return MODUS_KSL
    return None


def pagina_translit_pdf_path(md_path: Path, modus: str) -> Path:
    """``index.md`` + ``nls`` → ``index.md.translit-nls.pdf``."""
    m = (modus or "").casefold()
    if m not in {MODUS_NLS, MODUS_KSL, MODUS_BEIDE}:
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

    from input_paths import rel_for_log

    rel = rel_for_log(source, repo_root=REPO_ROOT)

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
        # Tooling ``mvsa/vsa svg --translit-modus`` schrijft meta-key ``svg``
        # naar het translit-bestand; herstel de kale scherm-SVG.
        main_svg = source.with_name(f"{source.name}.svg")
        if main_svg.is_file():
            written["svg"] = main_svg
        write_products_meta(source, written, merge=True)
    return written


def _stamp_ok_translit_mxl(mxl: Path, source_hash: str) -> bool:
    from product_meta import FIELD_SOURCE_KIND, FIELD_SOURCE_SHA, read_mxl_stamp

    if not mxl.is_file():
        return False
    stamp = read_mxl_stamp(mxl)
    kind = stamp.get(FIELD_SOURCE_KIND, SOURCE_KIND_MVSA)
    if kind not in {"", SOURCE_KIND_MVSA}:
        return False
    return stamp.get(FIELD_SOURCE_SHA, "") == source_hash


def translit_mxl_fresh(source: Path, digest: str | None = None) -> bool:
    """True als verwachte translit-``.mxl`` vers is (of niet verwacht)."""
    from street_meta import stamp_ok_or_meta

    if not expects_translit_mxl(source):
        return True
    digest = digest or source_sha256(source)
    path = product_translit_mxl(source)
    return stamp_ok_or_meta(
        source,
        required_keys={META_KEY_MXL},
        stamp_ok=_stamp_ok_translit_mxl(path, digest),
    )


def export_one_translit_mxl(source: Path) -> Path:
    """``mvsa mxl --translit-as-parts`` → ``{bron}.translit.mxl``."""
    if source.suffix.lower() != ".mvsa":
        raise ValueError(
            f"translit-MXL (--translit-as-parts) alleen voor .mvsa, niet {source.suffix!r}"
        )
    dest = product_translit_mxl(source)
    cmd = [
        sys.executable,
        "-m",
        "vsa.cli_mvsa",
        "mxl",
        str(source),
        "--translit-as-parts",
        "-o",
        str(dest),
    ]
    check_call(cmd, cwd=str(REPO_ROOT))
    if not dest.is_file():
        raise RuntimeError(f"translit-MXL ontbreekt na export: {dest}")
    return dest


def _stamp_translit_mxl_file(
    mxl: Path,
    *,
    source_hash: str,
    generated_at: str,
) -> None:
    from coria_mxl import load_score_xml, require_no_spaces, write_mxl
    from product_meta import stamp_mxl_source

    require_no_spaces(mxl)
    root = load_score_xml(mxl)
    stamp_mxl_source(
        root,
        source_hash=source_hash,
        source_kind=SOURCE_KIND_MVSA,
        generated_at=generated_at,
        generator=GENERATOR_MVSA,
    )
    write_mxl(mxl, root)


def sync_translit_mxl(
    source: Path,
    *,
    dry_run: bool = False,
    force: bool = False,
) -> dict[str, Path]:
    """Bouw ontbrekende/stale ``{bron}.translit.mxl``; merge products-meta."""
    if not expects_translit_mxl(source):
        return {}

    digest = source_sha256(source)
    generated_at = utc_now_iso()
    dest = product_translit_mxl(source)
    fresh = _stamp_ok_translit_mxl(dest, digest)
    if fresh and not force:
        return {META_KEY_MXL: dest}

    from input_paths import rel_for_log

    rel = rel_for_log(source, repo_root=REPO_ROOT)
    detail(f"  EXP  {rel} -> {dest.name} (--translit-as-parts)")
    if dry_run:
        return {META_KEY_MXL: dest}

    export_one_translit_mxl(source)
    _stamp_translit_mxl_file(
        dest, source_hash=digest, generated_at=generated_at
    )
    # Tooling ``mvsa mxl --translit-as-parts`` schrijft meta-key ``mxl`` naar
    # het translit-bestand. Zet canonieke Coria-``.mxl`` terug + translit-key.
    products: dict[str, Path] = {META_KEY_MXL: dest}
    main_mxl = source.with_name(f"{source.name}.mxl")
    if main_mxl.is_file():
        products["mxl"] = main_mxl
    write_products_meta(source, products, merge=True)
    return {META_KEY_MXL: dest}
