---
title: "VSA"
linkTitle: "VSA"
weight: 30
nav_sort: weight
---

**VSA** is de notatie voor tekst-plus-melodie in een gewoon tekstbestand
(extensie `.vsa`). `scripts\products.cmd --kinds vsa` maakt daar drie siblings
van: `{stam}.vsa.svg` (het plaatje op het scherm), `{stam}.vsa.pdf`
(download en print) en `{stam}.vsa.mxl` (**Oefenen** via ♪). `check`
controleert of die siblings bij de bron passen; `check` schrijft ze
niet. Zie [.vsa schrijven](1-vsa-schrijven/).

Pijplijn (waartoe, CI, commando’s): werktraject
[VSA → SVG en Coria](../werktrajecten/vsa/).

Voor een tropaar op **toon 4** kun je dat `.vsa`-bestand daarna combineren
met een formule-template. Dan komen alt, tenor en bas erbij (SATB). Dat
blad zet je vaak als print-vel neer (handmatige artefacten), niet als
automatische basispartituur — zie [template SATB](2-template-satb/).

Oefenbare `.vsa`-bestanden staan in het **bibliotheek**; het **koormap-slot**
in de liturgiemap toont ze via shortcode `bieb` (zelfde id
als de catalogus-map).

{{< cue >}}
- Antifoon / eenstemmig: `.vsa` in de catalogus → [schrijven](1-vsa-schrijven/) (SVG-plaatje + Coria-`.vsa.mxl`).
- Tropaar toon 4, meerstemmig blad: `.vsa` met `template: tropaar-toon-4` → [template SATB](2-template-satb/).
- Valideren: `vsa validate pad\naar\bestand.vsa`
{{< /cue >}}
