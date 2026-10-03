#!/usr/bin/env python3
"""Stap 2: normaliseer VSA uit _stap1 en vergelijk met catalogus + onderlinge duplicaten.

- Metadata blijft behouden (stap1-frontmatter + stap2-status).
- Normalisatie is veilig: regeleinden, trailing spaties, lege regels.
- Geen inhoudelijke VSA-correcties.
"""

from __future__ import annotations

import hashlib
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAP1 = ROOT / "content-source" / "input" / "vsa-demo" / "_stap1"
STAP2 = ROOT / "content-source" / "input" / "vsa-demo" / "_stap2"
CATALOGUS = ROOT / "content-source" / "catalogus"

HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
FM_SPLIT = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n?", re.DOTALL)
SOFT_THRESHOLD = 0.88
SOFT_NEAR = 0.75


@dataclass
class VsaDoc:
    path: Path
    rel: str
    frontmatter: str
    body: str
    soort: str = ""
    norm_ws: str = ""
    norm_nocomment: str = ""
    lyrics: str = ""
    hash_nocomment: str = ""
    hash_lyrics: str = ""


@dataclass
class Match:
    status: str  # exact | soft | geen
    catalog_rel: str = ""
    score: float = 0.0
    notes: list[str] = field(default_factory=list)


def split_fm(text: str) -> tuple[str, str]:
    m = FM_SPLIT.match(text)
    if not m:
        return "", text
    return m.group(1).strip(), text[m.end() :]


def fm_get(fm: str, key: str) -> str:
    m = re.search(rf"(?m)^{re.escape(key)}:\s*(.*)$", fm)
    if not m:
        return ""
    v = m.group(1).strip()
    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
        v = v[1:-1]
    return v


def normalize_whitespace(body: str) -> str:
    lines = [ln.rstrip() for ln in body.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    out: list[str] = []
    blank = 0
    for ln in lines:
        if ln == "":
            blank += 1
            if blank <= 2:
                out.append("")
        else:
            blank = 0
            # interne runs van spaties in gewone tekst niet aanpassen binnen {...}
            out.append(ln)
    while out and out[0] == "":
        out.pop(0)
    while out and out[-1] == "":
        out.pop()
    return "\n".join(out) + ("\n" if out else "")


def strip_comments(body: str) -> str:
    return normalize_whitespace(HTML_COMMENT.sub("", body))


def plain_lyrics(body: str) -> str:
    t = HTML_COMMENT.sub(" ", body)
    t = re.sub(r"\[[^\]]*\]", " ", t)
    t = re.sub(r"\{([^}]*)\}", lambda m: re.sub(r"[^A-Za-zÀ-ÿ\u0400-\u04FF]", "", m.group(1)), t)
    t = re.sub(r"[*_/\\+&~.\-–,;:!?\"']+", " ", t)
    t = re.sub(r"\s+", " ", t).strip().lower()
    return t


def sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


def load_doc(path: Path, root: Path) -> VsaDoc:
    text = path.read_text(encoding="utf-8")
    fm, body = split_fm(text)
    body = body.lstrip("\n")
    norm_ws = normalize_whitespace(body)
    norm_nc = strip_comments(body)
    lyrics = plain_lyrics(body)
    return VsaDoc(
        path=path,
        rel=path.relative_to(root).as_posix() if path.is_relative_to(root) else path.name,
        frontmatter=fm,
        body=body,
        soort=fm_get(fm, "soort") or path.name.split("-")[0],
        norm_ws=norm_ws,
        norm_nocomment=norm_nc,
        lyrics=lyrics,
        hash_nocomment=sha(norm_nc),
        hash_lyrics=sha(lyrics) if lyrics else "",
    )


def yaml_escape(s: str) -> str:
    if re.search(r'[:#"\'\n{}[\],&*?|><=@!`]', s) or s != s.strip():
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'
    return s


def best_catalog_match(doc: VsaDoc, catalog: list[VsaDoc]) -> Match:
    # Exact op genormaliseerde notatie zonder commentaar
    for c in catalog:
        if c.hash_nocomment and c.hash_nocomment == doc.hash_nocomment and doc.norm_nocomment.strip():
            return Match("exact", c.rel, 1.0, ["zelfde notatie (whitespace/commentaar genormaliseerd)"])

    if not doc.lyrics or len(doc.lyrics) < 20:
        return Match("geen", notes=["te weinig tekst voor zachte vergelijking"])

    best: Match | None = None
    for c in catalog:
        if not c.lyrics or len(c.lyrics) < 20:
            continue
        # snelle filter: zelfde lyrics-hash
        if c.hash_lyrics == doc.hash_lyrics:
            score = 1.0
        else:
            score = SequenceMatcher(None, doc.lyrics, c.lyrics).ratio()
        if best is None or score > best.score:
            best = Match("soft" if score >= SOFT_THRESHOLD else "geen", c.rel, score)
    if best is None:
        return Match("geen")
    if best.score >= SOFT_THRESHOLD:
        best.status = "soft"
        best.notes = [f"tekstgelijkenis {best.score:.2f} (notatie kan verschillen)"]
        return best
    if best.score >= SOFT_NEAR:
        best.status = "geen"
        best.notes = [f"zwakke tekstgelijkenis {best.score:.2f} met `{best.catalog_rel}` — twijfel"]
        return best
    return Match("geen", notes=[f"beste treffer {best.score:.2f} met `{best.catalog_rel}`"])


def render_stap2(doc: VsaDoc, match: Match, dup_group: str, dup_peers: list[str]) -> str:
    lines = ["---"]
    # oorspronkelijke stap1-fm behouden, minus oude stap2-velden indien herdraaien
    skip_keys = {"extractie", "stap2_status", "stap2_catalogus", "stap2_score", "stap2_duplicaat_groep"}
    for raw in doc.frontmatter.splitlines():
        key = raw.split(":", 1)[0].strip()
        if key in skip_keys:
            continue
        lines.append(raw)
    lines.append("extractie: stap2")
    if match.status == "exact":
        status = "al-in-bieb"
    elif match.status == "soft":
        status = "mogelijke-variant"
    elif any("twijfel" in n for n in match.notes):
        status = "twijfel"
    else:
        status = "nieuw"
    lines.append(f"stap2_status: {status}")
    if match.catalog_rel:
        lines.append(f"stap2_catalogus: {yaml_escape(match.catalog_rel)}")
    if match.score:
        lines.append(f"stap2_score: {match.score:.3f}")
    if dup_group:
        lines.append(f"stap2_duplicaat_groep: {yaml_escape(dup_group)}")
    if dup_peers:
        lines.append("stap2_duplicaten:")
        for p in dup_peers:
            lines.append(f"  - {yaml_escape(p)}")
    if match.notes:
        lines.append("stap2_notities:")
        for n in match.notes:
            lines.append(f"  - {yaml_escape(n)}")
    lines.append("---")
    lines.append("")
    lines.append(doc.norm_ws.rstrip())
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    if not STAP1.is_dir():
        print(f"Geen _stap1: {STAP1}", file=sys.stderr)
        return 1

    stap1_docs = [load_doc(p, STAP1) for p in sorted(STAP1.glob("*.vsa"))]
    catalog_docs = [load_doc(p, CATALOGUS) for p in sorted(CATALOGUS.rglob("*.vsa"))]

    # Onderlinge duplicaten op norm_nocomment
    by_hash: dict[str, list[VsaDoc]] = defaultdict(list)
    for d in stap1_docs:
        if d.norm_nocomment.strip():
            by_hash[d.hash_nocomment].append(d)

    dup_groups: dict[str, list[VsaDoc]] = {
        h: docs for h, docs in by_hash.items() if len(docs) > 1
    }
    # stabiele groep-id
    group_id_by_hash = {h: f"dup-{i:03d}" for i, h in enumerate(sorted(dup_groups), 1)}

    STAP2.mkdir(parents=True, exist_ok=True)
    for old in STAP2.glob("*.vsa"):
        old.unlink()
    if (STAP2 / "VERGELIJKING.md").exists():
        (STAP2 / "VERGELIJKING.md").unlink()

    results: list[tuple[VsaDoc, Match, str, list[str]]] = []
    counts = {"al-in-bieb": 0, "mogelijke-variant": 0, "twijfel": 0, "nieuw": 0}

    for d in stap1_docs:
        match = best_catalog_match(d, catalog_docs)
        gid = ""
        peers: list[str] = []
        if d.hash_nocomment in group_id_by_hash:
            gid = group_id_by_hash[d.hash_nocomment]
            peers = sorted(x.path.name for x in dup_groups[d.hash_nocomment] if x.path != d.path)
        rendered = render_stap2(d, match, gid, peers)
        out = STAP2 / d.path.name
        out.write_text(rendered, encoding="utf-8", newline="\n")

        if match.status == "exact":
            status = "al-in-bieb"
        elif match.status == "soft":
            status = "mogelijke-variant"
        elif any("twijfel" in n for n in match.notes):
            status = "twijfel"
        else:
            status = "nieuw"
        counts[status] += 1
        results.append((d, match, status, peers))

    # Rapport
    lines = [
        "# Stap 2 - vergelijking met catalogus",
        "",
        f"Bron: `{STAP1.relative_to(ROOT).as_posix()}`",
        f"Doel: `{STAP2.relative_to(ROOT).as_posix()}`",
        f"Catalogus-VSA: {len(catalog_docs)}",
        f"Stap1-VSA: {len(stap1_docs)}",
        "",
        "## Samenvatting",
        "",
        f"- **al in bieb** (notatie gelijk na normalisatie): {counts['al-in-bieb']}",
        f"- **mogelijke variant** (tekst ~gelijk, notatie anders): {counts['mogelijke-variant']}",
        f"- **twijfel** (zwakke tekstgelijkenis): {counts['twijfel']}",
        f"- **nieuw** (geen bruikbare treffer): {counts['nieuw']}",
        f"- **duplicaatgroepen** binnen stap1: {len(dup_groups)}",
        "",
        "Normalisatie: LF, trailing spaties weg, max. 2 lege regels; "
        "vergelijking zonder HTML-commentaar. Geen ELM-/tekstcorrecties.",
        "",
    ]

    def section(title: str, status: str) -> None:
        lines.append(f"## {title}")
        lines.append("")
        rows = [(d, m, s, p) for d, m, s, p in results if s == status]
        if not rows:
            lines.append("(geen)")
            lines.append("")
            return
        for d, m, s, peers in sorted(rows, key=lambda x: x[0].path.name):
            cat = f" -> `{m.catalog_rel}`" if m.catalog_rel else ""
            score = f" ({m.score:.2f})" if m.score and s != "al-in-bieb" else ""
            dup = f"; duplicaat van {len(peers)} ander(e)" if peers else ""
            lines.append(f"- `{d.path.name}`{cat}{score}{dup}")
        lines.append("")

    section("Al in bibliotheek", "al-in-bieb")
    section("Mogelijke variant", "mogelijke-variant")
    section("Twijfel", "twijfel")
    section("Nieuw", "nieuw")

    lines.append("## Duplicaatgroepen (binnen stap1)")
    lines.append("")
    if not dup_groups:
        lines.append("(geen)")
    else:
        for h, gid in sorted(group_id_by_hash.items(), key=lambda x: x[1]):
            docs = dup_groups[h]
            lines.append(f"### {gid}")
            lines.append("")
            for d in sorted(docs, key=lambda x: x.path.name):
                lines.append(f"- `{d.path.name}` (bron: `{fm_get(d.frontmatter, 'bron_md') or '?'}`)")
            lines.append("")

    (STAP2 / "VERGELIJKING.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"Stap2: {len(stap1_docs)} bestanden -> {STAP2}")
    print(
        f"al-in-bieb={counts['al-in-bieb']} variant={counts['mogelijke-variant']} "
        f"twijfel={counts['twijfel']} nieuw={counts['nieuw']} dup-groepen={len(dup_groups)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
