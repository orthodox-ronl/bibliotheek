"""Batch (historisch): leeg _stap2/nieuw → catalogus (na beslisvragen).

De map ``content-source/input/vsa-demo/`` is na opname verwijderd.
Verslag: ``docs/history/vsa-demo-opname.md``.

Near-dups: feesteigen houden, liturgie-kopieën wissen.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
NIEUW = REPO / "content-source/input/vsa-demo/_stap2/nieuw"
FM = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n?", re.DOTALL)

# Liturgie-near-dups: weg (feesteigen wint)
DELETE = {
    "eerste-antifoon-20260921-feest-van-de-geboorte-van-de-moeder-gods-20260921-ma-liturgie-geboorte-moeder-gods-n01.vsa",
    "tweede-antifoon-20260921-feest-van-de-geboorte-van-de-moeder-gods-20260921-ma-liturgie-geboorte-moeder-gods-n02.vsa",
    "derde-antifoon-20260921-feest-van-de-geboorte-van-de-moeder-gods-20260921-ma-liturgie-geboorte-moeder-gods-n03.vsa",
    "derde-antifoon-derde-feestantifoon-20260819-wo-liturgie-transfiguratie-n03.vsa",
    "kondak-kondak-profeet-elia-20260802-zo-liturgie-profeet-elias-n04.vsa",
}

# expliciete id-map (bestandsnaam → catalogus-id + title)
MAP: dict[str, tuple[str, str]] = {
    # antifonen feesten (feesteigen → liturgikon tenzij Hemelum-bewerking)
    "eerste-antifoon-geboorte-van-de-moeder-gods-09-08-geboorte-van-de-moeder-gods-n01.vsa": (
        "eerste-antifoon/geboorte-moeder-gods/liturgikon",
        "Eerste antifoon Geboorte Moeder Gods (Liturgikon)",
    ),
    "tweede-antifoon-geboorte-van-de-moeder-gods-09-08-geboorte-van-de-moeder-gods-n02.vsa": (
        "tweede-antifoon/geboorte-moeder-gods/liturgikon",
        "Tweede antifoon Geboorte Moeder Gods (Liturgikon)",
    ),
    "derde-antifoon-geboorte-van-de-moeder-gods-09-08-geboorte-van-de-moeder-gods-n03.vsa": (
        "derde-antifoon/geboorte-moeder-gods/liturgikon",
        "Derde antifoon Geboorte Moeder Gods (Liturgikon)",
    ),
    "eerste-antifoon-kruisverheffing-incl-09-14-kruisverheffing-n01.vsa": (
        "eerste-antifoon/kruisverheffing/liturgikon",
        "Eerste antifoon Kruisverheffing (Liturgikon)",
    ),
    "tweede-antifoon-kruisverheffing-incl-09-14-kruisverheffing-n02.vsa": (
        "tweede-antifoon/kruisverheffing/liturgikon",
        "Tweede antifoon Kruisverheffing (Liturgikon)",
    ),
    "derde-antifoon-kruisverheffing-incl-09-14-kruisverheffing-n03.vsa": (
        "derde-antifoon/kruisverheffing/liturgikon",
        "Derde antifoon Kruisverheffing (Liturgikon)",
    ),
    "eerste-antifoon-verheerlijking-op-de-berg-thabor-dup-008.vsa": (
        "eerste-antifoon/transfiguratie/liturgikon",
        "Eerste antifoon Transfiguratie (Liturgikon)",
    ),
    "tweede-antifoon-verheerlijking-op-de-berg-thabor-dup-005.vsa": (
        "tweede-antifoon/transfiguratie/liturgikon",
        "Tweede antifoon Transfiguratie (Liturgikon)",
    ),
    "derde-antifoon-verheerlijking-op-de-berg-thabor-08-06-verheerlijking-op-de-berg-thabor-n03.vsa": (
        "derde-antifoon/transfiguratie/liturgikon",
        "Derde antifoon Transfiguratie (Liturgikon)",
    ),
    "derde-antifoon-ontslaping-van-de-moeder-gods-dup-012.vsa": (
        "derde-antifoon/ontslapen-moeder-gods/liturgikon",
        "Derde antifoon Ontslapen Moeder Gods (Liturgikon)",
    ),
    # communievers
    "communievers-communievers-kruisverheffing-20260930-wo-liturgie-n03.vsa": (
        "communievers/kruisverheffing/hemelum",
        "Communievers Kruisverheffing (Hemelum)",
    ),
    "communievers-communievers-moeder-gods-dup-007.vsa": (
        "communievers/moeder-gods-liturgikon/liturgikon",
        "Communievers Moeder Gods — Liturgikon-melodie",
    ),
    "communievers-communievers-moeder-gods-20260908-di-liturgie-icoon-mgods-vladimir-n03.vsa": (
        "communievers/moeder-gods-vokn-25/hemelum",
        "Communievers Moeder Gods — VOKN-25 (Hemelum)",
    ),
    # eer aan de vader
    "eer-aan-de-vader-ontslaping-van-de-moeder-gods-dup-016.vsa": (
        "eer-aan-de-vader/default/liturgikon",
        "Eer aan de Vader (Liturgikon)",
    ),
    # kleine intocht feesten (Hemelum-liturgie)
    "kleine-intocht-20260814-feest-van-de-kruisuitdraging-en-kleine-wa-20260814-vr-liturgie-kruisuitdraging-n01.vsa": (
        "kleine-intocht/kruisuitdraging/hemelum",
        "Kleine intocht Kruisuitdraging (Hemelum)",
    ),
    "kleine-intocht-20260819-feest-van-de-h-transfiguratie-vd-heer-woe-20260819-wo-liturgie-transfiguratie-n05.vsa": (
        "kleine-intocht/transfiguratie/hemelum",
        "Kleine intocht Transfiguratie (Hemelum)",
    ),
    # kondaken
    "kondak-h-johannes-aartsbisschop-van-shanghai-en-san-franc-07-02-johannes-aartsbisschop-van-shanghai-en-san-francisco-n02.vsa": (
        "kondak/johannes-shanghai-toon-2/hemelum",
        "Kondak Johannes Shanghai toon 2 (Hemelum)",
    ),
    "kondak-h-marina-grootmartelares-07-17-grootmartelares-marina-n02.vsa": (
        "kondak/marina-grootmartelares-toon-3/hemelum",
        "Kondak Marina grootmartelares toon 3 (Hemelum)",
    ),
    "kondak-kondak-h-apostel-thaddeos-nls-nl-20260903-vr-liturgie-apostel-thaddeos-n02.vsa": (
        "kondak/apostel-thaddeos-toon-4/hemelum",
        "Kondak Apostel Thaddeos toon 4 (Hemelum)",
    ),
    "kondak-kondak-hh-vera-nadjezjda-ljoebov-nl-20260930-wo-liturgie-n01.vsa": (
        "kondak/vera-nadjezjda-ljoebov/hemelum",
        "Kondak Vera, Nadjezjda, Ljoebov (Hemelum)",
    ),
    "kondak-kondak-icoon-mgs-nls-en-ksl-nl-20260908-di-liturgie-icoon-mgods-vladimir-n02.vsa": (
        "kondak/icoon-moeder-gods-vladimir-toon-8/liturgikon",
        "Kondak Icoon Moeder Gods Vladimir toon 8 (Liturgikon)",
    ),
    "kondak-kondakion-t-2-11-30-apostel-andreas-n02.vsa": (
        "kondak/apostel-andreas-toon-2/hemelum",
        "Kondak Apostel Andreas toon 2 (Hemelum)",
    ),
    "kondak-kondakion-t-4-11-21-tempelgang-moeder-gods-n02.vsa": (
        "kondak/tempelgang-moeder-gods-toon-4/hemelum",
        "Kondak Tempelgang Moeder Gods toon 4 (Hemelum)",
    ),
    "kondak-maria-magdalena-07-22-maria-magdalena-heiligenjaar-n02.vsa": (
        "kondak/maria-magdalena-toon-4/heiligenjaar",
        "Kondak Maria Magdalena toon 4 (Heiligenjaar)",
    ),
    "kondak-maria-magdalena-07-22-maria-magdalena-liturgikon-n02.vsa": (
        "kondak/maria-magdalena-toon-3/liturgikon",
        "Kondak Maria Magdalena toon 3 (Liturgikon)",
    ),
    "kondak-onthoofing-van-h-johannes-de-doper-dup-029.vsa": (
        "kondak/onthoofding-johannes-de-doper-toon-5/hemelum",
        "Kondak Onthoofding Johannes de Doper toon 5 (Hemelum)",
    ),
    "kondak-ontslaping-van-de-moeder-gods-dup-006.vsa": (
        "kondak/ontslapen-moeder-gods-toon-2/liturgikon",
        "Kondak Ontslapen Moeder Gods toon 2 (Liturgikon)",
    ),
    "kondak-profeet-elia-07-20-profeet-elia-n02.vsa": (
        "kondak/profeet-elia-toon-2/liturgikon",
        "Kondak Profeet Elia toon 2 (Liturgikon)",
    ),
    "kondak-verheerlijking-op-de-berg-thabor-dup-004.vsa": (
        "kondak/transfiguratie-toon-7/liturgikon",
        "Kondak Transfiguratie toon 7 (Liturgikon)",
    ),
    # prijslied
    "prijslied-20260908-feest-van-de-icoon-moeder-gods-van-vladim-nl-20260908-di-liturgie-icoon-mgods-vladimir-n04.vsa": (
        "prijslied/icoon-moeder-gods-vladimir/hemelum",
        "Prijslied Icoon Moeder Gods Vladimir (Hemelum)",
    ),
    "prijslied-wij-verheerlijken-u-bisschop-gregorios-nl-20260825-di-liturgie-n05.vsa": (
        "prijslied/gregorios-van-utrecht/hemelum",
        "Prijslied Gregorios van Utrecht (Hemelum)",
    ),
    "prijslied-wij-verheerlijken-u-bisschop-gregorios-ksl-20260825-di-liturgie-n06.vsa": (
        "prijslied/gregorios-van-utrecht/hemelum-ksl",
        "Prijslied Gregorios van Utrecht (Hemelum, ksl)",
    ),
    # prokimen
    "prokimen-20260819-feest-van-de-h-transfiguratie-vd-heer-woe-20260819-wo-liturgie-transfiguratie-n08.vsa": (
        "prokimen/transfiguratie-toon-4/hemelum",
        "Prokimen Transfiguratie toon 4 (Hemelum)",
    ),
    # troparen
    "tropaar-besnijdenis-des-heren-01-01-besnijdenis-des-heren-n01.vsa": (
        "tropaar/besnijdenis-des-heren-toon-2/hemelum",
        "Tropaar Besnijdenis des Heren toon 2 (Hemelum)",
    ),
    "tropaar-geboorte-van-johannes-de-voorloper-06-24-geboorte-johannes-de-voorloper-n01.vsa": (
        "tropaar/geboorte-johannes-de-voorloper-toon-4/hemelum",
        "Tropaar Geboorte Johannes de Voorloper toon 4 (Hemelum)",
    ),
    "tropaar-h-marina-grootmartelares-07-17-grootmartelares-marina-n01.vsa": (
        "tropaar/marina-grootmartelares-toon-4/hemelum",
        "Tropaar Marina grootmartelares toon 4 (Hemelum)",
    ),
    "tropaar-maria-magdalena-07-22-maria-magdalena-heiligenjaar-n01.vsa": (
        "tropaar/maria-magdalena-toon-1/heiligenjaar",
        "Tropaar Maria Magdalena toon 1 (Heiligenjaar)",
    ),
    "tropaar-maria-magdalena-07-22-maria-magdalena-liturgikon-n01.vsa": (
        "tropaar/maria-magdalena-toon-1/liturgikon",
        "Tropaar Maria Magdalena toon 1 (Liturgikon)",
    ),
    "tropaar-ontslaping-van-de-moeder-gods-dup-017.vsa": (
        "tropaar/ontslapen-moeder-gods-toon-1/hemelum",
        "Tropaar Ontslapen Moeder Gods toon 1 (Hemelum)",
    ),
    "tropaar-tropaar-profeet-elia-toon-4-liturgikon-p-266-267-dup-028.vsa": (
        "tropaar/profeet-elia-toon-4/liturgikon",
        "Tropaar Profeet Elia toon 4 (Liturgikon)",
    ),
    "tropaar-troparion-t-4-11-21-tempelgang-moeder-gods-n01.vsa": (
        "tropaar/tempelgang-moeder-gods-toon-4/hemelum",
        "Tropaar Tempelgang Moeder Gods toon 4 (Hemelum)",
    ),
    "tropaar-troparion-t-4-11-30-apostel-andreas-n01.vsa": (
        "tropaar/apostel-andreas-toon-4/hemelum",
        "Tropaar Apostel Andreas toon 4 (Hemelum)",
    ),
    "tropaar-verheerlijking-op-de-berg-thabor-dup-024.vsa": (
        "tropaar/transfiguratie-toon-7/hemelum",
        "Tropaar Transfiguratie toon 7 (Hemelum)",
    ),
}


def split_fm(text: str) -> tuple[dict, str]:
    m = FM.match(text)
    if not m:
        return {}, text
    data = yaml.safe_load(m.group(1)) or {}
    if not isinstance(data, dict):
        data = {}
    return data, text[m.end() :]


def clean_frontmatter(path: Path, ident: str) -> None:
    """Schrijf valide catalogus-FM; herkomst onder herkomst_vsa_demo."""
    raw = path.read_text(encoding="utf-8")
    data, body = split_fm(raw)
    soort = data.get("soort") or ident.split("/")[0]
    taal = data.get("taal")
    korte = data.get("korte_titel")
    bronnen = data.get("bronnen")
    # bepaal bron.uitgangspunt grof
    uitgangspunt = None
    if isinstance(bronnen, list):
        for b in bronnen:
            if not isinstance(b, dict):
                continue
            fmblock = b.get("bron_md_frontmatter") or ""
            if "Liturgikon" in fmblock or "liturgikon" in (b.get("bron_md") or ""):
                uitgangspunt = "Liturgikon"
                break
            if "VOKN" in body[:500] or "VOKN" in fmblock:
                uitgangspunt = "VOKN-25"
                break
            if "Meneon" in fmblock:
                uitgangspunt = "Meneon I"
                break
            if "Hemelum" in fmblock or "Hemelum" in (b.get("bron_md") or ""):
                uitgangspunt = "Hemelum (koorinstructie / liturgie)"
    if "VOKN" in body[:800]:
        uitgangspunt = uitgangspunt or "VOKN-25"
    if "Liturgikon" in body[:800] and not uitgangspunt:
        uitgangspunt = "Liturgikon"
    if not uitgangspunt:
        uv = ident.split("/")[-1]
        if uv.startswith("hemelum"):
            uitgangspunt = "Hemelum (koorinstructie / liturgie)"
        elif uv == "liturgikon":
            uitgangspunt = "Liturgikon"
        elif uv == "heiligenjaar":
            uitgangspunt = "Heiligenjaar"
        elif uv == "meneon-1":
            uitgangspunt = "Meneon I"
        else:
            uitgangspunt = uv

    new: dict = {
        "do": "F4",
        "mode": "major",
        "tempo": 130,
        "soort": soort,
        "bron": {"uitgangspunt": uitgangspunt},
    }
    if taal:
        new["taal"] = taal
    herkomst: dict = {"soort": soort}
    if korte:
        herkomst["korte_titel"] = korte
    if data.get("duplicaat_groep"):
        herkomst["duplicaat_groep"] = data["duplicaat_groep"]
    if bronnen:
        herkomst["bronnen"] = bronnen
    if herkomst:
        new["herkomst_vsa_demo"] = herkomst

    dumped = yaml.safe_dump(new, allow_unicode=True, sort_keys=False, default_flow_style=False)
    path.write_text(f"---\n{dumped}---\n{body.lstrip()}" if not body.startswith("\n") else f"---\n{dumped}---\n{body}", encoding="utf-8", newline="\n")


def accepteer(ident: str, path: Path, title: str, *, skip_validate: bool = False) -> None:
    cmd = [
        sys.executable,
        str(REPO / "scripts/bieb_accepteer.py"),
        ident,
        str(path),
        "--title",
        title,
        "--status",
        "reviewable",
        "--move",
    ]
    if skip_validate:
        cmd.append("--skip-vsa-validate")
    proc = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(proc.stdout, end="")
    if proc.returncode != 0:
        print(proc.stderr, file=sys.stderr)
        raise SystemExit(f"FAIL {ident}: {proc.returncode}")


def validate_ok(path: Path) -> bool:
    v = subprocess.run(
        ["vsa", "validate", str(path)],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if v.returncode == 0:
        return True
    print(f"  WARN validate: skip-vsa-validate ({path.name})")
    err = (v.stdout or v.stderr or "").strip().splitlines()
    for line in err[:3]:
        print(f"    {line}")
    return False


def fix_link_title(ident: str) -> None:
    """Zet linkTitle op uitvoeringsvorm-label."""
    _z, _v, uv = ident.split("/")
    index = REPO / "content-source/catalogus" / Path(ident) / "index.md"
    if not index.is_file():
        return
    text = index.read_text(encoding="utf-8")
    labels = {
        "hemelum": "Hemelum",
        "hemelum-ksl": "Hemelum (ksl)",
        "liturgikon": "Liturgikon",
        "heiligenjaar": "Heiligenjaar",
        "meneon-1": "Meneon I",
        "vokn-25": "VOKN-25",
        "default": "Standaard",
    }
    label = labels.get(uv, uv)
    text2 = re.sub(r"(?m)^linkTitle:\s*.*$", f'linkTitle: "{label}"', text, count=1)
    if text2 != text:
        index.write_text(text2, encoding="utf-8", newline="\n")


def main() -> int:
    files = sorted(NIEUW.glob("*.vsa"))
    print(f"nieuw/: {len(files)} bestanden")
    mapped = set(MAP) | DELETE
    unknown = [p.name for p in files if p.name not in mapped]
    if unknown:
        print("ONBEKEND (geen map):")
        for n in unknown:
            print(" ", n)
        return 1

    for name in sorted(DELETE):
        p = NIEUW / name
        if p.is_file():
            p.unlink()
            print(f"DELETE near-dup {name}")

    skipped_val: list[str] = []
    for name, (ident, title) in MAP.items():
        p = NIEUW / name
        if not p.is_file():
            print(f"SKIP ontbreekt (al verwerkt?) {name}")
            continue
        print(f"\n== {name} -> {ident}")
        clean_frontmatter(p, ident)
        ok = validate_ok(p)
        if not ok:
            skipped_val.append(ident)
        accepteer(ident, p, title, skip_validate=not ok)
        fix_link_title(ident)

    left = list(NIEUW.glob("*.vsa"))
    print(f"\nResterend in nieuw/: {len(left)}")
    for p in left:
        print(" ", p.name)
    if skipped_val:
        print(f"\nZonder vsa validate ({len(skipped_val)}), status reviewable:")
        for i in skipped_val:
            print(" ", i)
    return 0 if not left else 1


if __name__ == "__main__":
    raise SystemExit(main())
