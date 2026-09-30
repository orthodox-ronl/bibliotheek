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
- Geen vierde padlaag «collectie» — zie besluit 5
- Hernoemen van bestaande ids gebeurt pas na akkoord (besluiten hieronder)
{{< /cue >}}

## Drie soorten

| Soort | Betekenis | Voorbeelden (huidige ids) |
| --- | --- | --- |
| **Genre-emmer** | Catalogus van losse werken onder één genre. Elk werk is een **variant**. | `tropaar`, `kondak` |
| **Liturgische familie** | Zelfde liturgische rol of tekstfamilie; meerdere teksten of settings als variant. | `ektinia`, `cherubijnenhymne`, `trisagion`, antifonen, `prokimen`, `alleluia`, `prijslied`, `moeder-godslied` |
| **Enkelvoudig werk** | Eén herkenbaar stuk; hoogstens settings of talen als variant. | `eniggeboren-zoon`, `wij-hebben-het-ware-licht`, `de-naam-des-heren-zij-gezegend` |

**Alias-varianten** (`alias_van`) blijven een apart mechanisme: dezelfde
variant onder een tweede naam (bijvoorbeeld maandag-tropaar = tropaar van
de Heilige Engelen). Dat is geen vierde soort zangstuk.

De woorden *genre-emmer*, *liturgische familie* en *enkelvoudig werk*
zijn **cataloguslabels** in deze handleiding. Ze zijn geen nieuwe
org-termen in de glossary van `bron`, en ze vormen geen extra maplaag
onder `content-source\bibliotheek\`.

## Padmodel: geen collectie-laag

Het bibliotheek-id blijft altijd drie padsegmenten:

`zangstuk-id` / `variant-id` / `uitvoeringsvorm-id`

Daaronder liggen de bestanden (`.vsa`, `.mscz`, …): dat is de
**representatie** uit de org-glossary, geen vierde URL-segment.

**Collectie** in
[Bibliotheek en koormappen](/handleiding/start/bibliotheek-en-koormappen/)
is een *soort koormap* (thematische view, bijvoorbeeld «alle
cherubijnen»). Dat is geen tussenmap boven zangstukken.

### Waarom geen extra map «collectie»

Stel je de bibliotheek voor als een ladekast. Elke lade heeft een naam
(`tropaar`, `eerste-antifoon`, `eniggeboren-zoon`). In de lade zitten
varianten; daaronder de uitvoeringsvorm die je oefent. Shortcode `bieb`,
publicatiestam, zoekindex en ID-REGISTER verwachten precies die drie
stukken.

Een tussenmap als `content-source\bibliotheek\genres\tropaar\…` zou die
afspraak breken: tooling zou de eerste drie padstukken als id lezen en
colofon, `bieb` en zoeken zouden niet meer kloppen — tenzij alles
org-breed wordt omgebouwd. Dat is disproportioneel: genre-emmers werken
al als `zangstuk-id`.

### Padvoorbeelden

| Soort | Voorbeeld-id | Betekenis |
| --- | --- | --- |
| Genre-emmer | `tropaar/zondag-toon-3/groningen` | Catalogus «Troparen»; elk werk = variant |
| Liturgische familie | `ektinia/kleine/hemelum` | Familie «Ektinia»; soort ektinia = variant |
| Familie + VO-code | `cherubijnenhymne/15c-kastorski/hemelum` | Setting/VO-label op variant |
| Enkelvoudig werk | `eniggeboren-zoon/default/hemelum` (kandidaat: `eniggeboren-zoon/…`) | Eén stuk; `default` tot er een tweede setting is |

### Spanning met de org-glossary (bewust)

De glossary in `bron` zegt: varianten onder één zangstuk delen dezelfde
liturgische functie. Bij `tropaar` en `kondak` is de variant juist *welk*
tropaar of kondak (andere tekst of feestdag). Dat is een bewuste
cataloguskeuze van de bibliotheek: browsen op genre. De liturgische plek
in de dienst blijft in de **koormap**. Die spanning lossen we niet op met
een vierde padlaag.

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

   Voorbeeld:

   | Laag | Voorbeeld |
   | --- | --- |
   | Zangstuk | `cherubijnenhymne` — titel «Cherubijnenhymne» |
   | Variant | `15c-kastorski` — `linkTitle` «Kastorski (15c)» |
   | Variant | `15d-kastorski` — `linkTitle` «Kastorski (15d)» |
   | Uitvoeringsvorm | `hemelum`, … |

   Zo zeg je in gewone taal «de cherubijnenhymne», en bij de keuze
   tussen twee Kastorski’s zie je **welke** zonder te moeten afspelen.
   Zelfde patroon voor trisagion-varianten (`8a-nederlands`, …).

5. **Geen collectie-padlaag** — Genre-emmers en liturgische families blijven
   een gewoon `zangstuk-id`. Geen tussenmap en geen vierde id-segment.
   «Collectie» blijft een koormap-type. Zie [Padmodel](#padmodel-geen-collectie-laag)
   hierboven. Geen glossary-PR op `bron` nodig voor dit besluit.

## Inventaris (stand na PR #16–#20)

Kolom **Huidig** = mapnaam onder `content-source\bibliotheek\` nu.
Kolom **Kandidaat** = beoogd id na een latere hernoem-golf (1:1, tenzij
anders vermeld).

### Klaar (geen nummer meer in het zangstuk-id)

| Huidig `zangstuk-id` | Soort | Opmerking |
| --- | --- | --- |
| `tropaar` | genre-emmer | Was `110-tropaar`; kruisvarianten `heer-red-uw-volk`, `uw-heilig-kruis` eronder |
| `kondak` | genre-emmer | Was `120-kondak` |
| `ektinia` | liturgische familie | Was aparte litanie-zangstukken; koormap-slots houden pleknamen |
| `cherubijnenhymne` | liturgische familie | Was `15-cherubijnenhymne`; VO-codes op variant |
| `trisagion` | liturgische familie | Was `8-trisagion`; VO-/taallabel op variant |
| `eerste-antifoon` | liturgische familie | Was `2-eerste-antifoon` |
| `tweede-antifoon` | liturgische familie | Was `4-tweede-antifoon` |
| `derde-antifoon` | liturgische familie | Was `6-derde-antifoon` |
| `kleine-intocht` | liturgische familie | Was `7-kleine-intocht` |
| `prokimen` | liturgische familie | Was `9-prokimen`; koormap-slot was `9a-prokimen` |
| `alleluia` | liturgische familie | Was `9-alleluia`; koormap-slot was `9b-alleluia` |
| `prijslied` | liturgische familie | Was `250-prijslied` |
| `eniggeboren-zoon` | enkelvoudig werk | Was `5-eniggeboren-zoon` |
| `dialoog-met-diaken` | enkelvoudig werk | Was `7d-dialoog-met-diaken` |
| `evangelielezing` | enkelvoudig / liturgische plek | Was `10-evangelielezing` |
| `vredeswens` | enkelvoudig werk | Was `17-vredeswens` |
| `geloofsbelijdenis` | enkelvoudig werk | Was `18-geloofsbelijdenis` |
| `eucharistische-canon` | liturgische familie | Was `19-eucharistische-canon`; koormap-slot was `19a-eucharistische-kanon` |
| `moeder-godslied` | liturgische familie | Was `20-moeder-godslied` |
| `en-allen` | enkelvoudig werk | Was `21-en-allen` |
| `onze-vader` | enkelvoudig werk | Was `23-onze-vader` |
| `een-is-heilig` | enkelvoudig werk | Was `24-een-is-heilig` |
| `communievers` | liturgische familie | Was `25-communievers` |
| `gezegend-hij-die-komt` | enkelvoudig werk | Was `26-gezegend-hij-die-komt` |
| `communiezang` | enkelvoudig of familie | Was `27-communiezang` |
| `wij-hebben-het-ware-licht` | enkelvoudig werk | Was `28-wij-hebben-het-ware-licht` |
| `de-naam-des-heren-zij-gezegend` | enkelvoudig werk | Was `29-de-naam-des-heren-zij-gezegend` |

Er staan geen genummerde top-level zangstuk-ids meer onder
`content-source\bibliotheek\` (behalve variant-ids zoals `9a-…` /
`15c-…` / `20d-…` en koormap-litanie-slots die bewust de pleknaam
houden).

### Geen zangstuk-taxonomie

| Map | Rol |
| --- | --- |
| `speciaal` | Hulppagina’s (voorzien, ongerefereerd, …) |
| `zoeken` | Sitezoeken |

## Wat al gebeurd is

- Overzicht-`weight` van genre-/familie-emmers rechtgezet (`tropaar` 750,
  `kondak` 760, kruis-buurt 755/765, `prijslied` 3000).
- Leesbare `title` / `linkTitle` op een aantal slug-achtige variantpagina’s.
- Sitezoeken + lyrics-producten (zie [Zoeken](/bibliotheek/zoeken/)).
- Eerste hernoem-golf: `110-tropaar` → `tropaar`, `120-kondak` → `kondak`
  (oude URL’s via Hugo-`aliases`).
- Ektinia-golf: litanie-zangstukken geconsolideerd onder `ektinia`
  (varianten `vrede`, `kleine`, `dringend`, `ontslapenen`, `catechumenen`,
  `gelovigen`, `vragend`). `16` en `22` vragende → één variant; koormap-slots
  blijven gescheiden. Script: `scripts/migrate_ektinia.py`.
- Cherubijnen-golf: `15-cherubijnenhymne` → `cherubijnenhymne`; variant-
  `linkTitle` met VO-label (bijv. «Kastorski (15c)»).
- Trisagion-golf: `8-trisagion` → `trisagion`.
- Kruis-golf: `210-heer-red-uw-volk-en-zegen-uw-erfdeel` →
  `tropaar/heer-red-uw-volk`; `220-uw-heilig-kruis` →
  `tropaar/uw-heilig-kruis`. Script: `scripts/migrate_tropaar_kruis.py`.
- Koormap-slotmappen voor trisagion/cherubijnenhymne hernoemd zodat
  inhoudsopgave-links en mapnamen weer overeenkomen.
- Antifonen + intocht: `2-eerste-antifoon` → `eerste-antifoon`,
  `4-tweede-antifoon` → `tweede-antifoon`, `6-derde-antifoon` →
  `derde-antifoon`, `7-kleine-intocht` → `kleine-intocht` (inclusief
  koormap-slots weekdagen/zondag).
- Prokimen + alleluia: `9-prokimen` → `prokimen`, `9-alleluia` →
  `alleluia`; koormap-slots `9a-prokimen` → `prokimen`,
  `9b-alleluia` → `alleluia` (TOC-kolom blijft 9a/9b).
- Prijslied: `250-prijslied` → `prijslied`.
- Enkelvoudige / overige genummerde zangstukken: `5`, `7d`, `10`,
  `17`–`29` zonder liturgienummer in het zangstuk-id; koormap-slots
  meegenomen (inclusief `19a-eucharistische-kanon` →
  `eucharistische-canon`).

## Volgende stappen

1. Eventueel `speciaal` beoordelen (utility, geen zangstuk).
2. Hernoem-tooling (koormap-slots automatisch + slotlink-check) uit
   stash landen — nu alle hernoemingen inhoudelijk klaar zijn.
3. PR van deze branch naar `development`.

{{< navbuttons "Bibliotheek en koormappen|/handleiding/start/bibliotheek-en-koormappen/" "Woorden|/handleiding/start/woorden/" >}}
