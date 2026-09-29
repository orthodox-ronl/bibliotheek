---
title: "audio"
linkTitle: "audio"
weight: 85
---

# audio

**Preview-audio** is een **actief** publicatiespoor: uit een canonieke
bron (`.mvsa`, basispartituur-`.mscz` of `.vsa`) hoort een afspeelbaar
`{stam}.{bron-ext}.mp3` te staan. Op de site verschijnt dan de knop
**Beluisteren**.

## Waartoe

Even de klank horen (idee van de melodie/harmonie), niet oefenen met
stemkeuze (dat blijft Coria via **Oefenen**) en niet het printblad
(dat blijft **Downloaden** / **Printen**).

## Eindresultaat

| Rol | Bestand |
| --- | --- |
| Bron | `{stam}.mvsa` / `{stam}.mscz` / `{stam}.vsa` |
| Preview-audio | `{stam}.mvsa.mp3` / `{stam}.mscz.mp3` / `{stam}.vsa.mp3` |

Meerdere bronnen in één bladermap mogen elk hun eigen mp3 hebben. De
Beluisteren-knop toont dan een keuzelijst (meerstemmig `.mvsa` eerst,
daarna MuseScore, daarna eenstemmig `.vsa`).

## Wanneer wel / wanneer niet

**Wel:** bij dezelfde bronnen als de Coria-`.mxl` (canonieke `.mvsa`,
basis-`.mscz`, `.vsa`), behalve mappen met `artefacten_handmatig: true`.
Ontbrekende of verouderde audio faalt `check --strict` / CI.

Bij `.vsa` syllabificeert `audio-products` in een **tijdelijk** bestand
vóór `vsa audio` — dezelfde stap als `vsa-products` voor Coria-`.vsa.mxl`.
De canonieke `.vsa` (en het SVG) blijven zonder orthografische `-`.

## Bestanden en scripts

- Lokaal maken: [audio-products](/handleiding/scripts/audio-products/)
- Alles tegelijk: [all-products](/handleiding/scripts/all-products/)
- Controle: [check](/handleiding/scripts/check/)
- Namen: [Publicatiecontrole](/handleiding/start/publicatiecontrole/)

## CI / handmatig

CI genereert geen MuseScore-audio. Vernieuw lokaal met `audio-products`
of `all-products`, commit bron én `.mp3`.

{{< navbuttons "mvsa|/handleiding/werktrajecten/mvsa/" "Werktrajecten|/handleiding/werktrajecten/" >}}
