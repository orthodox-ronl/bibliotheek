"""MSCX inhoudsopkuis (geen A4-layout). Uit VSA-demo apply_mscz_layout gehaald."""
from __future__ import annotations

import re
from fractions import Fraction

from nl_hyphen import hyphenate_token, split_syllabic

MEASURE_RE = re.compile(r"<Measure\b.*?</Measure>", re.S)
VOICE_RE = re.compile(r"<voice>.*?</voice>", re.S)
CHORD_REST_RE = re.compile(r"<(Chord|Rest)\b.*?</\1>", re.S)
LYRICS_RE = re.compile(r"<Lyrics>.*?</Lyrics>", re.S)
TEXT_INNER_RE = re.compile(r"<text>(.*?)</text>", re.S)
_QUARTERS = {
    "long": Fraction(16),
    "breve": Fraction(8),
    "whole": Fraction(4),
    "half": Fraction(2),
    "quarter": Fraction(1),
    "eighth": Fraction(1, 2),
    "16th": Fraction(1, 4),
    "32nd": Fraction(1, 8),
    "64th": Fraction(1, 16),
}


def _plain(fragment: str) -> str:
    return re.sub(r"<[^>]+>", "", fragment).replace("&amp;", "&").strip()


def _xml_text(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _measure_staff(mscx: str, staff_id: str = "1") -> re.Match[str] | None:
    """Eerste `<Staff id>`-blok dat maten bevat (niet de Part-definitie)."""
    pat = re.compile(
        rf'<Staff id="{re.escape(staff_id)}">.*?</Staff>',
        re.S,
    )
    for m in pat.finditer(mscx):
        if "<Measure" in m.group(0):
            return m
    return None


def _staff_plain(block: str) -> str:
    xm = TEXT_INNER_RE.search(block)
    return _plain(xm.group(1)) if xm else ""


def _chord_lyric_plain(chord: str) -> str:
    ly = LYRICS_RE.search(chord)
    if ly is None:
        return ""
    t = TEXT_INNER_RE.search(ly.group(0))
    return _plain(t.group(1)) if t else ""


def _chord_syllabic(chord: str) -> str:
    ly = LYRICS_RE.search(chord)
    if ly is None:
        return "single"
    m = re.search(r"<syllabic>(.*?)</syllabic>", ly.group(0))
    return m.group(1).strip() if m else "single"


def _chord_midi(chord: str) -> str | None:
    m = re.search(r"<Note>.*?<pitch>(\d+)</pitch>", chord, re.S)
    return m.group(1) if m else None


def _chord_slur_starts(chord: str) -> bool:
    return bool(
        re.search(r'<Spanner type="Slur">(?:(?!</Spanner>).)*<next>', chord, re.S)
    )


def _frac_attr(fr: Fraction) -> str:
    return f"{fr.numerator}/{fr.denominator}"


def _event_quarters(block: str) -> Fraction:
    dt = re.search(r"<durationType>(.*?)</durationType>", block)
    if not dt:
        return Fraction(0)
    base = _QUARTERS.get(dt.group(1).strip())
    if base is None:
        return Fraction(0)
    dots_m = re.search(r"<dots>(\d+)</dots>", block)
    dots = int(dots_m.group(1)) if dots_m else 0
    add = base
    extra = Fraction(0)
    for _ in range(dots):
        add /= 2
        extra += add
    return base + extra


def _encode_duration(quarters: Fraction) -> tuple[str, int] | None:
    """(durationType, dots) of None als geen enkele MuseScore-duur past."""
    if quarters <= 0:
        return None
    for dots in (0, 1, 2):
        for name, base in _QUARTERS.items():
            total = base
            add = base
            for _ in range(dots):
                add /= 2
                total += add
            if total == quarters:
                return name, dots
    return None


def _set_event_duration(block: str, quarters: Fraction) -> str:
    enc = _encode_duration(quarters)
    if enc is None:
        raise ValueError(f"geen durationType voor {quarters} kwarten")
    name, dots = enc
    out = re.sub(
        r"<durationType>.*?</durationType>",
        f"<durationType>{name}</durationType>",
        block,
        count=1,
    )
    out = re.sub(r"\s*<dots>.*?</dots>", "", out)
    if dots:
        out = re.sub(
            r"(<durationType>.*?</durationType>)",
            rf"\1\n            <dots>{dots}</dots>",
            out,
            count=1,
        )
    return out


def _lyric_onset_times(voice: str) -> list[Fraction]:
    """Starttijden (in kwarten) van lettergreep-noten in een stem."""
    t = Fraction(0)
    onsets: list[Fraction] = []
    for ev in CHORD_REST_RE.finditer(voice):
        if ev.group(1) == "Chord" and _chord_lyric_plain(ev.group(0)):
            if not _in_tuplet(voice, ev.start()):
                onsets.append(t)
        t += _event_quarters(ev.group(0))
    return onsets


def _split_event_at_cuts(block: str, start: Fraction, end: Fraction, cuts: list[Fraction]) -> list[str]:
    points = [start, *cuts, end]
    pieces: list[str] = []
    for i, (a, b) in enumerate(zip(points, points[1:])):
        dur = b - a
        if dur <= 0:
            continue
        piece = block if i == 0 else _strip_eids(block)
        # Nooit feathered glyph vermenigvuldigen bij knippen
        piece = re.sub(r"\s*<headType>\w+</headType>", "", piece)
        piece = re.sub(r"\s*<noStem>[^<]*</noStem>", "", piece)
        piece = _set_event_duration(piece, dur)
        if i > 0:
            piece = LYRICS_RE.sub("", piece)
        pieces.append(piece)
    return pieces


def _split_voice_at_lyric_onsets(voice: str, onsets: list[Fraction]) -> tuple[str, int]:
    """Knip noten/rusten die over een lettergreep-inzet heen liggen."""
    if not onsets:
        return voice, 0
    onset_set = set(onsets)
    events = list(CHORD_REST_RE.finditer(voice))
    if not events:
        return voice, 0
    n_split = 0
    # Van achter naar voren, zodat indices geldig blijven.
    for ev in reversed(events):
        if _in_tuplet(voice, ev.start()):
            continue
        start = Fraction(0)
        for prev in events:
            if prev.start() >= ev.start():
                break
            start += _event_quarters(prev.group(0))
        dur = _event_quarters(ev.group(0))
        end = start + dur
        cuts = sorted(t for t in onset_set if start < t < end)
        if not cuts:
            continue
        try:
            pieces = _split_event_at_cuts(ev.group(0), start, end, cuts)
        except ValueError:
            continue
        if len(pieces) <= 1:
            continue
        voice = voice[: ev.start()] + "".join(pieces) + voice[ev.end() :]
        n_split += 1
    return voice, n_split


def _ensure_note_per_syllable(mscx: str) -> tuple[str, int]:
    """Elke partij: minstens een noot-inzet per lettergreep van de lead-stem.

    Lead = eerste stem van de bovenste muziekbalk (lyrics). Langere noten in
    andere stemmen die over zo'n inzet heen liggen, worden geknipt (zelfde
    toon; som van duren blijft gelijk). Idempotent.
    """
    staff_pat = re.compile(r'(<Staff id="\d+">)(.*?)(</Staff>)', re.S)
    staffs = [
        m
        for m in staff_pat.finditer(mscx)
        if MEASURE_RE.search(m.group(2))
    ]
    if not staffs:
        return mscx, 0

    inners = [list(MEASURE_RE.finditer(m.group(2))) for m in staffs]
    nmeas = min(len(x) for x in inners)
    total = 0

    new_inners: list[str] = []
    for si, sm in enumerate(staffs):
        body = sm.group(2)
        pieces: list[str] = []
        pos = 0
        for mi, mm in enumerate(inners[si]):
            pieces.append(body[pos : mm.start()])
            meas = mm.group(0)
            if mi < nmeas:
                lead = inners[0][mi].group(0)
                lead_voices = list(VOICE_RE.finditer(lead))
                onsets: list[Fraction] = []
                if lead_voices:
                    onsets = _lyric_onset_times(lead_voices[0].group(0))
                if onsets:
                    def fix_voice(vm: re.Match[str]) -> str:
                        nonlocal total
                        new_v, n = _split_voice_at_lyric_onsets(vm.group(0), onsets)
                        total += n
                        return new_v

                    meas = VOICE_RE.sub(fix_voice, meas)
            pieces.append(meas)
            pos = mm.end()
        pieces.append(body[pos:])
        new_inners.append("".join(pieces))

    out = mscx
    for sm, inner in zip(reversed(staffs), reversed(new_inners)):
        out = out[: sm.start()] + sm.group(1) + inner + sm.group(3) + out[sm.end() :]
    return out, total


def _in_tuplet(voice: str, pos: int) -> bool:
    before = voice[:pos]
    return before.count("<Tuplet>") > before.count("<endTuplet/>")


def _strip_eids(xml: str) -> str:
    return re.sub(r"\s*<eid>.*?</eid>", "", xml)


def _set_chord_lyric(chord: str, text: str, syllabic: str) -> str:
    ly_m = LYRICS_RE.search(chord)
    if ly_m is None:
        insert = (
            "            <Lyrics>\n"
            f"              <syllabic>{syllabic}</syllabic>\n"
            f"              <text>{_xml_text(text)}</text>\n"
            "              </Lyrics>\n"
        )
        return re.sub(r"<Note>", insert + "            <Note>", chord, count=1)
    block = ly_m.group(0)
    if "<syllabic>" in block:
        block = re.sub(
            r"<syllabic>.*?</syllabic>",
            f"<syllabic>{syllabic}</syllabic>",
            block,
            count=1,
        )
    else:
        block = block.replace(
            "<Lyrics>",
            f"<Lyrics>\n              <syllabic>{syllabic}</syllabic>",
            1,
        )
    block = re.sub(
        r"<text>.*?</text>",
        f"<text>{_xml_text(text)}</text>",
        block,
        count=1,
        flags=re.S,
    )
    return chord[: ly_m.start()] + block + chord[ly_m.end() :]


def _rewrite_measure_len(meas: str, wholes: Fraction) -> str:
    attr = _frac_attr(wholes)
    if re.match(r"<Measure\b[^>]*\blen=", meas):
        return re.sub(r'\blen="[^"]*"', f'len="{attr}"', meas, count=1)
    return re.sub(r"<Measure\b", f'<Measure len="{attr}"', meas, count=1)


def _split_voice_lyrics(
    voice: str,
    ops: list[tuple[int, list[str], str]],
    *,
    with_lyrics: bool,
) -> str:
    """Voeg kopie-akkoorden in; ops van achter naar voren (index blijft geldig)."""
    for idx, parts, orig_syll in reversed(ops):
        items = list(CHORD_REST_RE.finditer(voice))
        if idx >= len(items):
            continue
        hit = items[idx]
        if hit.group(1) != "Chord" or _in_tuplet(voice, hit.start()):
            continue
        src = hit.group(0)
        n = len(parts)
        first = src
        extras: list[str] = []
        if with_lyrics:
            first = _set_chord_lyric(
                src, parts[0], split_syllabic(orig_syll, 0, n)
            )
            for i in range(1, n):
                copy = _strip_eids(src)
                copy = _set_chord_lyric(
                    copy, parts[i], split_syllabic(orig_syll, i, n)
                )
                extras.append(copy)
        else:
            for _ in range(n - 1):
                extras.append(_strip_eids(src))
        voice = voice[: hit.start()] + first + "".join(extras) + voice[hit.end() :]
    return voice


def _split_undersplit_lyrics(mscx: str) -> tuple[str, int]:
    """Tokens met meerdere klinkergroepen -> extra noten (zelfde duur), SATB."""
    staff_pat = re.compile(r'(<Staff id="\d+">)(.*?)(</Staff>)', re.S)
    staffs = [
        m
        for m in staff_pat.finditer(mscx)
        if MEASURE_RE.search(m.group(2))
    ]
    if not staffs:
        return mscx, 0

    inners = [list(MEASURE_RE.finditer(m.group(2))) for m in staffs]
    nmeas = min(len(x) for x in inners)
    splits = 0

    new_inners: list[str] = []
    for si, sm in enumerate(staffs):
        body = sm.group(2)
        pieces: list[str] = []
        pos = 0
        for mi, mm in enumerate(inners[si]):
            pieces.append(body[pos : mm.start()])
            meas = mm.group(0)
            if mi < nmeas:
                lead = inners[0][mi].group(0)
                lead_voices = list(VOICE_RE.finditer(lead))
                ops: list[tuple[int, list[str], str]] = []
                if lead_voices:
                    v0 = lead_voices[0].group(0)
                    events = list(CHORD_REST_RE.finditer(v0))
                    for i, ev in enumerate(events):
                        if ev.group(1) != "Chord" or _in_tuplet(v0, ev.start()):
                            continue
                        chord = ev.group(0)
                        # Basispartituur ||O|| niet splitsen — recite-collaps beheert die tekst.
                        if "<headType>breve</headType>" in chord and (
                            "<noStem>1</noStem>" in chord or "<noStem>true</noStem>" in chord
                        ):
                            continue
                        raw = _chord_lyric_plain(chord)
                        if not raw:
                            continue
                        # Multi-woord recite-tekst niet via hyphenate_token uit elkaar trekken
                        if " " in raw.strip():
                            continue
                        parts = hyphenate_token(raw)
                        if len(parts) <= 1:
                            continue
                        ops.append((i, parts, _chord_syllabic(chord)))
                if ops:
                    vi = 0

                    def fix_voice(vm: re.Match[str]) -> str:
                        nonlocal vi
                        with_ly = si == 0 and vi == 0
                        vi += 1
                        return _split_voice_lyrics(
                            vm.group(0), ops, with_lyrics=with_ly
                        )

                    meas = VOICE_RE.sub(fix_voice, meas)
                    v1 = VOICE_RE.search(meas)
                    if v1 is not None:
                        q = sum(
                            _event_quarters(ev.group(0))
                            for ev in CHORD_REST_RE.finditer(v1.group(0))
                        )
                        if q > 0:
                            meas = _rewrite_measure_len(meas, q / 4)
                    if si == 0:
                        splits += len(ops)
            pieces.append(meas)
            pos = mm.end()
        pieces.append(body[pos:])
        new_inners.append("".join(pieces))

    out = mscx
    for sm, inner in zip(reversed(staffs), reversed(new_inners)):
        out = out[: sm.start()] + sm.group(1) + inner + sm.group(3) + out[sm.end() :]
    return out, splits


def _strip_empty_staves(mscx: str) -> tuple[str, int]:
    """Verwijder maat-balken zonder noten (Capella SAT+B -> SA/TB + lege 3e balk).

    Part-definities (`<Staff id>` zonder `<Measure>`) zijn geen lege balken:
    die mogen nooit de reden zijn om een id te droppen, anders verdwijnt de
    hele partituur (VOW e.d.).
    """
    score_pat = re.compile(r'<Staff id="(\d+)">.*?</Staff>', re.S)
    hits = list(score_pat.finditer(mscx))
    measure_hits = [m for m in hits if "<Measure" in m.group(0)]
    if len(measure_hits) < 2:
        return mscx, 0
    drop_ids: set[int] = set()
    keep: list[tuple[int, str]] = []
    for m in measure_hits:
        sid = int(m.group(1))
        block = m.group(0)
        empty = "<Chord" not in block and "<Note" not in block
        if empty:
            drop_ids.add(sid)
        else:
            keep.append((sid, block))
    if not drop_ids or not keep:
        return mscx, 0

    mapping = {old: i + 1 for i, (old, _) in enumerate(keep)}
    n_keep = len(keep)
    pieces: list[str] = []
    pos = 0
    for m in hits:
        pieces.append(mscx[pos : m.start()])
        sid = int(m.group(1))
        if sid not in drop_ids:
            block = m.group(0)
            new_id = mapping.get(sid, sid)
            if new_id != sid:
                block = re.sub(
                    rf'<Staff id="{sid}">',
                    f'<Staff id="{new_id}">',
                    block,
                    count=1,
                )
            pieces.append(block)
        pos = m.end()
    pieces.append(mscx[pos:])
    out = "".join(pieces)

    def fix_part(pm: re.Match[str]) -> str:
        head, inner, tail = pm.group(1), pm.group(2), pm.group(3)
        defs = list(re.finditer(r"<Staff>.*?</Staff>\s*", inner, re.S))
        if not defs:
            return pm.group(0)
        buf: list[str] = []
        p0 = 0
        for i, d in enumerate(defs):
            buf.append(inner[p0 : d.start()])
            if (i + 1) not in drop_ids:
                buf.append(d.group(0))
            p0 = d.end()
        buf.append(inner[p0:])
        inner = "".join(buf)
        inner = re.sub(
            r'(<bracket\b[^>]*\bspan=")(\d+)(")',
            lambda bm: f"{bm.group(1)}{n_keep}{bm.group(3)}",
            inner,
            count=1,
        )
        return head + inner + tail

    out = re.sub(
        r"(<Part(?:\s[^>]*)?>)(.*?)(</Part>)",
        fix_part,
        out,
        count=1,
        flags=re.S,
    )
    return out, len(drop_ids)


def content_cleanup_mscx(mscx: str) -> tuple[str, list[str]]:
    """Alleen inhoudelijke MSCX-fixes (geen A4-layout / copyright / reciteer-collaps).

    Gebruikt door opkuisen (diepte content) en als eerste stap van process_mscz.
    """
    notes: list[str] = []
    mscx, n_empty = _strip_empty_staves(mscx)
    mscx, n_split = _split_undersplit_lyrics(mscx)
    mscx, n_syll = _ensure_note_per_syllable(mscx)
    if n_empty:
        notes.append(f"lege notenbalken verwijderd: {n_empty}")
    if n_split:
        notes.append(f"lettergrepen gesplitst: {n_split}")
    if n_syll:
        notes.append(f"noten per lettergreep geknipt: {n_syll}")
    return mscx, notes


