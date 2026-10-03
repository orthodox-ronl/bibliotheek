"""Lees ``bron.uitgangspunt`` uit VSA/MVSA-frontmatter (bibliotheek-helper)."""

from __future__ import annotations

from pathlib import Path


def bron_uitgangspunt_from_text(text: str) -> str | None:
    try:
        from vsa.yaml_frontmatter import (
            bron_uitgangspunt_from_frontmatter,
            parse_vsa_frontmatter,
        )
    except ImportError:
        return _fallback_parse(text)
    fm, _ = parse_vsa_frontmatter(text)
    return bron_uitgangspunt_from_frontmatter(fm)


def _fallback_parse(text: str) -> str | None:
    """Minimale YAML-greep als vsa-tool ontbreekt."""
    if not text.startswith("---"):
        return None
    try:
        import yaml
    except ImportError:
        return None
    after = text[3:]
    close = after.find("\n---")
    if close < 0:
        return None
    data = yaml.safe_load(after[:close]) or {}
    if not isinstance(data, dict):
        return None
    bron = data.get("bron")
    if isinstance(bron, dict):
        val = bron.get("uitgangspunt")
        if val is not None and str(val).strip():
            return str(val).strip()
    return None


def bron_uitgangspunt_from_file(path: Path) -> str | None:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    return bron_uitgangspunt_from_text(text)


def bron_uitgangspunt_near(path: Path) -> str | None:
    """Uit dit bestand (als .vsa/.mvsa) of een sibling in dezelfde map."""
    suffix = path.suffix.lower()
    if suffix in {".vsa", ".mvsa"}:
        return bron_uitgangspunt_from_file(path)
    for pattern in ("*.vsa", "*.mvsa"):
        for cand in sorted(path.parent.glob(pattern)):
            if cand.name.lower().endswith(".syl.vsa"):
                continue
            val = bron_uitgangspunt_from_file(cand)
            if val:
                return val
    return None
