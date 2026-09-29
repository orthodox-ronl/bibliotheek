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
- Hernoemen van bestaande ids gebeurt pas na akkoord op de tabel hieronder
{{< /cue >}}

## Drie soorten

| Soort | Betekenis | Voorbeelden (huidige ids) |
| --- | --- | --- |
| **Genre-emmer** | Catalogus van losse werken onder één genre. Elk werk is een **variant**. | `110-tropaar`, `120-kondak` |
| **Liturgische familie** | Zelfde liturgische rol of tekstfamilie; meerdere teksten of settings als variant. | antifonen, litanieën, communieverzen, prijsliederen, moeder-godsliederen |
| **Enkelvoudig werk** | Eén herkenbaar stuk; hoogstens settings of talen als variant. | `5-eniggeboren-zoon`, `28-wij-hebben-het-ware-licht`, `29-de-naam-des-heren-zij-gezegend` |

**Alias-varianten** (`alias_van`) blijven een apart mechanisme: dezelfde
variant onder een tweede naam (bijvoorbeeld maandag-tropaar = tropaar van
de Heilige Engelen). Dat is geen vierde soort zangstuk.

## Wat wél en niet in het id hoort

| Wel | Niet (op den duur) |
| --- | --- |
| Stabiele, leesbare naam (`tropaar`, `eerste-antifoon`) | Sorteernummer alleen voor mappenlijst (`110-`, `250-`) |
| Spellingnorm voor nieuwe ids (`johannes`, `alleluia`) | Afkortingen die alleen insiders kennen (`mg`, `zo-wk-mg`) |
| Volgorde via `weight` en via de koormap | Liturgienummer verplicht in elke bibliotheek-titel |

Nieuwe zangstukken volgen dit beleid meteen. Bestaande genummerde ids
blijven geldig tot een bewuste hernoem-golf.

## Inventaris (huidige top-level zangstukken)

Voorstel-soort en kandidaat-id zijn **richting**, geen migratie. Open
vragen staan onder de tabel.

| Huidig `zangstuk-id` | Voorstel-soort | Kandidaat-id (later) | Opmerking |
| --- | --- | --- | --- |
| `1-vredeslitanie` | liturgische familie of enkelvoudig | `vredeslitanie` of onder `litanie/…` | Zie open vraag litanieën |
| `2-eerste-antifoon` | liturgische familie | `eerste-antifoon` | Varianten: weekdagen, zondag, … |
| `3-eerste-kleine-litanie` | liturgische familie of enkelvoudig | `eerste-kleine-litanie` | Zie litanieën |
| `4-tweede-antifoon` | liturgische familie | `tweede-antifoon` | |
| `5-eniggeboren-zoon` | enkelvoudig werk | `eniggeboren-zoon` | |
| `6-derde-antifoon` | liturgische familie | `derde-antifoon` | |
| `7-kleine-intocht` | liturgische familie | `kleine-intocht` | |
| `7d-dialoog-met-diaken` | enkelvoudig werk | `dialoog-met-diaken` | |
| `8-trisagion` | liturgische familie | `trisagion` | Varianten: NL, slav, … |
| `9-prokimen` | liturgische familie | `prokimen` | |
| `9-alleluia` | liturgische familie | `alleluia` | |
| `10-evangelielezing` | enkelvoudig / liturgische plek | `evangelielezing` | Vaak tekstblad/dialoog |
| `11-dringende-litanie` | liturgische familie of enkelvoudig | `dringende-litanie` | Zie litanieën |
| `110-tropaar` | genre-emmer | `tropaar` | Eerste hernoem-kandidaat |
| `12-ontslapenen-litanie` | liturgische familie of enkelvoudig | `ontslapenen-litanie` | Zie litanieën |
| `120-kondak` | genre-emmer | `kondak` | Eerste hernoem-kandidaat |
| `13-catechumenen-litanie` | liturgische familie of enkelvoudig | `catechumenen-litanie` | Zie litanieën |
| `14-gelovigen-litanie` | liturgische familie of enkelvoudig | `gelovigen-litanie` | Zie litanieën |
| `15-cherubijnenhymne` | liturgische familie | `cherubijnenhymne` | Varianten = settings |
| `16-vragende-litanie` | liturgische familie of enkelvoudig | `vragende-litanie`? | Zie dubbele vragende |
| `17-vredeswens` | enkelvoudig werk | `vredeswens` | |
| `18-geloofsbelijdenis` | enkelvoudig werk | `geloofsbelijdenis` | |
| `19-eucharistische-canon` | liturgische familie | `eucharistische-canon` | |
| `20-moeder-godslied` | liturgische familie | `moeder-godslied` | |
| `21-en-allen` | enkelvoudig werk | `en-allen` | |
| `210-heer-red-uw-volk-en-zegen-uw-erfdeel` | enkelvoudig of tropaar-familie | open | Zie kruis/tropaar |
| `22-vragende-litanie` | liturgische familie of enkelvoudig | open | Zie dubbele vragende |
| `220-uw-heilig-kruis` | enkelvoudig of tropaar-familie | open | Zie kruis/tropaar |
| `23-onze-vader` | enkelvoudig werk | `onze-vader` | |
| `24-een-is-heilig` | enkelvoudig werk | `een-is-heilig` | |
| `25-communievers` | liturgische familie | `communievers` | |
| `250-prijslied` | liturgische familie / collectie | `prijslied` | |
| `26-gezegend-hij-die-komt` | enkelvoudig werk | `gezegend-hij-die-komt` | |
| `27-communiezang` | enkelvoudig of familie | `communiezang` | |
| `28-wij-hebben-het-ware-licht` | enkelvoudig werk | `wij-hebben-het-ware-licht` | |
| `29-de-naam-des-heren-zij-gezegend` | enkelvoudig werk | `de-naam-des-heren-zij-gezegend` | |

## Open vragen (beslispunten)

Beantwoord deze vóór een hernoem-golf buiten `tropaar` / `kondak`.

1. **Litanieën** — Eén zangstuk `litanie` met varianten `vrede`, `klein`,
   `vragend`, `dringend`, …? Of blijft elke litanie een eigen zangstuk
   (zoals nu), alleen zonder nummer in het id?

2. **Dubbele vragende litanie** — `16-vragende-litanie` en
   `22-vragende-litanie` staan op verschillende liturgische plekken. Is dat
   hetzelfde werk (één id, twee koormap-slots) of twee ids?

3. **Kruis / «Heer, red Uw volk»** — Hoe verhouden
   `210-heer-red-uw-volk-en-zegen-uw-erfdeel`, tropaar-alias
   `heer-red-uw-volk` en `220-uw-heilig-kruis` zich tot elkaar: één
   tekstfamilie onder `tropaar`, of bewuste aparte zangstukken?

4. **Cherubijnen en trisagion** — Duidelijk familie met settings als
   variant. Akkoord om nummers (`15-`, `8a-`) alleen in `linkTitle` /
   historische mapnamen te houden tot hernoemen?

## Wat al gebeurd is (zonder hernoemen)

- Overzicht-`weight` van genre-/collectie-emmers rechtgezet (`tropaar` 750,
  `kondak` 760, kruis-buurt 755/765, `prijslied` 3000), zodat ze niet meer
  tussen de eerste litanieën vallen.
- Leesbare `title` / `linkTitle` op een aantal slug-achtige variantpagina’s.

## Volgende stappen

1. Sitezoeken op platte tekst uit VSA/MVSA (eigen index).
2. Naamgevingsbeleid voor *nieuwe* ids vastzetten (dit blad +
   [Bibliotheek en koormappen](../bibliotheek-en-koormappen/)).
3. Hernoem-tooling; eerste golf naar verwachting alleen `tropaar` en
   `kondak`, na akkoord.

{{< navbuttons "Bibliotheek en koormappen|/handleiding/start/bibliotheek-en-koormappen/" "Woorden|/handleiding/start/woorden/" >}}
