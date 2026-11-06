"""Catalogus-id met optionele ``@sectie``-fragment.

Vorm: ``zangstuk/variant/uitvoeringsvorm`` of
``zangstuk/variant/uitvoeringsvorm@sectie-id``.
Alleen ``@sectie``-ids (MVSA); nooit ``@blok``.
"""

from __future__ import annotations

import re
from pathlib import Path

SECTIE_ID_RE = re.compile(r"^[a-z][a-z0-9_-]*$")
# Hugo shortcode: id="z/v/u@sectie" of id='…'
_ID_AT_SECTIE_RE = re.compile(
    r"""id\s*=\s*(?P<q>["'])(?P<ref>[^"'=]+@[a-z][a-z0-9_-]*)(?P=q)""",
    re.IGNORECASE,
)


def split_catalogus_ref(ref: str) -> tuple[str, str | None]:
    """Splits ``z/v/u`` of ``z/v/u@sectie`` → ``(uv_id, sectie|None)``.

    Raises ``ValueError`` bij ongeldige vorm.
    """
    raw = (ref or "").strip()
    if not raw:
        raise ValueError("leeg catalogus-id")
    if "@" not in raw:
        return raw, None
    left, at, right = raw.partition("@")
    if at != "@" or not left or not right:
        raise ValueError(f"ongeldig catalogus-id met @: {ref!r}")
    if "@" in right:
        raise ValueError(f"hoogstens één @sectie in id: {ref!r}")
    if not SECTIE_ID_RE.match(right):
        raise ValueError(
            f"ongeldige @sectie-id {right!r} in {ref!r} "
            "(verwacht [a-z][a-z0-9_-]*, geen @blok)"
        )
    parts = left.split("/")
    if len(parts) != 3 or not all(parts):
        raise ValueError(
            f"catalogus-id vóór @ moet zangstuk/variant/uitvoeringsvorm zijn: "
            f"{ref!r}"
        )
    return left, right


def product_svg_for_sectie(mvsa: Path, sectie: str) -> Path:
    """``lied.mvsa`` + sectie ``vrede`` → ``lied.mvsa@vrede.svg``."""
    return mvsa.with_name(f"{mvsa.name}@{sectie}.svg")


def product_from_ir_for_sectie(mvsa: Path, sectie: str) -> Path:
    """``lied.mvsa`` + sectie → ``lied.mvsa@vrede.from-ir.musicxml``."""
    return mvsa.with_name(f"{mvsa.name}@{sectie}.from-ir.musicxml")


def product_score_ir_for_sectie(mvsa: Path, sectie: str) -> Path:
    """``lied.mvsa`` + sectie → ``lied.mvsa@vrede.score-ir.json``."""
    return mvsa.with_name(f"{mvsa.name}@{sectie}.score-ir.json")


def collect_sectie_refs(content_root: Path) -> dict[str, set[str]]:
    """Zoek ``id=\"…@sectie\"`` in Markdown onder *content_root*.

    Returns: ``uv_id → set van sectie-ids``.
    """
    out: dict[str, set[str]] = {}
    if not content_root.is_dir():
        return out
    for path in content_root.rglob("*.md"):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        for m in _ID_AT_SECTIE_RE.finditer(text):
            ref = m.group("ref").strip()
            try:
                uv_id, sectie = split_catalogus_ref(ref)
            except ValueError:
                continue
            if sectie is None:
                continue
            out.setdefault(uv_id, set()).add(sectie)
    return out


def mvsa_in_uv_dir(leaf: Path) -> Path | None:
    """Eerste canonieke ``.mvsa`` in een uitvoeringsvorm-map (geen import)."""
    if not leaf.is_dir():
        return None
    mvsas = sorted(
        p
        for p in leaf.glob("*.mvsa")
        if not p.name.lower().endswith(".mscz.mvsa")
    )
    return mvsas[0] if mvsas else None
