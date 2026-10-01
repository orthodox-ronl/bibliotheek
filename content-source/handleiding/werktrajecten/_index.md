---
title: "Werktrajecten"
linkTitle: "Werktrajecten"
weight: 15
nav_sort: weight
aliases:
  - /handleiding/start/publicatietrajecten/
---

Een **werktraject** is een vaste pijplijn: van bronbestand naar eindproduct
dat koorleden (of jij als beheerder) op de site gebruiken. Elke pagina hier
beschrijft waartoe die pijplijn dient, wat het eindresultaat is, wanneer je
hem wel of niet gebruikt, welke bestanden in welke volgorde ontstaan, wat
GitHub Actions (CI) automatisch doet, en welke `scripts\….cmd`-regels je
lokaal plakt.

**Nog niet klaar met je pc?** Begin bij [Start](../start/) (programma’s,
mappen, woorden). Stapsgewijze MuseScore- of VSA-HOW’s staan onder
[Partituur](../partituur/) en [VSA](../vsa/). Commando-flags: [Scripts](../scripts/).

{{< cue >}}
- **Poort / lifecycle:** [Levenscyclus](../start/levenscyclus/) —
  Werkbank → Catalogus; [Opnemen](opnemen-in-catalogus/) — `bieb accepteer`
- **Namen / publicatiecontrole:** [Publicatiecontrole](../start/publicatiecontrole/) — bron vs afgeleide
- **Publicatiesporen:** [Basispartituur](basispartituur/), [VSA](vsa/),
  [mvsa](mvsa/), [audio](audio/), [Print-vel](print-vel/) (legacy `.print.mscz`),
  [Tekstblad](tekstblad/)
- **Site zichtbaar maken:** [Site-build](site-build/)
- **Apart:** [Markdown naar PDF](markdown-naar-pdf/),
  [Ingebedde VSA](ingebedde-vsa/)
{{< /cue >}}

## Hoe de trajecten in elkaar haken

```text
Werkbank (input/ + _werk/)
    |
    v
Opnemen in de catalogus  (bieb accepteer → Catalogus)
    |
    +-- Basispartituur  ->  PDF + Coria-.mxl + .mscz.mp3
    +-- VSA             ->  SVG + Coria-.vsa.mxl + .vsa.pdf + .vsa.mp3
    +-- mvsa            ->  Coria-.mvsa.mxl + .mvsa.pdf + .mvsa.mp3
    +-- Print-vel       ->  handmatige PDF
    +-- Tekstblad       ->  .tekstblad.md -> .tekstblad.pdf
    |
    v
Site-build  (check / build / serve, of CI)  ->  generated/site + GitHub Pages
```

[Markdown naar PDF](markdown-naar-pdf/) en [Ingebedde VSA](ingebedde-vsa/)
zijn aparte sporen (demo’s, handleidingen, samenstellingen). Die vervangen
geen bibliotheek-producten.

## Catalogus

| Werktraject | Waartoe (kort) | Pagina |
| --- | --- | --- |
| Opnemen in de catalogus | Ruw bestand bewaren en later als klaar oefenbestand in de catalogus zetten | [Opnemen](opnemen-in-catalogus/) |
| Basispartituur | MuseScore-basispartituur naar A4-PDF en Coria-`.mxl` | [Basispartituur](basispartituur/) |
| VSA | Eenstemmige `.vsa` naar SVG, Coria-`.vsa.mxl` en A4-`.vsa.pdf` | [VSA](vsa/) |
| mvsa | Meerstemmige `.mvsa` naar Coria-`.mvsa.mxl` en A4-`.mvsa.pdf` | [mvsa](mvsa/) |
| audio | Preview-`.mp3` voor Beluisteren (zelfde bronnen als Coria-MXL) | [audio](audio/) |
| Print-vel | Print-`.mscz` met handmatige PDF, buiten de basispartituur-keten | [Print-vel](print-vel/) |
| Tekstblad | Liturgische tekst/dialoog: `.tekstblad.md` naar A4-PDF | [Tekstblad](tekstblad/) |
| Site-build | `content-source` naar lokale site of GitHub Pages | [Site-build](site-build/) |
| Markdown naar PDF | Markdownblad met VSA naar A4-PDF (generiek / demo) | [Markdown naar PDF](markdown-naar-pdf/) |
| Ingebedde VSA | VSA buiten de catalogus naar SVG (en optioneel MXL) | [Ingebedde VSA](ingebedde-vsa/) |

**Bestandsnamen en publicatiecontroles** (bron = één extensie; afgeleide =
`{stam}.{bron-ext}.{doel-ext}`; wat CI controleert):
[Publicatiecontrole](../start/publicatiecontrole/). Termen: [Woorden](../start/woorden/).

{{< navbuttons "Start|/handleiding/start/" "Opnemen|/handleiding/werktrajecten/opnemen-in-catalogus/" >}}
