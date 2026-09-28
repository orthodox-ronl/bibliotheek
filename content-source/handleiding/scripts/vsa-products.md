---
title: "vsa-products"
linkTitle: "vsa-products"
weight: 110
---

# NAME

`scripts\vsa-products.cmd` — Coria-`.vsa.mxl` maken bij een bibliotheek-`.vsa`

# SYNOPSIS

```cmd
scripts\vsa-products.cmd [pad] [--force] [--dry-run]
```

# DESCRIPTION

Maakt naast een bibliotheek-`.vsa` het siblingbestand `{stam}.vsa.mxl` voor
Coria-afspelen (Oefenen-knop). Het script:

1. syllabificeert in een tijdelijk bestand (canonieke `.vsa` blijft ongewijzigd);
2. exporteert via `vsa musicxml --musicxml-profile playback`;
3. saniteert voor Coria;
4. zet een `vsa-source-sha256`-stempel van de canonieke `.vsa`.

Mappen met `artefacten_handmatig: true` in de frontmatter worden
overgeslagen. Zonder pad werkt het onder `content-source\bibliotheek`.

Lokaal vernieuw je producten met dit commando. CI genereert **niet** —
`check_vsa_products` faalt bij ontbrekende of verouderde siblings.

# OPTIONS

| Optie | Betekenis |
| --- | --- |
| `--force` | Bestaande `.vsa.mxl` overschrijven |
| `--dry-run` | Alleen tonen wat er zou gebeuren |

# WHEN

Na een wijziging aan een `.vsa` in de bibliotheek, of als `check --strict`
meldt dat de `.vsa.mxl` verouderd of zonder stamp is.

# SEE ALSO

- [check](../check/)
- [validate](../validate/)
- [Productgates](/handleiding/start/productgates/)
- Workflow: [VSA → SVG en Coria](/handleiding/werktrajecten/vsa/)
