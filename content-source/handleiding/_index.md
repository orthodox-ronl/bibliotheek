---
title: "Handleiding voor beheerders"
linkTitle: "Handleiding"
weight: 90
hide_page_list: true
hide_section_list: true
---

Deze handleiding is bedoeld voor **beheerders**: mensen die zangmateriaal
klaarzetten in deze bibliotheek. Het einddoel is een pagina waarop koorleden
kunnen oefenen (of, bij een printvel, een PDF in de koormap).

Koorleden die alleen willen zingen, gebruiken de
[bibliotheek](/overzichten/) of een [koormap](/koormappen/), niet deze handleiding.

Je hoeft geen programmeur te zijn. Wel een eenmalige pc-setup: Git, Python
3.14, Hugo Extended, MuseScore 4, ffmpeg, de juiste **PATH**-mappen, de
repository-map **`bibliotheek`**, en het **Windows-opdrachtvenster** (`cmd`).
Stappen en controletabel: [Wat heb je nodig](start/wat-heb-je-nodig/).

## Wat vind je waar

| Onderdeel | Voor wie / waartoe |
| --- | --- |
| [Start](start/) | Beginnende beheerder: programma’s, mappen, woorden, model bibliotheek/koormap |
| [Levenscyclus](start/levenscyclus/) | Werkbank vs catalogus: status per uitvoeringsvorm, overgang, scripts |
| [Werktrajecten](werktrajecten/) | Per productpijplijn: waartoe, eindresultaat, wanneer wel/niet |
| [Partituur](partituur/) | Stapsgewijze HOW in MuseScore |
| [VSA](vsa/) | HOW: `.vsa` schrijven |
| [Publiceren](publiceren/) | Opnemen met `bieb accepteer`, koormap-slot, publicatiestatus |
| [Scripts](scripts/) | Man-pages van `scripts\….cmd` |

**Bibliotheek** = catalogus van oefenbestanden. **Koormap** = geordende
route (nu vooral de Hemelum-liturgiemap) met slots die via `bieb`
verwijzen. Model: [Catalogus en koormappen](start/catalogus-en-koormappen/).
Lifecycle: [Levenscyclus](start/levenscyclus/) (Werkbank → Catalogus).

Bestaand id: [Zoeken](/overzichten/zoeken/). Hemelum-naslag: [Id-register](/overzichten/id-register/).

{{< navbuttons "Start|/handleiding/start/" "Levenscyclus|/handleiding/start/levenscyclus/" >}}
