---
title: "mvsa"
linkTitle: "mvsa"
weight: 80
---

# mvsa

**mvsa** (meerstemmige VSA) is een **actief** publicatiespoor: canonieke
bron `{stam}.mvsa`, afgeleiden `{stam}.mvsa.mxl` (Coria) en
`{stam}.mvsa.pdf` (A4 voor zangers).

## Waartoe

Meerstemmige notatie in tekstvorm bewerken en publiceren, met dezelfde
soort siblings als bij [VSA](../vsa/) (Coria) en
[Basispartituur](../basispartituur/) (PDF), maar vanuit `.mvsa`.

## Eindresultaat

| Rol | Bestand |
| --- | --- |
| Canonieke bron | `{stam}.mvsa` |
| Coria | `{stam}.mvsa.mxl` + `vsa-source-sha256` |
| Print-PDF | `{stam}.mvsa.pdf` + `vsa-source-sha256` |

In één bladermap mag ook een basispartituur-`.mscz` staan; elk spoor houdt
eigen siblings bij. Import-siblings `{stam}.mscz.mvsa` horen bij
[import-mvsa](/handleiding/scripts/import-mvsa/), niet bij dit spoor.

## Wanneer wel / wanneer niet

**Wel:** meerstemmige bron die je in `.mvsa` onderhoudt (alleluia’s,
litanieën, …). **Niet** als enige bron: eenstemmig werk → [VSA](../vsa/);
alleen MuseScore → [Basispartituur](../basispartituur/).

## Bestanden en scripts

- Lokaal producten: [mvsa-products](/handleiding/scripts/mvsa-products/)
- Controle: [check](/handleiding/scripts/check/) / CI
- Namen: [Publicatiecontrole](/handleiding/start/publicatiecontrole/)

## CI / handmatig

CI genereert geen MuseScore-PDF. Vernieuw lokaal met `mvsa-products`,
commit bron én siblings. Syntax: VSA-tooling
(`docs/specification-mvsa/`).

{{< navbuttons "Ingebedde VSA|/handleiding/werktrajecten/ingebedde-vsa/" "Werktrajecten|/handleiding/werktrajecten/" >}}
