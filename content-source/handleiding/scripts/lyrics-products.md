---
title: "products — lyrics"
linkTitle: "products (lyrics)"
weight: 106
---

# NAME

`scripts\products.cmd --kinds lyrics` — platte zoektekst naast `.vsa` / `.mvsa` /
`.mscz` (gewoon product-spoor; ook via `products` / `products --kinds all`)

# SYNOPSIS

```cmd
scripts\products.cmd --kinds lyrics [pad] [--force] [--dry-run]
```

# DESCRIPTION

Haalt de **gezongen tekst** uit een catalogus-bron (via `vsa text` /
MusicXML-lyrics in VSA-tooling) en schrijft die naast de bron als sibling:

| Bron | Lyrics-product |
| --- | --- |
| `{stam}.vsa` | `{stam}.vsa.lyrics.txt` |
| `{stam}.mvsa` | `{stam}.mvsa.lyrics.txt` |
| `{stam}.mscz` (basispartituur) | `{stam}.mscz.lyrics.txt` |

Bij een basispartituur-`.mscz` gebruikt het script een **verse** sibling
`{stam}.mscz.mxl`. Ontbreekt die of past de herkomststempel niet meer bij
de `.mscz`, dan draait eerst `mscz mxl` (zelfde straat als
[products (mscz)](../mscz-products/)). Lukt dat niet, dan valt tooling terug
op een tijdelijke export uit de `.mscz` (geen `.mscz.mvsa`).

Bovenaan het tekstbestand staan herkomstregels (`# vsa-source-sha256:` …),
zodat `check` kan zien of de bron nieuwer is dan de lyrics. Bij `.mscz` is
`vsa-source-kind` = `partituur`. Na een geslaagde run vernieuwt dit script
ook `static\zoek\index.json` (zelfde stap als `products` en `check`). Op
GitHub Pages (productie, preview én branch-previews) bouwt de deploy-workflow
die index opnieuw vóór Hugo, zodat zoeken altijd bij de gecommitte catalogus
past.

Zoekt onder het opgegeven pad (of, zonder pad, onder
`content-source\catalogus`). Overgeslagen: `input\`, mappen met
`manueel: true`, `*.print.mscz`, en afgeleide `*.vsa.mscz` /
`*.mvsa.mscz` (tenzij je zo’n bestand expliciet als pad doorgeeft).

CI genereert **geen** lyrics; jij wel lokaal (of via `products` /
`products --kinds all`), daarna committen. De **zoekindex** wel: die wordt
bij elke Pages-deploy opnieuw gebouwd.

# EXAMPLES

```cmd
scripts\products.cmd --kinds lyrics
scripts\products.cmd --kinds lyrics content-source\catalogus\cherubijnenhymne
scripts\products.cmd --kinds lyrics --dry-run
```

# SEE ALSO

[products](../products/), [products (mscz)](../mscz-products/),
[check](../check/),
[Zoeken (handleiding)](/handleiding/start/zoeken/),
[Publicatiecontrole](/handleiding/start/publicatiecontrole/),
[Zangstuk-soorten](/handleiding/start/zangstuk-soorten/)
