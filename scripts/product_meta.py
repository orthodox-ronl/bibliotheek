"""Provenance-stamps in afgeleide producten (consumer-beleid).

VSA-Coria-``.vsa.mxl``: ``vsa-source-sha256`` + ``vsa-source-kind=vsa``.
Basispartituur-PDF/MXL volgt later met ``vsa-partituur-sha256``.
"""

from __future__ import annotations

import hashlib
import re
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

FIELD_SOURCE_SHA = "vsa-source-sha256"
FIELD_SOURCE_KIND = "vsa-source-kind"
FIELD_GENERATED_AT = "vsa-generated-at"
FIELD_GENERATOR = "vsa-generator"
GENERATOR_VSA = "vsa-musicxml"
SOURCE_KIND_VSA = "vsa"


def source_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def _child(el: ET.Element, name: str) -> ET.Element | None:
    for c in el:
        if _local(c.tag) == name:
            return c
    return None


def _children(el: ET.Element, name: str) -> list[ET.Element]:
    return [c for c in el if _local(c.tag) == name]


def _ensure_identification(root: ET.Element) -> ET.Element:
    ident = _child(root, "identification")
    if ident is None:
        ident = ET.Element("identification")
        insert_at = 0
        for i, c in enumerate(list(root)):
            if _local(c.tag) in {"work", "movement-number", "movement-title"}:
                insert_at = i + 1
        root.insert(insert_at, ident)
    return ident


def _set_misc_field(ident: ET.Element, name: str, value: str) -> None:
    misc = _child(ident, "miscellaneous")
    if misc is None:
        misc = ET.SubElement(ident, "miscellaneous")
    for field in _children(misc, "miscellaneous-field"):
        if field.get("name") == name:
            field.text = value
            return
    field = ET.SubElement(misc, "miscellaneous-field", name=name)
    field.text = value


def stamp_mxl_source(
    root: ET.Element,
    *,
    source_hash: str,
    source_kind: str,
    generated_at: str,
    generator: str,
) -> None:
    ident = _ensure_identification(root)
    enc = _child(ident, "encoding")
    if enc is None:
        enc = ET.SubElement(ident, "encoding")
    date_el = _child(enc, "encoding-date")
    if date_el is None:
        date_el = ET.Element("encoding-date")
        enc.insert(0, date_el)
    date_el.text = generated_at[:10]
    sw = ET.Element("software")
    sw.text = f"{generator} {source_kind}={source_hash[:12]}"
    enc.append(sw)
    _set_misc_field(ident, FIELD_SOURCE_SHA, source_hash)
    _set_misc_field(ident, FIELD_SOURCE_KIND, source_kind)
    _set_misc_field(ident, FIELD_GENERATED_AT, generated_at)
    _set_misc_field(ident, FIELD_GENERATOR, generator)


def read_mxl_stamp(path: Path) -> dict[str, str]:
    """Lees stamp uit .mxl of .musicxml/.xml."""
    if path.suffix.lower() == ".mxl":
        with zipfile.ZipFile(path) as z:
            names = [
                n
                for n in z.namelist()
                if n.endswith((".xml", ".musicxml")) and not n.startswith("META")
            ]
            if not names:
                return {}
            raw = z.read(names[0])
    else:
        raw = path.read_bytes()
    raw = re.sub(rb"<!DOCTYPE[\s\S]*?>", b"", raw, count=1, flags=re.I)
    root = ET.fromstring(raw)
    ident = _child(root, "identification")
    if ident is None:
        return {}
    out: dict[str, str] = {}
    misc = _child(ident, "miscellaneous")
    if misc is not None:
        for field in _children(misc, "miscellaneous-field"):
            name = field.get("name") or ""
            if name and (field.text or "").strip():
                out[name] = (field.text or "").strip()
    return out
