"""Probe of Coria gepubliceerde MusicXML-canaries kan ophalen.

Coria ``play_from_url`` haalt server-side op. Wij meten dat door Coria's
HTML te lezen (``failed to retrieve file`` vs partijkeuze), niet door alleen
GitHub 200 te checken.

Steekproef: minstens één fingerprint per bronsoort (``.mscz.mxl``,
``.mvsa.mxl``, ``.vsa.mxl``) die op **beide** kandidaten al publiek is.
Een host is alleen ``ok`` als Coria **alle** samples vanaf die host
slikt — zo vangen we raw×MSCZ-falen die een enkele MVSA-canary mist.

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
    DATA_FILE,
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

# Steekproef alleen productstraten (niet legacy/other): MSCZ eerst
# (bekend raw×MSCZ-falen), daarna mvsa/vsa.
KIND_ORDER = ("mscz", "mvsa", "vsa")
SAMPLES_PER_KIND = 1
# MSCZ: meer samples (Untitled/raw-risico); mvsa/vsa blijven zuinig.
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
    return f"{URL_PREFIX}/{files[0].name}"


def published_on_all_hosts(rel: str, bases: dict[str, str]) -> bool:
    return all(
        _http_head_ok(f"{base.rstrip('/')}/{rel}") for base in bases.values()
    )


def select_sample_canaries(
    mapping: dict[str, str],
    *,
    published: set[str] | None = None,
    per_kind: int = SAMPLES_PER_KIND,
) -> list[str]:
    """Stabiele steekproef: tot ``per_kind`` unieke paden per bronsoort.

    ``published``: relatieve ``mxl/c/…``-paden die op alle hosts staan.
    Zonder ``published``: alle mapping-waarden (alleen voor unit tests).
    """
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
    """Steekproef: per bronsoort HEAD tot limiet op alle hosts publiek is.

    Geen HEAD over de hele catalogus — alleen tot de steekproef vol is.
    Bij MSCZ: voorkeur voor lokaal «Untitled» / zonder identification (raw-risico),
    en tot ``MSCZ_SAMPLES`` stuks (andere soorten: ``per_kind``).
    """
    # Kandidaten per kind: (sort_key, fp_key, rel)
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
                checked[rel] = published_on_all_hosts(rel, bases)
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
    host_names: tuple[str, ...] = ("raw", "pages"),
) -> dict[str, str]:
    """Host ``ok`` als alle samples lukken, behalve universeel kapotte samples.

    Een sample dat op **alle** hosts faalt (inhoud/Coria-vertaling) telt niet
    mee voor de hostkeuze — anders maakt één slecht fingerprint beide hosts
    ten onrechte ``fail``.
    """
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
    """Zonder netwerk: raw primair, pages als alternate (historische default)."""
    bases = candidate_bases(branch)
    return {
        "base": bases["raw"],
        "alternate": bases["pages"],
        "probed_at": None,
        "canary": None,
        "canaries": [],
        "results": {"raw": "skipped", "pages": "skipped"},
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

    samples: list[str]
    if canary:
        samples = [canary.lstrip("/")]
    else:
        mapping = load_fp_mapping()
        print(
            "Coria-probe: zoek gepubliceerde steekproef "
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
            "Coria-probe: geen gepubliceerde steekproef op raw én pages "
            "(nieuwe hashes nog niet op gh-pages?). "
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

    # Voorkeur als beide ok: pages (juiste MusicXML Content-Type).
    order = ("pages", "raw")
    winner = next((n for n in order if results.get(n) == "ok"), None)
    probed_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if winner is None:
        cfg = {
            "base": bases["pages"],
            "alternate": bases["raw"],
            "probed_at": probed_at,
            "canary": samples[0],
            "canaries": samples,
            "results": results,
            "sample_results": sample_results,
        }
        write_config(cfg)
        print(
            "Coria-probe FAILED: geen host slikte alle samples "
            f"({samples}). ♪ krijgt pages als base + raw als alternate.",
            flush=True,
        )
        return 0 if warn_only else 1

    alternate_name = "raw" if winner == "pages" else "pages"
    cfg = {
        "base": bases[winner],
        "alternate": bases[alternate_name],
        "probed_at": probed_at,
        "canary": samples[0],
        "canaries": samples,
        "results": results,
        "sample_results": sample_results,
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
        description=(
            "Meet of Coria raw/pages-MusicXML kan ophalen "
            "(steekproef mscz/mvsa/vsa); schrijf coria-public-base.json."
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
        per_kind=max(1, args.per_kind),
    )


if __name__ == "__main__":
    raise SystemExit(main())
