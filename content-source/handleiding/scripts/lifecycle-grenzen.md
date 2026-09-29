---
title: "lifecycle-grenzen"
linkTitle: "lifecycle-grenzen"
weight: 133
---

# NAME

`scripts\lifecycle-grenzen.cmd` — controleer grenzen Werkbank ↔ Catalogus

# SYNOPSIS

```cmd
scripts\lifecycle-grenzen.cmd [--fail]
```

# DESCRIPTION

Loopt `content-source\bibliotheek` na op signalen dat **werkbank-materiaal**
per ongeluk als catalogus-bron geldt:

- bestandsnamen **met spaties**;
- ruwe formats (`.cap`, `.capx`, `.musicxml`, `.xml`);
- een kale `.mxl` die geen product-sibling is (`.mscz.mxl` / `.vsa.mxl` /
  `.mvsa.mxl`), of een **verouderde** `{stam}.mxl` naast een `.vsa`/`.mscz`
  (hoort `{stam}.vsa.mxl` / `{stam}.mscz.mxl`).

Default: print problemen en eindigt met exitcode 0. Met `--fail`: exitcode
1 als er minstens één probleem is (handig vóór een strenge commit).

Zit **niet** standaard in `check` (catalogus-publicatiecontrole dekt
productversheid al). Gebruik dit apart als je twijfelt over maprommel.

# EXAMPLES

```cmd
scripts\lifecycle-grenzen.cmd
scripts\lifecycle-grenzen.cmd --fail
```

# WHEN

Na rommelen in mappen, of als `bieb accepteer` weigert en je wilt zien of
er al iets verkeerds onder `bibliotheek\` ligt. Model:
[Levenscyclus](/handleiding/start/levenscyclus/).

# SEE ALSO

- [werkbank-status](../werkbank-status/)
- [bieb accepteer](../bieb-accepteer/)
- [Publicatiecontrole](/handleiding/start/publicatiecontrole/)
