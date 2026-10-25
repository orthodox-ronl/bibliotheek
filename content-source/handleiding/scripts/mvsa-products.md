---
title: "products — mvsa"
linkTitle: "products (mvsa)"
weight: 106
---

# NAME

`scripts\products.cmd --kinds mvsa` — Coria-`.mxl`, A4-PDF, koormap-SVG en
Score-IR/OSMD-MusicXML maken bij een catalogus-`.mvsa`

# SYNOPSIS

```cmd
scripts\products.cmd --kinds mvsa [pad] [--force] [--dry-run]
```

# DESCRIPTION

Exporteert naast een **canonieke catalogus-`.mvsa`** de siblings die
koorleden en de site gebruiken:

| Product | Bestand | Waartoe |
| --- | --- | --- |
| Coria-MXL | `{stam}.mvsa.mxl` | Afspelen / Coria-contract |
| A4-PDF | `{stam}.mvsa.pdf` | Nog productketen; blad printen = **Download/Print pagina** |
| Koormap-SVG | `{stam}.mvsa.svg` | Scherm-fallback zonder OSMD; `check` eist dit niet als from-ir er is |
| Score-IR | `{stam}.mvsa.score-ir.json` | Brug naar scherm/CoriB |
| OSMD-MusicXML | `{stam}.mvsa.from-ir.musicxml` | Schermpartituur via OSMD |

Het script schrijft herkomstinformatie (`vsa-source-sha256`,
`vsa-source-kind=mvsa`, `vsa-generated-at`) in die producten.

Het zoekt `.mvsa` onder het opgegeven pad (of, zonder pad, onder
`content-source\catalogus`). Import-siblings die eindigen op
`.mscz.mvsa`, bestanden in `input\`, en mappen met
`manueel: true` worden overgeslagen. Geen passende `.mvsa`
op het pad = overslaan (geen fout; zelfde schil als
[products](../all-products/)).

Onder de motorkap: tooling `mvsa products` (Coria-`.mxl` + Score-IR +
from-ir; SVG alleen als dat slot nodig is, anders `--skip-svg`) schrijft
ook de herkomst-sidecar (`*.products-meta.json`, schema 2). Versheid voor
check/regen komt uit die meta, niet uit stempels in de productbestanden.
Optionele A4-PDF nog via `mvsa pdf` (layout `partituur`, catalogus-id uit
het bladermap-pad). Geen fork van VSA-tooling-exportlogica.

CI genereert deze producten niet; jij wel lokaal, daarna committen. Zonder
MuseScore vernieuwt het script `.mxl` en Score-IR/from-ir (`--skip-svg`)
en meldt het ontbrekende PDF’s en SVG’s.

# OPTIONS

| Optie | Betekenis |
| --- | --- |
| `--force` | Bestaande producten overschrijven |
| `--dry-run` | Alleen tonen wat er zou gebeuren |

# EXAMPLES

```cmd
scripts\products.cmd --kinds mvsa
scripts\products.cmd --kinds mvsa content-source\catalogus\ektinia\vrede\hemelum --force
```

# WHEN

Als een catalogus-`.mvsa` klaar is voor Coria, print-PDF, schermpartituur
(OSMD) en eventueel koormap-SVG, of als `check --strict` meldt dat
`.mvsa.mxl` / `.mvsa.pdf` / `.score-ir.json` / `.from-ir.musicxml`
ontbreekt of verouderd is. Ontbrekende `.mvsa.svg` is geen fout zolang
from-ir geldig is.

# SEE ALSO

- [check](../check/)
- [import-mvsa](../import-mvsa/) (bewerkvorm naast `.mscz`; ander spoor)
- [Publicatiecontrole](/handleiding/start/publicatiecontrole/)
- Werktraject: [mvsa](/handleiding/werktrajecten/mvsa/)
- Spec (repo): `docs/specs/koormap-paginataal.md` — onderdeel `muziek`
