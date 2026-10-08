#!/usr/bin/env python3
"""Stap 1 (historisch): haal ::: vsa-notatie-blokken uit input/vsa-demo/*.md.

De map ``content-source/input/vsa-demo/`` is na opname verwijderd.
Verslag: ``docs/history/vsa-demo-opname.md``.

Schreef ruwe input-.vsa naar content-source/input/vsa-demo/_stap1/
met herkomst-metadata. Geen gissing: onduidelijke gevallen -> rapport.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "content-source" / "input" / "vsa-demo"
OUT = SRC / "_stap1"

FENCE_OPEN = re.compile(r"^::: ?vsa[ -]notatie\s*$", re.IGNORECASE | re.MULTILINE)
FENCE_CLOSE = re.compile(r"^:::\s*$", re.MULTILINE)
HEADER = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
HTML_COMMENT_OPEN_ONLY = re.compile(r"<!--")

ELM_RE = re.compile(r"\{[^}]*[_/\\+&~]")
BRON_MET_PAGINA = re.compile(
    r"(?i)\b(liturgikon|meneon|apostel|horolog(?:ion)?|tonenboek)\b"
    r".{0,60}?\b(?:p{1,2}\.?|blz\.?|pag(?:ina)?\.?)\s*\d"
)
# "iets als wij prijzen u / wij verheerlijken u" (ook: "Wij prijzen, wij prijzen u")
PRIJSLIED_START = re.compile(r"(?is)^\s*wij\s+(?:prijzen|verheerlijken)\b")
DERDE_ANT_HDR = re.compile(
    r"(?i)\b(?:derde|3e|3de)[\s-]*(?:feest)?antifoon\b"
)
TROPAAR_HDR = re.compile(r"(?i)\btropa{1,2}r(?:ion)?\b")
SOORT_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"(?i)\btropa{1,2}r(?:ion)?\b"), "tropaar"),
    (re.compile(r"(?i)\bkonda{1,2}k(?:ion)?\b|\bkontakion\b"), "kondak"),
    (
        re.compile(
            r"(?i)\b(?:eerste|1e|1ste)[\s-]*(?:feest)?antifoon\b"
            r"|\beerste\s+feestantifoon\b"
        ),
        "eerste-antifoon",
    ),
    (
        re.compile(
            r"(?i)\b(?:tweede|2e)[\s-]*(?:feest)?antifoon\b"
            r"|\btweede\s+feestantifoon\b"
        ),
        "tweede-antifoon",
    ),
    (
        re.compile(r"(?i)\b(?:derde|3e|3de)[\s-]*(?:feest)?antifoon\b"),
        "derde-antifoon",
    ),
    (re.compile(r"(?i)\bprokimen\b"), "prokimen"),
    (re.compile(r"(?i)\bcommunievers\b"), "communievers"),
    (re.compile(r"(?i)\bkleine\s+intocht\b"), "kleine-intocht"),
    (re.compile(r"(?i)\buw\s+heilig\s+kruis\b"), "uw-heilig-kruis"),
    (re.compile(r"(?i)\bmoeder\s*gods\s*lied\b"), "moeder-godslied"),
    (re.compile(r"(?i)\bprijslied\b"), "prijslied"),
    (re.compile(r"(?i)\beer\s+aan\s+de\s+vader\b"), "eer-aan-de-vader"),
]
_GENERIC_TITLES = re.compile(
    r"(?i)^(tropaar|troparion|kondak|kondakion|kontakion|prijslied|"
    r"moeder\s*gods\s*lied|prokimen|communievers|eerste\s+antifoon|"
    r"tweede\s+antifoon|derde\s+antifoon|kleine\s+intocht)"
    r"(?:\s*\(.*\))?$"
)


@dataclass
class Header:
    level: int
    text: str
    pos: int


@dataclass
class VsaBlock:
    start: int
    end: int
    body: str
    headers: list[Header]
    nearest_header: str
    index_in_file: int


@dataclass
class Emit:
    soort: str
    korte_titel: str
    body: str
    headers: list[str]
    md_rel: str
    md_stem: str
    md_frontmatter: str
    notes: list[str] = field(default_factory=list)
    extractie_rol: str = ""
    sort_key: float = 0.0
    taal: str = ""  # nl | ksl | leeg


def comment_ranges(text: str) -> list[tuple[int, int]]:
    ranges = [(m.start(), m.end()) for m in HTML_COMMENT.finditer(text)]
    for m in HTML_COMMENT_OPEN_ONLY.finditer(text):
        if any(a <= m.start() < b for a, b in ranges):
            continue
        if "-->" not in text[m.start() :]:
            ranges.append((m.start(), len(text)))
    return ranges


def in_ranges(pos: int, ranges: list[tuple[int, int]]) -> bool:
    return any(a <= pos < b for a, b in ranges)


def parse_frontmatter(text: str) -> tuple[str, str]:
    m = FRONTMATTER.match(text)
    if not m:
        return "", text
    return m.group(1).strip(), text[m.end() :]


def collect_headers(text: str, comments: list[tuple[int, int]]) -> list[Header]:
    out: list[Header] = []
    for m in HEADER.finditer(text):
        if in_ranges(m.start(), comments):
            continue
        out.append(Header(level=len(m.group(1)), text=m.group(2).strip(), pos=m.start()))
    return out


def headers_at(pos: int, headers: list[Header]) -> list[Header]:
    stack: list[Header] = []
    for h in headers:
        if h.pos >= pos:
            break
        while stack and stack[-1].level >= h.level:
            stack.pop()
        stack.append(h)
    return list(stack)


def find_vsa_blocks(text: str, comments: list[tuple[int, int]], headers: list[Header]) -> list[VsaBlock]:
    blocks: list[VsaBlock] = []
    opens = [m for m in FENCE_OPEN.finditer(text) if not in_ranges(m.start(), comments)]
    for i, m in enumerate(opens):
        body_start = m.end()
        if body_start < len(text) and text[body_start] == "\n":
            body_start += 1
        close = None
        for c in FENCE_CLOSE.finditer(text, m.end()):
            if in_ranges(c.start(), comments):
                continue
            close = c
            break
        next_open = opens[i + 1].start() if i + 1 < len(opens) else len(text)
        if close is None or close.start() > next_open:
            body_end = next_open
            end = next_open
            body = text[body_start:body_end].rstrip()
        else:
            body_end = close.start()
            end = close.end()
            body = text[body_start:body_end].rstrip("\n")
        stack = headers_at(m.start(), headers)
        nearest = stack[-1].text if stack else ""
        blocks.append(
            VsaBlock(
                start=m.start(),
                end=end,
                body=body,
                headers=stack,
                nearest_header=nearest,
                index_in_file=len(blocks),
            )
        )
    return blocks


def slug(s: str, max_len: int = 60) -> str:
    s = s.lower().strip()
    s = re.sub(r"[áàäâ]", "a", s)
    s = re.sub(r"[éèëê]", "e", s)
    s = re.sub(r"[íìïî]", "i", s)
    s = re.sub(r"[óòöô]", "o", s)
    s = re.sub(r"[úùüû]", "u", s)
    s = s.replace("ĳ", "ij").replace("ß", "ss")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    if len(s) > max_len:
        s = s[:max_len].rstrip("-")
    return s or "zonder-titel"


def plain_lyrics(vsa: str) -> str:
    t = HTML_COMMENT.sub(" ", vsa)
    t = re.sub(r"\[[^\]]*\]", " ", t)
    t = re.sub(r"\{([^}]*)\}", lambda m: re.sub(r"[^A-Za-zÀ-ÿ]", "", m.group(1)), t)
    t = re.sub(r"[*_/\\+&~.\-]+", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def fm_title(frontmatter: str) -> str:
    m = re.search(r'(?m)^title:\s*["\']?(.*?)["\']?\s*$', frontmatter)
    return m.group(1).strip() if m else ""


def detect_soort(headers: list[str], body: str) -> str:
    """Soort uit dichtstbijzijnde kop; anders commentaar. Geen gissing."""
    nearest = headers[-1] if headers else ""
    label_blob = nearest
    for cm in re.finditer(r"<!--(.*?)-->", body, re.DOTALL):
        label_blob += " | " + cm.group(1)
    lyrics = plain_lyrics(body)

    # Expliciet prijslied / moeder-godslied-label
    if re.search(r"(?i)\bprijslied\b|\bmoeder\s*gods\s*lied\b", label_blob):
        if PRIJSLIED_START.search(lyrics):
            return "prijslied"
        return "moeder-godslied"

    # "Wij verheerlijken U…" (o.a. Bisschop Gregorios) = prijslied
    if re.search(r"(?i)\bwij\s+verheerlijken\b", nearest) or PRIJSLIED_START.search(lyrics):
        return "prijslied"

    if nearest:
        for pat, soort in SOORT_PATTERNS:
            if soort in ("prijslied", "moeder-godslied"):
                continue
            if pat.search(nearest):
                return soort

    for cm in re.finditer(r"<!--(.*?)-->", body, re.DOTALL):
        for pat, soort in SOORT_PATTERNS:
            if soort in ("prijslied", "moeder-godslied"):
                continue
            if pat.search(cm.group(1)):
                return soort

    for h in reversed(headers[:-1]):
        for pat, soort in SOORT_PATTERNS:
            if soort in ("prijslied", "moeder-godslied"):
                continue
            if pat.search(h):
                return soort
    return "onbekend"


CYRILLIC_RE = re.compile(r"[\u0400-\u04FF]")
# Latijnse transliteratie van Kerkslavisch (geen NL; soms gemengd met 1 Cyrillische letter)
TRANSLIT_HINT = re.compile(
    r"(?i)\b(svjetitele|velichajem|vlichajem|krestoe|mostjsjej|otsje|"
    r"po.?klan.?ja.?jem.?sja|voskres|svjatoe)\b"
)


def detect_taal(headers: list[str], body: str) -> str:
    """nl | ksl | translit | '' (onbekend/niet van toepassing)."""
    blob = " ".join(headers)
    if re.search(r"(?i)getranslitereerd", blob):
        return "translit"
    lyrics = plain_lyrics(body)
    # Translit-hints vóór Cyrillisch: bodies mixen soms Latin + Cyrillische е
    if TRANSLIT_HINT.search(lyrics) or TRANSLIT_HINT.search(body):
        # Echte Ksl-tekst heeft wél veel Cyrillisch; translit nauwelijks
        cyr_count = len(CYRILLIC_RE.findall(body))
        if cyr_count < 12:
            return "translit"
    cyr_count = len(CYRILLIC_RE.findall(body))
    if cyr_count >= 12:
        return "ksl"
    if re.search(r"(?i)\b(?:ksl|kerkslav)\b", blob) and not re.search(
        r"(?i)\b(?:nls|nederlands|\bnl\b)", blob
    ):
        if not re.search(r"(?i)\b(wij|gij|heer|uw|het|de|een)\b", lyrics):
            return "translit"
        return "ksl"
    if re.search(r"(?i)\b(?:nls|nederlands)\b", blob):
        return "nl"
    if lyrics and re.search(r"(?i)\b(wij|gij|heer|de|het|een|van)\b", lyrics):
        return "nl"
    return ""


def korte_titel_from(
    headers: list[str], soort: str, md_stem: str, body: str, frontmatter: str = ""
) -> str:
    nearest = ""
    for h in reversed(headers):
        clean = re.sub(r"\*+", "", h)
        clean = re.sub(r"\([^)]*\)", "", clean)
        clean = re.sub(r"\s+", " ", clean).strip(" -–—:")
        if clean:
            nearest = clean
            break

    title = fm_title(frontmatter)
    cm = re.search(r"<!--\s*(.*?)\s*-->", body, re.DOTALL)
    comment_first = cm.group(1).split("\n")[0].strip() if cm else ""

    if nearest and _GENERIC_TITLES.match(nearest):
        if title:
            return slug(title, 50)
        if comment_first:
            return slug(comment_first, 50)
        return slug(md_stem, 50)

    if nearest:
        return slug(nearest, 50)
    if comment_first:
        return slug(comment_first, 50)
    if title:
        return slug(f"{soort}-{title}", 50)
    return slug(f"{soort}-{md_stem}", 50)


def has_elms(body: str) -> bool:
    return bool(ELM_RE.search(HTML_COMMENT.sub("", body)))


def has_bron_met_pagina(body: str, headers: list[str]) -> bool:
    blob = body + "\n" + "\n".join(headers)
    return bool(BRON_MET_PAGINA.search(blob))


def is_eer_aan_blok(body: str, headers: list[str]) -> bool:
    """Alleen korte doxologie-blokken, geen antifoon die met 'Eer aan' begint."""
    stripped = HTML_COMMENT.sub("", body)
    if re.search(r"(?m)^\s*\d+\.", stripped):
        return False
    if re.search(r"(?i)\brefrein\b", stripped):
        return False
    lyrics = plain_lyrics(body)
    if len(lyrics) > 160:
        return False
    low = lyrics.lower()
    if low.startswith("eer aan de vader") or "eer aan de vader" in low[:40]:
        return True
    if re.search(r"(?i)^\s*nu en altijd", lyrics):
        return True
    blob = " ".join(headers).lower()
    if "eer aan" in blob and len(lyrics) < 120:
        return True
    return False


def yaml_escape(s: str) -> str:
    if s is None:
        return '""'
    if re.search(r'[:#"\'\n{}[\],&*?|><=@!`]', s) or s != s.strip():
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'
    return s


def render_vsa(em: Emit) -> str:
    lines = ["---"]
    lines.append("extractie: stap1")
    lines.append(f"soort: {yaml_escape(em.soort)}")
    if em.taal:
        lines.append(f"taal: {yaml_escape(em.taal)}")
    if em.extractie_rol:
        lines.append(f"extractie_rol: {yaml_escape(em.extractie_rol)}")
    lines.append(f"bron_md: {yaml_escape(em.md_rel)}")
    lines.append(f"korte_titel: {yaml_escape(em.korte_titel)}")
    if em.headers:
        lines.append("headers:")
        for h in em.headers:
            lines.append(f"  - {yaml_escape(h)}")
    if em.md_frontmatter:
        lines.append("bron_md_frontmatter: |")
        for fl in em.md_frontmatter.splitlines():
            lines.append(f"  {fl}")
    if em.notes:
        lines.append("notities:")
        for n in em.notes:
            lines.append(f"  - {yaml_escape(n)}")
    lines.append("---")
    lines.append("")
    lines.append(em.body.rstrip())
    lines.append("")
    return "\n".join(lines)


def is_derde_ant_context(headers: list[Header]) -> bool:
    return any(DERDE_ANT_HDR.search(h.text) for h in headers)


def is_tropaar_block(b: VsaBlock) -> bool:
    if b.headers and TROPAAR_HDR.search(b.headers[-1].text):
        return True
    if re.search(r"(?i)<!--\s*tropa", b.body):
        return True
    return False


def is_derde_ant_openingsblok(b: VsaBlock) -> bool:
    """Eerste psalmvers(en): dichtstbijzijnde kop is zelf de derde-antifoon-kop."""
    if not b.headers:
        return False
    return DERDE_ANT_HDR.search(b.headers[-1].text) is not None


def is_vervolg_antifoonblok(b: VsaBlock) -> bool:
    """Vervolg ná de tropaar: commentaar 'Vervolg' of psalmvers 2./3."""
    if re.search(r"(?i)vervolg\s*3e?\s*antifoon|vervolg\s+derde", b.body[:300]):
        return True
    stripped = HTML_COMMENT.sub("", b.body).lstrip()
    if re.match(r"[2-9]\.\s", stripped):
        return True
    return False


def process_file(path: Path) -> tuple[list[Emit], list[str]]:
    text = path.read_text(encoding="utf-8")
    rel = path.relative_to(SRC).as_posix()
    stem = path.stem
    fm, _ = parse_frontmatter(text)
    comments = comment_ranges(text)
    headers = collect_headers(text, comments)
    blocks = find_vsa_blocks(text, comments, headers)
    warns: list[str] = []
    emits: list[Emit] = []
    consumed: set[int] = set()

    groups: dict[int, tuple[int, int, int]] = {}
    i = 0
    while i < len(blocks) - 2:
        a, b, c = blocks[i], blocks[i + 1], blocks[i + 2]
        if (
            is_derde_ant_openingsblok(a)
            and is_tropaar_block(b)
            and is_vervolg_antifoonblok(c)
        ):
            groups[i] = (i, i + 1, i + 2)
            consumed.update({i, i + 1, i + 2})
            i += 3
            continue
        i += 1

    for idx, bl in enumerate(blocks):
        if idx in groups:
            ai, bi, ci = groups[idx]
            a, b, c = blocks[ai], blocks[bi], blocks[ci]
            parts: list[str] = []
            if a.nearest_header:
                parts.append(f"<!-- header: {a.nearest_header} -->")
            parts.append(a.body.rstrip())
            parts.append("")
            if b.nearest_header:
                parts.append(f"<!-- header: {b.nearest_header} -->")
            parts.append(b.body.rstrip())
            parts.append("")
            if c.nearest_header:
                parts.append(f"<!-- header: {c.nearest_header} -->")
            parts.append(c.body.rstrip())
            # Headers van de antifoon-sectie (niet de tropaar-subheader als enige)
            hdrs = [h.text for h in a.headers]
            emits.append(
                Emit(
                    soort="derde-antifoon",
                    korte_titel=korte_titel_from(hdrs, "derde-antifoon", stem, a.body, fm),
                    body="\n".join(parts).rstrip() + "\n",
                    headers=hdrs,
                    md_rel=rel,
                    md_stem=stem,
                    md_frontmatter=fm,
                    notes=[
                        "samengevoegd uit 3 vsa-blokken (begin + tropaar + vervolg); tropaar blijft erin"
                    ],
                    extractie_rol="derde-antifoon-met-tropaar",
                    sort_key=float(a.start),
                )
            )
            th = [h.text for h in b.headers]
            emits.append(
                Emit(
                    soort="tropaar",
                    korte_titel=korte_titel_from(th, "tropaar", stem, b.body, fm),
                    body=b.body if b.body.endswith("\n") else b.body + "\n",
                    headers=th,
                    md_rel=rel,
                    md_stem=stem,
                    md_frontmatter=fm,
                    notes=[
                        "ook opgenomen in derde-antifoon-met-tropaar van hetzelfde bronbestand"
                    ],
                    extractie_rol="tropaar-uit-derde-antifoon",
                    sort_key=float(b.start) + 0.1,
                )
            )
            continue

        if idx in consumed:
            continue

        hdrs = [h.text for h in bl.headers]
        if is_eer_aan_blok(bl.body, hdrs):
            if has_elms(bl.body) and has_bron_met_pagina(bl.body, hdrs):
                emits.append(
                    Emit(
                        soort="eer-aan-de-vader",
                        korte_titel=slug(fm_title(fm) or stem, 50),
                        body=bl.body if bl.body.endswith("\n") else bl.body + "\n",
                        headers=hdrs,
                        md_rel=rel,
                        md_stem=stem,
                        md_frontmatter=fm,
                        extractie_rol="los-blok-met-bron",
                        sort_key=float(bl.start),
                    )
                )
            else:
                warns.append(
                    f"{rel}: overgeslagen doxologie/eer-aan-blok (geen ELM+bron-met-pagina) "
                    f"[blok {bl.index_in_file + 1}]"
                )
            continue

        taal = detect_taal(hdrs, bl.body)
        if taal == "translit":
            warns.append(
                f"{rel}: overgeslagen transliteratie-blok [blok {bl.index_in_file + 1}] "
                f"(header={bl.nearest_header!r})"
            )
            continue

        soort = detect_soort(hdrs, bl.body)
        notes: list[str] = []
        if soort == "onbekend":
            notes.append("soort onduidelijk uit headers/commentaar; niet gegist")
            warns.append(
                f"{rel}: soort onbekend voor blok {bl.index_in_file + 1} "
                f"(header={bl.nearest_header!r})"
            )

        if re.search(r"(?m)^##\s+", bl.body):
            notes.append("mogelijk kapotte vsa-fence: markdown-kop in body")
            warns.append(f"{rel}: mogelijk kapotte fence in blok {bl.index_in_file + 1}")

        # Taal-suffix vooral bij prijslied (nl/ksl-paren) en expliciete Nls/Ksl-koppen
        use_taal = ""
        if taal in ("nl", "ksl") and (
            soort == "prijslied"
            or re.search(r"(?i)\b(?:nls|ksl|nederlands|kerkslav)\b", " ".join(hdrs))
        ):
            use_taal = taal

        emits.append(
            Emit(
                soort=soort,
                korte_titel=korte_titel_from(hdrs, soort, stem, bl.body, fm),
                body=bl.body if bl.body.endswith("\n") else bl.body + "\n",
                headers=hdrs,
                md_rel=rel,
                md_stem=stem,
                md_frontmatter=fm,
                notes=notes,
                sort_key=float(bl.start),
                taal=use_taal,
            )
        )

    emits.sort(key=lambda e: e.sort_key)
    return emits, warns


def main() -> int:
    if not SRC.is_dir():
        print(f"Bronmap ontbreekt: {SRC}", file=sys.stderr)
        return 1
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.vsa"):
        old.unlink()
    if (OUT / "RAPPORT.md").exists():
        (OUT / "RAPPORT.md").unlink()

    all_emits: list[Emit] = []
    all_warns: list[str] = []
    md_files = sorted(
        p for p in SRC.rglob("*.md") if "_stap1" not in p.parts and p.name != "_index.md"
    )
    for path in md_files:
        emits, warns = process_file(path)
        all_emits.extend(emits)
        all_warns.extend(warns)

    counters: dict[str, int] = {}
    written: list[tuple[str, Emit]] = []
    for em in all_emits:
        counters[em.md_stem] = counters.get(em.md_stem, 0) + 1
        n = counters[em.md_stem]
        taal_part = f"-{em.taal}" if em.taal else ""
        fname = f"{em.soort}-{em.korte_titel}{taal_part}-{em.md_stem}-n{n:02d}.vsa"
        target = OUT / fname
        k = 2
        while target.exists():
            target = OUT / f"{em.soort}-{em.korte_titel}{taal_part}-{em.md_stem}-n{n:02d}-{k}.vsa"
            k += 1
        target.write_text(render_vsa(em), encoding="utf-8", newline="\n")
        written.append((target.name, em))

    by_soort: dict[str, int] = {}
    for _, em in written:
        by_soort[em.soort] = by_soort.get(em.soort, 0) + 1
    lines = [
        "# Stap 1-extractie rapport",
        "",
        f"Bron: `{SRC.relative_to(ROOT).as_posix()}`",
        f"Doel: `{OUT.relative_to(ROOT).as_posix()}`",
        f"Markdown-bestanden verwerkt: {len(md_files)}",
        f"VSA-bestanden geschreven: {len(written)}",
        "",
        "## Per soort",
        "",
    ]
    for s in sorted(by_soort):
        lines.append(f"- `{s}`: {by_soort[s]}")
    lines += ["", "## Waarschuwingen / open punten", ""]
    if all_warns:
        for w in all_warns:
            lines.append(f"- {w}")
    else:
        lines.append("- (geen)")
    lines += ["", "## Bestanden", ""]
    for name, em in written:
        rol = f" ({em.extractie_rol})" if em.extractie_rol else ""
        lines.append(f"- `{name}` <- `{em.md_rel}`{rol}")
    (OUT / "RAPPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"Geschreven: {len(written)} .vsa -> {OUT}")
    print(f"Waarschuwingen: {len(all_warns)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
