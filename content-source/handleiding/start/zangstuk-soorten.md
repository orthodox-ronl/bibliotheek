---
title: "Zangstuk-soorten"
linkTitle: "Zangstuk-soorten"
weight: 27
---

# Zangstuk-soorten

De bibliotheek gebruikt overal dezelfde drie lagen:
`zangstuk` → `variant` → `uitvoeringsvorm`. Niet elk zangstuk betekent
hetzelfde. Dit blad legt drie soorten uit, zodat ids, titels en later
hernoemen dezelfde taal spreken.

{{< cue >}}
- Soort zegt wat het zangstuk *is*; de koormap zegt waar je het in de
  dienst *zet*
- Liturgische nummers horen in de koormap en in Hugo-`weight`, niet per
  se in het `zangstuk-id`
- Hernoemen van bestaande ids gebeurt pas na akkoord (besluiten hieronder)
{{< /cue >}}

## Drie soorten

| Soort | Betekenis | Voorbeelden (huidige ids) |
| --- | --- | --- |
| **Genre-emmer** | Catalogus van losse werken onder één genre. Elk werk is een **variant**. | `tropaar`, `kondak` |
| **Liturgische familie** | Zelfde liturgische rol of tekstfamilie; meerdere teksten of settings als variant. | antifonen, **ektinia’s** (litanieën), communieverzen, prijsliederen, moeder-godsliederen, cherubijnenhymne |
| **Enkelvoudig werk** | Eén herkenbaar stuk; hoogstens settings of talen als variant. | `5-eniggeboren-zoon`, `28-wij-hebben-het-ware-licht`, `29-de-naam-des-heren-zij-gezegend` |

**Alias-varianten** (`alias_van`) blijven een apart mechanisme: dezelfde
variant onder een tweede naam (bijvoorbeeld maandag-tropaar = tropaar van
de Heilige Engelen). Dat is geen vierde soort zangstuk.

## Wat wél en niet in het id hoort

| Wel | Niet (op den duur) |
| --- | --- |
| Stabiele, leesbare naam (`tropaar`, `ektinia`, `eerste-antifoon`) | Sorteernummer alleen voor mappenlijst (`110-`, `250-`) |
| Spellingnorm voor nieuwe ids (`johannes`, `alleluia`) | Afkortingen die alleen insiders kennen (`mg`, `zo-wk-mg`) |
| Volgorde via `weight` en via de koormap | Liturgienummer verplicht in elke bibliotheek-titel |

Nieuwe zangstukken volgen dit beleid meteen. Bestaande genummerde ids
blijven geldig tot een bewuste hernoem-golf.

## Besluiten (vastgelegd)

1. **Ektinia’s** — Eén zangstuk-id `ektinia` (meervoud/familie).
   **Litanieën** is synoniem/alias in titels en zoeken, niet een tweede
   canonieke id. Varianten = soort ektinia (`vrede`, `kleine`,
   `vragend`, `dringend`, …).

2. **Vragende ektinia** — `16-vragende-litanie` en `22-vragende-litanie`
   zijn **hetzelfde werk**: één variant onder `ektinia` (bijv.
   `ektinia/vragend/…`). De twee liturgische plekken zijn alleen
   **koormap-slots** die naar datzelfde id wijzen.

3. **Kruis / «Heer, red Uw volk»** — `210-heer-red-uw-volk-en-zegen-uw-erfdeel`,
   tropaar-alias `heer-red-uw-volk` en `220-uw-heilig-kruis` horen bij de
   **tropaar**-familie (varianten onder `tropaar` na migratie), geen
   aparte top-level zangstukken op den duur.

4. **Cherubijnen / trisagion (VO-nummers)** — Het zangstuk heet gewoon
   `cherubijnenhymne` / `trisagion` (geen `15-` / `8-` in het
   zangstuk-id). De codes **15b, 15c, 15d, …** komen uit de index van de
   Vereniging van Orthodoxen en onderscheiden settings die anders
   botsen (twee verschillende Kastorski’s). Die code hoort op
   **variant-niveau**, in id én zichtbaar label — niet alleen via
   beluisteren.

   Voorbeeld (richting, nog niet gemigreerd):

   | Laag | Voorbeeld |
   | --- | --- |
   | Zangstuk | `cherubijnenhymne` — titel «Cherubijnenhymne» |
   | Variant | `15c-kastorski` — `linkTitle` «Kastorski (15c)» |
   | Variant | `15d-kastorski` — `linkTitle` «Kastorski (15d)» |
   | Uitvoeringsvorm | `hemelum`, … |

   Zo zeg je in gewone taal «de cherubijnenhymne», en bij de keuze
   tussen twee Kastorski’s zie je **welke** zonder te moeten afspelen.
   Zelfde patroon voor trisagion-varianten (`8a-nederlands`, …).

## Inventaris (huidige top-level → richting)

| Huidig `zangstuk-id` | Soort | Kandidaat-id (later) | Opmerking |
| --- | --- | --- | --- |
| `1-vredeslitanie` | liturgische familie | `ektinia` (variant `vrede`) | Besluit 1 |
| `2-eerste-antifoon` | liturgische familie | `eerste-antifoon` | |
| `3-eerste-kleine-litanie` | liturgische familie | `ektinia` (variant `kleine` / `eerste-kleine`) | Besluit 1 |
| `4-tweede-antifoon` | liturgische familie | `tweede-antifoon` | |
| `5-eniggeboren-zoon` | enkelvoudig werk | `eniggeboren-zoon` | |
| `6-derde-antifoon` | liturgische familie | `derde-antifoon` | |
| `7-kleine-intocht` | liturgische familie | `kleine-intocht` | |
| `7d-dialoog-met-diaken` | enkelvoudig werk | `dialoog-met-diaken` | |
| `8-trisagion` | liturgische familie | `trisagion` | Varianten houden VO-/settinglabel (besluit 4) |
| `9-prokimen` | liturgische familie | `prokimen` | |
| `9-alleluia` | liturgische familie | `alleluia` | |
| `10-evangelielezing` | enkelvoudig / liturgische plek | `evangelielezing` | |
| `11-dringende-litanie` | liturgische familie | `ektinia` (variant `dringend`) | Besluit 1 |
| `tropaar` | genre-emmer | `tropaar` | Was `110-tropaar` (hernoemd) |
| `12-ontslapenen-litanie` | liturgische familie | `ektinia` (variant `ontslapenen`) | Besluit 1 |
| `kondak` | genre-emmer | `kondak` | Was `120-kondak` (hernoemd) |
| `13-catechumenen-litanie` | liturgische familie | `ektinia` (variant `catechumenen`) | Besluit 1 |
| `14-gelovigen-litanie` | liturgische familie | `ektinia` (variant `gelovigen`) | Besluit 1 |
| `15-cherubijnenhymne` | liturgische familie | `cherubijnenhymne` | VO-codes op variant (besluit 4) |
| `16-vragende-litanie` | liturgische familie | `ektinia` (variant `vragend`) | Zelfde als 22 (besluit 2) |
| `17-vredeswens` | enkelvoudig werk | `vredeswens` | |
| `18-geloofsbelijdenis` | enkelvoudig werk | `geloofsbelijdenis` | |
| `19-eucharistische-canon` | liturgische familie | `eucharistische-canon` | |
| `20-moeder-godslied` | liturgische familie | `moeder-godslied` | |
| `21-en-allen` | enkelvoudig werk | `en-allen` | |
| `210-heer-red-uw-volk-en-zegen-uw-erfdeel` | genre-emmer (tropaar) | onder `tropaar` | Besluit 3 |
| `22-vragende-litanie` | liturgische familie | `ektinia` (variant `vragend`) | Alias/slot van 16 (besluit 2) |
| `220-uw-heilig-kruis` | genre-emmer (tropaar) | onder `tropaar` | Besluit 3 |
| `23-onze-vader` | enkelvoudig werk | `onze-vader` | |
| `24-een-is-heilig` | enkelvoudig werk | `een-is-heilig` | |
| `25-communievers` | liturgische familie | `communievers` | |
| `250-prijslied` | liturgische familie / collectie | `prijslied` | |
| `26-gezegend-hij-die-komt` | enkelvoudig werk | `gezegend-hij-die-komt` | |
| `27-communiezang` | enkelvoudig of familie | `communiezang` | |
| `28-wij-hebben-het-ware-licht` | enkelvoudig werk | `wij-hebben-het-ware-licht` | |
| `29-de-naam-des-heren-zij-gezegend` | enkelvoudig werk | `de-naam-des-heren-zij-gezegend` | |

## Wat al gebeurd is

- Overzicht-`weight` van genre-/collectie-emmers rechtgezet (`tropaar` 750,
  `kondak` 760, kruis-buurt 755/765, `prijslied` 3000).
- Leesbare `title` / `linkTitle` op een aantal slug-achtige variantpagina’s.
- Sitezoeken + lyrics-producten (zie [Zoeken](/bibliotheek/zoeken/)).
- Eerste hernoem-golf: `110-tropaar` → `tropaar`, `120-kondak` → `kondak`
  (oude URL’s via Hugo-`aliases`).
- Ektinia-golf: litanie-zangstukken geconsolideerd onder `ektinia`
  (varianten `vrede`, `kleine`, `dringend`, `ontslapenen`, `catechumenen`,
  `gelovigen`, `vragend`). `16` en `22` vragende → één variant; koormap-slots
  blijven gescheiden. Script: `scripts/migrate_ektinia.py`.

## Volgende stappen

1. Latere golven: cherubijnen/trisagion zonder zangstuk-nummer,
   kruisstukken onder `tropaar`.

{{< navbuttons "Bibliotheek en koormappen|/handleiding/start/bibliotheek-en-koormappen/" "Woorden|/handleiding/start/woorden/" >}}
