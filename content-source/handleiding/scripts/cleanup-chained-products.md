---
title: "cleanup-chained-products"
linkTitle: "cleanup-chained-products"
weight: 175
---

# NAME

`cleanup-chained-products` — ketting-afgeleiden (product van product) in
de catalogus melden of verwijderen

# SYNOPSIS

```cmd
scripts\cleanup-chained-products.cmd [map|bestand] [--apply]
```

Met `.\scripts` op PATH: `cleanup-chained-products …`. Korte hulp:
`h cleanup-chained-products` of `cleanup-chained-products -h`.

# DESCRIPTION

Soms zijn per ongeluk afgeleiden gemaakt *van* een afgeleide, bijvoorbeeld
een `.mp3` naast `{stam}.mvsa.mscz` in plaats van naast `{stam}.mvsa`.
Die kettingbestanden hoort de catalogus niet te hebben.

**Dit script verwijdert** bestanden waarvan de naam zo’n ketting is, onder
meer:

- twee notatie-extensies + nog iets: `{stam}.mvsa.mscz.mp3`, …
- kaal `{stam}.mscz.mscz` en alles met `.mscz.mscz.` erin
- `{stam}.mscz.mvsa.…` (afgeleide van een import-bewerkvorm)
- Score-IR / from-ir op `.mscz` of `.vsa` (die horen alleen bij `.mvsa`)

**Het laat staan** geldige enkele producten naast een bron, onder meer:

- `{stam}.mvsa.mscz`, `{stam}.mvsa.mp3`, `{stam}.vsa.svg`
- `{stam}.mscz.mvsa` (import-bewerkvorm zelf)
- `{stam}.mvsa.score-ir.json`, `{stam}.mvsa.from-ir.musicxml`
- `{stam}.mscz-1.svg` / scherm-SVG bij basis-`.mscz`

Standaardmap: `content-source\catalogus`. Zonder `--apply` alleen tonen
(dry-run); met `--apply` echt wissen.

# EXAMPLES

```cmd
scripts\cleanup-chained-products.cmd
scripts\cleanup-chained-products.cmd --apply
scripts\cleanup-chained-products.cmd content-source\catalogus\alleluia --apply
```

# WHEN

Na een productrun die kettingnamen heeft gemaakt, vóór je die rommel
commit. Product-scripts slaan afgeleide `*.mvsa.mscz` / `*.vsa.mscz` in
een map-scan over; alleen een expliciet CLI-bestandspad mag zo’n bron
nog zijn.

# SEE ALSO

[products](../products/),
[Publicatiecontrole](../../start/publicatiecontrole/),
[opkuisen](../opkuisen/)
