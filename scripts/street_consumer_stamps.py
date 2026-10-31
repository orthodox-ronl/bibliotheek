"""Bibliotheek-stempels na kale tooling-``… products``.

Tooling schrijft lyrics/mp3 expres zonder bibliotheek-herkomststempels
(products-meta is genoeg voor tooling). Bibliotheek-check voor lyrics en
audio eist wél die stempels. Na ``mvsa``/``vsa``/``mscz products`` opnieuw
zetten zonder opnieuw te exporteren.
"""

from __future__ import annotations

from pathlib import Path

from product_meta import (
    FIELD_GENERATED_AT,
    FIELD_GENERATOR,
    FIELD_SOURCE_KIND,
    FIELD_SOURCE_SHA,
    GENERATOR_AUDIO,
    GENERATOR_LYRICS,
    SOURCE_KIND_MVSA,
    SOURCE_KIND_PARTITUUR,
    SOURCE_KIND_VSA,
    stamp_audio,
    utc_now_iso,
)


def _source_kind(source: Path) -> str:
    suf = source.suffix.lower()
    if suf == ".mvsa":
        return SOURCE_KIND_MVSA
    if suf == ".mscz":
        return SOURCE_KIND_PARTITUUR
    return SOURCE_KIND_VSA


def restamp_lyrics_sibling(source: Path) -> bool:
    """Zet `# vsa-source-sha256:` op bestaande ``{bron}.lyrics.txt``. True als gedaan."""
    from sync_lyrics_products import (
        digest_for_source,
        lyrics_body,
        product_path_for_source,
        source_kind_for,
    )

    lyrics = product_path_for_source(source)
    if not lyrics.is_file():
        return False
    body = lyrics_body(lyrics)
    src_hash = digest_for_source(source)
    generated_at = utc_now_iso()
    kind = source_kind_for(source)
    header = "\n".join(
        [
            f"# {FIELD_SOURCE_SHA}: {src_hash}",
            f"# {FIELD_SOURCE_KIND}: {kind}",
            f"# {FIELD_GENERATED_AT}: {generated_at}",
            f"# {FIELD_GENERATOR}: {GENERATOR_LYRICS}",
            "",
            "",
        ]
    )
    payload = body.strip() + ("\n" if body.strip() else "")
    lyrics.write_text(header + payload, encoding="utf-8", newline="\n")
    return True


def restamp_mp3_sibling(source: Path) -> bool:
    """Zet ID3-herkomststempel op bestaande ``{bron}.mp3``. True als gedaan."""
    from sync_lyrics_products import digest_for_source

    mp3 = Path(str(source) + ".mp3")
    if not mp3.is_file():
        return False
    digest = digest_for_source(source)
    kind = _source_kind(source)
    generated_at = utc_now_iso()
    if kind == SOURCE_KIND_PARTITUUR:
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
            source_kind=kind,
            generated_at=generated_at,
            generator=GENERATOR_AUDIO,
        )
    return True


def restamp_after_street_products(source: Path) -> None:
    """Herstel lyrics- + mp3-stempels na kale street-``products``.

    Werkt daarna products-meta bij (merge), zodat de hashes van die
    bestanden weer kloppen na het stempelen.
    """
    from street_meta import write_products_meta
    from sync_lyrics_products import product_path_for_source

    did_lyrics = restamp_lyrics_sibling(source)
    did_mp3 = restamp_mp3_sibling(source)
    if not did_lyrics and not did_mp3:
        return
    products: dict[str, Path] = {}
    if did_lyrics:
        products["lyrics"] = product_path_for_source(source)
    if did_mp3:
        products["mp3"] = Path(str(source) + ".mp3")
    write_products_meta(source, products, merge=True)
