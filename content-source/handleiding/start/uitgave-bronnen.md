---
title: "Uitgave-bronnen"
linkTitle: "Uitgave-bronnen"
weight: 85
---

# Uitgave-bronnen (Liturgikon, Meneon, koormappen, …)

In een `.vsa` of `.mvsa` staat bij de herkomst vaak een **korte naam**:
`Liturgikon, p.58`, `Meneon I, p.12-13`, `Koormap Groningen`. Die korte
naam hoort in `bron.uitgangspunt` (of bij meerstemmig werk in
`@bron "…"`). Deze pagina legt uit **welke uitgave** zo’n korte naam
bedoelt: titel, druk, jaar, uitgeverij — voor zover bekend.

**Waartoe:** een lichte copyright-trace en duidelijkheid voor beheerders,
zonder elke partituur vol te schrijven met ISBN’s.

De machineleesbare lijst staat in `data\bronnen.yaml` in de
repository-map `bibliotheek`. Werk die bij als je een druk of jaar
achterhaalt; deze pagina volgt die lijst.

## Hoe je een bron in een bestand zet

1. Kies de **korte naam** uit de tabel hieronder.
2. Voeg pagina of plek toe waar dat helpt (`Liturgikon, p.270`).
3. Zet dat in het frontmatter-veld `bron.uitgangspunt` van de `.vsa`
   (of in `@bron "…"` bij een `.mvsa`). De volledige sleutellijst staat
   in de repository in `docs\specs\vsa-frontmatter.md`.
4. Afwijkingen t.o.v. die bron: `bron.bewerking` (niet in de korte naam
   proppen).

Bij export gaat `bron.uitgangspunt` naar de **bronvermelding** van de
afgeleide bestanden: MusicXML-veld `source` (`.mxl`) en MuseScore-meta
`source` (`.mscz`, plus colofonregel “Bron: …”).

## Lijst (uit `data/bronnen.yaml`)

| Korte naam | Ook als | Opmerking |
| ---------- | ------- | --------- |
| Liturgikon | Liturgicon | Nederlandstalig liturgikon zoals in Hemelum/Groningen gebruikt; precieze druk nog vastleggen. |
| Meneon I | Meneon 1 | Eerste deel van het Meneon; in VSA vaak met pagina’s. |
| Koormap Groningen | koormap Groningen, Groningen | Praktijk-/koormap Groningen; geen handelsuitgave. |
| Hemelum | praktijk Hemelum | Lokale praktijk / zetting; vaak bewerking of arrangeur. |
| VOKN-25 | VOKN, VOKN 25 | Goddelijke Liturgie (Pasen 2000), uitgegeven door de Vereniging van Orthodoxen „Nikolaas van Myra”. Vaak melodiebron; lokale arrangeur in `bron.bewerking`. |
| Apostel | — | Apostelboek; pagina’s soms naast Liturgikon (bijv. communievers). |

Velden *volledige titel*, *druk*, *jaar* en *uitgeverij* zijn in
`data\bronnen.yaml` nog grotendeels leeg — vul ze bij wanneer je de
fysieke uitgave voor je hebt.

## Gerelateerd

- Frontmatter-spec (repo): `docs\specs\vsa-frontmatter.md`
- Werkbank-voorbeelden: `docs\voorbeelden\werkbank\`
- Partituur-colofon / MuseScore-meta: [Standaard-.mscz](../partituur/3-standaard-mscz/)

{{< navbuttons "Woorden|/handleiding/start/woorden/" "Publicatiecontrole|/handleiding/start/publicatiecontrole/" >}}
