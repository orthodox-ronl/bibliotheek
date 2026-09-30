"""Overzicht open werkbank-cases (pre-productie).

Leest de werkvoorraad-tabel, optioneel input/_werk, en bibliotheek-stubs
(publicatiestatus voorzien zonder canonieke bron). Schrijft
data/werkbank-status.json voor de special page.

Geen VSA-logica; alleen paden + markdown-tabel.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

from catalogus import CATALOGUS_ROOT, REPO_ROOT, leaf_folders, parse_id
from score_filenames import is_tekstblad_md

INPUT = REPO_ROOT / "content-source" / "input"
WERKVOORRAAD = INPUT / "werkvoorraad.md"
WERK = INPUT / "_werk"
STATUS_PATH = REPO_ROOT / "data" / "werkbank-status.json"
BEGIN = "<!-- werkvoorraad-tabel:begin -->"
END = "<!-- werkvoorraad-tabel:einde -->"

CANONICAL_SUFFIXES = frozenset({".mscz", ".vsa", ".mvsa"})
_FM_STATUS = re.compile(
    r"(?im)^publicatiestatus:\s*[\"']?(\w+)[\"']?\s*$"
)


@dataclass
class OpenInput:
    input: str
    doel_id: str
    stap: str
    volgende: str
    notitie: str
    werk_dir: str = ""


@dataclass
class StubCase:
    id: str
    dir: str
    publicatiestatus: str


@dataclass
class WerkDir:
    stam: str
    path: str
    files: list[str] = field(default_factory=list)


@dataclass
class StatusReport:
    open_inputs: list[OpenInput]
    stubs: list[StubCase]
    werk_dirs: list[WerkDir]


def _fm_publicatiestatus(index: Path) -> str:
    text = index.read_text(encoding="utf-8")
    m = _FM_STATUS.search(text)
    return (m.group(1).strip().lower() if m else "") or ""


def _has_canonical_source(folder: Path) -> bool:
    if not folder.is_dir():
        return False
    for path in folder.iterdir():
        if not path.is_file():
            continue
        if is_tekstblad_md(path):
            return True
        if path.suffix.lower() in CANONICAL_SUFFIXES:
            return True
    return False


def _parse_werkvoorraad_rows(text: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    if BEGIN not in text or END not in text:
        return rows
    body = text.split(BEGIN, 1)[1].split(END, 1)[0]
    for line in body.splitlines():
        if not line.startswith("| `"):
            continue
        parts = [p.strip() for p in line.strip().strip("|").split("|")]
        if len(parts) < 7:
            continue
        rows.append(
            {
                "input": parts[0].strip().strip("`"),
                "doel_id": parts[1].strip().strip("`"),
                "stap": parts[4].strip(),
                "volgende": parts[5].strip(),
                "notitie": parts[6].strip(),
            }
        )
    return rows


def _werk_stam_for(doel_id: str) -> str:
    if not doel_id:
        return ""
    try:
        z, v, u = parse_id(doel_id)
        return f"{z}-{v}-{u}"
    except ValueError:
        return ""


def collect() -> StatusReport:
    open_inputs: list[OpenInput] = []
    if WERKVOORRAAD.is_file():
        for row in _parse_werkvoorraad_rows(
            WERKVOORRAAD.read_text(encoding="utf-8")
        ):
            if row["stap"] == "gepubliceerd":
                continue
            stam = _werk_stam_for(row["doel_id"])
            werk_rel = ""
            if stam and (WERK / stam).is_dir():
                werk_rel = f"content-source/input/_werk/{stam}"
            open_inputs.append(
                OpenInput(
                    input=row["input"],
                    doel_id=row["doel_id"],
                    stap=row["stap"],
                    volgende=row["volgende"],
                    notitie=row["notitie"],
                    werk_dir=werk_rel,
                )
            )

    stubs: list[StubCase] = []
    for ident, folder in leaf_folders():
        index = folder / "index.md"
        if not index.is_file():
            continue
        if _has_canonical_source(folder):
            continue
        status = _fm_publicatiestatus(index)
        if status and status != "voorzien":
            # Lege leaf met andere status: toch als stub/werkbank tonen
            pass
        try:
            rel = folder.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
        except ValueError:
            rel = folder.as_posix()
        stubs.append(
            StubCase(id=ident, dir=rel, publicatiestatus=status or "(geen)")
        )

    werk_dirs: list[WerkDir] = []
    if WERK.is_dir():
        for child in sorted(WERK.iterdir(), key=lambda p: p.name.lower()):
            if not child.is_dir() or child.name.startswith("."):
                continue
            files = sorted(
                p.name for p in child.iterdir() if p.is_file()
            )
            try:
                rel = child.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
            except ValueError:
                rel = child.as_posix()
            werk_dirs.append(
                WerkDir(stam=child.name, path=rel, files=files)
            )

    return StatusReport(
        open_inputs=open_inputs,
        stubs=stubs,
        werk_dirs=werk_dirs,
    )


def write_json(report: StatusReport, path: Path = STATUS_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "fix_page": "/handleiding/start/werkbank/",
        "open_inputs": [asdict(x) for x in report.open_inputs],
        "stubs": [asdict(x) for x in report.stubs],
        "werk_dirs": [asdict(x) for x in report.werk_dirs],
    }
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def print_report(report: StatusReport) -> None:
    print(
        f"Werkbank: {len(report.open_inputs)} open input(s), "
        f"{len(report.stubs)} stub(s) zonder canonieke bron, "
        f"{len(report.werk_dirs)} _werk-map(pen).",
        flush=True,
    )
    if report.open_inputs:
        print("\nOpen werkvoorraad (niet gepubliceerd):", flush=True)
        for row in report.open_inputs:
            doel = row.doel_id or "(geen doel-id)"
            print(
                f"  - {row.input} -> {doel}  [{row.stap} -> {row.volgende}]",
                flush=True,
            )
            if row.werk_dir:
                print(f"      _werk: {row.werk_dir}", flush=True)
    if report.stubs:
        print("\nBibliotheek-stubs (geen canonieke bron):", flush=True)
        for stub in report.stubs:
            print(
                f"  - {stub.id}  ({stub.publicatiestatus})  {stub.dir}",
                flush=True,
            )
    if report.werk_dirs:
        print("\nLokale _werk-mappen (niet in git):", flush=True)
        for w in report.werk_dirs:
            n = len(w.files)
            print(f"  - {w.stam}/  ({n} bestand(en))", flush=True)
    print(
        "\nHandleiding: content-source\\handleiding\\start\\werkbank.md",
        flush=True,
    )
    print(
        f"JSON: {STATUS_PATH.relative_to(REPO_ROOT).as_posix()}",
        flush=True,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Overzicht open werkbank-cases; schrijft data/werkbank-status.json"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Alleen JSON schrijven, geen console-overzicht",
    )
    args = parser.parse_args(argv)
    report = collect()
    write_json(report)
    if not args.quiet:
        print_report(report)
    else:
        print(
            f"Werkbank-status geschreven "
            f"({STATUS_PATH.relative_to(REPO_ROOT).as_posix()}).",
            flush=True,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
