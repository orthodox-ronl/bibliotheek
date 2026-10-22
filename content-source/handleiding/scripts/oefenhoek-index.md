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

Met **`--svg`** schrijft dit commando een **legacy** plaatje van een
canonieke catalogus-`.vsa` naar `static\vsa\bladermap\…`. Het scherm
gebruikt dat plaatje alleen als er nog geen sibling `{stam}.vsa.svg`
naast de bron staat. Die sibling maak je met
[vsa-products](../vsa-products/); `check` eist daar een herkomststempel
voor. Hetzelfde geldt voor `.mvsa`: het webplaatje is `{stam}.mvsa.svg`
via [mvsa-products](../mvsa-products/), niet dit commando.

`check`, `build`, `serve` en de Pages-build draaien `--svg` nog vóór
Hugo, zodat de fallback bij de huidige `.vsa` past zolang de sibling
ontbreekt. Er is geen stempel en CI faalt niet op een verouderd
legacy-plaatje. Sidecar-bestanden `*.syl.vsa` worden overgeslagen. Een
basispartituur-`.mscz` in dezelfde map onderdrukt dit plaatje (een
`.print.mscz` niet).

Zonder flags haalt het script legacy auto-includes / score-shortcodes uit
bladermap-`index.md`. Pagina’s met shortcode `bieb` of met
`automatische_inhoud: false` worden niet aangepast.

# OPTIONS

| Optie | Betekenis |
| --- | --- |
| `--dry-run` | Toon wat de strip zou wijzigen, zonder te schrijven |
| `--svg` | Legacy plaatje uit `.vsa` naar `static\vsa\bladermap\` |
| `--verbose` | Detail per bestand |

# EXAMPLES

```cmd
scripts\oefenhoek-index.cmd --svg
scripts\oefenhoek-index.cmd --dry-run
```

# WHEN

Automatisch in `check` / `build` / `serve` / Pages-CI (alleen `--svg`),
als fallback. Na een wijziging aan een `.vsa` die op het scherm moet:
eerst `vsa-products`, niet alleen dit commando.

# SEE ALSO

- [check](../check/)
- [vsa-products](../vsa-products/) — `{stam}.vsa.svg` voor het scherm, mét stempel
- [Publicatiecontrole](/handleiding/start/publicatiecontrole/)
- Workflow: [VSA → SVG en Coria](/handleiding/werktrajecten/vsa/)
