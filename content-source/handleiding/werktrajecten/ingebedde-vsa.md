---
title: "Ingebedde VSA"
linkTitle: "Ingebedde VSA"
weight: 70
---

# Ingebedde VSA

`check`, `build`, `serve` en de Pages-build draaien geen
`vsa build-markdown` en maken geen embed-MusicXML onder `static\vsa\mxl\`.
Notatie op de bibliotheek-site komt uit een catalogusbron.

| Bron in de catalogus | Plaatje op het scherm | Commando |
| --- | --- | --- |
| `{stam}.vsa` | `{stam}.vsa.svg` ernaast | [products (vsa)](../../scripts/vsa-products/) |
| `{stam}.mvsa` | `{stam}.mvsa.svg` ernaast | [products (mvsa)](../../scripts/mvsa-products/) |

Zolang `{stam}.vsa.svg` ontbreekt, vult `oefenhoek-index --svg` nog een
legacy-plaatje onder `static\vsa\bladermap\`. Dat is een fallback, geen
apart werktraject voor demo- of handleidingpagina’s.

Een koormap toont die catalogusnotatie met shortcode `bieb`. Zie
[VSA](../vsa/) en [mvsa](../mvsa/).

{{< navbuttons "VSA|/handleiding/werktrajecten/vsa/" "mvsa|/handleiding/werktrajecten/mvsa/" >}}
