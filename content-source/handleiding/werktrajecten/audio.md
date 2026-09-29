---
title: "audio"
linkTitle: "audio"
weight: 85
---

# audio

**Preview-audio** is een **optioneel** publicatiespoor: uit een canonieke
bron (`.mvsa`, basispartituur-`.mscz` of `.vsa`) maakt je een
afspeelbaar `{stam}.{bron-ext}.mp3`. Op de site verschijnt dan de knop
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

**Wel:** als je Beluisteren op de bladermap wilt. **Niet verplicht:**
ontbrekende audio faalt `check` niet. Zodra een mp3 bestaat, moet die
vers blijven bij wijzigingen in de bron.

## Bestanden en scripts

- Lokaal maken: [audio-products](/handleiding/scripts/audio-products/)
- Controle (bestaande siblings): [check](/handleiding/scripts/check/)
- Namen: [Publicatiecontrole](/handleiding/start/publicatiecontrole/)

## CI / handmatig

CI genereert geen MuseScore-audio. Vernieuw lokaal met `audio-products`,
commit bron én `.mp3`.

{{< navbuttons "mvsa|/handleiding/werktrajecten/mvsa/" "Werktrajecten|/handleiding/werktrajecten/" >}}
