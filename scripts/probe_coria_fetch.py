"""Probe of Coria MusicXML vanaf github.io kan ophalen.

Coria ``play_from_url`` haalt server-side op. ``raw.githubusercontent.com``
gebruiken we **niet**: GitHub behandelt zulke serverfetches als scraping;
mislukte URL's cachet Coria permanent (geen retry). Canonieke fetch-host:
``orthodox-ronl.github.io/bibliotheek/`` (+ branch-subdir).

Steekproef: fingerprints per bronsoort (``.mscz.mxl``, ``.mvsa.mxl``,
``.vsa.mxl``) die al op github.io staan. Host ``ok`` alleen als Coria alle
relevante samples slikte. Schrijft ``data/coria-public-base.json``
(``base`` = pages; ``alternate`` leeg).
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
    DATA_FILE,
    DEST_ROOT,
    PUBLIC_BASE_FILE,
    URL_PREFIX,
    detect_git_branch,
    github_pages_base_url,
)

CORIA_PLAY = "https://coria.nl/play_from_url"
TIMEOUT_S = 20
USER_AGENT = "orthodox-ronl-bibliotheek-coria-probe/1.0"

KIND_ORDER = ("mscz", "mvsa", "vsa")
SAMPLES_PER_KIND = 1
MSCZ_SAMPLES = 5

FAIL_MARKERS = (
    "failed to retrieve file",
    "fout: failed to retrieve",
)
OK_MARKERS = (
    "kies de partij",
    "kies de partij die je wilt oefenen",
    'value="P1"',
    'name="Soprano"',
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


def source_kind(fp_key: str) -> str:
    """Bronsoort uit coria-fp-sleutel (``…foo.mscz.mxl`` → ``mscz``)."""
    k = (fp_key or "").lower().replace("\\", "/")
    if k.endswith(".mscz.mxl") or ".mscz.mxl" in k:
        return "mscz"
    if k.endswith(".mvsa.mxl") or ".mvsa.mxl" in k:
        return "mvsa"
    if k.endswith(".vsa.mxl") or ".vsa.mxl" in k:
        return "vsa"
    return "other"


def load_fp_mapping(path: Path | None = None) -> dict[str, str]:
    p = path or DATA_FILE
    if not p.is_file():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(data, dict):
        return {}
    return {str(k): str(v).strip() for k, v in data.items() if v}


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
    """Alleen github.io (Coria-fetch). Geen raw.githubusercontent.com."""
    return {"pages": github_pages_base_url(branch)}


def pick_canary(*, dest_root: Path = DEST_ROOT) -> str | None:
    """Relatief pad ``mxl/c/<hash>.musicxml`` of None."""
    if not dest_root.is_dir():
        return None
    files = sorted(dest_root.glob("*.musicxml"))
    if not files:
        return None
    return f"{URL_PREFIX}/{files[0].name}"


def published_on_host(rel: str, base: str) -> bool:
    return _http_head_ok(f"{base.rstrip('/')}/{rel}")


def select_sample_canaries(
    mapping: dict[str, str],
    *,
    published: set[str] | None = None,
    per_kind: int = SAMPLES_PER_KIND,
) -> list[str]:
    """Stabiele steekproef: tot ``per_kind`` unieke paden per bronsoort."""
    by_kind: dict[str, list[str]] = {k: [] for k in KIND_ORDER}
    seen: set[str] = set()
    for key in sorted(mapping):
        rel = mapping[key].lstrip("/")
        if not rel.startswith(f"{URL_PREFIX}/"):
            continue
        if published is not None and rel not in published:
            continue
        if rel in seen:
            continue
        kind = source_kind(key)
        bucket = by_kind.setdefault(kind, [])
        if len(bucket) >= per_kind:
            continue
        bucket.append(rel)
        seen.add(rel)

    out: list[str] = []
    for kind in KIND_ORDER:
        out.extend(by_kind.get(kind, []))
    return out


def _local_mscz_risk(rel: str, *, dest_root: Path = DEST_ROOT) -> int:
    """Lager = eerder in steekproef (Untitled / geen identification)."""
    path = dest_root / Path(rel).name
    if not path.is_file():
        return 1
    try:
        head = path.read_bytes()[:800]
    except OSError:
        return 1
    risky = b"Untitled score" in head or b"<identification" not in head
    return 0 if risky else 1


def kind_sample_limit(kind: str, per_kind: int) -> int:
    if kind == "mscz":
        return max(per_kind, MSCZ_SAMPLES)
    return per_kind


def find_published_samples(
    bases: dict[str, str],
    mapping: dict[str, str],
    *,
    per_kind: int = SAMPLES_PER_KIND,
    dest_root: Path = DEST_ROOT,
) -> list[str]:
    """Steekproef: per bronsoort HEAD tot limiet op github.io publiek is."""
    pages = bases.get("pages") or next(iter(bases.values()))
    buckets: dict[str, list[tuple[tuple, str, str]]] = {k: [] for k in KIND_ORDER}
    for key in mapping:
        kind = source_kind(key)
        if kind not in buckets:
            continue
        rel = mapping[key].lstrip("/")
        if not rel.startswith(f"{URL_PREFIX}/"):
            continue
        risk = _local_mscz_risk(rel, dest_root=dest_root) if kind == "mscz" else 1
        buckets[kind].append(((risk, key), key, rel))

    for kind in buckets:
        buckets[kind].sort(key=lambda t: t[0])

    chosen: dict[str, list[str]] = {k: [] for k in KIND_ORDER}
    seen_rel: set[str] = set()
    checked: dict[str, bool] = {}

    for kind in KIND_ORDER:
        limit = kind_sample_limit(kind, per_kind)
        for _sort, _key, rel in buckets[kind]:
            if len(chosen[kind]) >= limit:
                break
            if rel in seen_rel:
                continue
            if rel not in checked:
                checked[rel] = published_on_host(rel, pages)
            if not checked[rel]:
                continue
            chosen[kind].append(rel)
            seen_rel.add(rel)

    out: list[str] = []
    for kind in KIND_ORDER:
        out.extend(chosen.get(kind, []))
    return out


def host_ok_from_sample_results(sample_statuses: list[str]) -> bool:
    """Host ok alleen als er samples zijn en allemaal ``ok``."""
    if not sample_statuses:
        return False
    return all(s == "ok" for s in sample_statuses)


def score_hosts(
    sample_results: dict[str, dict[str, str]],
    samples: list[str],
    host_names: tuple[str, ...] = ("pages",),
) -> dict[str, str]:
    """Host ``ok`` als alle (relevante) samples lukken.

    Bij meerdere hosts: sample dat overal faalt telt niet mee (inhoudsfout).
    Bij één host (pages): alle samples tellen.
    """
    if len(host_names) <= 1:
        relevant = list(samples)
    else:
        relevant = [
            rel
            for rel in samples
            if any(sample_results.get(h, {}).get(rel) == "ok" for h in host_names)
        ]
    out: dict[str, str] = {}
    for host in host_names:
        statuses = [
            sample_results.get(host, {}).get(rel, "fail") for rel in relevant
        ]
        out[host] = "ok" if host_ok_from_sample_results(statuses) else "fail"
    return out


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
    """Zonder netwerk: github.io als base; geen raw-alternate."""
    bases = candidate_bases(branch)
    return {
        "base": bases["pages"],
        "alternate": "",
        "probed_at": None,
        "canary": None,
        "canaries": [],
        "results": {"pages": "skipped"},
        "sample_results": {},
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
    per_kind: int = SAMPLES_PER_KIND,
) -> int:
    """Schrijf coria-public-base.json. Exit 1 als pages faalt (tenzij warn_only)."""
    br = branch or detect_git_branch()
    bases = candidate_bases(br)
    if skip_network:
        cfg = provisional_config(br)
        write_config(cfg)
        print(
            "Coria-probe overgeslagen (--skip-network); "
            f"base={cfg['base']}",
            flush=True,
        )
        return 0

    samples: list[str]
    if canary:
        samples = [canary.lstrip("/")]
    else:
        mapping = load_fp_mapping()
        print(
            "Coria-probe: zoek gepubliceerde steekproef op github.io "
            f"(mscz/mvsa/vsa, {per_kind} per soort)…",
            flush=True,
        )
        try:
            samples = find_published_samples(
                bases, mapping, per_kind=per_kind
            )
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            print(f"Coria-probe: sample-zoekfout ({exc}); provisional.", flush=True)
            cfg = provisional_config(br)
            write_config(cfg)
            return 0

    if not samples:
        local = pick_canary()
        cfg = provisional_config(br)
        cfg["canary"] = local
        cfg["canaries"] = [local] if local else []
        write_config(cfg)
        print(
            "Coria-probe: geen gepubliceerde steekproef op github.io "
            "(nieuwe hashes nog niet gedeployed?). "
            f"Provisional base={cfg['base']}",
            flush=True,
        )
        return 0

    print(f"Coria-probe samples ({len(samples)}): {', '.join(samples)}", flush=True)
    sample_results: dict[str, dict[str, str]] = {}

    for name, base in bases.items():
        per_sample: dict[str, str] = {}
        for rel in samples:
            file_url = f"{base.rstrip('/')}/{rel}"
            status = probe_coria_for_file(file_url)
            normalized = "ok" if status == "ok" else "fail"
            per_sample[rel] = normalized
            print(
                f"  {name} {rel}: {status} → {normalized}",
                flush=True,
            )
        sample_results[name] = per_sample

    results = score_hosts(sample_results, samples, tuple(bases.keys()))
    for name, verdict in results.items():
        print(f"  {name} host: {verdict}", flush=True)

    probed_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    pages_ok = results.get("pages") == "ok"
    cfg = {
        "base": bases["pages"],
        "alternate": "",
        "probed_at": probed_at,
        "canary": samples[0],
        "canaries": samples,
        "results": results,
        "sample_results": sample_results,
    }
    write_config(cfg)

    if not pages_ok:
        print(
            "Coria-probe FAILED: github.io slikte niet alle samples "
            f"({samples}). ♪ blijft op pages-base; zie sample_results.",
            flush=True,
        )
        return 0 if warn_only else 1

    print(f"Coria-probe OK: base=pages ({cfg['base']})", flush=True)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Meet of Coria github.io-MusicXML kan ophalen "
            "(steekproef mscz/mvsa/vsa); schrijf coria-public-base.json. "
            "Gebruikt geen raw.githubusercontent.com."
        ),
    )
    parser.add_argument(
        "--branch",
        default=None,
        help="Git-branch voor subdir (default: detecteer).",
    )
    parser.add_argument(
        "--canary",
        default=None,
        help="Eén relatief pad mxl/c/<hash>.musicxml (overschrijft steekproef).",
    )
    parser.add_argument(
        "--per-kind",
        type=int,
        default=SAMPLES_PER_KIND,
        help=f"Samples per bronsoort (default {SAMPLES_PER_KIND}).",
    )
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="Exit 0 ook als github.io-probe faalt.",
    )
    parser.add_argument(
        "--skip-network",
        action="store_true",
        help="Geen HTTP; schrijf provisional pages-base.",
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
        per_kind=max(1, args.per_kind),
    )


if __name__ == "__main__":
    raise SystemExit(main())
