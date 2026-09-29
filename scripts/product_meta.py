"""Provenance-stamps in afgeleide producten (consumer-beleid).

VSA-Coria-``.vsa.mxl``: ``vsa-source-sha256`` + ``vsa-source-kind=vsa``.
Basispartituur-PDF/MXL: ``vsa-partituur-sha256`` (+ legacy ``vsa-hub-sha256``).
Import-``.mscz.mvsa``: comment-regels ``# vsa-partituur-sha256: …``.
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
FIELD_PARTITUUR_SHA = "vsa-partituur-sha256"
FIELD_PARTITUUR_SHA_LEGACY = "vsa-hub-sha256"
FIELD_GENERATED_AT = "vsa-generated-at"
FIELD_GENERATOR = "vsa-generator"
GENERATOR_VSA = "vsa-musicxml"
GENERATOR_MSCZ = "mscz-products"
GENERATOR_TEKSTBLAD = "tekstblad-products"
GENERATOR_IMPORT_MVSA = "import-mvsa"
SOURCE_KIND_VSA = "vsa"
SOURCE_KIND_PARTITUUR = "partituur"
SOURCE_KIND_TEKSTBLAD = "tekstblad"
_MVSA_STAMP_LINE = re.compile(
    r"^#\s*(vsa-(?:partituur-sha256|hub-sha256|source-sha256|source-kind|"
    r"generated-at|generator))\s*:\s*(.+?)\s*$"
)
_MVSA_STAMP_KEYS = frozenset(
    {
        FIELD_PARTITUUR_SHA,
        FIELD_PARTITUUR_SHA_LEGACY,
        FIELD_SOURCE_SHA,
        FIELD_SOURCE_KIND,
        FIELD_GENERATED_AT,
        FIELD_GENERATOR,
    }
)
PDF_KEY_PARTITUUR = "/VSAPartituurSHA256"
PDF_KEY_PARTITUUR_LEGACY = "/VSAHubSHA256"
PDF_KEY_SOURCE_SHA = "/VSASourceSHA256"
PDF_KEY_SOURCE_KIND = "/VSASourceKind"
PDF_KEY_GENERATED = "/VSAGeneratedAt"
PDF_KEY_GENERATOR = "/VSAGenerator"


def source_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def partituur_sha256(mscz: Path) -> str:
    return hashlib.sha256(mscz.read_bytes()).hexdigest()


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def stamp_sha_from_dict(stamp: dict[str, str]) -> str:
    """Lees partituur-hash uit stamp-dict (nieuw of legacy veld)."""
    return (
        stamp.get(FIELD_PARTITUUR_SHA, "")
        or stamp.get(FIELD_PARTITUUR_SHA_LEGACY, "")
        or ""
    )


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


def stamp_mxl_partituur(
    root: ET.Element,
    *,
    partituur_hash: str,
    generated_at: str,
    generator: str = GENERATOR_MSCZ,
) -> None:
    """Stamp basispartituur-Coria-``.mxl`` (partituur-sha + source-kind)."""
    stamp_mxl_source(
        root,
        source_hash=partituur_hash,
        source_kind=SOURCE_KIND_PARTITUUR,
        generated_at=generated_at,
        generator=generator,
    )
    ident = _ensure_identification(root)
    _set_misc_field(ident, FIELD_PARTITUUR_SHA, partituur_hash)
    _set_misc_field(ident, FIELD_PARTITUUR_SHA_LEGACY, partituur_hash)


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


def stamp_pdf(
    path: Path,
    *,
    generated_at: str,
    partituur_hash: str | None = None,
    source_hash: str | None = None,
    source_kind: str | None = None,
    generator: str = GENERATOR_MSCZ,
) -> None:
    if not partituur_hash and not source_hash:
        raise ValueError("partituur_hash of source_hash verplicht")
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError as exc:
        raise RuntimeError(
            "pypdf ontbreekt; installeer met: python -m pip install pypdf"
        ) from exc

    reader = PdfReader(str(path))
    writer = PdfWriter()
    writer.append(reader)
    meta: dict[str, str] = {
        PDF_KEY_GENERATED: generated_at,
        PDF_KEY_GENERATOR: generator,
    }
    if partituur_hash:
        meta[PDF_KEY_PARTITUUR] = partituur_hash
        meta[PDF_KEY_PARTITUUR_LEGACY] = partituur_hash
    if source_hash:
        meta[PDF_KEY_SOURCE_SHA] = source_hash
        if source_kind:
            meta[PDF_KEY_SOURCE_KIND] = source_kind
    writer.add_metadata(meta)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("wb") as fh:
        writer.write(fh)
    tmp.replace(path)


def read_pdf_stamp(path: Path) -> dict[str, str]:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError(
            "pypdf ontbreekt; installeer met: python -m pip install pypdf"
        ) from exc
    try:
        reader = PdfReader(str(path))
    except Exception:  # noqa: BLE001
        return {}
    meta = reader.metadata
    if meta is None:
        return {}
    raw = {str(k): str(v) for k, v in dict(meta).items() if v is not None}
    out: dict[str, str] = {}
    mapping = {
        PDF_KEY_PARTITUUR: FIELD_PARTITUUR_SHA,
        "VSAPartituurSHA256": FIELD_PARTITUUR_SHA,
        PDF_KEY_PARTITUUR_LEGACY: FIELD_PARTITUUR_SHA_LEGACY,
        "VSAHubSHA256": FIELD_PARTITUUR_SHA_LEGACY,
        PDF_KEY_SOURCE_SHA: FIELD_SOURCE_SHA,
        "VSASourceSHA256": FIELD_SOURCE_SHA,
        PDF_KEY_SOURCE_KIND: FIELD_SOURCE_KIND,
        "VSASourceKind": FIELD_SOURCE_KIND,
        PDF_KEY_GENERATED: FIELD_GENERATED_AT,
        "VSAGeneratedAt": FIELD_GENERATED_AT,
        PDF_KEY_GENERATOR: FIELD_GENERATOR,
        "VSAGenerator": FIELD_GENERATOR,
    }
    for key, field in mapping.items():
        if key in raw and raw[key].strip():
            out[field] = raw[key].strip()
    return out


def _strip_mvsa_stamp_lines(text: str) -> str:
    lines = text.splitlines(keepends=True)
    kept: list[str] = []
    for line in lines:
        bare = line.rstrip("\r\n")
        if _MVSA_STAMP_LINE.match(bare):
            continue
        kept.append(line)
    return "".join(kept)


def stamp_mvsa_partituur(
    path: Path,
    *,
    partituur_hash: str,
    generated_at: str,
    generator: str = GENERATOR_IMPORT_MVSA,
) -> None:
    """Schrijf herkomstcommentaren bovenaan een import-``.mvsa``."""
    raw = path.read_text(encoding="utf-8")
    body = _strip_mvsa_stamp_lines(raw).lstrip("\n")
    block = "\n".join(
        [
            f"# {FIELD_PARTITUUR_SHA}: {partituur_hash}",
            f"# {FIELD_SOURCE_KIND}: {SOURCE_KIND_PARTITUUR}",
            f"# {FIELD_GENERATED_AT}: {generated_at}",
            f"# {FIELD_GENERATOR}: {generator}",
            "",
        ]
    )
    if body.startswith("---"):
        # Frontmatter eerst; stamps direct daarna.
        end = body.find("\n---", 3)
        if end >= 0:
            close = end + len("\n---")
            if close < len(body) and body[close] == "\n":
                close += 1
            path.write_text(
                body[:close] + block + body[close:].lstrip("\n"),
                encoding="utf-8",
                newline="\n",
            )
            return
    path.write_text(block + body, encoding="utf-8", newline="\n")


def read_mvsa_stamp(path: Path) -> dict[str, str]:
    """Lees ``# vsa-…:``-stamps uit een ``.mvsa`` (of andere tekst)."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return {}
    out: dict[str, str] = {}
    for line in text.splitlines():
        m = _MVSA_STAMP_LINE.match(line)
        if not m:
            continue
        key, value = m.group(1), m.group(2).strip()
        if key in _MVSA_STAMP_KEYS and value:
            out[key] = value
    return out
