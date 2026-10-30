"""Probe of Coria een gepubliceerde MusicXML-canary kan ophalen.

Coria ``play_from_url`` haalt server-side op. Wij meten dat door Coria's
HTML te lezen (``failed to retrieve file`` vs partijkeuze), niet door alleen
GitHub 200 te checken.

Kandidaten: raw.githubusercontent.com (gh-pages) en github.io — zelfde
branch-subdir als ``fingerprint_coria_mxl``. Winnaar → ``base``, andere →
``alternate`` in ``data/coria-public-base.json``.
"""

from __future__ import annotations

import argparse
import json
import os
import ssl
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from fingerprint_coria_mxl import (
    DEST_ROOT,
    PUBLIC_BASE_FILE,
    URL_PREFIX,
    coria_fetch_base_url,
    detect_git_branch,
    github_pages_base_url,
)

CORIA_PLAY = "https://coria.nl/play_from_url"
TIMEOUT_S = 20
USER_AGENT = "orthodox-ronl-bibliotheek-coria-probe/1.0"

FAIL_MARKERS = (
    "failed to retrieve file",
    "fout: failed to retrieve",
)
OK_MARKERS = (
    "kies de partij",
    "kies de partij die je wilt oefenen",
    'value="P1"',
    "name=\"Soprano\"",
    ">Soprano<",
)


def classify_coria_html(html: str) -> str:
    """Return ``ok``, ``fail`` of ``unknown`` op basis van Coria-HTML."""
    text = (html or "").lower()
    if any(m in text for m in FAIL_MARKERS):
        return "fail"
    if any(m in text for m in OK_MARKERS):
        return "ok"
    if "translation failed" in text:
        return "fail"
    return "unknown"


def coria_play_url(file_url: str) -> str:
    return (
        f"{CORIA_PLAY}?back=coria.nl&url="
        f"{urllib.parse.quote(file_url, safe='')}"
    )


def _http_get(url: str, *, timeout: float = TIMEOUT_S) -> tuple[int, str]:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "text/html,*/*"},
        method="GET",
    )
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
        body = resp.read().decode("utf-8", errors="replace")
        return int(resp.status), body


def _http_head_ok(url: str, *, timeout: float = TIMEOUT_S) -> bool:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT},
        method="HEAD",
    )
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return 200 <= int(resp.status) < 400
    except urllib.error.HTTPError as exc:
        # Sommige hosts weigeren HEAD; probeer korte GET.
        if exc.code in {403, 405}:
            try:
                code, _ = _http_get(url, timeout=timeout)
                return 200 <= code < 400
            except (urllib.error.URLError, TimeoutError, OSError):
                return False
        return False
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def candidate_bases(branch: str) -> dict[str, str]:
    """Naam → fetch-root (eindigend op /)."""
    return {
        "raw": coria_fetch_base_url(branch),
        "pages": github_pages_base_url(branch),
    }


def pick_canary(*, dest_root: Path = DEST_ROOT) -> str | None:
    """Relatief pad ``mxl/c/<hash>.musicxml`` of None."""
    if not dest_root.is_dir():
        return None
    files = sorted(dest_root.glob("*.musicxml"))
    if not files:
        return None
    # Stabiele keuze: kleinste bestandsnaam (hash), deterministisch.
    return f"{URL_PREFIX}/{files[0].name}"


def find_published_canary(
    bases: dict[str, str],
    *,
    dest_root: Path = DEST_ROOT,
) -> str | None:
    """Eerste lokale fingerprint die op minstens één host al publiek is."""
    if not dest_root.is_dir():
        return None
    for path in sorted(dest_root.glob("*.musicxml")):
        rel = f"{URL_PREFIX}/{path.name}"
        for base in bases.values():
            url = f"{base.rstrip('/')}/{rel}"
            if _http_head_ok(url):
                return rel
    return None


def probe_coria_for_file(file_url: str) -> str:
    """``ok`` / ``fail`` / ``unknown`` / ``error``."""
    play = coria_play_url(file_url)
    try:
        _code, html = _http_get(play)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        print(f"  Coria-probe netwerkfout voor {file_url}: {exc}", flush=True)
        return "error"
    result = classify_coria_html(html)
    if result == "unknown":
        snippet = " ".join(html.split())[:180]
        print(f"  Coria-probe onbekende HTML ({file_url}): {snippet!r}", flush=True)
    return result


def provisional_config(branch: str) -> dict:
    """Zonder netwerk: raw primair, pages als alternate (historische default)."""
    bases = candidate_bases(branch)
    return {
        "base": bases["raw"],
        "alternate": bases["pages"],
        "probed_at": None,
        "canary": None,
        "results": {"raw": "skipped", "pages": "skipped"},
    }


def write_config(cfg: dict) -> None:
    PUBLIC_BASE_FILE.parent.mkdir(parents=True, exist_ok=True)
    PUBLIC_BASE_FILE.write_text(
        json.dumps(cfg, indent=2) + "\n",
        encoding="utf-8",
    )


def apply_probe(
    *,
    branch: str | None = None,
    warn_only: bool = False,
    skip_network: bool = False,
    canary: str | None = None,
) -> int:
    """Schrijf coria-public-base.json. Exit 1 als beide hosts falen (tenzij warn_only)."""
    br = branch or detect_git_branch()
    bases = candidate_bases(br)
    if skip_network:
        cfg = provisional_config(br)
        write_config(cfg)
        print(
            "Coria-probe overgeslagen (--skip-network); "
            f"base={cfg['base']} alternate={cfg['alternate']}",
            flush=True,
        )
        return 0

    chosen = canary
    if not chosen:
        print("Coria-probe: zoek gepubliceerde canary…", flush=True)
        try:
            chosen = find_published_canary(bases)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            print(f"Coria-probe: canary-zoekfout ({exc}); provisional.", flush=True)
            cfg = provisional_config(br)
            write_config(cfg)
            return 0 if warn_only else 0

    if not chosen:
        local = pick_canary()
        cfg = provisional_config(br)
        cfg["canary"] = local
        write_config(cfg)
        print(
            "Coria-probe: geen gepubliceerde canary op raw/pages "
            "(nieuwe hashes nog niet op gh-pages?). "
            f"Provisional base={cfg['base']}",
            flush=True,
        )
        return 0

    results: dict[str, str] = {}
    print(f"Coria-probe canary={chosen}", flush=True)
    for name, base in bases.items():
        file_url = f"{base.rstrip('/')}/{chosen}"
        status = probe_coria_for_file(file_url)
        # unknown/error tellen als niet-ok voor hostkeuze
        results[name] = "ok" if status == "ok" else "fail"
        print(f"  {name}: {status} → {results[name]} ({file_url})", flush=True)

    # Voorkeur als beide ok: pages (juiste MusicXML Content-Type).
    order = ("pages", "raw")
    winner = next((n for n in order if results.get(n) == "ok"), None)

    if winner is None:
        cfg = {
            "base": bases["pages"],
            "alternate": bases["raw"],
            "probed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "canary": chosen,
            "results": results,
        }
        write_config(cfg)
        msg = (
            "Coria-probe FAILED: geen host kon de canary ophalen "
            f"(canary={chosen}). ♪ krijgt pages als base + raw als alternate."
        )
        print(msg, flush=True)
        return 0 if warn_only else 1

    alternate_name = "raw" if winner == "pages" else "pages"
    cfg = {
        "base": bases[winner],
        "alternate": bases[alternate_name],
        "probed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "canary": chosen,
        "results": results,
    }
    write_config(cfg)
    print(
        f"Coria-probe OK: base={winner} ({cfg['base']}) "
        f"alternate={alternate_name} ({cfg['alternate']})",
        flush=True,
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Meet of Coria raw/pages-MusicXML kan ophalen; schrijf coria-public-base.json.",
    )
    parser.add_argument(
        "--branch",
        default=None,
        help="Git-branch voor subdir (default: detecteer).",
    )
    parser.add_argument(
        "--canary",
        default=None,
        help="Relatief pad mxl/c/<hash>.musicxml (default: eerste gepubliceerde).",
    )
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="Exit 0 ook als beide hosts falen.",
    )
    parser.add_argument(
        "--skip-network",
        action="store_true",
        help="Geen HTTP; schrijf provisional raw+pages.",
    )
    args = parser.parse_args(argv)
    warn = args.warn_only or os.environ.get("CORIA_PROBE_WARN_ONLY", "").strip() in {
        "1",
        "true",
        "yes",
    }
    return apply_probe(
        branch=args.branch,
        warn_only=warn,
        skip_network=args.skip_network,
        canary=args.canary,
    )


if __name__ == "__main__":
    raise SystemExit(main())
