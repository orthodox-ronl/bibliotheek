---
title: "oefenhoek-index"
linkTitle: "oefenhoek-index"
weight: 140
---

# NAME

`scripts\oefenhoek-index.cmd` — SVG-plaatjes uit catalogus-`.vsa`; optioneel
legacy widgets uit `index.md` strippen

# SYNOPSIS

```cmd
scripts\oefenhoek-index.cmd [--dry-run] [--svg] [--verbose]
```

# DESCRIPTION

Met **`--svg`** schrijft dit commando SVG-plaatjes van canonieke
catalogus-`.vsa`-bestanden naar `static\vsa\bladermap\…`. Shortcode
`bieb` toont die plaatjes wanneer er **geen** basispartituur-`.mscz` in
dezelfde bladermap staat (een `.print.mscz` mag wel). Sidecar-bestanden
`*.syl.vsa` worden overgeslagen.

Dit is **geen** publicatiecontrole: er is geen herkomststempel en CI faalt
niet op “stale SVG”. De SVG is een site-plaatje. `check` / `build` /
`serve` / Pages-CI vernieuwen de plaatjes vóór Hugo, zodat ze bij de
huidige `.vsa` passen. Je mag de SVG’s ook committen (handig voor diff);
verplicht is dat niet voor de build.

Zonder flags haalt het script legacy auto-includes / score-shortcodes uit
bladermap-`index.md`. Pagina’s met shortcode `bieb` of met
`automatische_inhoud: false` worden niet aangepast.

# OPTIONS

| Optie | Betekenis |
| --- | --- |
| `--dry-run` | Toon wat de strip zou wijzigen, zonder te schrijven |
| `--svg` | Schrijf SVG uit `.vsa` |
| `--verbose` | Detail per bestand |

# EXAMPLES

```cmd
scripts\oefenhoek-index.cmd --svg
scripts\oefenhoek-index.cmd --dry-run
```

# WHEN

Automatisch in `check` / `build` / `serve` / Pages-CI (alleen `--svg`).
Handmatig na een `.vsa`-edit als je geen volle check wilt draaien.

# SEE ALSO

- [check](../check/)
- [vsa-products](../vsa-products/) (Coria-`.vsa.mxl` — wél publicatiecontrole)
- [Publicatiecontrole](/handleiding/start/publicatiecontrole/)
- Workflow: [VSA → SVG en Coria](/handleiding/werktrajecten/vsa/)
