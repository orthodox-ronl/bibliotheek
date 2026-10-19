"""Coria-postprocess voor bestaande MusicXML/.mxl (eenstemmig VSA-pad).

Gegroeid uit VSA-demo ``export_mscz_coria_mxl.process_existing_mxl``:
alleen laden, Coria-sanitize, playback-accidentals, terugschrijven.
Geen MuseScore-/SATB-export — dat blijft buiten deze module.
"""

from __future__ import annotations

import io
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

_MXL_CONTAINER = """\
<?xml version="1.0" encoding="UTF-8"?>
<container>
  <rootfiles>
    <rootfile full-path="score.xml"/>
  </rootfiles>
</container>
"""

# notehead: Coria play_from_url → translation failed bij o.a. notehead=none
_NOTE_MARKUP = frozenset({"beam", "stem", "notations", "accidental", "notehead"})
_LAYOUT_ATTR_PREFIXES = ("default-", "relative-")
_LAYOUT_ATTRS = frozenset({"width", "print-object", "color"})
# Spiegel VSA-tooling M20: Coria faalt op lyric vóór staff / accidental vóór dot.
_NOTE_CHILD_ORDER = (
    "grace",
    "cue",
    "chord",
    "pitch",
    "rest",
    "unpitched",
    "duration",
    "tie",
    "instrument",
    "voice",
    "type",
    "dot",
    "accidental",
    "time-modification",
    "stem",
    "notehead",
    "staff",
    "beam",
    "notations",
    "lyric",
    "play",
)
_NOTE_CHILD_MULTI = frozenset({"dot", "beam", "notations", "lyric", "tie"})
_STEPS = "CDEFGAB"
_SHARP_ORDER = "FCGDAEB"
_FLAT_ORDER = "BEADGCF"
_ALTER_TO_ACCIDENTAL = {
    -2: "double-flat",
    -1: "flat",
    0: "natural",
    1: "sharp",
    2: "double-sharp",
}


def local(tag: str) -> str:
    return tag.split("}")[-1] if "}" in tag else tag


def child(el: ET.Element, name: str) -> ET.Element | None:
    for c in el:
        if local(c.tag) == name:
            return c
    return None


def children(el: ET.Element, name: str) -> list[ET.Element]:
    return [c for c in el if local(c.tag) == name]


def text(el: ET.Element | None) -> str:
    return (el.text or "").strip() if el is not None else ""


def require_no_spaces(path: Path) -> None:
    if " " in path.name:
        raise SystemExit(f"bestandsnaam mag geen spaties hebben: {path.name}")


def parse_score_xml(raw: bytes) -> ET.Element:
    raw = re.sub(rb"<!DOCTYPE[\s\S]*?>", b"", raw, count=1, flags=re.I)
    return ET.fromstring(raw)


def load_score_xml(path: Path) -> ET.Element:
    if path.suffix.lower() == ".mxl":
        with zipfile.ZipFile(path) as z:
            names = [
                n
                for n in z.namelist()
                if n.endswith((".xml", ".musicxml")) and not n.startswith("META")
            ]
            if not names:
                raise ValueError(f"geen MusicXML in {path}")
            raw = z.read(names[0])
    else:
        raw = path.read_bytes()
    return parse_score_xml(raw)


def write_mxl(path: Path, root: ET.Element) -> None:
    # Altijd: geen identification/source in Coria-MXL (ook na latere stamps).
    strip_identification_source(root)
    # Stamp zet vaak miscellaneous vóór encoding; Coria eist encoding eerst.
    from product_meta import ensure_encoding_before_miscellaneous

    ident = child(root, "identification")
    if ident is not None:
        ensure_encoding_before_miscellaneous(ident)
    ET.indent(root, space="  ")
    body = ET.tostring(root, encoding="unicode")
    xml_text = '<?xml version="1.0" encoding="UTF-8"?>\n' + body
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("META-INF/container.xml", _MXL_CONTAINER)
        z.writestr("score.xml", xml_text.encode("utf-8"))
    path.write_bytes(buf.getvalue())


def music_parts(root: ET.Element) -> list[ET.Element]:
    return [c for c in root if local(c.tag) == "part"]


def _misc_bron(ident: ET.Element) -> ET.Element | None:
    misc = child(ident, "miscellaneous")
    if misc is None:
        return None
    for field in children(misc, "miscellaneous-field"):
        if field.get("name") == "bron":
            return field
    return None


def strip_identification_source(root: ET.Element) -> int:
    """Verwijder ``identification/source`` (Coria: source+encoding → translation failed).

    Bewaar de tekst in ``miscellaneous-field name="bron"`` als die nog leeg is.
    """
    ident = child(root, "identification")
    if ident is None:
        return 0
    source_el = child(ident, "source")
    if source_el is None:
        return 0
    src_text = text(source_el)
    if src_text and not text(_misc_bron(ident)):
        misc = child(ident, "miscellaneous")
        if misc is None:
            misc = ET.SubElement(ident, "miscellaneous")
        field = ET.SubElement(misc, "miscellaneous-field", name="bron")
        field.text = src_text
    ident.remove(source_el)
    return 1


def canonicalize_note_children(note: ET.Element) -> bool:
    """Herschik ``<note>``-kinderen (M20 / Coria). Returns True bij wijziging."""
    kids = list(note)
    if not kids:
        return False
    buckets: dict[str, list[ET.Element]] = {tag: [] for tag in _NOTE_CHILD_ORDER}
    unknown: list[ET.Element] = []
    for item in kids:
        tag = local(item.tag)
        if tag in buckets:
            if tag in _NOTE_CHILD_MULTI or not buckets[tag]:
                buckets[tag].append(item)
            else:
                unknown.append(item)
        else:
            unknown.append(item)
    new: list[ET.Element] = []
    for tag in _NOTE_CHILD_ORDER:
        new.extend(buckets[tag])
    new.extend(unknown)
    old_tags = tuple(local(c.tag) for c in kids)
    new_tags = tuple(local(c.tag) for c in new)
    if old_tags == new_tags:
        return False
    for item in kids:
        note.remove(item)
    for item in new:
        note.append(item)
    return True


def canonicalize_all_notes(root: ET.Element) -> int:
    n = 0
    for el in root.iter():
        if local(el.tag) == "note" and canonicalize_note_children(el):
            n += 1
    return n


def sanitize_coria_importer(root: ET.Element) -> None:
    """Strip visuele MusicXML die Coria's vertaler laat crashen."""
    root.set("version", "3.1")
    for el in list(root):
        if local(el.tag) == "movement-title":
            root.remove(el)
    ident = child(root, "identification")
    if ident is not None:
        enc = child(ident, "encoding")
        if enc is not None:
            for el in list(enc):
                if local(el.tag) == "supports":
                    enc.remove(el)
        strip_identification_source(root)
    for el in list(root.iter()):
        for attr in list(el.attrib):
            if attr.startswith(_LAYOUT_ATTR_PREFIXES) or attr in _LAYOUT_ATTRS:
                del el.attrib[attr]
        if local(el.tag) != "note":
            continue
        for child_el in list(el):
            ctag = local(child_el.tag)
            if ctag in _NOTE_MARKUP or ctag == "tie":
                el.remove(child_el)
                continue
            if ctag != "lyric":
                continue
            for grand in list(child_el):
                if local(grand.tag) == "extend":
                    child_el.remove(grand)
        canonicalize_note_children(el)
    plist = child(root, "part-list")
    if plist is not None:
        for el in list(plist):
            if local(el.tag) == "part-group":
                plist.remove(el)


def key_alters(fifths: int) -> dict[str, int]:
    alters = {step: 0 for step in _STEPS}
    if fifths > 0:
        for step in _SHARP_ORDER[:fifths]:
            alters[step] = 1
    elif fifths < 0:
        for step in _FLAT_ORDER[:-fifths]:
            alters[step] = -1
    return alters


def note_sounding_alter(note: ET.Element) -> int | None:
    pitch = child(note, "pitch")
    if pitch is None:
        return None
    alter_el = child(pitch, "alter")
    if alter_el is None or not text(alter_el):
        return 0
    try:
        return int(float(text(alter_el)))
    except ValueError:
        return None


def _insert_accidental(note: ET.Element, name: str) -> None:
    """Insert ``<accidental>`` na ``<dot>``s (of na ``<type>``) — nooit ertussen."""
    acc = ET.Element("accidental")
    acc.text = name
    kids = list(note)
    last_dot: ET.Element | None = None
    type_el: ET.Element | None = None
    for item in kids:
        tag = local(item.tag)
        if tag == "dot":
            last_dot = item
        elif tag == "type":
            type_el = item
        elif tag == "accidental":
            note.remove(item)
    kids = list(note)
    if last_dot is not None:
        note.insert(kids.index(last_dot) + 1, acc)
    elif type_el is not None:
        note.insert(kids.index(type_el) + 1, acc)
    else:
        note.append(acc)


def apply_playback_accidentals(root: ET.Element) -> int:
    """Zet <accidental> waar de klinkende toon afwijkt van voortekening/maat."""
    n = 0
    for part in music_parts(root):
        fifths = 0
        for measure in children(part, "measure"):
            attrs = child(measure, "attributes")
            if attrs is not None:
                key = child(attrs, "key")
                if key is not None:
                    raw = text(child(key, "fifths"))
                    if raw.lstrip("-").isdigit():
                        fifths = int(raw)
            implied_key = key_alters(fifths)
            state: dict[tuple[str, str], int] = {}
            for note in children(measure, "note"):
                sounding = note_sounding_alter(note)
                pitch = child(note, "pitch")
                if sounding is None or pitch is None:
                    continue
                step = text(child(pitch, "step"))
                octave = text(child(pitch, "octave"))
                if step not in implied_key:
                    continue
                current = state.get((step, octave), implied_key[step])
                if sounding == current:
                    continue
                name = _ALTER_TO_ACCIDENTAL.get(sounding)
                if name is None:
                    continue
                _insert_accidental(note, name)
                state[(step, octave)] = sounding
                n += 1
    canonicalize_all_notes(root)
    return n


def process_existing_mxl(path: Path) -> None:
    require_no_spaces(path)
    root = load_score_xml(path)
    sanitize_coria_importer(root)
    apply_playback_accidentals(root)
    write_mxl(path, root)
