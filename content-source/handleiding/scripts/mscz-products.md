---
title: "products — mscz"
linkTitle: "products (mscz)"
weight: 100
---

# NAME

`scripts\products.cmd --kinds mscz` — PDF en Coria-`.mxl` maken bij een basispartituur-`.mscz`

# SYNOPSIS

```cmd
scripts\products.cmd --kinds mscz [pad] [--force] [--dry-run]
```

# DESCRIPTION

Exporteert naast een **basispartituur-`.mscz`** de sibling-bestanden die
koorleden gebruiken: een A4-**PDF** (`{stam}.mscz.pdf`) en een
**Coria-`.mxl`** (`{stam}.mscz.mxl`). Het script schrijft ook
herkomstinformatie (`vsa-partituur-sha256`, `vsa-generated-at`) in die
producten.

Het zoekt basispartituur-`.mscz` onder het opgegeven pad (of, zonder pad,
onder `content-source\catalogus`). Bestanden in `input\`, namen die
eindigen op `.print.mscz`, afgeleide `*.vsa.mscz` / `*.mvsa.mscz`, en
mappen met `manueel: true` worden overgeslagen. Een afgeleide
`*.mvsa.mscz` wél behandelen: geef dat bestand expliciet als pad. Geef
je een ander brontype (bijvoorbeeld een `.mvsa`), dan slaat dit spoor
over — dat is geen fout (zelfde gedrag als bij
[products](../all-products/)).

Onder de motorkap: tooling `mscz products` (Coria-`.mxl` + optioneel
scherm-SVG; `--skip-svg` als alleen MXL nodig is) schrijft ook
`*.products-meta.json` (schema 2). Versheid = die meta. Optionele A4-PDF
nog via MuseScore 4. Geen fork van VSA-tooling-exportlogica.

**Volgorde:** eerst [layout](../layout/), daarna eventueel een editslag in
MuseScore 4, daarna dit commando — niet meteen PDF maken als je nog gaat
editen. CI genereert deze producten niet; jij wel lokaal, daarna committen.

# OPTIONS

| Optie | Betekenis |
| --- | --- |
| `--force` | Bestaande PDF/MXL overschrijven |
| `--dry-run` | Alleen tonen wat er zou gebeuren |

# EXAMPLES

```cmd
scripts\products.cmd --kinds mscz
scripts\products.cmd --kinds mscz content-source\catalogus\trisagion --force
```

# WHEN

Als de basispartituur-`.mscz` inhoudelijk en qua layout klaar is voor
publicatie-PDF en Coria, of als `check --strict` meldt dat PDF/MXL
verouderd of zonder stamp is.

# SEE ALSO

- [check](../check/)
- [layout](../layout/)
- Workflow: [PDF en Coria](/handleiding/partituur/5-pdf-en-coria/)
- [Publicatiecontrole](/handleiding/start/publicatiecontrole/)
