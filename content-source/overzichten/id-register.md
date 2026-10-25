---
title: "Id-register Hemelum"
linkTitle: "Id-register"
weight: 30
publicatiestatus: concept
automatische_inhoud: false
vsa_nav_exclude: true
aliases:
  - /catalogus/id-register/
---

# Id-register — Hemelum: id-naslag en reserveringen

Dit is **geen** bron van waarheid voor wat er in de catalogus staat.
Wat er wél bestaat, zie je in de [catalogus](/overzichten/) en de
automatische lijsten onder [Speciaal](/overzichten/speciaal/) (o.a.
Oefenbaar, Voorzien, Ongerefereerd). Nieuw werk gaat via
`bieb accepteer`, niet via deze pagina.

**Waar dit register wél voor is:** afspraken en naslag voor de
liturgiemap Hemelum — welk koormap-pad bij welk catalogus-id hoort,
welke ids nog gereserveerd of voorzien zijn, en welke conventies
(taalsuffix, `default`, …) we daarbij hanteren. Handmatig bijgehouden;
kan achterlopen op de catalogus.

Een catalogus-id heeft drie lagen: `zangstuk-id` / `variant-id` /
`uitvoeringsvorm-id` (elk segment `[a-z0-9_-]+`). De **publicatiestam**
voor basispartituur-bestanden is
`{zangstuk}-{variant}-{uitvoeringsvorm}`.

De migratietabellen SCORE / PRINT / STUB staan onder
[Geschiedenis](#geschiedenis-hemelum-migratie).

---

## Prokimen / alleluia (Kiev + znameni-reservering)

**Koormap-slots:** `9a-prokimen/` (prokimens eerder in de liturgie) en
`9b-alleluia/`. In de **catalogus** is `9a-` / `9b-` op de *variant*-laag
de melodieklasse (Kiev / znameni), niet het liturgienummer.

| Koormap-pad | Bibliotheek-id (voorbeeld) | Status |
| --- | --- | --- |
| `9a-prokimen/weekdagen/` | `prokimen/9a-maandag/groningen` … `9a-zaterdag` | VSA; compositieblad |
| `9a-prokimen/zondag-toon-N/` | `prokimen/9a-zondag-toon-N/groningen` + `alleluia/9a-toon-N/groningen` | alleluia: `.mvsa` (reviewable); prokimen zondag: voorzien |
| `9b-alleluia/` | `alleluia/9a-toon-1/groningen` … `9a-toon-8` | `.mvsa` (reviewable) |

**Znameni (alleen register):** `prokimen/9b-{naam}/{uitvoeringsvorm}`,
`alleluia/9b-toon-{1..8}/{uitvoeringsvorm}` — nog geen leafs.

## Tropaar / kondak

Zangstuk-ids `tropaar/` en `kondak/`. Variant bv. `zondag-toon-3`,
`maandag-toon-4`, `nikolaas-van-myra-toon-4`. Alias-varianten: veld
`alias_van` op de variant-`_index.md` (geen tweede `.vsa`, geen
uitvoeringsvorm-map).

| Voorbeeld | Id |
| --- | --- |
| Zondag tropaar toon 1 | `tropaar/zondag-toon-1/groningen` |
| Weekdag + alias | canonieke variant `tropaar/maandag-toon-4` ← alias `tropaar/heilige-engelen-toon-4` |
| Nikolaas tropaar | `tropaar/nikolaas-van-myra-toon-4/hemelum` |
| Nikolaas kondak | `kondak/nikolaas-van-myra-toon-3/hemelum` |
| Moeder Gods kondak | `kondak/moeder-gods-toon-6/hemelum` |
| Losse Hemelum-troparen | `tropaar/heilige-martelaren-toon-4/hemelum`, `…/icoon-moeder-gods-vladimir-toon-4/…`, `…/mantel-moeder-gods-toon-4/…` |
| Uw heilig kruis (koormap) | `troparen-en-kondaken/uw-heilig-kruis/` → `tropaar/uw-heilig-kruis/hemelum` |

`default` als variant-id betekent: één uitvoeringsvorm in Hemelum, geen
geneste varianten in de koormap.

## Taal op de uitvoeringsvorm (voorkeursconventie)

Nederlands vs kerkslavisch = **aparte uitvoeringsvormen**. Geen suffix =
Nederlands; andere talen via suffix op het derde segment. Handleiding
(beheerder):
[Taalvarianten](/handleiding/start/catalogus-en-koormappen/#taalvarianten-op-de-uitvoeringsvorm).

| Suffix op uitvoeringsvorm-id | Betekenis | Wanneer |
| --- | --- | --- |
| *(geen)* | Nederlands | Altijd voor NL (ook naast een andere taal) |
| `-ksl` | Kerkslavisch, Cyrillisch | KSL-uitvoeringsvorm |
| `-nl-ksl` | Mengvorm NL + kerkslavisch | Zeldzaam; één partituur met beide |

Voorbeelden (publicatiestam):

- `cherubijnenhymne-15c-kastorski-hemelum` — Nederlands (geen suffix)
- `prijslied-bisschop-gregorios-hemelum` / `…-hemelum-ksl` — paar (schets)
- `tropaar-uw-heilig-kruis-groningen-ksl` — KSL Cyrillisch
- `cherubijnenhymne-15c-kastorski-hemelum-nl-ksl` — mengvorm (indien nodig)

Getranslitereerde producten later; bestaande stub
`hemelum-ksl-trlat` blijft staan tot die conventie vastligt.

**Legacy:** `trisagion/8a-nederlands/…` en `trisagion/8a-slav/…` houden taal
nog in de *variant*-laag; niet hernoemen tot een aparte migratie. Voor
**nieuw** werk: suffix op de uitvoeringsvorm, niet op de variant.

---

## Open reviewpunten

### Inputs met doel-id — deels gezet

| Input | Doel-id | Status |
| --- | --- | --- |
| `capella/15c - cherubijnenhymne - kastorski - ksl.mxl` | `cherubijnenhymne/15c-kastorski/hemelum-ksl` | leaf bestaat (stub); nog converteren |
| `capella/15e Cherubijnenhymne Bortnjanski no.5.mxl` | `cherubijnenhymne/15e-bortnjanski/hemelum` | leaf + producten staan; input mag archief |
| `vow/Tropaar-opstanding-toon*.mscz` | *(leeg)* | voorlopig laten zitten |

### Dankzegging / eind-liturgie — strategie (voorstel)

Probleem: bestandsnamen mengen liturgische plek (`dankzegging`, `eind-liturgie`)
met variantinfo (`toon_2_Kyiv`). In de **catalogus** hoort de liturgische
functie in `zangstuk-id`, de melodische/traditionele uitwerking in
`variant-id`. De **koormap-TOC** mag wél de variantnaam tonen (`linkTitle`).

Voorstel:

1. Eerst inhoudelijk bepalen: is `dankzegging_toon_2_Kyiv` hetzelfde zangstuk
   als slot 28, een ander danklied, of een medley? Idem voor `eind-liturgie`
   (één stuk, of bundel 28+29?).
2. Bibliotheek: `zangstuk-id` = functie (bijv. `dankzegging` of het bestaande
   `wij-hebben-het-ware-licht` als het dát is); `variant-id` =
   `kyiv-toon-2` (niet de functienaam).
3. Koormap: map/slot blijft functioneel (`28-…` of `dankzegging/`); kindpagina
   of `linkTitle` mag “Kyiv toon 2” heten.
4. Doel-id leeg houden tot stap 1 klaar is — niet raden.

---

## Geschiedenis (Hemelum-migratie)

Afgerond rond 2026-09-16 (o.a. legacy-`8a-trisagion*`-mappen weg,
variant-id `default` i.p.v. `standaard`, taal-suffix op uitvoeringsvorm
gedocumenteerd). De tabellen hieronder zijn **naslag uit die migratie**,
geen dagelijkse workflow. Bij twijfel over wat er nu bestaat: catalogus
of Speciaal.

**Statuslegenda (alleen voor deze historische tabellen)**

| Status | Betekenis |
| --- | --- |
| score | Had basispartituur of VSA-bundle in de migratie |
| print | Had print-`.mscz` + PDF (geen Coria-basispartituur-pijplijn) |
| stub | Geen partituur; catalogus-stub + `bieb` op de koormap |
| catalogus | Koormap bleef catalogus-include; geen aparte leaf in die migratiefase |
| legacy | Dubbele/oude map; opruimen na migratie |
| open | Id of migratiepad nog afspreken |

### SCORE — basispartituur, VSA of gemengd

| Koormap-pad (t.o.v. `liturgiemap-hemelum/`) | Bibliotheek-id | Publicatiestam (basispartituur) | Bestanden nu | Opmerking |
| --- | --- | --- | --- | --- |
| `cherubijnenhymne/15c-kastorski/` | `cherubijnenhymne/15c-kastorski/hemelum` | `cherubijnenhymne-15c-kastorski-hemelum` | mscz, mxl, pdf | reviewable; NL (ongemerkt) |
| *(alleen catalogus voorlopig)* | `cherubijnenhymne/15c-kastorski/hemelum-ksl` | `cherubijnenhymne-15c-kastorski-hemelum-ksl` | — | Kerkslavisch getranslitereerd; stub |
| `cherubijnenhymne/15b-fatejev/` | `cherubijnenhymne/15b-fatejev/hemelum` | — | — | voorzien |
| `cherubijnenhymne/15d-kastorski/` | `cherubijnenhymne/15d-kastorski/hemelum` | — | — | voorzien (andere Kastorski dan 15c) |
| `cherubijnenhymne/15e-bortnjanski/` | `cherubijnenhymne/15e-bortnjanski/hemelum` | `cherubijnenhymne-15e-bortnjanski-hemelum` | mscz, mvsa, mxl, pdf, … | reviewable; Capella was 15e |

**Cherubijnen-varianten (Hemelum):** 15b Fatejev, 15c Kastorski, 15d Kastorski,
15e Bortnjanski. Niet: 15a Staro-Simonovskaja, 15f Lvovsky.

| Koormap-pad (t.o.v. `liturgiemap-hemelum/`) | Bibliotheek-id | Publicatiestam (basispartituur) | Bestanden nu | Opmerking |
| --- | --- | --- | --- | --- |
| `trisagion/8a-trisagion/` | `trisagion/8a-nederlands/hemelum` | `trisagion-8a-nederlands-hemelum` | mscz, mxl, pdf | Canoniek; niet de legacy-map `8a-trisagion/` |
| `trisagion/8a-trisagion-slav/` | `trisagion/8a-slav/hemelum` | `trisagion-8a-slav-hemelum` | mscz, mxl, pdf, mvsa | Idem legacy `8a-trisagion-slav/` |
| `19a-eucharistische-kanon/` | `eucharistische-canon/19a-feofan/hemelum` | `eucharistische-canon-19a-feofan-hemelum` | mscz, mxl, pdf | |
| `moeder-godslied/20d-in-waarheid-moeder-godslied/` | `moeder-godslied/20d-in-waarheid/hemelum` | `moeder-godslied-20d-in-waarheid-hemelum` | mscz, mxl, pdf | |
| `moeder-godslied/moeder-godslied-ontslapen-mgods/` | `moeder-godslied/ontslapen-moeder-gods/hemelum` | `moeder-godslied-ontslapen-moeder-gods-hemelum` | print.mscz, mxl, pdf, vsa | `manueel` / `manual`; print-track |
| `communievers/communievers-onthoofding-johannes-de-doper/` | `communievers/onthoofding-johannes-de-doper/hemelum` | `communievers-onthoofding-johannes-de-doper-hemelum` | vsa, vsa.mxl, pdf | Geen basispartituur-mscz; Coria via VSA-publicatiecontrole |
| `troparen-en-kondaken/tropaar-nikolaas-van-myra/` | `tropaar/nikolaas-van-myra-toon-4/hemelum` | `tropaar-nikolaas-van-myra-toon-4-hemelum` | print.mscz, mxl, pdf, vsa | `manueel` / `manual`; onder zangstuk `tropaar/` |
| `eerste-antifoon/weekdagen/` | `eerste-antifoon/weekdagen/hemelum` | `eerste-antifoon-weekdagen` | vsa, vsa.mxl | Koormap = Hemelum; bestandsstam zonder `-hemelum` |
| *(alleen catalogus)* | `eerste-antifoon/weekdagen/liturgikon` | `eerste-antifoon-weekdagen-liturgikon` | vsa, vsa.mxl | Uitvoeringsvorm `liturgikon`; niet in Hemelum-koormap |
| `eerste-antifoon/zondag/` | `eerste-antifoon/zondag/hemelum` | `eerste-antifoon-zondag-hemelum` | mscz, mxl, pdf | stub-achtig in koormap |
| `tweede-antifoon/weekdagen/` | `tweede-antifoon/weekdagen/hemelum` | `tweede-antifoon-weekdagen-hemelum` | vsa, vsa.mxl | |
| `tweede-antifoon/zondag/` | `tweede-antifoon/zondag/hemelum` | `tweede-antifoon-zondag-hemelum` | mscz, mxl, pdf | |
| `derde-antifoon/weekdagen/` | `derde-antifoon/weekdagen/hemelum` | `derde-antifoon-weekdagen-hemelum` | vsa, vsa.mxl | |
| `derde-antifoon/zondag/` | `derde-antifoon/zondag/hemelum` | `derde-antifoon-zondag-hemelum` | mscz, mxl, pdf | Variant-id = koormap-mapnaam |
| `eniggeboren-zoon/` | `eniggeboren-zoon/default/hemelum` | `eniggeboren-zoon-default-hemelum` | mscz, mxl, pdf | `default` = enige variant |
| `kleine-intocht/zondag/` | `kleine-intocht/zondag/hemelum` | `kleine-intocht-zondag-hemelum` | mscz, mxl, pdf, mvsa | |
| `kleine-intocht/weekdagen/` | `kleine-intocht/weekdagen/hemelum` | `kleine-intocht-weekdagen-hemelum` | mscz, mxl, pdf | |
| `kleine-intocht/moeder-gods/` | `kleine-intocht/moeder-gods/hemelum` | `kleine-intocht-moeder-gods-hemelum` | mscz, mxl, pdf | |
| `wij-hebben-het-ware-licht/` | `wij-hebben-het-ware-licht/default/hemelum` | `wij-hebben-het-ware-licht-default-hemelum` | mscz, mxl, pdf | |
| `de-naam-des-heren-zij-gezegend/` | `de-naam-des-heren-zij-gezegend/default/groningen` | `de-naam-des-heren-zij-gezegend-default-groningen` | mscz, mxl, pdf | |

### PRINT — koormap-vel (geen basispartituur-pijplijn)

| Koormap-pad | Bibliotheek-id | Bestanden nu | Opmerking |
| --- | --- | --- | --- |
| `kleine-intocht/zo-wk-mg/` | `kleine-intocht/zo-wk-mg/hemelum` | `*.print.mscz`, pdf | Print-vel; bij voorkeur `manueel: true` |
| `troparen-en-kondaken/tropaar-nikolaas-van-myra/` | `tropaar/nikolaas-van-myra-toon-4/hemelum` | print.mscz, mxl, pdf, vsa | Handmatige artefacten |
| `moeder-godslied/…` | `moeder-godslied/ontslapen-moeder-gods/hemelum` | print.mscz, mxl, pdf, vsa | Handmatige artefacten |

### STUB — alleen koormap + lege catalogus-leaf

| Koormap-pad | Bibliotheek-id | Opmerking |
| --- | --- | --- |
| `vredeslitanie/` | `ektinia/vrede/hemelum` | `.mvsa` (reviewable) |
| `eerste-kleine-litanie/` | `ektinia/eerste-kleine/hemelum` | `.mvsa` (reviewable) |
| `tweede-kleine-litanie/` | `ektinia/tweede-kleine/hemelum` | `.mvsa` (reviewable) |
| `evangelielezing/` | `evangelielezing/default/hemelum` | |
| `dringende-litanie/` | `ektinia/dringend/hemelum` + `…/hemelum-ksl` | `.mvsa` (reviewable) |
| `ontslapenen-litanie/` | `ektinia/ontslapenen/hemelum` + `…/hemelum-ksl` | `.mvsa` (reviewable) |
| `catechumenen-litanie/` | `ektinia/catechumenen/hemelum` + `…/hemelum-ksl` | `.mvsa` (reviewable) |
| `gelovigen-litanie/` | `ektinia/gelovigen/hemelum` + `…/hemelum-ksl` | `.mvsa` (reviewable) |
| `vragende-litanie-16/` | `ektinia/vragend-16/hemelum` + `…/hemelum-ksl` | `.mvsa` (reviewable) |
| `vredeswens/` | `vredeswens/default/hemelum` | |
| `geloofsbelijdenis/` | `geloofsbelijdenis/default/hemelum` | |
| `en-allen/` | `en-allen/default/hemelum` | |
| `vragende-litanie-22/` | `ektinia/vragend-22/hemelum` + `…/hemelum-ksl` | `.mvsa` (reviewable) |
| `onze-vader/` | `onze-vader/default/hemelum` | |
| `een-is-heilig/` | `een-is-heilig/default/hemelum` | |
| `gezegend-hij-die-komt/` | `gezegend-hij-die-komt/default/hemelum` | |
| `communiezang/` | `communiezang/default/hemelum` | |
| `dialoog-met-diaken/` | `dialoog-met-diaken/default/hemelum` | tekstblad.md, tekstblad.pdf |

### Oude catalogus-paden → huidige ids

Kondaken en troparen staan als catalogus-leafs onder `kondak/` en
`tropaar/`, met `bieb` op de koormap (geen `:::include` meer naar
catalogus/`lokaal/`).

| Was (oude catalogus) | Nu (catalogus) |
| --- | --- |
| `kondak-nikolaas-van-myra/liturgikon/Liturgikon` | `kondak/nikolaas-van-myra-toon-3/hemelum` |
| `kondak-moeder-gods-toon-6/hemelum/Hemelum` | `kondak/moeder-gods-toon-6/hemelum` |

### Legacy — opgeruimd (2026-09-16)

| Pad | Actie |
| --- | --- |
| `liturgiemap-hemelum/8a-trisagion/` | Verwijderd (dubbel van `trisagion/8a-trisagion/`) |
| `liturgiemap-hemelum/8a-trisagion-slav/` | Verwijderd (dubbel van `trisagion/8a-trisagion-slav/`) |
