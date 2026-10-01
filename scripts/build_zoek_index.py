"""Bouw ``static/zoek/index.json`` voor client-side bibliotheekzoeken.

Leest ``*.lyrics.txt`` (fallback: live ``vsa.text_export``), frontmatter van
bladermap-pagina's, en ``data/zoek-synoniemen.yaml``.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

from sync_lyrics_products import (
    DEFAULT_ROOT,
    collect_lyric_sources,
    lyrics_body,
    product_path_for_source,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = REPO_ROOT / "static" / "zoek" / "index.json"
SYNONYM_PATH = REPO_ROOT / "data" / "zoek-synoniemen.yaml"
_PUNCT_RE = re.compile(r"[^\w\s]+", re.UNICODE)
_SPACE_RE = re.compile(r"\s+")


def _fm(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return {}
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    block = text[3:end]
    out: dict[str, str] = {}
    for line in block.splitlines():
        if ":" not in line or line.strip().startswith("#"):
            continue
        key, _, val = line.partition(":")
        out[key.strip().lower()] = val.strip().strip("\"'")
    return out


def _load_synonyms() -> dict[str, str]:
    if not SYNONYM_PATH.is_file():
        return {}
    raw = SYNONYM_PATH.read_text(encoding="utf-8")
    data: dict = {}
    if yaml is not None:
        loaded = yaml.safe_load(raw) or {}
        if isinstance(loaded, dict):
            data = loaded
    else:
        # Minimale fallback zonder PyYAML: "key: value" regels.
        for line in raw.splitlines():
            s = line.strip()
            if not s or s.startswith("#") or ":" not in s:
                continue
            k, _, v = s.partition(":")
            data[k.strip()] = v.strip()
    mapping: dict[str, str] = {}
    for key, val in data.items():
        if key is None or val is None:
            continue
        canon = str(val).strip().lower()
        mapping[str(key).strip().lower()] = canon
        mapping[canon] = canon
    return mapping


def normalize_text(text: str, synonyms: dict[str, str]) -> str:
    lowered = text.casefold()
    stripped = _PUNCT_RE.sub(" ", lowered)
    parts: list[str] = []
    for token in _SPACE_RE.split(stripped.strip()):
        if not token:
            continue
        parts.append(synonyms.get(token, token))
    return " ".join(parts)


def token_sort_key(normalized: str) -> str:
    toks = sorted(set(normalized.split()))
    return " ".join(toks)


def _bibliotheek_id(source: Path) -> str | None:
    try:
        rel = source.resolve().relative_to(
            (REPO_ROOT / "content-source" / "catalogus").resolve()
        )
    except ValueError:
        return None
    parts = rel.parts
    if len(parts) < 3:
        return None
    return "/".join(parts[:3])


def _plain_for_source(source: Path) -> str:
    lyrics = product_path_for_source(source)
    if lyrics.is_file():
        body = lyrics_body(lyrics)
        if body:
            return body
    try:
        from vsa.text_export import plain_text_from_path
    except ImportError:
        return ""
    try:
        return plain_text_from_path(source)
    except Exception:  # noqa: BLE001
        return ""


def build_entries(root: Path) -> list[dict]:
    synonyms = _load_synonyms()
    by_id: dict[str, dict] = {}
    for source in collect_lyric_sources(root):
        ident = _bibliotheek_id(source)
        if not ident:
            continue
        zangstuk, variant, uitvoeringsvorm = ident.split("/")
        leaf = (
            REPO_ROOT
            / "content-source"
            / "catalogus"
            / zangstuk
            / variant
            / uitvoeringsvorm
            / "index.md"
        )
        var_idx = (
            REPO_ROOT
            / "content-source"
            / "catalogus"
            / zangstuk
            / variant
            / "_index.md"
        )
        zs_idx = REPO_ROOT / "content-source" / "catalogus" / zangstuk / "_index.md"
        leaf_fm = _fm(leaf)
        var_fm = _fm(var_idx)
        zs_fm = _fm(zs_idx)
        plain = _plain_for_source(source)
        title = leaf_fm.get("title") or var_fm.get("title") or ident
        link = leaf_fm.get("linktitle") or leaf_fm.get("title") or uitvoeringsvorm
        norm = normalize_text(
            " ".join(
                [
                    title,
                    link,
                    zs_fm.get("title", ""),
                    var_fm.get("title", ""),
                    ident.replace("/", " ").replace("-", " "),
                    plain,
                ]
            ),
            synonyms,
        )
        entry = {
            "id": ident,
            "url": f"/catalogus/{ident}/",
            "title": title,
            "linkTitle": link,
            "zangstukTitle": zs_fm.get("title") or zangstuk,
            "variantTitle": var_fm.get("title") or variant,
            "status": leaf_fm.get("publicatiestatus") or "",
            "text": norm,
            "tokens": token_sort_key(norm),
            "incipit": " ".join(plain.split()[:12]),
        }
        prev = by_id.get(ident)
        if prev is None or len(entry["text"]) > len(prev["text"]):
            by_id[ident] = entry
    return [by_id[k] for k in sorted(by_id)]


def main() -> int:
    parser = argparse.ArgumentParser(description="Bouw static/zoek/index.json")
    parser.add_argument(
        "root",
        nargs="?",
        type=Path,
        default=DEFAULT_ROOT,
    )
    args = parser.parse_args()
    root = args.root if args.root.is_absolute() else REPO_ROOT / args.root
    synonyms = _load_synonyms()
    entries = build_entries(root)
    payload = {
        "generated_at": datetime.now(timezone.utc)
            .replace(microsecond=0)
            .isoformat(),
        "count": len(entries),
        # Client-side zoeken past dezelfde map toe op de zoekterm (en titel/id).
        "synonyms": synonyms,
        "entries": entries,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"zoek-index: {len(entries)} uitvoeringsvorm(en) -> {OUT_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
