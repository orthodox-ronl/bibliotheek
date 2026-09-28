---
title: "mscz-products"
linkTitle: "mscz-products"
weight: 100
---

# NAME

`scripts\mscz-products.cmd` — PDF en Coria-`.mxl` maken bij een basispartituur-`.mscz`

# SYNOPSIS

```cmd
scripts\mscz-products.cmd [pad] [--force] [--dry-run]
```

# DESCRIPTION

Exporteert naast een **basispartituur-`.mscz`** de sibling-bestanden die
koorleden gebruiken: een A4-**PDF** (`{stam}.mscz.pdf`) en een
**Coria-`.mxl`** (`{stam}.mscz.mxl`). Het script schrijft ook
herkomstinformatie (`vsa-partituur-sha256`, `vsa-generated-at`) in die
producten.

Het zoekt basispartituur-`.mscz` onder het opgegeven pad (of, zonder pad,
onder `content-source\bibliotheek`). Bestanden in `input\`, namen die
eindigen op `.print.mscz`, en mappen met `artefacten_handmatig: true`
worden overgeslagen.

Onder de motorkap: MuseScore 4 voor de PDF; de tooling-CLI `mscz mxl` voor
Coria (vier parts). Geen fork van VSA-tooling-logica.

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
scripts\mscz-products.cmd
scripts\mscz-products.cmd content-source\bibliotheek\8-trisagion --force
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
