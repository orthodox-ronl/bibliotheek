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

Haalt de **gezongen tekst** uit een bibliotheek-`.vsa` of `.mvsa` (via
`vsa text` in VSA-tooling) en schrijft die naast de bron als sibling:

| Bron | Lyrics-product |
| --- | --- |
| `{stam}.vsa` | `{stam}.vsa.lyrics.txt` |
| `{stam}.mvsa` | `{stam}.mvsa.lyrics.txt` |

Bovenaan het tekstbestand staan herkomstregels (`# vsa-source-sha256:` …),
zodat `check` kan zien of de bron nieuwer is dan de lyrics. De site bouwt
daarna `static\zoek\index.json` (`python scripts\build_zoek_index.py`,
ook vanuit `check`) voor de pagina
[Zoeken in de catalogus](/catalogus/zoeken/).

Zoekt onder het opgegeven pad (of, zonder pad, onder
`content-source\catalogus`). Overgeslagen: `input\`, mappen met
`artefacten_handmatig: true`.

CI genereert **geen** lyrics; jij wel lokaal (of via `all-products`),
daarna committen.

# EXAMPLES

```cmd
scripts\lyrics-products.cmd
scripts\lyrics-products.cmd content-source\catalogus\2-eerste-antifoon
scripts\lyrics-products.cmd --dry-run
```

# SEE ALSO

[all-products](../all-products/), [check](../check/),
[Publicatiecontrole](/handleiding/start/publicatiecontrole/),
[Zangstuk-soorten](/handleiding/start/zangstuk-soorten/)
