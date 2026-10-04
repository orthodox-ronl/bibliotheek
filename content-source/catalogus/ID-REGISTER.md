---
title: "Id-register Hemelum"
linkTitle: "Id-register"
weight: 9800
publicatiestatus: concept
automatische_inhoud: false
vsa_nav_exclude: true
---

# Id-register — liturgiemap Hemelum → catalogus

Dit register is de **bron van waarheid** voor catalogus-id's tijdens de
conversie (historisch begonnen op `feat/oefenhoek-mxl-opkuis`). Een
catalogus-id heeft altijd drie lagen: `zangstuk-id` / `variant-id` /
`uitvoeringsvorm-id` (elk segment `[a-z0-9_-]+`). De **publicatiestam**
voor basispartituur-bestanden is `{zangstuk}-{variant}-{uitvoeringsvorm}`
(functie `stem()` in `scripts/catalogus.py`).

Het oude migratiescript `scripts/migrate_oefenhoek_bibliotheek.py` volgde
de tabellen **SCORE**, **PRINT** en **STUB** hieronder (niet meer in
dagelijks gebruik; nieuwe stukken via `bieb accepteer`). Wijzig id's eerst
hier en in tooling tegelijk.

**Status legenda**

| Status | Betekenis |
| --- | --- |
| score | Basispartituur of VSA-bundle verhuist via `SCORE_MOVES` |
| print | Print-`.mscz` + PDF via `PRINT_MOVES` (geen Coria-basispartituur) |
| stub | Geen partituur; catalogus-stub + `bieb` op koormap |
| catalogus | Koormap blijft catalogus-include; **geen** catalogus-leaf in fase 2 |
| legacy | Dubbele/oude map; opruimen na migratie |
| open | Id of migratiepad nog afspreken |

---

## SCORE — basispartituur, VSA of gemengd

| Koormap-pad (t.o.v. `liturgiemap-hemelum/`) | Bibliotheek-id | Publicatiestam (basispartituur) | Bestanden nu | Opmerking |
| --- | --- | --- | --- | --- |
| `cherubijnenhymne/15c-kastorski/` | `cherubijnenhymne/15c-kastorski/hemelum` | `cherubijnenhymne-15c-kastorski-hemelum` | mscz, mxl, pdf | reviewable; NL (ongemerkt) |
| *(alleen catalogus voorlopig)* | `cherubijnenhymne/15c-kastorski/hemelum-ksl-trlat` | `cherubijnenhymne-15c-kastorski-hemelum-ksl-trlat` | — | Kerkslavisch getranslitereerd; stub |
| `cherubijnenhymne/15b-fatejev/` | `cherubijnenhymne/15b-fatejev/hemelum` | — | — | voorzien |
| `cherubijnenhymne/15d-kastorski/` | `cherubijnenhymne/15d-kastorski/hemelum` | — | — | voorzien (andere Kastorski dan 15c) |
| `cherubijnenhymne/15e-bortnjanski/` | `cherubijnenhymne/15e-bortnjanski/hemelum` | `cherubijnenhymne-15e-bortnjanski-hemelum` | — | voorzien; Capella-input aanwezig |

**Cherubijnen-varianten (Hemelum):** 15b Fatejev, 15c Kastorski, 15d Kastorski,
15e Bortnjanski. Niet: 15a Staro-Simonovskaja, 15f Lvovsky.
| `trisagion/8a-trisagion/` | `trisagion/8a-nederlands/hemelum` | `trisagion-8a-nederlands-hemelum` | mscz, mxl, pdf | Canoniek; niet de legacy-map `8a-trisagion/` |
| `trisagion/8a-trisagion-slav/` | `trisagion/8a-slav/hemelum` | `trisagion-8a-slav-hemelum` | mscz, mxl, pdf, mvsa | Idem legacy `8a-trisagion-slav/` |
| `19a-eucharistische-kanon/` | `eucharistische-canon/19a-feofan/hemelum` | `eucharistische-canon-19a-feofan-hemelum` | mscz, mxl, pdf | |
| *(alleen catalogus voorlopig)* | `eucharistische-canon/rostov/hemelum` | `eucharistische-canon-rostov-hemelum` | — | VOW-input; stub |
| `moeder-godslied/20d-in-waarheid-moeder-godslied/` | `moeder-godslied/20d-in-waarheid/hemelum` | `moeder-godslied-20d-in-waarheid-hemelum` | mscz, mxl, pdf | |
| `moeder-godslied/moeder-godslied-ontslapen-mgods/` | `moeder-godslied/ontslapen-moeder-gods/hemelum` | `moeder-godslied-ontslapen-moeder-gods-hemelum` | print.mscz, mxl, pdf, vsa | `artefacten_handmatig`; print-track |
| `communievers/communievers-onthoofding-johannes-de-doper/` | `communievers/onthoofding-johannes-de-doper/hemelum` | `communievers-onthoofding-johannes-de-doper-hemelum` | vsa, vsa.mxl, pdf | Geen basispartituur-mscz; Coria via VSA-publicatiecontrole |
| `troparen-en-kondaken/tropaar-nikolaas-van-myra/` | `tropaar/nikolaas-van-myra-toon-4/hemelum` | `tropaar-nikolaas-van-myra-toon-4-hemelum` | print.mscz, mxl, pdf, vsa | `artefacten_handmatig`; onder zangstuk `tropaar/` |
| `eerste-antifoon/weekdagen/` | `eerste-antifoon/weekdagen/hemelum` | `eerste-antifoon-weekdagen-hemelum-hemelum` | vsa, vsa.mxl | Koormap = Hemelum; geen `liturgikon/`-slot meer |
| *(alleen catalogus)* | `eerste-antifoon/weekdagen-liturgikon/hemelum` | `eerste-antifoon-weekdagen-liturgikon-hemelum` | vsa, vsa.mxl | Niet in Hemelum-koormap |
| `eerste-antifoon/zondag/` | `eerste-antifoon/zondag/hemelum` | `eerste-antifoon-zondag-hemelum` | mscz, mxl, pdf | stub-achtig in koormap |
| `tweede-antifoon/weekdagen/` | `tweede-antifoon/weekdagen/hemelum` | `tweede-antifoon-weekdagen-hemelum-hemelum` | vsa, vsa.mxl | |
| `tweede-antifoon/zondag/` | `tweede-antifoon/zondag/hemelum` | `tweede-antifoon-zondag-hemelum` | mscz, mxl, pdf | |
| `derde-antifoon/weekdagen/` | `derde-antifoon/weekdagen/hemelum` | `derde-antifoon-weekdagen-hemelum-hemelum` | vsa, vsa.mxl | |
| `derde-antifoon/zondag/` | `derde-antifoon/zondag/hemelum` | `derde-antifoon-zondag-hemelum` | mscz, mxl, pdf | Variant-id = koormap-mapnaam |
| `eniggeboren-zoon/` | `eniggeboren-zoon/default/hemelum` | `eniggeboren-zoon-default-hemelum` | mscz, mxl, pdf | `default` = enige variant |
| `kleine-intocht/zondag/` | `kleine-intocht/zondag/hemelum` | `kleine-intocht-zondag-hemelum` | mscz, mxl, pdf, mvsa | |
| `kleine-intocht/weekdagen/` | `kleine-intocht/weekdagen/hemelum` | `kleine-intocht-weekdagen-hemelum` | mscz, mxl, pdf | |
| `kleine-intocht/moeder-gods/` | `kleine-intocht/moeder-gods/hemelum` | `kleine-intocht-moeder-gods-hemelum` | mscz, mxl, pdf | |
| `wij-hebben-het-ware-licht/` | `wij-hebben-het-ware-licht/default/hemelum` | `wij-hebben-het-ware-licht-default-hemelum` | mscz, mxl, pdf | |
| `de-naam-des-heren-zij-gezegend/` | `de-naam-des-heren-zij-gezegend/default/hemelum` | `de-naam-des-heren-zij-gezegend-default-hemelum` | mscz, mxl, pdf | |

---

## PRINT — koormap-vel (geen basispartituur-pijplijn)

| Koormap-pad | Bibliotheek-id | Bestanden nu | Opmerking |
| --- | --- | --- | --- |
| `kleine-intocht/zo-wk-mg/` | `kleine-intocht/zo-wk-mg/hemelum` | `*.print.mscz`, pdf | Print-vel; bij voorkeur `artefacten_handmatig: true` |
| `troparen-en-kondaken/tropaar-nikolaas-van-myra/` | `tropaar/nikolaas-van-myra-toon-4/hemelum` | print.mscz, mxl, pdf, vsa | Handmatige artefacten |
| `moeder-godslied/…` | `moeder-godslied/ontslapen-moeder-gods/hemelum` | print.mscz, mxl, pdf, vsa | Handmatige artefacten |

---

## STUB — alleen koormap + lege catalogus-leaf

| Koormap-pad | Bibliotheek-id | Opmerking |
| --- | --- | --- |
| `vredeslitanie/` | `ektinia/vrede/hemelum` | `.mvsa` (reviewable) |
| `eerste-kleine-litanie/` | `ektinia/eerste-kleine/hemelum` | `.mvsa` (reviewable) |
| `tweede-kleine-litanie/` | `ektinia/tweede-kleine/hemelum` | `.mvsa` (reviewable) |
| `evangelielezing/` | `evangelielezing/default/hemelum` | |
| `dringende-litanie/` | `ektinia/dringend/hemelum-nl` + `…/hemelum-ksl` | `.mvsa` (reviewable) |
| `ontslapenen-litanie/` | `ektinia/ontslapenen/hemelum-nl` + `…/hemelum-ksl` | `.mvsa` (reviewable) |
| `catechumenen-litanie/` | `ektinia/catechumenen/hemelum-nl` + `…/hemelum-ksl` | `.mvsa` (reviewable) |
| `gelovigen-litanie/` | `ektinia/gelovigen/hemelum-nl` + `…/hemelum-ksl` | `.mvsa` (reviewable) |
| `vragende-litanie-16/` | `ektinia/vragend-16/hemelum-nl` + `…/hemelum-ksl` | `.mvsa` (reviewable) |
| `vredeswens/` | `vredeswens/default/hemelum` | |
| `geloofsbelijdenis/` | `geloofsbelijdenis/default/hemelum` | |
| `en-allen/` | `en-allen/default/hemelum` | |
| `vragende-litanie-22/` | `ektinia/vragend-22/hemelum-nl` + `…/hemelum-ksl` | `.mvsa` (reviewable) |
| `onze-vader/` | `onze-vader/default/hemelum` | |
| `een-is-heilig/` | `een-is-heilig/default/hemelum` | |
| `gezegend-hij-die-komt/` | `gezegend-hij-die-komt/default/hemelum` | |
| `communiezang/` | `communiezang/default/hemelum` | |
| `dialoog-met-diaken/` | `dialoog-met-diaken/default/hemelum` | tekstblad.md, tekstblad.pdf |

### Prokimen / alleluia (Kiev + znameni-reservering)

**Koormap-slots:** `9a-prokimen/` (prokimens eerder in de liturgie) en
`9b-alleluia/`. In de **catalogus** is `9a-` / `9b-` op de *variant*-laag
de melodieklasse (Kiev / znameni), niet het liturgienummer.

| Koormap-pad | Bibliotheek-id (voorbeeld) | Status |
| --- | --- | --- |
| `9a-prokimen/weekdagen/` | `prokimen/9a-maandag/groningen` … `9a-zaterdag` | score (VSA); compositieblad |
| `9a-prokimen/zondag-toon-N/` | `prokimen/9a-zondag-toon-N/groningen` + `alleluia/9a-toon-N/groningen` | alleluia: `.mvsa` (reviewable); prokimen zondag: voorzien |
| `9b-alleluia/` | `alleluia/9a-toon-1/groningen` … `9a-toon-8` | `.mvsa` (reviewable) |

**Znameni (alleen register):** `prokimen/9b-{naam}/{uv}`,
`alleluia/9b-toon-{1..8}/{uv}` — nog geen leafs.

### Tropaar / kondak

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

`default` als variant-id betekent: één uitvoeringsvorm in Hemelum, geen
geneste varianten in de koormap.

### Taal op de uitvoeringsvorm (voorkeursconventie)

Nederlands vs kerkslavisch = **aparte uitvoeringsvormen** via suffix op
het derde segment. Handleiding (beheerder):
[Taalvarianten (-nl / -ksl)](/handleiding/start/catalogus-en-koormappen/#taalvarianten-op-de-uitvoeringsvorm).

| Suffix op uitvoeringsvorm-id | Betekenis | Wanneer |
| --- | --- | --- |
| *(geen)* | Nederlands | Alleen NL; geen kerkslavisch-sibling |
| `-nl` | Nederlands | Expliciet naast een `-ksl`-sibling |
| `-ksl` | Kerkslavisch, Cyrillisch | KSL-uitvoeringsvorm |
| `-nl-ksl` | Mengvorm NL + kerkslavisch | Zeldzaam; één partituur met beide |

Voorbeelden (publicatiestam):

- `cherubijnenhymne-15c-kastorski-hemelum` — NL zonder sibling (ongemerkt)
- `prijslied-bisschop-gregorios-hemelum-nl` / `…-hemelum-ksl` — paar (schets)
- `tropaar-uw-heilig-kruis-groningen-ksl` — KSL Cyrillisch
- `cherubijnenhymne-15c-kastorski-hemelum-nl-ksl` — mengvorm (indien nodig)

Getranslitereerde producten later; bestaande stub
`hemelum-ksl-trlat` blijft staan tot die conventie vastligt.

**Legacy:** `trisagion/8a-nederlands/…` en `trisagion/8a-slav/…` houden taal
nog in de *variant*-laag; niet hernoemen tot een aparte migratie. Voor
**nieuw** werk: suffix op de uitvoeringsvorm, niet op de variant.

---

## CATALOGUS_KOORMAP — niet meer in oefenhoek

Oefenhoek-pagina’s gebruiken **geen** `:::include` naar catalogus/`lokaal/`.
Kondaken en troparen staan als catalogus-leafs onder `kondak/` en
`tropaar/`; losse gezangen onder eigen zangstuk-ids (bv. `220-uw-heilig-kruis/`),
met `bieb` op de koormap.

| Was (oude catalogus) | Nu (catalogus) |
| --- | --- |
| `kondak-nikolaas-van-myra/liturgikon/Liturgikon` | `kondak/nikolaas-van-myra-toon-3/hemelum` |
| `kondak-moeder-gods-toon-6/hemelum/Hemelum` | `kondak/moeder-gods-toon-6/hemelum` |

### Diversen

| Koormap-pad | Bibliotheek-id |
| --- | --- |
| `troparen-en-kondaken/uw-heilig-kruis/` | `tropaar/uw-heilig-kruis/hemelum` |

---

## LEGACY — opgeruimd (2026-09-16)

| Pad | Actie |
| --- | --- |
| `liturgiemap-hemelum/8a-trisagion/` | Verwijderd (dubbel van `trisagion/8a-trisagion/`) |
| `liturgiemap-hemelum/8a-trisagion-slav/` | Verwijderd (dubbel van `trisagion/8a-trisagion-slav/`) |

---

## OPEN — reviewpunten

### 1. Tropaar Nikolaas — besloten

Bibliotheek-id: `tropaar/nikolaas-van-myra-toon-4/hemelum` (zangstuk
`tropaar/`, niet een apart zangstuk-id). Oude map
`tropaar-nikolaas-van-myra/…` verwijderd.

### 2. Variant-id `default` — besloten

Voor slots zonder geneste varianten: middelste laag = `default`
(bijv. `eniggeboren-zoon/default/hemelum`).

### 3. Derde antifoon zondag — besloten

Bibliotheek-id: `derde-antifoon/zondag/hemelum` (niet `zaligsprekingen-zondag`).

### 4. Familie-`_index.md` zonder `bieb` — besloten

Alleen leaves krijgen `bieb`; familie-pagina’s blijven TOC
(`automatische_inhoud: true`).

### 5. Capella `5a Eniggeboren Zoon.mxl` — afgerond

Doel-id: `eniggeboren-zoon/default/hemelum`.

### 6. Inputs met doel-id — deels gezet

| Input | Doel-id | Status |
| --- | --- | --- |
| `capella/…kastorskij - ksl.mxl` | `cherubijnenhymne/15c-kastorski/hemelum-ksl-trlat` | stub; nog converteren |
| `capella/15e … Bortnjanski….mxl` | `cherubijnenhymne/15e-bortnjanski/hemelum` | stub; Capella zegt **15e** (niet 15c) |
| `vow/Eucharistische Canon-Rostov.mscz` | `eucharistische-canon/rostov/hemelum` | stub naast Feofan |
| `vow/Tropaar-opstanding-toon*.mscz` | *(leeg)* | voorlopig laten zitten |

### 7. Dankzegging / eind-liturgie — strategie (voorstel)

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

### 8. Eucharistische kanon + moeder-godslied — al in catalogus

Lokaal aanwezig (nog untracked tot commit):

- `eucharistische-canon/19a-feofan/hemelum` (+ stub `rostov/hemelum`)
- `moeder-godslied/20d-in-waarheid/hemelum`
- `moeder-godslied/ontslapen-moeder-gods/hemelum`

Koormap-slots verwijzen via `bieb`; basispartituur-bestanden staan niet meer
in de liturgiemap (dat is de migratie, geen verdwijning).

---

## Review-checklist (na migratie)

- [x] Geen basispartituur-bestanden meer in koormap-leaves (`*.print.mscz` alleen in catalogus)
- [x] Legacy-mappen `8a-trisagion*` weg
- [x] Catalogus-kondak-pagina's ongewijzigd qua includes
- [x] `check --strict` groen (2026-09-16)
- [x] Variant-id `default` (was `standaard`)
- [x] Derde antifoon zondag: catalogus-variant `zondag`
- [x] Familie-`_index` zonder `bieb`
- [x] Werkvoorraad: gepubliceerde rijen op catalogus-id; open inputs nog zonder doel-id
- [x] Uitvoeringsvorm mét partituur → `reviewable` (koormap + catalogus)
- [x] Term “input” (niet “dump”) in werkvoorraad/handleiding
- [x] Taal-suffix op uitvoeringsvorm gedocumenteerd (`-nl` / `-ksl`, alleen waar nodig; legacy variant-taal)
