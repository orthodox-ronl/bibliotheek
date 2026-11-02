"""Controleer bibliotheek-``.vsa``/``.mvsa``/``.mscz`` vs sibling ``*.lyrics.txt``.

Schrijft ``data/lyrics-product-status.json``. Exit 1 bij problemen tenzij
``--warn-only`` (default zonder ``--fail``).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from fix_cmds import products_fix_cmd
from product_meta import (
    FIELD_GENERATED_AT,
    FIELD_SOURCE_KIND,
    FIELD_SOURCE_SHA,
    read_mvsa_stamp,
)
from sync_lyrics_products import (
    DEFAULT_ROOT,
    collect_lyric_sources,
    digest_for_source,
    product_path_for_source,
    source_kind_for,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
STATUS_PATH = REPO_ROOT / "data" / "lyrics-product-status.json"
FIX_PAGE = "/handleiding/start/zangstuk-soorten/"


@dataclass
class Issue:
    kind: str
    file: str
    detail: str


@dataclass
class FolderStatus:
    dir: str
    source: str
    ok: bool
    issues: list[Issue]
    fix_cmd: str


def _rel(path: Path) -> str:
    from input_paths import rel_for_log

    return rel_for_log(path, repo_root=REPO_ROOT)


def _bladermap_key(source: Path) -> str:
    from input_paths import rel_for_log

    return rel_for_log(source.parent, repo_root=REPO_ROOT)


def check_one(source: Path) -> FolderStatus:
    lyrics = product_path_for_source(source)
    issues: list[Issue] = []
    src_hash = digest_for_source(source)
    expect_kind = source_kind_for(source)
    fix = products_fix_cmd("lyrics", source)
    if not lyrics.is_file():
        issues.append(
            Issue(
                "missing_lyrics",
                _rel(lyrics),
                "lyrics.txt ontbreekt naast de bron (.vsa/.mvsa/.mscz)",
            )
        )
    else:
        stamp = read_mvsa_stamp(lyrics)
        kind = stamp.get(FIELD_SOURCE_KIND, "")
        got = stamp.get(FIELD_SOURCE_SHA, "")
        if not got:
            issues.append(
                Issue(
                    "unstamped_lyrics",
                    _rel(lyrics),
                    "lyrics.txt mist vsa-source-sha256 (opnieuw products --kinds lyrics)",
                )
            )
        elif kind and kind != expect_kind:
            issues.append(
                Issue(
                    "wrong_kind",
                    _rel(lyrics),
                    f"lyrics source-kind is {kind!r}, verwacht {expect_kind!r}",
                )
            )
        elif got != src_hash:
            when = stamp.get(FIELD_GENERATED_AT, "?")
            issues.append(
                Issue(
                    "stale_lyrics",
                    _rel(lyrics),
                    f"lyrics ouder dan bron (stamp {when})",
                )
            )
    return FolderStatus(
        dir=_bladermap_key(source),
        source=_rel(source),
        ok=not issues,
        issues=issues,
        fix_cmd=fix,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Controleer .lyrics.txt-siblings bij .vsa/.mvsa/.mscz."
    )
    parser.add_argument(
        "root",
        nargs="?",
        type=Path,
        default=DEFAULT_ROOT,
    )
    parser.add_argument(
        "--fail",
        action="store_true",
        help="Exit 1 bij ontbrekende/stale lyrics.",
    )
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="Nooit falen (overschrijft --fail).",
    )
    args = parser.parse_args()
    root = args.root if args.root.is_absolute() else REPO_ROOT / args.root

    fail = args.fail and not args.warn_only
    if not fail and os.environ.get("BIBLIOTHEEK_PRODUCTS_STRICT", "").strip() in {
        "1",
        "true",
        "yes",
    }:
        fail = True

    sources = collect_lyric_sources(root)
    statuses = [check_one(s) for s in sources]
    bad = [s for s in statuses if not s.ok]
    STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATUS_PATH.write_text(
        json.dumps([asdict(s) for s in statuses], indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    from check_report import print_check_findings

    if bad:
        print_check_findings(
            headline=(
                f"Lyrics: {len(statuses) - len(bad)} ok, {len(bad)} probleem "
                f"({STATUS_PATH.relative_to(REPO_ROOT).as_posix()})"
            ),
            what="Controle: of .lyrics.txt bij de notatiebron past",
            bad=bad,
            fix_page=FIX_PAGE,
            max_dirs=20,
        )
        if fail:
            return 1
        print("(waarschuwing — zonder --fail geen exit 1)", flush=True)
        return 0

    print(f"Lyrics: OK ({len(statuses)} bronnen)", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
