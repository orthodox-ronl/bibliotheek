---
title: "mvsa-products"
linkTitle: "mvsa-products"
weight: 106
---

# NAME

`scripts\mvsa-products.cmd` — Coria-`.mxl`, A4-PDF en koormap-SVG maken bij
een catalogus-`.mvsa`

# SYNOPSIS

```cmd
scripts\mvsa-products.cmd [pad] [--force] [--dry-run]
```

# DESCRIPTION

Exporteert naast een **canonieke catalogus-`.mvsa`** de siblings die
koorleden gebruiken: een **Coria-`.mxl`** (`{stam}.mvsa.mxl`), een
A4-**PDF** (`{stam}.mvsa.pdf`) voor download/print, en een
**muziek-only SVG** (`{stam}.mvsa.svg`) voor de webweergave van shortcode
`muziek` / `bieb` (partituur zonder titel/colofon, bijgesneden hoogte).
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
PDF; `mvsa svg` voor de koormap-SVG (MuseScore 4, layout `muziek`). Geen
fork van VSA-tooling-logica. Een `.mvsa` die meer dan één SVG-pagina zou
geven, faalt bij `mvsa svg` — verkort het stuk of gebruik `--section` in
de tooling (niet in dit script).

CI genereert deze producten niet; jij wel lokaal, daarna committen. Zonder
MuseScore kan het script alleen de `.mxl` vernieuwen en meldt het ontbrekende
PDF’s en SVG’s.

# OPTIONS

| Optie | Betekenis |
| --- | --- |
| `--force` | Bestaande MXL/PDF/SVG overschrijven |
| `--dry-run` | Alleen tonen wat er zou gebeuren |

# EXAMPLES

```cmd
scripts\mvsa-products.cmd
scripts\mvsa-products.cmd content-source\catalogus\ektinia\vrede\hemelum --force
```

# WHEN

Als een catalogus-`.mvsa` klaar is voor Coria, print-PDF en koormap-weergave,
of als `check --strict` meldt dat `.mvsa.mxl` / `.mvsa.pdf` / `.mvsa.svg`
ontbreekt of verouderd is.

# SEE ALSO

- [check](../check/)
- [import-mvsa](../import-mvsa/) (bewerkvorm naast `.mscz`; ander spoor)
- [Publicatiecontrole](/handleiding/start/publicatiecontrole/)
- Werktraject: [mvsa](/handleiding/werktrajecten/mvsa/)
- Spec (repo): `docs/specs/koormap-paginataal.md` — onderdeel `muziek`
