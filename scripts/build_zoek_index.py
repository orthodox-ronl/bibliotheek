"""Bouw ``static/zoek/index.json`` voor client-side bibliotheekzoeken.

Indexeert elke catalogus-uitvoeringsvorm (leaf ``index.md``) op titel, id en
status — ook mappen met ``artefacten_handmatig: true``. Gezongen tekst komt
uit ``*.lyrics.txt`` / live ``vsa.text_export`` wanneer er een ``.vsa``,
``.mvsa`` of basis-``.mscz`` is.
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
    lyrics_body,
    product_path_for_source,
)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from catalogus import (  # noqa: E402
    derived_leaf_link_title,
    derived_leaf_title,
    section_title,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
CATALOGUS_ROOT = REPO_ROOT / "content-source" / "catalogus"
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


def _catalogus_id_for_leaf_dir(leaf_dir: Path) -> str | None:
    try:
        rel = leaf_dir.resolve().relative_to(CATALOGUS_ROOT.resolve())
    except ValueError:
        return None
    parts = rel.parts
    if len(parts) != 3:
        return None
    return "/".join(parts)


def collect_leaf_index_mds(root: Path) -> list[Path]:
    """``index.md`` van uitvoeringsvormen onder ``root`` (diepte zangstuk/variant/uv)."""
    out: list[Path] = []
    if not root.is_dir():
        return out
    for path in sorted(root.rglob("index.md")):
        if not path.is_file():
            continue
        if "input" in path.parts:
            continue
        if _catalogus_id_for_leaf_dir(path.parent) is None:
            continue
        # artefacten_handmatig slaat auto-producten over, niet het zoeken:
        # die leaves horen wél in de index (titel/id; lyrics uit .vsa e.d.).
        out.append(path)
    return out


def _lyric_sources_in_dir(leaf_dir: Path) -> list[Path]:
    """``.vsa`` / canonieke ``.mvsa`` / basis-``.mscz`` in de bladermap."""
    from score_filenames import is_print_mscz

    out: list[Path] = []
    if not leaf_dir.is_dir():
        return out
    for path in sorted(leaf_dir.iterdir()):
        if not path.is_file():
            continue
        suf = path.suffix.lower()
        if suf not in {".vsa", ".mvsa", ".mscz"}:
            continue
        name = path.name.lower()
        if name.endswith(".syl.vsa"):
            continue
        if name.endswith(".mscz.mvsa"):
            continue
        if suf == ".mscz" and is_print_mscz(path):
            continue
        if " " in path.name:
            raise SystemExit(f"bestandsnaam mag geen spaties hebben: {path.name}")
        out.append(path)
    return out


def _plain_for_leaf(leaf_dir: Path) -> str:
    """Langste bruikbare gezongen tekst uit vsa/mvsa/mscz in de bladermap."""
    best = ""
    for source in _lyric_sources_in_dir(leaf_dir):
        plain = _plain_for_source(source)
        if len(plain) > len(best):
            best = plain
    return best


def _audio_rank(name: str) -> int:
    """Lagere rank = voorkeur (mvsa → mscz/partituur → vsa → overig)."""
    n = name.lower()
    if n.endswith(".mvsa.mp3"):
        return 0
    if n.endswith(".mscz.mp3"):
        return 1
    if n.endswith(".vsa.mp3"):
        return 2
    if n.endswith(".mp3"):
        return 3
    return 99


def preferred_audio_url(leaf_dir: Path, ident: str) -> str:
    """Site-absoluut pad naar voorkeurs-``.mp3`` in de bladermap, of leeg."""
    if not leaf_dir.is_dir():
        return ""
    mp3s = [p for p in leaf_dir.iterdir() if p.is_file() and p.suffix.lower() == ".mp3"]
    if not mp3s:
        return ""
    best = sorted(mp3s, key=lambda p: (_audio_rank(p.name), p.name.lower()))[0]
    return f"/catalogus/{ident}/{best.name}"


def _plain_for_source(source: Path) -> str:
    lyrics = product_path_for_source(source)
    if lyrics.is_file():
        body = lyrics_body(lyrics)
        if body:
            return body
    try:
        from sync_lyrics_products import _extract_plain
    except ImportError:
        _extract_plain = None  # type: ignore
    if _extract_plain is not None:
        try:
            return _extract_plain(source)
        except Exception:  # noqa: BLE001
            return ""
    try:
        from vsa.text_export import plain_text_from_path
    except ImportError:
        return ""
    try:
        return plain_text_from_path(source)
    except Exception:  # noqa: BLE001
        return ""


def _entry_for_leaf(leaf: Path, synonyms: dict[str, str]) -> dict | None:
    leaf_dir = leaf.parent
    ident = _catalogus_id_for_leaf_dir(leaf_dir)
    if not ident:
        return None
    zangstuk, variant, _uitvoeringsvorm = ident.split("/")
    leaf_fm = _fm(leaf)
    plain = _plain_for_leaf(leaf_dir)
    title = derived_leaf_title(ident, leaf_dir=leaf_dir)
    link = derived_leaf_link_title(ident)
    zs_title = section_title(zangstuk)
    var_title = section_title(variant)
    norm = normalize_text(
        " ".join(
            [
                title,
                link,
                zs_title,
                var_title,
                ident.replace("/", " ").replace("-", " "),
                plain,
            ]
        ),
        synonyms,
    )
    return {
        "id": ident,
        "url": f"/catalogus/{ident}/",
        "title": title,
        "linkTitle": link,
        "zangstukTitle": zs_title,
        "variantTitle": var_title,
        "status": leaf_fm.get("publicatiestatus") or "",
        "text": norm,
        "tokens": token_sort_key(norm),
        "incipit": " ".join(plain.split()[:12]),
        "audio": preferred_audio_url(leaf_dir, ident),
    }


def build_entries(root: Path) -> list[dict]:
    synonyms = _load_synonyms()
    by_id: dict[str, dict] = {}
    for leaf in collect_leaf_index_mds(root):
        entry = _entry_for_leaf(leaf, synonyms)
        if not entry:
            continue
        by_id[entry["id"]] = entry
    return [by_id[k] for k in sorted(by_id)]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Bouw static/zoek/index.json")
    parser.add_argument(
        "root",
        nargs="?",
        type=Path,
        default=DEFAULT_ROOT,
    )
    args = parser.parse_args(argv)
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
    print(
        f"zoek-index: {len(entries)} uitvoeringsvorm(en) -> "
        f"{OUT_PATH.relative_to(REPO_ROOT)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
