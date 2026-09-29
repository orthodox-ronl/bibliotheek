---
title: "Werkbank (pre-productie)"
linkTitle: "Werkbank"
weight: 16
---

# Werkbank (pre-productie)

De **werkbank** is de lifecycle-fase waarin een uitvoeringsvorm nog
**niet** (of alleen als lege stub) als canonieke bron in de bibliotheek
staat. Hier reserveer je een id, haal je materiaal binnen, kuis je op,
layout je, en proefdraai je. Overzicht: [Levenscyclus](levenscyclus/).

{{< cue >}}
1. Bestand in `content-source\input\<herkomst>\` (of eerst `_inbox\`).
2. `scripts\update-werkvoorraad.cmd` — vul **Doel-id** in (niet raden).
3. Tussenwerk in `input\_werk\<publicatiestam>\` (niet in git).
4. Opkuisen / layout / review volgens Partituur of VSA.
5. Klaar? → [overgangscriteria](#overgangscriteria) → `bieb accepteer`
   → fase [Catalogus](catalogus/).
{{< /cue >}}

## Waar bestanden liggen

| Map | In git? | Rol |
| --- | --- | --- |
| `input\_inbox\` | Nee | Brievenbus; nog niet gekozen als te bewaren bron |
| `input\capella\` / `vow\` / `musescore\` / `musicxml\` / `pdf\` | Ja | Ruwe herkomst; **originele bestandsnaam** (spaties mag) |
| `input\_werk\<stam>\` | Nee | Tussenproducten (opgekuiste `.mxl`, layout-`.mscz`, proeven) |
| `bibliotheek\…\` met `--stub` | Ja | Alleen gereserveerd id / lege pagina (`voorzien`) |

Geen canonieke oefenbron onder `bibliotheek\` in deze fase — behalve een
bewuste stub. Zie [Waar ligt wat](waar-ligt-wat/).

## Toegestane bestanden (werkbank)

| Soort | Voorbeelden | Opmerking |
| --- | --- | --- |
| Ruwe input | `.capx`, `.mxl`, ruwe `.mscz`, PDF-scan, `.vsa` in `input\` | Herkomst bewaren |
| Tussenproduct | Opgekuiste `.mxl`, genormaliseerde `.mscz` in `_werk\` | Publicatiestam, geen spaties |
| Stub | Lege leaf via `bieb accepteer … --stub` | Nog geen partituur |

**Niet** in de catalogus-map zetten: ongekuiste Capella-`.mxl`, `.cap` /
`.capx`, of bestanden met spaties in de naam.

## Pijplijnen en scripts in deze fase

| Stap | Commando / HOW | Wat het hier doet |
| --- | --- | --- |
| Register | `scripts\update-werkvoorraad.cmd` | Rij per input; Doel-id / notitie bewaren |
| Status | `scripts\werkbank-status.cmd` | Open cases + `_werk` + stubs |
| Grenzen | `scripts\lifecycle-grenzen.cmd` | Waarschuwt als werkbank/catalogus door elkaar lopen |
| Opkuisen (zwaar) | `scripts\opkuisen.cmd` | Herkomstanalyse + inhoudsfixes; uitvoer naar `_werk\` |
| Layout | `scripts\layout.cmd` | Basispartituur-standaard → `_werk\<stam>\…mscz` |
| Review | MuseScore + [Reviewen](../partituur/4-reviewen/) | Menselijke check |
| VSA schrijven | [VSA](../vsa/) | Mag in `_werk` of klaar bestand klaarzetten voor acceptatie |
| Proefproducten | Optioneel `mscz-products` / `vsa-products` op een **proefpad** | Alleen om te kijken; catalogus-producten horen ná acceptatie |

### Zelfde naam, andere zwaarte: `opkuisen`

In de **werkbank** is `opkuisen` het zware werk: Capella-heuristieken,
inhoud opschonen, vaak met `-o` naar `_werk\`. In de **catalogus** gebruik
je `opkuisen` alleen gericht voor herstel op een al canonieke bron — niet
als “alles opnieuw uit de dump”. Detail: [opkuisen](../scripts/opkuisen/).

## Eén leidend spoor

Meerdere rijen in de werkvoorraad voor hetzelfde Doel-id mogen (Capella +
VOW). Kies **één** leidend spoor dat naar het bestand voor `bieb
accepteer` leidt. Zet in de notitie welk spoor leidend is. Andere inputs
blijven herkomst.

## Overgangscriteria (Werkbank → Catalogus)

Je mag overgaan als **alle** punten kloppen:

1. **Doel-id** is een geldig bibliotheek-id (drie lagen); zie
   [Id-register](/bibliotheek/id-register/) — niet verzinnen.
2. Er is een **bruikbaar bronbestand**: basispartituur-`.mscz`, `.vsa`,
   `.mvsa`, handmatig `.mscz` (later `artefacten_handmatig`), of
   `.tekstblad.md` — geen kale ongekuiste `.mxl` / `.capx`.
3. Bestandsnaam voor publicatie: **geen spaties**; stam = publicatiestam
   uit het id (of je laat `bieb accepteer` hernoemen).
4. Bij `.vsa` / `.mvsa`: `vsa validate` / `mvsa validate` slaagt (doet
   `bieb accepteer` standaard zelf).
5. Je hebt bewust gekozen welk input-spoor leidend is.

Dan:

```cmd
cd /d C:\Git\orthodox-ronl\bibliotheek
bieb accepteer
```

Daarna fase [Catalogus](catalogus/): producten maken en
`scripts\check.cmd --strict`.

HOW: [Opnemen in de bibliotheek](../publiceren/1-opnemen-in-bibliotheek/).
Werktraject: [Opnemen](../werktrajecten/opnemen-in-bibliotheek/).

## Overzicht op de site

- Special page: [Werkbank](/bibliotheek/speciaal/werkbank/)
- Uitklapbare tabel: werkvoorraad onderaan het
  [bibliotheek-overzicht](/bibliotheek/)

## Klaar als

Je weet waar het tussenwerk ligt, welk Doel-id hoort, en of je al aan de
overgangscriteria voldoet — of nog opkuisen/layout moet doen.

{{< navbuttons "Levenscyclus|/handleiding/start/levenscyclus/" "Catalogus|/handleiding/start/catalogus/" >}}
