"""Bouw ``data/check-fixlist.json`` uit product-/pdf-status-JSON’s.

Alleen items met ``ok: false`` en een niet-lege ``fix_cmd``. Aangeroepen
aan het eind van het product-checkblok in ``check.cmd``, en door
``fix --check``.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA = REPO_ROOT / "data"
FIXLIST_PATH = DATA / "check-fixlist.json"

# (checker-id, relatief pad onder data/, container-key of None voor list-root)
STATUS_SOURCES: tuple[tuple[str, str, str | None], ...] = (
    ("vsa", "vsa-product-status.json", "folders"),
    ("mscz", "mscz-product-status.json", "folders"),
    ("tekstblad", "tekstblad-product-status.json", "folders"),
    ("import", "import-mvsa-status.json", "pairs"),
    ("mvsa", "mvsa-product-status.json", "folders"),
    ("audio", "audio-product-status.json", "folders"),
    ("lyrics", "lyrics-product-status.json", None),
    ("pdf", "pdf-status.json", "folders"),
    ("mxl-contract", "mxl-playback-contract-status.json", "files"),
)


@dataclass(frozen=True)
class FixItem:
    id: str
    checker: str
    summary: str
    fix_cmd: str
    kind: str = ""
    file: str = ""
    source: str = ""


def _issue_bits(entry: dict) -> tuple[str, str, str]:
    issues = entry.get("issues") or []
    if isinstance(issues, list) and issues:
        first = issues[0] if isinstance(issues[0], dict) else {}
        kind = str(first.get("kind") or "")
        file = str(first.get("file") or "")
        detail = str(first.get("detail") or "")
        return kind, file, detail
    return "", "", ""


def _rel_content_source(path_str: str) -> str:
    """Pad t.o.v. content-source (posix), anders genormaliseerd pad."""
    text = (path_str or "").replace("\\", "/").strip()
    while text.startswith("./"):
        text = text[2:]
    prefix = "content-source/"
    if text.startswith(prefix):
        return text[len(prefix) :]
    return text


def _summary(key: str, entry: dict, *, kind: str, file: str, detail: str) -> str:
    """Korte regel: ``[soort] pad-t.o.v.-content-source``."""
    source = str(entry.get("source") or entry.get("mvsa") or key)
    path = file or source or key
    rel = _rel_content_source(path)
    label = kind or "probleem"
    return f"[{label}] {rel}"


def _item_from_entry(checker: str, key: str, entry: dict) -> FixItem | None:
    if not isinstance(entry, dict):
        return None
    if entry.get("ok", True):
        return None
    fix_cmd = str(entry.get("fix_cmd") or "").strip()
    if not fix_cmd:
        return None
    kind, file, detail = _issue_bits(entry)
    source = str(entry.get("source") or entry.get("mvsa") or key)
    item_id = f"{checker}:{key}"
    return FixItem(
        id=item_id,
        checker=checker,
        summary=_summary(key, entry, kind=kind, file=file, detail=detail),
        fix_cmd=fix_cmd,
        kind=kind,
        file=file,
        source=source,
    )


def collect_items(data_dir: Path = DATA) -> list[FixItem]:
    """Lees bekende status-JSON’s; retourneer fixbare problemen."""
    items: list[FixItem] = []
    seen: set[str] = set()

    for checker, rel, container in STATUS_SOURCES:
        path = data_dir / rel
        if not path.is_file():
            continue
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue

        entries: list[tuple[str, dict]] = []
        if container is None:
            if isinstance(raw, list):
                for i, entry in enumerate(raw):
                    if not isinstance(entry, dict):
                        continue
                    key = str(entry.get("dir") or entry.get("source") or i)
                    entries.append((key, entry))
        elif isinstance(raw, dict):
            block = raw.get(container)
            if isinstance(block, dict):
                for key, entry in block.items():
                    if isinstance(entry, dict):
                        entries.append((str(key), entry))

        for key, entry in entries:
            item = _item_from_entry(checker, key, entry)
            if item is None or item.id in seen:
                continue
            seen.add(item.id)
            items.append(item)

    items.sort(key=lambda x: (x.checker, x.id))
    return items


def write_fixlist(
    items: list[FixItem] | None = None,
    *,
    path: Path = FIXLIST_PATH,
    data_dir: Path = DATA,
) -> list[FixItem]:
    """Schrijf fixlist; return de items."""
    if items is None:
        items = collect_items(data_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 1,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "items": [asdict(i) for i in items],
    }
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return items


def load_fixlist(path: Path = FIXLIST_PATH) -> list[FixItem]:
    if not path.is_file():
        return []
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(raw, dict):
        return []
    out: list[FixItem] = []
    for entry in raw.get("items") or []:
        if not isinstance(entry, dict):
            continue
        fix_cmd = str(entry.get("fix_cmd") or "").strip()
        item_id = str(entry.get("id") or "").strip()
        if not fix_cmd or not item_id:
            continue
        out.append(
            FixItem(
                id=item_id,
                checker=str(entry.get("checker") or ""),
                summary=str(entry.get("summary") or item_id),
                fix_cmd=fix_cmd,
                kind=str(entry.get("kind") or ""),
                file=str(entry.get("file") or ""),
                source=str(entry.get("source") or ""),
            )
        )
    return out


def save_fixlist(items: list[FixItem], *, path: Path = FIXLIST_PATH) -> None:
    write_fixlist(items, path=path)


def print_fixlist(items: list[FixItem], *, stream=None) -> None:
    stream = stream or sys.stdout
    if not items:
        print("Fixlist leeg (geen auto-fixbare problemen).", file=stream)
        return
    print(f"Fixlist: {len(items)} item(s)", file=stream)
    for i, item in enumerate(items, 1):
        print(f"{i}. {item.summary}", file=stream)
        print(f"   fix: {item.fix_cmd}", file=stream)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Schrijf data/check-fixlist.json uit status-JSON’s."
    )
    parser.add_argument(
        "--print",
        action="store_true",
        help="Print de lijst na schrijven.",
    )
    args = parser.parse_args(argv)
    items = write_fixlist()
    rel = FIXLIST_PATH.relative_to(REPO_ROOT).as_posix()
    print(f"Fixlist: {len(items)} item(s) → {rel}", flush=True)
    if args.print:
        print_fixlist(items)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
