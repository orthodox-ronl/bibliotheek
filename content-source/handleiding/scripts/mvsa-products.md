---
title: "products — mvsa"
linkTitle: "products (mvsa)"
weight: 106
---

# NAME

`scripts\products.cmd --kinds mvsa` — Coria-`.mxl` (+ optioneel
`.translit.mxl`), koormap-SVG (+ translit-SVG), Score-IR/OSMD-MusicXML
maken bij een catalogus-`.mvsa`

# SYNOPSIS

```cmd
scripts\products.cmd --kinds mvsa [pad] [--force] [--dry-run]
```

# DESCRIPTION

Exporteert naast een **canonieke catalogus-`.mvsa`** de siblings die
koorleden en de site gebruiken:

| Product       | Bestand                                              | Waartoe                                                      |
| ------------- | ---------------------------------------------------- | ------------------------------------------------------------ |
| Coria-MXL     | `{stam}.mvsa.mxl`                                    | Afspelen / Coria (Translit uit)                              |
| Translit-MXL  | `{stam}.mvsa.translit.mxl`                           | Coria met Nls-/Ksl-hulp-parts (`--translit-as-parts`)        |
| Koormap-SVG   | `{stam}.mvsa.svg`                                    | Scherm (default); `check` eist dit niet als from-ir er is    |
| Translit-SVG  | `{stam}.mvsa.translit-nls.svg` / `.translit-ksl.svg` | Scherm bij Translit aan (Nls/Ksl); `check` eist die nog niet |
| Score-IR      | `{stam}.mvsa.score-ir.json`                          | Brug naar scherm/CoriB                                       |
| OSMD-MusicXML | `{stam}.mvsa.from-ir.musicxml`                       | Experimenteel OSMG-scherm (geen translit-pad)                |

Blad **Download pagina** = `index.md.pdf` (+ optioneel
`index.md.translit-*.pdf`) via [pdf](../pdf/), niet `{stam}.mvsa.pdf`.

Het script schrijft herkomstinformatie (`vsa-source-sha256`,
`vsa-source-kind=mvsa`, `vsa-generated-at`) in die producten.

Het zoekt `.mvsa` onder het opgegeven pad (of, zonder pad, onder
`content-source\catalogus`). Import-siblings die eindigen op
`.mscz.mvsa`, bestanden in `input\`, en mappen met
`manueel: true` worden overgeslagen. Geen passende `.mvsa`
op het pad = overslaan (geen fout; zelfde schil als
[products](../products/)).

Onder de motorkap: alleen wat nodig is. Coria-`.mxl` via `mvsa mxl`,
scherm-SVG via `mvsa svg`, Score-IR via `mvsa score-ir` (plus
`--musicxml` als from-ir nodig is). Niet het atomische `mvsa products`
(dat zou ook mp3/pdf/mscz meenemen). Alles schrijft mee in
`*.products-meta.json`. Versheid van mxl/score-ir/from-ir/svg komt uit
die meta. Bestaande lyrics-/Beluisteren-stempels worden desnoods
bijgewerkt. Optionele A4-PDF nog via `mvsa pdf` (layout `partituur`,
catalogus-id uit het bladermap-pad). Geen fork van
VSA-tooling-exportlogica.

CI genereert deze producten niet; jij wel lokaal, daarna committen. Zonder
MuseScore vernieuwt het script `.mxl` en Score-IR/from-ir (SVG-slot
wacht op MuseScore) en meldt het ontbrekende SVG’s.

# OPTIONS

| Optie       | Betekenis                         |
| ----------- | --------------------------------- |
| `--force`   | Bestaande producten overschrijven |
| `--dry-run` | Alleen tonen wat er zou gebeuren  |

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
