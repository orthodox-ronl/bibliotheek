---
title: "stichier-toon-6-groningen"
linkTitle: "stichier-toon-6-groningen"
weight: 10
publicatiestatus: concept
automatische_inhoud: false
formule_id: "stichier-toon-6-groningen"
---

# `stichier-toon-6-groningen`


![Formuleblad stichier-toon-6-groningen](template.svg)
| Veld         | Waarde    |
| ------------ | --------- |
| Soort        | stichier  |
| Toon         | 6         |
| Bron (in id) | groningen |
| same_as      | —         |
| also_used_as | —         |
| Aliassen     | —         |

Bronvermelding in de YAML: Koormap Groningen — stichiermelodie toon 6
(Moeder Gods-kondak; Heer ik roep / Laat mijn gebed).

## Speelplannen

Welk plan geldt, hangt af van het aantal tekstfrasen (strofes) in de VSA.

| Situatie                                      | Speelplan op het blad                                      |
| --------------------------------------------- | ---------------------------------------------------------- |
| Standaard                                     | `|:` 1, 2, 3 `:|` **laatste**                              |
| Aantal strofes is een veelvoud van 3          | `|:` 1, 2, 3 `:|` **voorlaatste**, **laatste**             |
| Verzamel met twee coupletten (6 + 5 = 11)     | couplet 1 als hierboven, daarna couplet 2 (`1,2,3,1,laatste`) |

**Vroeg uit de herhaling.** Als het strofe-aantal geen nette afronding van de
cycle is (bijvoorbeeld 5 of 8 strofes), stopt de herhaling van 1–2–3 alsnog
op tijd: de laatste tekstfrase krijgt altijd formulefrase *laatste*. Dat is
bedoeld gedrag, geen fout in de tekst alleen daarom.

**Verzamel-VSA.** Zet je beide coupletten in één bestand, dan telt de mapper
alle strofes samen (hier 11). Daarvoor bestaat plan `two-couplets`. Zonder
dat plan zou de machine één verkeerd speelplan over het hele bestand trekken.

De frase *voorlaatste* is een **eigen** melodie (niet stil hetzelfde als
frase 3 of 1). Zet in de VSA de sterke frasescheider `//` aan het **eind van
de een-na-laatste strofe**, zodat zangers al zien dat de volgende regel
*laatste* is.

Machinebestand: [stichier-toon-6-groningen/template.yaml](https://github.com/orthodox-ronl/VSA-tooling/blob/main/docs/specification-vsa-templates/library/stichier-toon-6-groningen/template.yaml).
Mappingregels (technisch): [mapping-vsa.md](https://github.com/orthodox-ronl/VSA-tooling/blob/main/docs/specification-vsa-templates/mapping-vsa.md).

Catalogus-voorbeeld (coupletten): [stichier/heer-ik-roep-toon-6]({{< relref "/catalogus/stichier/heer-ik-roep-toon-6" >}}).
Ook gebruikt met `formule: stichier` op liturgisch andere stukken, o.a.
[kondak Moeder Gods toon 6]({{< relref "/catalogus/kondak/moeder-gods-toon-6" >}}).
Handleiding: [Stichieren]({{< relref "/handleiding/start/stichieren" >}}).
