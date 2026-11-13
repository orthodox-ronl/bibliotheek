---
title: "stichier-toon-3-groningen"
linkTitle: "stichier-toon-3-groningen"
weight: 3
publicatiestatus: concept
automatische_inhoud: false
formule_id: "stichier-toon-3-groningen"
---

# `stichier-toon-3-groningen`


![Formuleblad stichier-toon-3-groningen](template.svg)
| Veld         | Waarde    |
| ------------ | --------- |
| Soort        | stichier  |
| Toon         | 3         |
| Bron (in id) | groningen |
| same_as      | —         |
| also_used_as | —         |
| Aliassen     | —         |

Bronvermelding in de YAML: Koormap Groningen — stichiermelodie toon 3
(Heer ik roep / Laat mijn gebed; MSCZ-schets). Pitches provisional.
Cycle is **1–2** (niet 1–2–3 zoals bij toon 6).

## Speelplannen

Welk plan geldt, hangt af van het aantal tekstfrasen (strofes) in de VSA.

| Situatie                                      | Speelplan op het blad                                        |
| --------------------------------------------- | ------------------------------------------------------------ |
| Standaard                                     | `|:` 1, 2 `:|` …, **laatste**                                |
| Aantal strofes is een veelvoud van 3 (≥ 6)    | `|:` 1, 2 `:|` **voorlaatste**, **laatste**                  |
| Verzamel met twee coupletten (6 + 5 = 11)     | couplet 1 als hierboven, daarna couplet 2 (`1,2,1,2,laatste`) |

**Vroeg uit de herhaling.** Past het strofe-aantal niet netjes op cycle 1–2,
dan stopt de herhaling op tijd en krijgt de laatste tekstfrase formulefrase
*laatste* (bijvoorbeeld bij 5 strofes: `1,2,1,2,laatste`).

**Verzamel-VSA.** Zet je beide coupletten in één bestand, dan telt de mapper
alle strofes samen (hier 11). Daarvoor bestaat plan `two-couplets`.

De frase *voorlaatste* is een **eigen** frase-id (zelfde open contour als
frase 1). Zet in de VSA de sterke frasescheider `//` aan het **eind van de
een-na-laatste strofe**.

Het plaatje hierboven is voorlopig het schermbeeld van het catalogusvoorbeeld
(couplet 1), geen apart formuleblad uit MuseScore.

Machinebestand: [stichier-toon-3-groningen/template.yaml](https://github.com/orthodox-ronl/VSA-tooling/blob/main/docs/specification-vsa-templates/library/stichier-toon-3-groningen/template.yaml).
Mappingregels (technisch): [mapping-vsa.md](https://github.com/orthodox-ronl/VSA-tooling/blob/main/docs/specification-vsa-templates/mapping-vsa.md).

Catalogus-voorbeeld (coupletten): [stichier/heer-ik-roep-toon-3]({{< relref "/catalogus/stichier/heer-ik-roep-toon-3" >}}).
Handleiding: [Stichieren]({{< relref "/handleiding/start/stichieren" >}}).
