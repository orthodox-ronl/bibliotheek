"""Beginnoot voor de knop Inzet bij stukken met alleen een melodie.

Voor elke catalogusmap met alleen een ``.vsa`` als notatiebron en zonder
``.from-ir.musicxml`` (dus geen S, A, T en B) schrijft dit script de eerste
noot van de melodie naar ``data/inzet-melodie.json``. De toonhoogte komt uit
VSA-tooling; hier staat geen eigen VSA-logica. Het bestand is een
bouwresultaat voor Hugo (niet in git; geen product voor check/fix).
Contract: docs/specs/schermpartituur.md §2.4.
"""

from __future__ import annotations

import json
from pathlib import Path

from vsa.pitch_resolver import parse_pitch_string
from vsa.template_instance import midi_of
from vsa.vsa_stanzas import extract_stanza_notes
from vsa.yaml_frontmatter import parse_vsa_frontmatter_with_body_offset

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTENT = REPO_ROOT / "content-source"
UITVOER = REPO_ROOT / "data" / "inzet-melodie.json"


def melodie_bron(map_: Path) -> Path | None:
    """De ``.vsa`` als de map geen andere notatiebron en geen from-ir heeft."""
    if any(map_.glob("*.from-ir.musicxml")):
        return None
    bronnen = [
        p
        for p in map_.iterdir()
        if p.suffix.lower() in {".vsa", ".mvsa", ".mscz"} and p.name.count(".") == 1
    ]
    if not bronnen or any(p.suffix.lower() != ".vsa" for p in bronnen):
        return None
    return sorted(bronnen)[0]


def beginnoot(bron: Path) -> dict[str, object] | None:
    tekst = bron.read_text(encoding="utf-8-sig")
    meta, _body, _offset = parse_vsa_frontmatter_with_body_offset(tekst)
    noot = next((n for regel in extract_stanza_notes(tekst) for n in regel), None)
    if noot is None:
        return None
    # Zelfde standaard-do als VSA-tooling (PitchResolver.from_metadata).
    do = parse_pitch_string(str(meta.get("do", "F4")))
    teken = {1: "#", -1: "b"}.get(int(do.alter), "")
    return {"midi": midi_of(noot.pitch), "do": f"{do.step}{teken}"}


def main() -> int:
    uit: dict[str, dict[str, object]] = {}
    mislukt: list[str] = []
    for map_ in sorted(p for p in (CONTENT / "catalogus").rglob("*") if p.is_dir()):
        bron = melodie_bron(map_)
        if bron is None:
            continue
        sleutel = map_.relative_to(CONTENT).as_posix()
        try:
            noot = beginnoot(bron)
        except Exception as fout:  # noqa: BLE001 - een stuk zonder knop is geen bouwfout
            mislukt.append(f"{sleutel}: {fout}")
            continue
        if noot:
            uit[sleutel] = noot
    UITVOER.parent.mkdir(parents=True, exist_ok=True)
    UITVOER.write_text(json.dumps(uit, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Inzet-melodie: {len(uit)} stukken, {len(mislukt)} zonder beginnoot")
    for regel in mislukt:
        print(f"  WAARSCHUWING {regel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
