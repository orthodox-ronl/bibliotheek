---
title: "mvsa-products"
linkTitle: "mvsa-products"
weight: 106
---

# NAME

`scripts\mvsa-products.cmd` — Coria-`.mxl`, A4-PDF, koormap-SVG en
Score-IR/OSMD-MusicXML maken bij een catalogus-`.mvsa`

# SYNOPSIS

```cmd
scripts\mvsa-products.cmd [pad] [--force] [--dry-run]
```

# DESCRIPTION

Exporteert naast een **canonieke catalogus-`.mvsa`** de siblings die
koorleden en de site gebruiken:

| Product | Bestand | Waartoe |
| --- | --- | --- |
| Coria-MXL | `{stam}.mvsa.mxl` | Afspelen / Coria-contract |
| A4-PDF | `{stam}.mvsa.pdf` | Downloaden en printen |
| Koormap-SVG | `{stam}.mvsa.svg` | Scherm-fallback zonder OSMD; `check` eist dit niet als from-ir er is |
| Score-IR | `{stam}.mvsa.score-ir.json` | Brug naar scherm/CoriB |
| OSMD-MusicXML | `{stam}.mvsa.from-ir.musicxml` | Schermpartituur via OSMD |

Het script schrijft herkomstinformatie (`vsa-source-sha256`,
`vsa-source-kind=mvsa`, `vsa-generated-at`) in die producten.

Het zoekt `.mvsa` onder het opgegeven pad (of, zonder pad, onder
`content-source\catalogus`). Import-siblings die eindigen op
`.mscz.mvsa`, bestanden in `input\`, en mappen met
`artefacten_handmatig: true` worden overgeslagen. Geen passende `.mvsa`
op het pad = overslaan (geen fout; zelfde schil als
[products](../all-products/)).

Onder de motorkap: tooling-CLI `mvsa musicxml` voor Coria; `mvsa pdf` met
layoutprofiel `partituur` en catalogus-id uit het bladermap-pad voor de
PDF; `mvsa svg` voor de koormap-SVG (MuseScore 4, layout `muziek`);
`mvsa score-ir --musicxml` voor Score-IR plus OSMD-MusicXML (geen
MuseScore). Geen fork van VSA-tooling-logica. Een `.mvsa` die meer dan één
SVG-pagina zou geven, faalt bij `mvsa svg` — verkort het stuk of gebruik
`--section` in de tooling (niet in dit script).

CI genereert deze producten niet; jij wel lokaal, daarna committen. Zonder
MuseScore kan het script de `.mxl` en Score-IR/MusicXML vernieuwen en meldt
het ontbrekende PDF’s en SVG’s.

# OPTIONS

| Optie | Betekenis |
| --- | --- |
| `--force` | Bestaande producten overschrijven |
| `--dry-run` | Alleen tonen wat er zou gebeuren |

# EXAMPLES

```cmd
scripts\mvsa-products.cmd
scripts\mvsa-products.cmd content-source\catalogus\ektinia\vrede\hemelum --force
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
