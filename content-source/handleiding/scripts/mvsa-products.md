---
title: "mvsa-products"
linkTitle: "mvsa-products"
weight: 106
---

# NAME

`scripts\mvsa-products.cmd` — Coria-`.mxl` en A4-PDF maken bij een bibliotheek-`.mvsa`

# SYNOPSIS

```cmd
scripts\mvsa-products.cmd [pad] [--force] [--dry-run]
```

# DESCRIPTION

Exporteert naast een **canonieke bibliotheek-`.mvsa`** de siblings die
koorleden gebruiken: een **Coria-`.mxl`** (`{stam}.mvsa.mxl`) en een
A4-**PDF** (`{stam}.mvsa.pdf`). Het script schrijft herkomstinformatie
(`vsa-source-sha256`, `vsa-source-kind=mvsa`, `vsa-generated-at`) in die
producten.

Het zoekt `.mvsa` onder het opgegeven pad (of, zonder pad, onder
`content-source\catalogus`). Import-siblings die eindigen op
`.mscz.mvsa`, bestanden in `input\`, en mappen met
`artefacten_handmatig: true` worden overgeslagen.

Onder de motorkap: tooling-CLI `mvsa musicxml` voor Coria; `mvsa pdf` met
layoutprofiel `partituur` en catalogus-id uit het bladermap-pad voor de
PDF (MuseScore 4). Geen fork van VSA-tooling-logica.

CI genereert deze producten niet; jij wel lokaal, daarna committen. Zonder
MuseScore kan het script alleen de `.mxl` vernieuwen en meldt het ontbrekende
PDF’s.

# OPTIONS

| Optie | Betekenis |
| --- | --- |
| `--force` | Bestaande MXL/PDF overschrijven |
| `--dry-run` | Alleen tonen wat er zou gebeuren |

# EXAMPLES

```cmd
scripts\mvsa-products.cmd
scripts\mvsa-products.cmd content-source\catalogus\9-alleluia --force
```

# WHEN

Als een bibliotheek-`.mvsa` klaar is voor Coria en print-PDF, of als
`check --strict` meldt dat `.mvsa.mxl` / `.mvsa.pdf` ontbreekt of
verouderd is.

# SEE ALSO

- [check](../check/)
- [import-mvsa](../import-mvsa/) (bewerkvorm naast `.mscz`; ander spoor)
- [Publicatiecontrole](/handleiding/start/publicatiecontrole/)
- Werktraject: [mvsa](/handleiding/werktrajecten/mvsa/)
