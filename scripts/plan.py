"""Leesbaar plan van alle productstraten (alleen lezen, schrijft niets).

Per bronsoort ("straat") staat hier welke producten eruit horen te komen, welke
nog ontbreken of verouderd zijn, welke bronnen zelf afgeleid zijn (``.vsa.mvsa``,
``.mscz.mvsa``), en of de volgorde van de sporen klopt: een afgeleide bron moet
ná zijn ouder gemaakt worden, en een straat mag niet in zichzelf eindigen
(``.vsa.mvsa.vsa`` bestaat niet).

Dit is stap 1 van het plan "één straat, één fix": de graaf als data. De
uitvoerder volgt later; ``plan`` laat nu al zien waar de huidige sporen elkaar
in de weg zitten.

Gebruik::

    python scripts/plan.py                 # samenvatting per straat
    python scripts/plan.py --lijst         # ook elk te maken product
    python scripts/plan.py --json plan.json
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOT = REPO_ROOT / "content-source" / "catalogus"

#: kind-id -> module met ``KIND`` (zelfde tabel als ``products.py``).
RUNNERS = {
    "vsa": "sync_vsa_products",
    "mscz": "sync_mscz_products",
    "tekstblad": "sync_tekstblad_products",
    "mvsa": "sync_mvsa_products",
    "import": "sync_import_mvsa",
    "audio": "sync_audio_products",
    "lyrics": "sync_lyrics_products",
}


@dataclass
class Product:
    kind: str
    bron: str
    pad: str
    bestaat: bool
    stempel_ok: bool
    contract_ok: bool | None
    alleen_lokaal: bool
    #: ``True`` als dit product nu nog klopt, maar verouderd raakt doordat zijn
    #: bron in dezelfde run opnieuw gemaakt wordt (gevolg, geen eigen reden).
    gevolg: bool = False

    @property
    def te_maken(self) -> bool:
        return (
            self.gevolg
            or (not self.bestaat)
            or (not self.stempel_ok)
            or self.contract_ok is False
        )

    @property
    def reden(self) -> str:
        if self.gevolg:
            return "gevolg"
        if not self.bestaat:
            return "ontbreekt"
        if not self.stempel_ok:
            return "verouderd"
        if self.contract_ok is False:
            return "contract"
        return "ok"


@dataclass
class PdfItem:
    pdf: str
    reden: str  # ok | ontbreekt | verouderd | gevolg
    via: str = ""  # welk te maken product (of nu verouderde afhankelijkheid)


@dataclass
class Plan:
    producten: list[Product] = field(default_factory=list)
    bronnen: dict[str, list[str]] = field(default_factory=dict)  # kind -> bronnen
    randen: list[tuple[str, str, str, str]] = field(default_factory=list)
    problemen: list[str] = field(default_factory=list)
    pdfs: list[PdfItem] = field(default_factory=list)


def _rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def bouw_plan(
    root: Path = DEFAULT_ROOT,
    *,
    kinds: tuple[str, ...] | None = None,
    contract: bool = False,
) -> Plan:
    """Verzamel bronnen en producten van alle sporen, en controleer de graaf."""
    from product_regen import KIND_ORDER, RegenPolicy

    volgorde = tuple(k for k in KIND_ORDER if kinds is None or k in kinds)
    policy = RegenPolicy(invalid=contract)
    plan = Plan()
    bron_kind: dict[str, str] = {}

    for kind in volgorde:
        mod = __import__(RUNNERS[kind])
        bronnen = mod.KIND.collect(root)
        plan.bronnen[kind] = [_rel(b, root) for b in bronnen]
        for bron in bronnen:
            bron_kind.setdefault(_rel(bron, root), kind)
            for slot in mod.KIND.slots_for(bron, policy):
                plan.producten.append(
                    Product(
                        kind=kind,
                        bron=_rel(bron, root),
                        pad=_rel(slot.path, root),
                        bestaat=slot.exists,
                        stempel_ok=slot.stamp_ok,
                        contract_ok=slot.contract_ok,
                        alleen_lokaal=slot.needs_musescore,
                    )
                )

    _controleer_graaf(plan, bron_kind, volgorde)
    sluit_af(plan)
    return plan


def _controleer_graaf(
    plan: Plan, bron_kind: dict[str, str], volgorde: tuple[str, ...]
) -> None:
    """Randen (bron -> afgeleide bron), volgorde en diepte."""
    positie = {k: i for i, k in enumerate(volgorde)}
    ouder: dict[str, str] = {}
    for p in plan.producten:
        kind_van_pad = bron_kind.get(p.pad)
        if kind_van_pad is None or p.pad == p.bron:
            continue
        plan.randen.append((p.bron, p.kind, p.pad, kind_van_pad))
        ouder[p.pad] = p.bron
        if positie[kind_van_pad] <= positie[p.kind]:
            plan.problemen.append(
                f"volgorde: {p.pad} wordt door '{p.kind}' gemaakt maar door "
                f"'{kind_van_pad}' als bron gebruikt, dat niet later komt"
            )

    def diepte(pad: str) -> int:
        n = 0
        while pad in ouder and n < 10:
            pad = ouder[pad]
            n += 1
        return n

    for pad in sorted(ouder):
        d = diepte(pad)
        if d > 1:
            plan.problemen.append(
                f"diepte: {pad} is {d} stappen van zijn oorspronkelijke bron "
                "(toegestaan: 1; bijv. .vsa -> .vsa.mvsa)"
            )
    for pad, kind in sorted(bron_kind.items()):
        naam = pad.rsplit("/", 1)[-1]
        delen = naam.split(".")[1:]
        bron_ext = [d for d in delen if d in {"vsa", "mvsa", "mscz"}]
        if len(bron_ext) >= 3 or (len(bron_ext) == 2 and bron_ext[0] == bron_ext[1]):
            plan.problemen.append(f"keten: {pad} bevat een niet-toegestane keten {bron_ext}")


def sluit_af(plan: Plan) -> None:
    """Markeer producten die verouderd raken omdat hun bron opnieuw gemaakt wordt.

    Een bron (bijv. ``a.vsa.mvsa``) die in dezelfde run vernieuwd wordt, maakt
    alles wat eruit afgeleid is verouderd, ook als dat nu nog klopt. Zo staat het
    volledige werk van één run vooraf in het plan.
    """
    nieuw = {p.pad for p in plan.producten if p.te_maken}
    veranderd = True
    while veranderd:
        veranderd = False
        for p in plan.producten:
            if p.te_maken or p.bron not in nieuw:
                continue
            p.gevolg = True
            nieuw.add(p.pad)
            veranderd = True


def beoordeel_pdfs(plan: Plan, jobs: list, root: Path) -> None:
    """Zet per ``index.md``-PDF (en weergave-variant) in het plan wat er moet.

    ``jobs`` zijn ``PaginaPdfJob``-achtige objecten (``out_path``, ``variants``,
    ``deps``). Een PDF is verouderd als een afhankelijkheid nieuwer is, of
    (nieuw) als een afhankelijkheid in deze run opnieuw gemaakt wordt.
    """
    vers: dict[Path, Product] = {}
    for p in plan.producten:
        if p.te_maken:
            vers[(root / p.pad).resolve()] = p
    for job in jobs:
        deps = [Path(d) for d in job.deps]
        dep_mtime = max((d.stat().st_mtime for d in deps if d.is_file()), default=0.0)
        via = next(
            (vers[d.resolve()] for d in deps if d.resolve() in vers),
            None,
        )
        for out in [job.out_path, *job.variants]:
            out = Path(out)
            naam = _rel(out, REPO_ROOT)
            if not out.is_file():
                plan.pdfs.append(PdfItem(naam, "ontbreekt"))
            elif dep_mtime and out.stat().st_mtime < dep_mtime:
                plan.pdfs.append(PdfItem(naam, "verouderd"))
            elif via is not None:
                plan.pdfs.append(PdfItem(naam, "gevolg", via.pad))
            else:
                plan.pdfs.append(PdfItem(naam, "ok"))


def _pdf_jobs() -> list:
    """Alle ``index.md``-PDF-jobs (zoals ``check_index_md_pdf`` ze bepaalt)."""
    from index_md_pdf import iter_bladermap_index_md, pagina_pdf_job

    jobs = []
    for md in iter_bladermap_index_md():
        try:
            job = pagina_pdf_job(md)
        except ValueError:
            continue
        if job is not None:
            jobs.append(job)
    return jobs


def samenvatting(plan: Plan) -> list[str]:
    regels: list[str] = []
    per_kind: dict[str, list[Product]] = {}
    for p in plan.producten:
        per_kind.setdefault(p.kind, []).append(p)
    for kind, bronnen in plan.bronnen.items():
        prods = per_kind.get(kind, [])
        te_maken = [p for p in prods if p.te_maken]
        lokaal = sum(1 for p in te_maken if p.alleen_lokaal)
        regel = (
            f"{kind:10} {len(bronnen):4} bronnen  {len(prods):5} producten  "
            f"{len(te_maken):4} te maken"
        )
        if lokaal:
            regel += f" ({lokaal} alleen lokaal: MuseScore)"
        regels.append(regel)
    if plan.pdfs:
        te_pdf = [x for x in plan.pdfs if x.reden != "ok"]
        gevolg = sum(1 for x in te_pdf if x.reden == "gevolg")
        regels.append(
            f"{'pdf':10} {len(plan.pdfs):4} bestanden {'':20}"
            f"{len(te_pdf):4} te maken ({gevolg} als gevolg van producten)"
        )
    afgeleid: dict[str, int] = {}
    for _b, kind, _pad, kind_van_pad in plan.randen:
        sleutel = f"{kind} -> {kind_van_pad}"
        afgeleid[sleutel] = afgeleid.get(sleutel, 0) + 1
    if afgeleid:
        regels.append("")
        regels.append("Afgeleide bronnen (spoor -> spoor dat ze als bron gebruikt):")
        for sleutel, n in sorted(afgeleid.items()):
            regels.append(f"  {n:4}  {sleutel}")
    regels.append("")
    if plan.problemen:
        regels.append(f"{len(plan.problemen)} probleem/problemen in de graaf:")
        regels.extend(f"  - {p}" for p in plan.problemen)
    else:
        regels.append("Graaf in orde: volgorde klopt, geen ketens, diepte <= 1.")
    return regels


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("root", nargs="?", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--lijst", action="store_true", help="toon elk te maken product")
    parser.add_argument("--contract", action="store_true", help="ook mxl-contract (traag)")
    parser.add_argument("--geen-pdf", action="store_true", help="sla de index.md-PDF's over")
    parser.add_argument("--json", type=Path, default=None, metavar="BESTAND")
    args = parser.parse_args(argv)

    plan = bouw_plan(args.root.resolve(), contract=args.contract)
    if not args.geen_pdf:
        beoordeel_pdfs(plan, _pdf_jobs(), args.root.resolve())
    for regel in samenvatting(plan):
        print(regel)
    if args.lijst:
        print()
        for p in plan.producten:
            if p.te_maken:
                extra = " [alleen lokaal]" if p.alleen_lokaal else ""
                print(f"  {p.reden:9} {p.kind:9} {p.pad}{extra}")
        for x in plan.pdfs:
            if x.reden != "ok":
                via = f"  (via {x.via})" if x.via else ""
                print(f"  {x.reden:9} {'pdf':9} {x.pdf}{via}")
    if args.json:
        args.json.write_text(
            json.dumps(
                {
                    "producten": [asdict(p) for p in plan.producten],
                    "pdfs": [asdict(x) for x in plan.pdfs],
                    "randen": plan.randen,
                    "problemen": plan.problemen,
                },
                indent=1,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
    return 1 if plan.problemen else 0


if __name__ == "__main__":
    sys.exit(main())
