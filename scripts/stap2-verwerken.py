#!/usr/bin/env python3
"""Stap2 afronden (historisch) volgens afspraak:

De map ``content-source/input/vsa-demo/`` is na opname verwijderd.
Verslag: ``docs/history/vsa-demo-opname.md``.

1. Duplicaatgroepen -> 1 VSA met geintegreerde metadata
2. al-in-bieb -> metadata in catalogus, daarna weg uit _stap2
3. mogelijke-variant -> _stap2/varianten/
4. twijfel -> _stap2/twijfel/ (aparte dingen, geen merge met catalogus-treffer)
5. nieuw -> _stap2/nieuw/
"""

from __future__ import annotations

import re
import shutil
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAP2 = ROOT / "content-source" / "input" / "vsa-demo" / "_stap2"
CATALOGUS = ROOT / "content-source" / "catalogus"

FM_SPLIT = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n?", re.DOTALL)


@dataclass
class Doc:
    path: Path
    name: str
    fm: str
    body: str
    status: str
    catalog_rel: str
    dup_group: str
    soort: str
    bron_md: str
    fields: dict[str, str] = field(default_factory=dict)


def split_fm(text: str) -> tuple[str, str]:
    m = FM_SPLIT.match(text)
    if not m:
        return "", text.lstrip("\n")
    return m.group(1).strip(), text[m.end() :].lstrip("\n")


def fm_get(fm: str, key: str) -> str:
    m = re.search(rf"(?m)^{re.escape(key)}:\s*(.*)$", fm)
    if not m:
        return ""
    v = m.group(1).strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1]
    return v


def yaml_escape(s: str) -> str:
    if s is None:
        return '""'
    if re.search(r'[:#"\'\n{}[\],&*?|><=@!`]', s) or s != s.strip() or s == "":
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'
    return s


def load_doc(path: Path) -> Doc:
    text = path.read_text(encoding="utf-8")
    fm, body = split_fm(text)
    return Doc(
        path=path,
        name=path.name,
        fm=fm,
        body=body,
        status=fm_get(fm, "stap2_status") or "onbekend",
        catalog_rel=fm_get(fm, "stap2_catalogus"),
        dup_group=fm_get(fm, "stap2_duplicaat_groep"),
        soort=fm_get(fm, "soort") or path.name.split("-")[0],
        bron_md=fm_get(fm, "bron_md"),
        fields={
            "korte_titel": fm_get(fm, "korte_titel"),
            "taal": fm_get(fm, "taal"),
            "extractie_rol": fm_get(fm, "extractie_rol"),
            "stap2_score": fm_get(fm, "stap2_score"),
        },
    )


def extract_block(fm: str, key: str) -> str:
    """Haal een multiline YAML-blok of list op als ruwe tekst (inclusief key-regel)."""
    lines = fm.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        if lines[i].startswith(f"{key}:"):
            out.append(lines[i])
            i += 1
            while i < len(lines):
                ln = lines[i]
                if ln and not ln.startswith((" ", "\t", "-")) and re.match(r"^[a-zA-Z0-9_]+:", ln):
                    break
                if ln.startswith("---"):
                    break
                out.append(ln)
                i += 1
            return "\n".join(out)
        i += 1
    return ""


def prefer_sort_key(d: Doc) -> tuple:
    """feesteigen/hemelum-eigen voor samenstellingen; kortere naam."""
    bron = d.bron_md or ""
    prio = 2
    if bron.startswith("feesteigen/"):
        prio = 0
    elif bron.startswith("hemelum-eigen/"):
        prio = 1
    return (prio, len(d.name), d.name)


def merge_docs(docs: list[Doc], group_id: str = "") -> tuple[str, str]:
    """Return (frontmatter, body) met geintegreerde metadata."""
    docs_sorted = sorted(docs, key=prefer_sort_key)
    lead = docs_sorted[0]
    statuses = {d.status for d in docs}
    # Als groep gemengde status heeft (zeldzaam): strengste / handmatig
    if len(statuses) == 1:
        status = next(iter(statuses))
    elif "mogelijke-variant" in statuses:
        status = "mogelijke-variant"
    elif "nieuw" in statuses:
        status = "nieuw"
    elif "twijfel" in statuses:
        status = "twijfel"
    else:
        status = "al-in-bieb"

    catalog_rels = sorted({d.catalog_rel for d in docs if d.catalog_rel})
    lines = [
        f"soort: {yaml_escape(lead.soort)}",
        f"korte_titel: {yaml_escape(lead.fields.get('korte_titel') or lead.soort)}",
    ]
    if lead.fields.get("taal"):
        lines.append(f"taal: {yaml_escape(lead.fields['taal'])}")
    if group_id:
        lines.append(f"duplicaat_groep: {yaml_escape(group_id)}")
    lines.append("bronnen:")
    for d in docs_sorted:
        lines.append(f"  - bestand: {yaml_escape(d.name)}")
        lines.append(f"    bron_md: {yaml_escape(d.bron_md)}")
        if d.fields.get("extractie_rol"):
            lines.append(f"    extractie_rol: {yaml_escape(d.fields['extractie_rol'])}")
        headers_block = extract_block(d.fm, "headers")
        if headers_block:
            hdr_items = []
            for ln in headers_block.splitlines()[1:]:
                m = re.match(r"^\s*-\s+(.*)$", ln)
                if m:
                    hdr_items.append(m.group(1).strip())
            if hdr_items:
                lines.append("    headers:")
                for h in hdr_items:
                    lines.append(f"      - {h}")
        fm_block = extract_block(d.fm, "bron_md_frontmatter")
        if fm_block:
            parts = fm_block.splitlines()
            lines.append("    bron_md_frontmatter: |")
            for pl in parts[1:]:
                content = pl[2:] if pl.startswith("  ") else pl
                if content.strip() == "":
                    lines.append("")
                else:
                    lines.append(f"      {content}")
    lines.append("extractie: stap2-merged" if group_id else "extractie: stap2")
    lines.append(f"stap2_status: {status}")
    if catalog_rels:
        if len(catalog_rels) == 1:
            lines.append(f"stap2_catalogus: {yaml_escape(catalog_rels[0])}")
        else:
            lines.append("stap2_catalogus_opties:")
            for c in catalog_rels:
                lines.append(f"  - {yaml_escape(c)}")
    if lead.fields.get("stap2_score"):
        lines.append(f"stap2_score: {lead.fields['stap2_score']}")
    return "\n".join(lines), lead.body


def render(fm: str, body: str) -> str:
    return f"---\n{fm}\n---\n\n{body.rstrip()}\n"


def build_herkomst_yaml(fm_merged: str) -> str:
    """Zet herkomst_vsa_demo-blok voor in catalogus-frontmatter."""
    bronnen = extract_block(fm_merged, "bronnen")
    soort = fm_get(fm_merged, "soort")
    korte = fm_get(fm_merged, "korte_titel")
    groep = fm_get(fm_merged, "duplicaat_groep")
    lines = ["herkomst_vsa_demo:"]
    if soort:
        lines.append(f"  soort: {yaml_escape(soort)}")
    if korte:
        lines.append(f"  korte_titel: {yaml_escape(korte)}")
    if groep:
        lines.append(f"  duplicaat_groep: {yaml_escape(groep)}")
    if bronnen:
        for ln in bronnen.splitlines():
            lines.append("  " + ln)
    else:
        bron_md = fm_get(fm_merged, "bron_md")
        if bron_md:
            lines.append("  bronnen:")
            lines.append(f"    - bron_md: {yaml_escape(bron_md)}")
    return "\n".join(lines)


def enrich_catalog(cat_rel: str, fm_merged: str) -> bool:
    """Voeg herkomst_vsa_demo toe aan catalogusbestand. Return True als geschreven."""
    path = CATALOGUS / cat_rel.replace("\\", "/")
    if not path.is_file():
        print(f"  WAARSCHUWING: catalogus ontbreekt: {cat_rel}", file=sys.stderr)
        return False
    text = path.read_text(encoding="utf-8")
    fm, body = split_fm(text)
    # Verwijder bestaand herkomst_vsa_demo-blok
    if fm and "herkomst_vsa_demo:" in fm:
        lines: list[str] = []
        skip = False
        for ln in fm.splitlines():
            if ln.startswith("herkomst_vsa_demo:"):
                skip = True
                continue
            if skip:
                if ln and not ln.startswith((" ", "\t")) and re.match(r"^[a-zA-Z0-9_]+:", ln):
                    skip = False
                    lines.append(ln)
                continue
            lines.append(ln)
        fm = "\n".join(lines).rstrip()
    herkomst = build_herkomst_yaml(fm_merged)
    new_fm = (fm.rstrip() + "\n" + herkomst).strip() if fm else herkomst
    path.write_text(render(new_fm, body), encoding="utf-8", newline="\n")
    return True


def out_name(docs: list[Doc], group_id: str = "") -> str:
    lead = sorted(docs, key=prefer_sort_key)[0]
    if group_id:
        base = lead.fields.get("korte_titel") or lead.soort
        base = re.sub(r"[^a-z0-9_-]+", "-", base.lower()).strip("-")
        return f"{lead.soort}-{base}-{group_id}.vsa"
    return lead.name


def main() -> int:
    if not STAP2.is_dir():
        print(f"Geen _stap2: {STAP2}", file=sys.stderr)
        return 1

    docs = [load_doc(p) for p in sorted(STAP2.glob("*.vsa"))]
    if not docs:
        print("Geen .vsa in _stap2 root (al verwerkt?)", file=sys.stderr)
        return 1

    # Mappen klaarzetten (oude inhoud weg voor herdraaien)
    for sub in ("varianten", "twijfel", "nieuw"):
        d = STAP2 / sub
        if d.is_dir():
            shutil.rmtree(d)
        d.mkdir(parents=True, exist_ok=True)

    by_group: dict[str, list[Doc]] = defaultdict(list)
    singles: list[Doc] = []
    for d in docs:
        if d.dup_group:
            by_group[d.dup_group].append(d)
        else:
            singles.append(d)

    # Bouw werklijst van (fm, body, status, catalog_rel, out_name, source_paths)
    work: list[tuple[str, str, str, str, str, list[Path]]] = []

    for gid, group in sorted(by_group.items()):
        fm, body = merge_docs(group, gid)
        status = fm_get(fm, "stap2_status")
        cat = fm_get(fm, "stap2_catalogus")
        name = out_name(group, gid)
        work.append((fm, body, status, cat, name, [d.path for d in group]))

    for d in singles:
        # normaliseer single ook naar bronnen-lijst voor uniforme herkomst
        fm, body = merge_docs([d], "")
        work.append((fm, body, d.status, d.catalog_rel, d.name, [d.path]))

    stats = {"catalogus_verrijkt": 0, "varianten": 0, "twijfel": 0, "nieuw": 0, "fout": 0}

    # Verwijder eerst alle oude root-.vsa na succesvolle verwerking — doe per item
    processed_sources: set[Path] = set()

    for fm, body, status, cat, name, sources in work:
        content = render(fm, body)

        if status == "al-in-bieb":
            if not cat:
                print(f"  FOUT al-in-bieb zonder catalogus: {name}", file=sys.stderr)
                stats["fout"] += 1
                # bewaar als nieuw ter controle
                (STAP2 / "nieuw" / name).write_text(content, encoding="utf-8", newline="\n")
            else:
                ok = enrich_catalog(cat, fm)
                if ok:
                    stats["catalogus_verrijkt"] += 1
                else:
                    stats["fout"] += 1
                    (STAP2 / "nieuw" / name).write_text(content, encoding="utf-8", newline="\n")
            for s in sources:
                processed_sources.add(s)
            continue

        if status == "mogelijke-variant":
            dest = STAP2 / "varianten" / name
            dest.write_text(content, encoding="utf-8", newline="\n")
            stats["varianten"] += 1
        elif status == "twijfel":
            # Aparte dingen: catalogus-treffer niet als waarheid behandelen
            fm2 = fm
            if "stap2_catalogus:" in fm2:
                fm2 = re.sub(
                    r"(?m)^stap2_catalogus:.*$",
                    "stap2_zwakke_treffer_negeren: true",
                    fm2,
                )
                # bewaar de zwakke treffer als notitie
                if cat:
                    if "stap2_notities:" in fm2:
                        fm2 += f"\n  - zwakke tekstgelijkenis met {cat} — apart houden"
                    else:
                        fm2 += (
                            f"\nstap2_notities:\n"
                            f"  - zwakke tekstgelijkenis met {cat} — apart houden"
                        )
            dest = STAP2 / "twijfel" / name
            dest.write_text(render(fm2, body), encoding="utf-8", newline="\n")
            stats["twijfel"] += 1
        else:
            dest = STAP2 / "nieuw" / name
            dest.write_text(content, encoding="utf-8", newline="\n")
            stats["nieuw"] += 1

        for s in sources:
            processed_sources.add(s)

    # Oude root-bestanden weg
    for p in processed_sources:
        if p.is_file() and p.parent == STAP2:
            p.unlink()

    # Rapport
    report = [
        "# Stap2 verwerking",
        "",
        f"- Catalogus verrijkt (al-in-bieb, daarna verwijderd uit _stap2): {stats['catalogus_verrijkt']}",
        f"- Varianten (map `varianten/`): {stats['varianten']}",
        f"- Twijfel (map `twijfel/`, apart gehouden): {stats['twijfel']}",
        f"- Nieuw (map `nieuw/`): {stats['nieuw']}",
        f"- Fouten: {stats['fout']}",
        f"- Duplicaatgroepen samengevoegd: {len(by_group)}",
        "",
        "Duplicaatgroepen: 1 bestand met `bronnen:`-lijst (metadata van alle leden).",
        "Al-in-bieb: `herkomst_vsa_demo` in catalogus-YAML.",
        "",
    ]
    (STAP2 / "VERWERKING.md").write_text("\n".join(report), encoding="utf-8", newline="\n")
    print("\n".join(report))
    return 0 if stats["fout"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
