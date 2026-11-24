"""Woordencontrole voor de opruimscripts (migratiestap 7, vervolg).

Zelfde regel als voor ``.vsa``/``.mvsa``: elk woord moet in de lettergreeplijst
staan (``data/syllable_dictionary.nl.txt``). Staat een woord er niet in, of
wijken de lettergrepen af, dan stopt het opruimen zónder iets te schrijven en
beslist de gebruiker: voeg het woord toe aan de lijst, of kuis met
``--allow-unknown-words`` (dan blijft het woord zoals het is).

Woorden worden herbouwd uit de ``syllabic``-markeringen (begin/middle/end) van
MusicXML en MuseScore, ook als de lettergrepen zonder streepjes in de noten staan.
"""
from __future__ import annotations

import html
import re
import xml.etree.ElementTree as ET
from collections.abc import Iterable

ALLOW_UNKNOWN: bool = False

_EDGE = re.compile(r"^[^\w]+|[^\w]+$", re.U)
_VOWELS = re.compile(r"[aeiouyáéíóúàèëïöü]+", re.I)


def words_from_syllables(items: Iterable[tuple[str, str]]) -> list[tuple[str, bool]]:
    """(tekst, syllabic) in zangvolgorde -> [(woordkern met streepjes, uit_keten)].

    Een woord loopt door als de ``syllabic`` begin/middle is óf de tekst op ``-`` eindigt
    (MuseScore-streepje). ``uit_keten`` is False voor een heel woord in één token
    (nog niet gesplitst); alleen die worden door de scripts zelf gesplitst.
    """
    words: list[tuple[str, bool]] = []
    chain: list[str] = []

    def flush() -> None:
        if chain:
            words.append(("-".join(chain), len(chain) > 1))
            chain.clear()

    for text, syllabic in items:
        raw = (text or "").replace("\xa0", " ").strip()
        if not raw:
            continue
        kind = (syllabic or "single").strip().lower()
        dash = raw.endswith("-") and len(raw) > 1
        piece = _EDGE.sub("", raw)
        if " " in raw.strip():
            flush()
            for part in raw.split():
                core = _EDGE.sub("", part)
                if core:
                    words.append((core, "-" in core))
            continue
        if kind in ("begin", "middle", "end") or dash or chain:
            if not piece:
                continue
            if kind == "begin":
                flush()
            chain.append(piece)
            if kind == "end" or (not dash and kind != "begin" and kind != "middle"):
                flush()
            continue
        flush()
        if piece:
            words.append((piece, "-" in piece))
    flush()
    return words


def findings_for(items: Iterable[tuple[str, str]]) -> tuple[list[str], list[str]]:
    """(blokkerend, advies). Blokkerend: een heel woord dat het script zelf wil splitsen
    maar niet in de lijst staat. Advies: woorden uit lettergreep-ketens die niet kloppen.
    """
    from vsa.syllable_dict_check import (
        CODE_MISMATCH,
        CODE_UNKNOWN,
        find_dictionary_syllable_issues_from_cores,
    )

    seen: set[str] = set()
    blocking: list[str] = []
    advice: list[str] = []
    for core, from_chain in words_from_syllables(items):
        if core.casefold() in seen or len(_VOWELS.findall(core)) < 2:
            continue
        seen.add(core.casefold())
        for f in find_dictionary_syllable_issues_from_cores([core], lyrics_lang="auto"):
            if f.code == CODE_UNKNOWN:
                line = f"onbekend woord `{core}`: niet in de lettergreeplijst"
                (advice if from_chain else blocking).append(line)
            elif f.code == CODE_MISMATCH and from_chain:
                advice.append(
                    f"lettergrepen `{core}` wijken af van de lijst (verwacht `{f.expected}`)"
                )
            # MISMATCH bij een heel woord zonder streepjes: het script splitst het zelf.
    return blocking, advice


def require_known_words(items: Iterable[tuple[str, str]], *, source: str) -> None:
    """Stop (zonder te schrijven) bij heel-woord-tokens die niet in de lijst staan.

    Woorden die uit lettergreep-ketens zijn herbouwd worden alleen gemeld: de
    markeringen (begin/middle/end en streepjes) in Capella- en MuseScore-bestanden
    zijn niet altijd betrouwbaar, dus daar beslist de gebruiker op basis van het rapport.
    """
    blocking, advice = findings_for(items)
    if advice:
        shown = advice[:10]
        more = f"\n  - (en nog {len(advice) - 10} meer)" if len(advice) > 10 else ""
        report = "\n".join(f"  - {line}" for line in shown) + more
        print(
            f"  CONTROLE {source}: {len(advice)} woord(en) uit lettergrepen om na te kijken "
            f"(niet blokkerend):\n{report}",
            flush=True,
        )
    if not blocking:
        return
    report = "\n".join(f"  - {line}" for line in blocking)
    message = (
        f"{source}: {len(blocking)} woord(en) waarover jij moet beslissen:\n{report}\n"
        "Voeg het woord toe aan bibliotheek/data/syllable_dictionary.nl.txt "
        "(met de gewenste lettergrepen) en start opnieuw, of kuis zonder die woorden "
        "te wijzigen met --allow-unknown-words."
    )
    if ALLOW_UNKNOWN:
        print(f"  WAARSCHUWING (--allow-unknown-words): {message}", flush=True)
        return
    raise SystemExit(message)


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def musicxml_items(root: ET.Element) -> list[tuple[str, str]]:
    """Lyrics van het eerste deel, eerste stem met tekst, couplet 1."""
    part = next((c for c in root if _local(c.tag) == "part"), None)
    if part is None:
        return []
    voice: str | None = None
    items: list[tuple[str, str]] = []
    for note in part.iter():
        if _local(note.tag) != "note":
            continue
        kids = {_local(k.tag): k for k in note}
        if "chord" in kids or "rest" in kids:
            continue
        lyric = next((k for k in note if _local(k.tag) == "lyric"), None)
        if lyric is None:
            continue
        v = (kids["voice"].text or "") if "voice" in kids else ""
        if voice is None:
            voice = v
        if v != voice:
            continue
        text = next((k.text for k in lyric if _local(k.tag) == "text"), "") or ""
        syl = next((k.text for k in lyric if _local(k.tag) == "syllabic"), "") or "single"
        items.append((text, syl))
    return items


def mscx_items(mscx: str) -> list[tuple[str, str]]:
    """Lyrics van de eerste notenbalk, eerste stem, eerste couplet."""
    from mscz_content_cleanup import (
        CHORD_REST_RE,
        MEASURE_RE,
        VOICE_RE,
        _chord_lyric_plain,
        _chord_syllabic,
    )

    staff = re.search(r'<Staff id="\d+">(.*?)</Staff>', mscx, re.S)
    if staff is None:
        return []
    items: list[tuple[str, str]] = []
    for meas in MEASURE_RE.finditer(staff.group(1)):
        voice = VOICE_RE.search(meas.group(0))
        if voice is None:
            continue
        for ev in CHORD_REST_RE.finditer(voice.group(0)):
            if ev.group(1) != "Chord":
                continue
            text = html.unescape(_chord_lyric_plain(ev.group(0)))
            if text:
                items.append((text, _chord_syllabic(ev.group(0))))
    return items
