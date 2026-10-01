---
title: "lyrics-products"
linkTitle: "lyrics-products"
weight: 106
---

# NAME

`scripts\lyrics-products.cmd` — platte zoektekst naast `.vsa` / `.mvsa`

# SYNOPSIS

```cmd
scripts\lyrics-products.cmd [pad] [--force] [--dry-run]
```

# DESCRIPTION

Haalt de **gezongen tekst** uit een catalogus-`.vsa` of `.mvsa` (via
`vsa text` in VSA-tooling) en schrijft die naast de bron als sibling:

| Bron | Lyrics-product |
| --- | --- |
| `{stam}.vsa` | `{stam}.vsa.lyrics.txt` |
| `{stam}.mvsa` | `{stam}.mvsa.lyrics.txt` |

Bovenaan het tekstbestand staan herkomstregels (`# vsa-source-sha256:` …),
zodat `check` kan zien of de bron nieuwer is dan de lyrics. Na een
geslaagde run vernieuwt dit script ook `static\zoek\index.json` (zelfde
stap als `products` en `check`). Op GitHub Pages (productie, preview én
branch-previews) bouwt de deploy-workflow die index opnieuw vóór Hugo,
zodat zoeken altijd bij de gecommitte catalogus past.

Zoekt onder het opgegeven pad (of, zonder pad, onder
`content-source\catalogus`). Overgeslagen: `input\`, mappen met
`artefacten_handmatig: true`.

CI genereert **geen** lyrics; jij wel lokaal (of via `products` /
`all-products`), daarna committen. De **zoekindex** wel: die wordt
bij elke Pages-deploy opnieuw gebouwd.

# EXAMPLES

```cmd
scripts\lyrics-products.cmd
scripts\lyrics-products.cmd content-source\catalogus\eerste-antifoon
scripts\lyrics-products.cmd --dry-run
```

# SEE ALSO

[all-products](../all-products/), [check](../check/),
[Publicatiecontrole](/handleiding/start/publicatiecontrole/),
[Zangstuk-soorten](/handleiding/start/zangstuk-soorten/)
