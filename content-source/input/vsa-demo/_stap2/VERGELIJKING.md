# Stap 2 - vergelijking met catalogus

Bron: `content-source/input/vsa-demo/_stap1`
Doel: `content-source/input/vsa-demo/_stap2`
Catalogus-VSA: 62
Stap1-VSA: 138

## Samenvatting

- **al in bieb** (notatie gelijk na normalisatie): 52
- **mogelijke variant** (tekst ~gelijk, notatie anders): 19
- **twijfel** (zwakke tekstgelijkenis): 2
- **nieuw** (geen bruikbare treffer): 65
- **duplicaatgroepen** binnen stap1: 29

Normalisatie: LF, trailing spaties weg, max. 2 lege regels; vergelijking zonder HTML-commentaar. Geen ELM-/tekstcorrecties.

## Al in bibliotheek

- `derde-antifoon-derde-antifoon-weekdagen-weekdagen-antifonen-hemelum-n03.vsa` -> `derde-antifoon/weekdagen/hemelum/derde-antifoon-weekdagen-hemelum.vsa`
- `kondak-geboorte-van-de-moeder-gods-09-08-geboorte-van-de-moeder-gods-n05.vsa` -> `kondak/geboorte-moeder-gods-toon-4/liturgikon/kondak-geboorte-moeder-gods-toon-4-liturgikon.vsa`; duplicaat van 2 ander(e)
- `kondak-h-nikolaas-van-myra-6-december-12-06-nikolaas-van-myra-hemelum-n02.vsa` -> `kondak/nikolaas-van-myra-toon-3/hemelum/kondak-nikolaas-van-myra-toon-3-hemelum.vsa`; duplicaat van 2 ander(e)
- `kondak-h-nikolaas-van-myra-6-december-12-06-nikolaas-van-myra-liturgikon-n02.vsa` -> `kondak/nikolaas-van-myra-toon-3/hemelum/kondak-nikolaas-van-myra-toon-3-hemelum.vsa`; duplicaat van 2 ander(e)
- `kondak-h-nikolaas-van-myra-6-december-tropaar-kondak-nikolaas-van-myra-n02.vsa` -> `kondak/nikolaas-van-myra-toon-3/hemelum/kondak-nikolaas-van-myra-toon-3-hemelum.vsa`; duplicaat van 2 ander(e)
- `kondak-kondak-h-johannes-de-doper-20260811-di-liturgie-n03.vsa` -> `kondak/dinsdag-toon-3/hemelum/kondak-dinsdag-toon-3-hemelum.vsa`; duplicaat van 1 ander(e)
- `kondak-kondak-h-kruis-nls-nl-20260814-vr-liturgie-kruisuitdraging-n04.vsa` -> `kondak/heilig-kruis-toon-1/hemelum/kondak-heilig-kruis-toon-1-hemelum.vsa`; duplicaat van 1 ander(e)
- `kondak-kondak-h-silouan-20260924-do-liturgie-nafeest-geboorte-mg-silouan-de-athoniet-n05.vsa` -> `kondak/silouan-de-athoniet-toon-4/asten/kondak-silouan-de-athoniet-toon-4-asten.vsa`
- `kondak-kondak-v-h-feest-20260921-ma-liturgie-geboorte-moeder-gods-n06.vsa` -> `kondak/geboorte-moeder-gods-toon-4/liturgikon/kondak-geboorte-moeder-gods-toon-4-liturgikon.vsa`; duplicaat van 2 ander(e)
- `kondak-kondak-v-h-feest-20260924-do-liturgie-nafeest-geboorte-mg-silouan-de-athoniet-n02.vsa` -> `kondak/geboorte-moeder-gods-toon-4/liturgikon/kondak-geboorte-moeder-gods-toon-4-liturgikon.vsa`; duplicaat van 2 ander(e)
- `kondak-troparen-en-kondaken-voor-de-weekdagen-hemelum-weekdagen-troparen-en-kondaken-hemelum-n02.vsa` -> `kondak/maandag-toon-2/hemelum/kondak-maandag-toon-2-hemelum.vsa`
- `kondak-troparen-en-kondaken-voor-de-weekdagen-hemelum-weekdagen-troparen-en-kondaken-hemelum-n04.vsa` -> `kondak/dinsdag-toon-3/hemelum/kondak-dinsdag-toon-3-hemelum.vsa`; duplicaat van 1 ander(e)
- `kondak-troparen-en-kondaken-voor-de-weekdagen-hemelum-weekdagen-troparen-en-kondaken-hemelum-n06.vsa` -> `kondak/heilig-kruis-toon-1/hemelum/kondak-heilig-kruis-toon-1-hemelum.vsa`; duplicaat van 1 ander(e)
- `kondak-troparen-en-kondaken-voor-de-weekdagen-hemelum-weekdagen-troparen-en-kondaken-hemelum-n09.vsa` -> `kondak/donderdag-toon-2/hemelum/kondak-donderdag-toon-2-hemelum.vsa`
- `kondak-troparen-en-kondaken-voor-de-weekdagen-hemelum-weekdagen-troparen-en-kondaken-hemelum-n11.vsa` -> `kondak/zaterdag-heiligen-toon-8/hemelum/kondak-zaterdag-heiligen-toon-8-hemelum.vsa`
- `kondak-troparen-en-kondaken-voor-de-weekdagen-hemelum-weekdagen-troparen-en-kondaken-hemelum-n13.vsa` -> `kondak/zaterdag-gestorvenen-toon-8/hemelum/kondak-zaterdag-gestorvenen-toon-8-hemelum.vsa`
- `moeder-godslied-20260903-nafeest-van-ontslapen-h-apostel-thaddeos-20260903-vr-liturgie-apostel-thaddeos-n05.vsa` -> `moeder-godslied/ontslapen-moeder-gods/hemelum/moeder-godslied-ontslapen-moeder-gods-hemelum.vsa`
- `moeder-godslied-20260924-nafeest-vd-geboorte-vd-mgods-h-silouan-de-20260924-do-liturgie-nafeest-geboorte-mg-silouan-de-athoniet-n03.vsa` -> `moeder-godslied/verhef-mijn-ziel-met-blijde-zang/liturgikon/moeder-godslied-verhef-mijn-ziel-met-blijde-zang-liturgikon.vsa`; duplicaat van 4 ander(e)
- `moeder-godslied-moeder-godslied-nls-nl-20260819-wo-liturgie-transfiguratie-n09.vsa` -> `moeder-godslied/verhef-mijn-ziel-met-blijde-zang/liturgikon/moeder-godslied-verhef-mijn-ziel-met-blijde-zang-liturgikon.vsa`; duplicaat van 4 ander(e)
- `moeder-godslied-moeder-godslied-v-h-feest-v-d-transfiguratie-08-06-verheerlijking-op-de-berg-thabor-n06.vsa` -> `moeder-godslied/verhef-mijn-ziel-met-blijde-zang/liturgikon/moeder-godslied-verhef-mijn-ziel-met-blijde-zang-liturgikon.vsa`; duplicaat van 4 ander(e)
- `moeder-godslied-moeder-godslied-v-h-feest-v-d-transfiguratie-20260825-di-liturgie-n04.vsa` -> `moeder-godslied/verhef-mijn-ziel-met-blijde-zang/liturgikon/moeder-godslied-verhef-mijn-ziel-met-blijde-zang-liturgikon.vsa`; duplicaat van 4 ander(e)
- `moeder-godslied-moeder-godslied-vh-feest-kruisverheffing-20260930-wo-liturgie-n02.vsa` -> `moeder-godslied/verhef-mijn-ziel-met-blijde-zang/liturgikon/moeder-godslied-verhef-mijn-ziel-met-blijde-zang-liturgikon.vsa`; duplicaat van 4 ander(e)
- `prijslied-20260921-feest-van-de-geboorte-van-de-moeder-gods-nl-20260921-ma-liturgie-geboorte-moeder-gods-n07.vsa` -> `prijslied/geboorte-moeder-gods/meneon-1/prijslied-geboorte-moeder-gods-meneon-1.vsa`
- `prokimen-20260828-feest-van-de-ontslaping-van-de-moeder-god-nl-20260828-vr-liturgie-ontslapen-moeder-gods-n06.vsa` -> `prokimen/9a-woensdag/groningen/prokimen-9a-woensdag-groningen.vsa`; duplicaat van 1 ander(e)
- `prokimen-onthoofing-van-h-johannes-de-doper-08-31-onthoofding-johannes-de-doper-n03.vsa` -> `prokimen/9a-dinsdag/groningen/prokimen-9a-dinsdag-groningen.vsa`; duplicaat van 2 ander(e)
- `prokimen-ontslaping-van-de-moeder-gods-08-15-ontslaping-van-de-moeder-gods-n05.vsa` -> `prokimen/9a-woensdag/groningen/prokimen-9a-woensdag-groningen.vsa`; duplicaat van 1 ander(e)
- `prokimen-prokimen-t-7-dinsdag-20260811-di-liturgie-n04.vsa` -> `prokimen/9a-dinsdag/groningen/prokimen-9a-dinsdag-groningen.vsa`; duplicaat van 2 ander(e)
- `prokimen-prokimen-t-7-dinsdag-20260825-di-liturgie-n03.vsa` -> `prokimen/9a-dinsdag/groningen/prokimen-9a-dinsdag-groningen.vsa`; duplicaat van 2 ander(e)
- `tropaar-20260921-feest-van-de-geboorte-van-de-moeder-gods-20260921-ma-liturgie-geboorte-moeder-gods-n04.vsa` -> `tropaar/geboorte-mg-toon-4/meneon-i-den-haag/tropaar-geboorte-mg-toon-4-meneon-i-den-haag.vsa`; duplicaat van 3 ander(e)
- `tropaar-geboorte-van-de-moeder-gods-09-08-geboorte-van-de-moeder-gods-n04.vsa` -> `tropaar/geboorte-mg-toon-4/meneon-i-den-haag/tropaar-geboorte-mg-toon-4-meneon-i-den-haag.vsa`; duplicaat van 3 ander(e)
- `tropaar-h-nikolaas-van-myra-6-december-12-06-nikolaas-van-myra-hemelum-n01.vsa` -> `tropaar/nikolaas-van-myra-toon-4/hemelum/tropaar-nikolaas-van-myra-toon-4-hemelum.vsa`; duplicaat van 1 ander(e)
- `tropaar-h-nikolaas-van-myra-6-december-tropaar-kondak-nikolaas-van-myra-n01.vsa` -> `tropaar/nikolaas-van-myra-toon-4/hemelum/tropaar-nikolaas-van-myra-toon-4-hemelum.vsa`; duplicaat van 1 ander(e)
- `tropaar-neerleggen-van-de-mantel-van-de-moeder-gods-blache-07-15-neerleggen-mantel-moeder-gods-blachernakerk-n01.vsa` -> `tropaar/mantel-moeder-gods-toon-4/hemelum/tropaar-mantel-moeder-gods-toon-4-hemelum.vsa`; duplicaat van 1 ander(e)
- `tropaar-onthoofing-van-h-johannes-de-doper-08-31-onthoofding-johannes-de-doper-n01.vsa` -> `tropaar/dinsdag-toon-2/hemelum/tropaar-dinsdag-toon-2-hemelum.vsa`; duplicaat van 3 ander(e)
- `tropaar-tropaar-h-joh-de-doper-20260802-zo-liturgie-profeet-elias-n02.vsa` -> `tropaar/dinsdag-toon-2/hemelum/tropaar-dinsdag-toon-2-hemelum.vsa`; duplicaat van 3 ander(e)
- `tropaar-tropaar-h-silouan-20260924-do-liturgie-nafeest-geboorte-mg-silouan-de-athoniet-n04.vsa` -> `tropaar/silouan-de-athoniet-toon-4/asten/tropaar-silouan-de-athoniet-toon-4-asten.vsa`
- `tropaar-tropaar-hh-martelaren-t-4-nl-20260811-di-liturgie-n02.vsa` -> `tropaar/heilige-martelaren-toon-4/hemelum/tropaar-heilige-martelaren-toon-4-hemelum.vsa`; duplicaat van 1 ander(e)
- `tropaar-tropaar-hh-martelaren-tropaar-heilige-martelaren-hemelum-n01.vsa` -> `tropaar/heilige-martelaren-toon-4/hemelum/tropaar-heilige-martelaren-toon-4-hemelum.vsa`; duplicaat van 1 ander(e)
- `tropaar-tropaar-icoon-moeder-gods-vladimir-nls-en-ksl-nl-20260908-di-liturgie-icoon-mgods-vladimir-n01.vsa` -> `tropaar/icoon-moeder-gods-vladimir-toon-4/hemelum/tropaar-icoon-moeder-gods-vladimir-toon-4-hemelum.vsa`; duplicaat van 1 ander(e)
- `tropaar-tropaar-icoon-moeder-gods-vladimir-tropaar-icoon-moeder-gods-vladimir-hemelum-n01.vsa` -> `tropaar/icoon-moeder-gods-vladimir-toon-4/hemelum/tropaar-icoon-moeder-gods-vladimir-toon-4-hemelum.vsa`; duplicaat van 1 ander(e)
- `tropaar-tropaar-nls-en-ksl-nl-20260911-vr-liturgie-onthoofding-johannes-de-doper-n01.vsa` -> `tropaar/dinsdag-toon-2/hemelum/tropaar-dinsdag-toon-2-hemelum.vsa`; duplicaat van 3 ander(e)
- `tropaar-tropaar-v-h-feest-20260921-ma-liturgie-geboorte-moeder-gods-n05.vsa` -> `tropaar/geboorte-mg-toon-4/meneon-i-den-haag/tropaar-geboorte-mg-toon-4-meneon-i-den-haag.vsa`; duplicaat van 3 ander(e)
- `tropaar-tropaar-van-de-mantel-van-de-moeder-gods-tropaar-mantel-moeder-gods-hemelum-n01.vsa` -> `tropaar/mantel-moeder-gods-toon-4/hemelum/tropaar-mantel-moeder-gods-toon-4-hemelum.vsa`; duplicaat van 1 ander(e)
- `tropaar-tropaar-vh-feest-vd-geb-mgods-nls-en-ksl-nl-20260924-do-liturgie-nafeest-geboorte-mg-silouan-de-athoniet-n01.vsa` -> `tropaar/geboorte-mg-toon-4/meneon-i-den-haag/tropaar-geboorte-mg-toon-4-meneon-i-den-haag.vsa`; duplicaat van 3 ander(e)
- `tropaar-troparen-en-kondaken-voor-de-weekdagen-hemelum-weekdagen-troparen-en-kondaken-hemelum-n01.vsa` -> `tropaar/maandag-toon-4/hemelum/tropaar-maandag-toon-4-hemelum.vsa`
- `tropaar-troparen-en-kondaken-voor-de-weekdagen-hemelum-weekdagen-troparen-en-kondaken-hemelum-n03.vsa` -> `tropaar/dinsdag-toon-2/hemelum/tropaar-dinsdag-toon-2-hemelum.vsa`; duplicaat van 3 ander(e)
- `tropaar-troparen-en-kondaken-voor-de-weekdagen-hemelum-weekdagen-troparen-en-kondaken-hemelum-n05.vsa` -> `tropaar/heilig-kruis-toon-1/hemelum/tropaar-heilig-kruis-toon-1-hemelum.vsa`
- `tropaar-troparen-en-kondaken-voor-de-weekdagen-hemelum-weekdagen-troparen-en-kondaken-hemelum-n08.vsa` -> `tropaar/donderdag-toon-3/hemelum/tropaar-donderdag-toon-3-hemelum.vsa`
- `tropaar-troparen-en-kondaken-voor-de-weekdagen-hemelum-weekdagen-troparen-en-kondaken-hemelum-n10.vsa` -> `tropaar/zaterdag-heiligen-toon-2/hemelum/tropaar-zaterdag-heiligen-toon-2-hemelum.vsa`
- `tropaar-troparen-en-kondaken-voor-de-weekdagen-hemelum-weekdagen-troparen-en-kondaken-hemelum-n12.vsa` -> `tropaar/zaterdag-gestorvenen-toon-2/hemelum/tropaar-zaterdag-gestorvenen-toon-2-hemelum.vsa`
- `tweede-antifoon-tweede-antifoon-weekdagen-weekdagen-antifonen-hemelum-n02.vsa` -> `tweede-antifoon/weekdagen/hemelum/tweede-antifoon-weekdagen-hemelum.vsa`
- `uw-heilig-kruis-ksl-naar-het-liturgikon-ksl-20260814-vr-liturgie-kruisuitdraging-n06.vsa` -> `tropaar/uw-heilig-kruis/liturgikon-ksl/tropaar-uw-heilig-kruis-liturgikon-ksl.vsa`

## Mogelijke variant

- `communievers-communievers-onthoofding-johannes-de-doper-08-31-onthoofding-johannes-de-doper-n04.vsa` -> `communievers/onthoofding-johannes-de-doper/hemelum/communievers-onthoofding-johannes-de-doper-hemelum.vsa` (0.99); duplicaat van 1 ander(e)
- `communievers-communievers-onthoofding-johannes-de-doper-20260911-vr-liturgie-onthoofding-johannes-de-doper-n03.vsa` -> `communievers/onthoofding-johannes-de-doper/hemelum/communievers-onthoofding-johannes-de-doper-hemelum.vsa` (0.99); duplicaat van 1 ander(e)
- `eerste-antifoon-eerste-antifoon-weekdagen-weekdagen-antifonen-hemelum-n01.vsa` -> `eerste-antifoon/weekdagen/hemelum/eerste-antifoon-weekdagen.vsa` (1.00)
- `kondak-kruisverheffing-incl-09-14-kruisverheffing-n04.vsa` -> `kondak/heilig-kruis-toon-1/hemelum/kondak-heilig-kruis-toon-1-hemelum.vsa` (1.00)
- `moeder-godslied-20260828-feest-van-de-ontslaping-van-de-moeder-god-20260828-vr-liturgie-ontslapen-moeder-gods-n07.vsa` -> `moeder-godslied/ontslapen-moeder-gods/hemelum/moeder-godslied-ontslapen-moeder-gods-hemelum.vsa` (1.00); duplicaat van 1 ander(e)
- `moeder-godslied-ontslaping-van-de-moeder-gods-08-15-ontslaping-van-de-moeder-gods-n06.vsa` -> `moeder-godslied/ontslapen-moeder-gods/hemelum/moeder-godslied-ontslapen-moeder-gods-hemelum.vsa` (1.00); duplicaat van 1 ander(e)
- `prijslied-20260911-feest-van-de-onthoofding-van-de-h-johanne-nl-20260911-vr-liturgie-onthoofding-johannes-de-doper-n04.vsa` -> `prijslied/johannes-de-voorloper/hemelum/prijslied-johannes-de-voorloper-hemelum.vsa` (1.00)
- `prijslied-geboorte-van-de-moeder-gods-nl-09-08-geboorte-van-de-moeder-gods-n06.vsa` -> `prijslied/geboorte-moeder-gods/meneon-1/prijslied-geboorte-moeder-gods-meneon-1.vsa` (1.00)
- `prokimen-20260903-nafeest-van-ontslapen-h-apostel-thaddeos-20260903-vr-liturgie-apostel-thaddeos-n04.vsa` -> `prokimen/9a-woensdag/groningen/prokimen-9a-woensdag-groningen.vsa` (0.99); duplicaat van 1 ander(e)
- `prokimen-prokimen-t-3-20260814-vr-liturgie-kruisuitdraging-n09.vsa` -> `prokimen/9a-woensdag/groningen/prokimen-9a-woensdag-groningen.vsa` (0.99); duplicaat van 1 ander(e)
- `tropaar-h-johannes-aartsbisschop-van-shanghai-en-san-franc-07-02-johannes-aartsbisschop-van-shanghai-en-san-francisco-n01.vsa` -> `tropaar/nikolaas-van-myra-toon-4/hemelum/tropaar-nikolaas-van-myra-toon-4-hemelum.vsa` (0.92)
- `tropaar-h-nikolaas-van-myra-6-december-12-06-nikolaas-van-myra-liturgikon-n01.vsa` -> `tropaar/nikolaas-van-myra-toon-4/hemelum/tropaar-nikolaas-van-myra-toon-4-hemelum.vsa` (0.89); duplicaat van 2 ander(e)
- `tropaar-tropaar-h-nikolaas-t-4-nl-20260811-di-liturgie-n01.vsa` -> `tropaar/nikolaas-van-myra-toon-4/hemelum/tropaar-nikolaas-van-myra-toon-4-hemelum.vsa` (0.89); duplicaat van 2 ander(e)
- `tropaar-tropaar-h-nikolaas-t-4-nl-20260814-vr-liturgie-kruisuitdraging-n03.vsa` -> `tropaar/nikolaas-van-myra-toon-4/hemelum/tropaar-nikolaas-van-myra-toon-4-hemelum.vsa` (0.89); duplicaat van 2 ander(e)
- `tropaar-tropaar-van-de-zondag-20260802-zo-liturgie-profeet-elias-n01.vsa` -> `tropaar/zondag-toon-8/groningen/tropaar-zondag-toon-8-groningen.vsa` (1.00)
- `uw-heilig-kruis-ksl-ksl-20260814-vr-liturgie-kruisuitdraging-n08.vsa` -> `tropaar/uw-heilig-kruis/groningen-ksl/tropaar-uw-heilig-kruis-groningen-ksl.vsa` (1.00)
- `uw-heilig-kruis-nls-versie-uit-groningen-nl-20260814-vr-liturgie-kruisuitdraging-n07.vsa` -> `tropaar/uw-heilig-kruis/liturgikon/tropaar-uw-heilig-kruis-liturgikon.vsa` (1.00)
- `uw-heilig-kruis-nls-versie-uit-liturgikon-nl-20260814-vr-liturgie-kruisuitdraging-n05.vsa` -> `tropaar/uw-heilig-kruis/groningen/tropaar-uw-heilig-kruis-groningen.vsa` (0.99); duplicaat van 1 ander(e)
- `uw-heilig-kruis-uw-heilig-kruis-weekdagen-troparen-en-kondaken-hemelum-n07.vsa` -> `tropaar/uw-heilig-kruis/groningen/tropaar-uw-heilig-kruis-groningen.vsa` (0.99); duplicaat van 1 ander(e)

## Twijfel

- `tropaar-tropaar-h-gregorios-van-utrecht-t-4-ksl-20260825-di-liturgie-n02.vsa` -> `tropaar/nikolaas-van-myra-toon-4/hemelum/tropaar-nikolaas-van-myra-toon-4-hemelum.vsa` (0.86)
- `tropaar-tropaar-h-kruis-nl-20260814-vr-liturgie-kruisuitdraging-n02.vsa` -> `tropaar/heilig-kruis-toon-1/hemelum/tropaar-heilig-kruis-toon-1-hemelum.vsa` (0.88)

## Nieuw

- `communievers-communievers-kruisverheffing-20260930-wo-liturgie-n03.vsa`
- `communievers-communievers-moeder-gods-08-15-ontslaping-van-de-moeder-gods-n07.vsa`; duplicaat van 2 ander(e)
- `communievers-communievers-moeder-gods-20260828-vr-liturgie-ontslapen-moeder-gods-n08.vsa`; duplicaat van 2 ander(e)
- `communievers-communievers-moeder-gods-20260903-vr-liturgie-apostel-thaddeos-n06.vsa`; duplicaat van 2 ander(e)
- `communievers-communievers-moeder-gods-20260908-di-liturgie-icoon-mgods-vladimir-n03.vsa`
- `derde-antifoon-20260828-feest-van-de-ontslaping-van-de-moeder-god-20260828-vr-liturgie-ontslapen-moeder-gods-n01.vsa`; duplicaat van 1 ander(e)
- `derde-antifoon-20260921-feest-van-de-geboorte-van-de-moeder-gods-20260921-ma-liturgie-geboorte-moeder-gods-n03.vsa`
- `derde-antifoon-derde-feestantifoon-20260819-wo-liturgie-transfiguratie-n03.vsa`
- `derde-antifoon-geboorte-van-de-moeder-gods-09-08-geboorte-van-de-moeder-gods-n03.vsa`
- `derde-antifoon-kruisverheffing-incl-09-14-kruisverheffing-n03.vsa`
- `derde-antifoon-ontslaping-van-de-moeder-gods-08-15-ontslaping-van-de-moeder-gods-n01.vsa`; duplicaat van 1 ander(e)
- `derde-antifoon-verheerlijking-op-de-berg-thabor-08-06-verheerlijking-op-de-berg-thabor-n03.vsa`
- `eer-aan-de-vader-20260828-feest-van-de-ontslaping-van-de-moeder-god-20260828-vr-liturgie-ontslapen-moeder-gods-n04.vsa`; duplicaat van 1 ander(e)
- `eer-aan-de-vader-ontslaping-van-de-moeder-gods-08-15-ontslaping-van-de-moeder-gods-n04.vsa`; duplicaat van 1 ander(e)
- `eerste-antifoon-20260921-feest-van-de-geboorte-van-de-moeder-gods-20260921-ma-liturgie-geboorte-moeder-gods-n01.vsa`
- `eerste-antifoon-eerste-feestantifoon-nls-nl-20260819-wo-liturgie-transfiguratie-n01.vsa`; duplicaat van 1 ander(e)
- `eerste-antifoon-geboorte-van-de-moeder-gods-09-08-geboorte-van-de-moeder-gods-n01.vsa`
- `eerste-antifoon-kruisverheffing-incl-09-14-kruisverheffing-n01.vsa`
- `eerste-antifoon-verheerlijking-op-de-berg-thabor-08-06-verheerlijking-op-de-berg-thabor-n01.vsa`; duplicaat van 1 ander(e)
- `kleine-intocht-20260814-feest-van-de-kruisuitdraging-en-kleine-wa-20260814-vr-liturgie-kruisuitdraging-n01.vsa`
- `kleine-intocht-20260819-feest-van-de-h-transfiguratie-vd-heer-woe-20260819-wo-liturgie-transfiguratie-n05.vsa`
- `kondak-20260911-feest-van-de-onthoofding-van-de-h-johanne-20260911-vr-liturgie-onthoofding-johannes-de-doper-n02.vsa`; duplicaat van 1 ander(e)
- `kondak-h-johannes-aartsbisschop-van-shanghai-en-san-franc-07-02-johannes-aartsbisschop-van-shanghai-en-san-francisco-n02.vsa`
- `kondak-h-marina-grootmartelares-07-17-grootmartelares-marina-n02.vsa`
- `kondak-kondak-h-apostel-thaddeos-nls-nl-20260903-vr-liturgie-apostel-thaddeos-n02.vsa`
- `kondak-kondak-hh-vera-nadjezjda-ljoebov-nl-20260930-wo-liturgie-n01.vsa`
- `kondak-kondak-icoon-mgs-nls-en-ksl-nl-20260908-di-liturgie-icoon-mgods-vladimir-n02.vsa`
- `kondak-kondak-nls-en-ksl-nl-20260828-vr-liturgie-ontslapen-moeder-gods-n05.vsa`; duplicaat van 2 ander(e)
- `kondak-kondak-profeet-elia-20260802-zo-liturgie-profeet-elias-n04.vsa`
- `kondak-kondak-van-het-feest-nls-en-ksl-nl-20260819-wo-liturgie-transfiguratie-n07.vsa`; duplicaat van 1 ander(e)
- `kondak-kondak-van-ontslapen-ksl-ksl-20260903-vr-liturgie-apostel-thaddeos-n03.vsa`; duplicaat van 2 ander(e)
- `kondak-kondakion-t-2-11-30-apostel-andreas-n02.vsa`
- `kondak-kondakion-t-4-11-21-tempelgang-moeder-gods-n02.vsa`
- `kondak-maria-magdalena-07-22-maria-magdalena-heiligenjaar-n02.vsa`
- `kondak-maria-magdalena-07-22-maria-magdalena-liturgikon-n02.vsa`
- `kondak-onthoofing-van-h-johannes-de-doper-08-31-onthoofding-johannes-de-doper-n02.vsa`; duplicaat van 1 ander(e)
- `kondak-ontslaping-van-de-moeder-gods-08-15-ontslaping-van-de-moeder-gods-n03.vsa`; duplicaat van 2 ander(e)
- `kondak-profeet-elia-07-20-profeet-elia-n02.vsa`
- `kondak-verheerlijking-op-de-berg-thabor-08-06-verheerlijking-op-de-berg-thabor-n05.vsa`; duplicaat van 1 ander(e)
- `prijslied-20260908-feest-van-de-icoon-moeder-gods-van-vladim-nl-20260908-di-liturgie-icoon-mgods-vladimir-n04.vsa`
- `prijslied-wij-verheerlijken-u-bisschop-gregorios-ksl-20260825-di-liturgie-n06.vsa`
- `prijslied-wij-verheerlijken-u-bisschop-gregorios-nl-20260825-di-liturgie-n05.vsa`
- `prokimen-20260819-feest-van-de-h-transfiguratie-vd-heer-woe-20260819-wo-liturgie-transfiguratie-n08.vsa`
- `tropaar-20260819-feest-van-de-h-transfiguratie-vd-heer-woe-20260819-wo-liturgie-transfiguratie-n04.vsa`; duplicaat van 3 ander(e)
- `tropaar-20260828-feest-van-de-ontslaping-van-de-moeder-god-20260828-vr-liturgie-ontslapen-moeder-gods-n02.vsa`; duplicaat van 3 ander(e)
- `tropaar-besnijdenis-des-heren-01-01-besnijdenis-des-heren-n01.vsa`
- `tropaar-geboorte-van-johannes-de-voorloper-06-24-geboorte-johannes-de-voorloper-n01.vsa`
- `tropaar-h-marina-grootmartelares-07-17-grootmartelares-marina-n01.vsa`
- `tropaar-maria-magdalena-07-22-maria-magdalena-heiligenjaar-n01.vsa`
- `tropaar-maria-magdalena-07-22-maria-magdalena-liturgikon-n01.vsa`
- `tropaar-ontslaping-van-de-moeder-gods-08-15-ontslaping-van-de-moeder-gods-n02.vsa`; duplicaat van 3 ander(e)
- `tropaar-tropaar-profeet-elia-20260802-zo-liturgie-profeet-elias-n03.vsa`; duplicaat van 1 ander(e)
- `tropaar-tropaar-profeet-elia-toon-4-liturgikon-p-266-267-07-20-profeet-elia-n01.vsa`; duplicaat van 1 ander(e)
- `tropaar-tropaar-transfiguratie-nls-en-ksl-nl-20260825-di-liturgie-n01.vsa`; duplicaat van 3 ander(e)
- `tropaar-tropaar-van-het-feest-nls-en-ksl-nl-20260819-wo-liturgie-transfiguratie-n06.vsa`; duplicaat van 3 ander(e)
- `tropaar-tropaar-van-het-feest-nls-en-ksl-nl-20260828-vr-liturgie-ontslapen-moeder-gods-n03.vsa`; duplicaat van 3 ander(e)
- `tropaar-tropaar-van-ontslapen-nls-en-ksl-nl-20260903-vr-liturgie-apostel-thaddeos-n01.vsa`; duplicaat van 3 ander(e)
- `tropaar-troparion-t-4-11-21-tempelgang-moeder-gods-n01.vsa`
- `tropaar-troparion-t-4-11-30-apostel-andreas-n01.vsa`
- `tropaar-verheerlijking-op-de-berg-thabor-08-06-verheerlijking-op-de-berg-thabor-n04.vsa`; duplicaat van 3 ander(e)
- `tweede-antifoon-20260921-feest-van-de-geboorte-van-de-moeder-gods-20260921-ma-liturgie-geboorte-moeder-gods-n02.vsa`
- `tweede-antifoon-geboorte-van-de-moeder-gods-09-08-geboorte-van-de-moeder-gods-n02.vsa`
- `tweede-antifoon-kruisverheffing-incl-09-14-kruisverheffing-n02.vsa`
- `tweede-antifoon-tweede-feestantifoon-nls-nl-20260819-wo-liturgie-transfiguratie-n02.vsa`; duplicaat van 1 ander(e)
- `tweede-antifoon-verheerlijking-op-de-berg-thabor-08-06-verheerlijking-op-de-berg-thabor-n02.vsa`; duplicaat van 1 ander(e)

## Duplicaatgroepen (binnen stap1)

### dup-001

- `kondak-geboorte-van-de-moeder-gods-09-08-geboorte-van-de-moeder-gods-n05.vsa` (bron: `feesteigen/09-08-geboorte-van-de-moeder-gods.md`)
- `kondak-kondak-v-h-feest-20260921-ma-liturgie-geboorte-moeder-gods-n06.vsa` (bron: `samenstellingen/20260921-ma-liturgie-geboorte-moeder-gods.md`)
- `kondak-kondak-v-h-feest-20260924-do-liturgie-nafeest-geboorte-mg-silouan-de-athoniet-n02.vsa` (bron: `samenstellingen/20260924-do-liturgie-nafeest-geboorte-mg-silouan-de-athoniet.md`)

### dup-002

- `prokimen-onthoofing-van-h-johannes-de-doper-08-31-onthoofding-johannes-de-doper-n03.vsa` (bron: `feesteigen/08-31-onthoofding-johannes-de-doper.md`)
- `prokimen-prokimen-t-7-dinsdag-20260811-di-liturgie-n04.vsa` (bron: `samenstellingen/20260811-di-liturgie.md`)
- `prokimen-prokimen-t-7-dinsdag-20260825-di-liturgie-n03.vsa` (bron: `samenstellingen/20260825-di-liturgie.md`)

### dup-003

- `tropaar-onthoofing-van-h-johannes-de-doper-08-31-onthoofding-johannes-de-doper-n01.vsa` (bron: `feesteigen/08-31-onthoofding-johannes-de-doper.md`)
- `tropaar-tropaar-h-joh-de-doper-20260802-zo-liturgie-profeet-elias-n02.vsa` (bron: `samenstellingen/20260802-zo-liturgie-profeet-elias.md`)
- `tropaar-tropaar-nls-en-ksl-nl-20260911-vr-liturgie-onthoofding-johannes-de-doper-n01.vsa` (bron: `samenstellingen/20260911-vr-liturgie-onthoofding-johannes-de-doper.md`)
- `tropaar-troparen-en-kondaken-voor-de-weekdagen-hemelum-weekdagen-troparen-en-kondaken-hemelum-n03.vsa` (bron: `hemelum-eigen/weekdagen-troparen-en-kondaken-hemelum.md`)

### dup-004

- `kondak-kondak-van-het-feest-nls-en-ksl-nl-20260819-wo-liturgie-transfiguratie-n07.vsa` (bron: `samenstellingen/20260819-wo-liturgie-transfiguratie.md`)
- `kondak-verheerlijking-op-de-berg-thabor-08-06-verheerlijking-op-de-berg-thabor-n05.vsa` (bron: `feesteigen/08-06-verheerlijking-op-de-berg-thabor.md`)

### dup-005

- `tweede-antifoon-tweede-feestantifoon-nls-nl-20260819-wo-liturgie-transfiguratie-n02.vsa` (bron: `samenstellingen/20260819-wo-liturgie-transfiguratie.md`)
- `tweede-antifoon-verheerlijking-op-de-berg-thabor-08-06-verheerlijking-op-de-berg-thabor-n02.vsa` (bron: `feesteigen/08-06-verheerlijking-op-de-berg-thabor.md`)

### dup-006

- `kondak-kondak-nls-en-ksl-nl-20260828-vr-liturgie-ontslapen-moeder-gods-n05.vsa` (bron: `samenstellingen/20260828-vr-liturgie-ontslapen-moeder-gods.md`)
- `kondak-kondak-van-ontslapen-ksl-ksl-20260903-vr-liturgie-apostel-thaddeos-n03.vsa` (bron: `samenstellingen/20260903-vr-liturgie-apostel-thaddeos.md`)
- `kondak-ontslaping-van-de-moeder-gods-08-15-ontslaping-van-de-moeder-gods-n03.vsa` (bron: `feesteigen/08-15-ontslaping-van-de-moeder-gods.md`)

### dup-007

- `communievers-communievers-moeder-gods-08-15-ontslaping-van-de-moeder-gods-n07.vsa` (bron: `feesteigen/08-15-ontslaping-van-de-moeder-gods.md`)
- `communievers-communievers-moeder-gods-20260828-vr-liturgie-ontslapen-moeder-gods-n08.vsa` (bron: `samenstellingen/20260828-vr-liturgie-ontslapen-moeder-gods.md`)
- `communievers-communievers-moeder-gods-20260903-vr-liturgie-apostel-thaddeos-n06.vsa` (bron: `samenstellingen/20260903-vr-liturgie-apostel-thaddeos.md`)

### dup-008

- `eerste-antifoon-eerste-feestantifoon-nls-nl-20260819-wo-liturgie-transfiguratie-n01.vsa` (bron: `samenstellingen/20260819-wo-liturgie-transfiguratie.md`)
- `eerste-antifoon-verheerlijking-op-de-berg-thabor-08-06-verheerlijking-op-de-berg-thabor-n01.vsa` (bron: `feesteigen/08-06-verheerlijking-op-de-berg-thabor.md`)

### dup-009

- `tropaar-h-nikolaas-van-myra-6-december-12-06-nikolaas-van-myra-liturgikon-n01.vsa` (bron: `feesteigen/12-06-nikolaas-van-myra-liturgikon.md`)
- `tropaar-tropaar-h-nikolaas-t-4-nl-20260811-di-liturgie-n01.vsa` (bron: `samenstellingen/20260811-di-liturgie.md`)
- `tropaar-tropaar-h-nikolaas-t-4-nl-20260814-vr-liturgie-kruisuitdraging-n03.vsa` (bron: `samenstellingen/20260814-vr-liturgie-kruisuitdraging.md`)

### dup-010

- `tropaar-h-nikolaas-van-myra-6-december-12-06-nikolaas-van-myra-hemelum-n01.vsa` (bron: `feesteigen/12-06-nikolaas-van-myra-hemelum.md`)
- `tropaar-h-nikolaas-van-myra-6-december-tropaar-kondak-nikolaas-van-myra-n01.vsa` (bron: `hemelum-eigen/tropaar-kondak-nikolaas-van-myra.md`)

### dup-011

- `prokimen-20260903-nafeest-van-ontslapen-h-apostel-thaddeos-20260903-vr-liturgie-apostel-thaddeos-n04.vsa` (bron: `samenstellingen/20260903-vr-liturgie-apostel-thaddeos.md`)
- `prokimen-prokimen-t-3-20260814-vr-liturgie-kruisuitdraging-n09.vsa` (bron: `samenstellingen/20260814-vr-liturgie-kruisuitdraging.md`)

### dup-012

- `derde-antifoon-20260828-feest-van-de-ontslaping-van-de-moeder-god-20260828-vr-liturgie-ontslapen-moeder-gods-n01.vsa` (bron: `samenstellingen/20260828-vr-liturgie-ontslapen-moeder-gods.md`)
- `derde-antifoon-ontslaping-van-de-moeder-gods-08-15-ontslaping-van-de-moeder-gods-n01.vsa` (bron: `feesteigen/08-15-ontslaping-van-de-moeder-gods.md`)

### dup-013

- `kondak-kondak-h-kruis-nls-nl-20260814-vr-liturgie-kruisuitdraging-n04.vsa` (bron: `samenstellingen/20260814-vr-liturgie-kruisuitdraging.md`)
- `kondak-troparen-en-kondaken-voor-de-weekdagen-hemelum-weekdagen-troparen-en-kondaken-hemelum-n06.vsa` (bron: `hemelum-eigen/weekdagen-troparen-en-kondaken-hemelum.md`)

### dup-014

- `tropaar-neerleggen-van-de-mantel-van-de-moeder-gods-blache-07-15-neerleggen-mantel-moeder-gods-blachernakerk-n01.vsa` (bron: `feesteigen/07-15-neerleggen-mantel-moeder-gods-blachernakerk.md`)
- `tropaar-tropaar-van-de-mantel-van-de-moeder-gods-tropaar-mantel-moeder-gods-hemelum-n01.vsa` (bron: `hemelum-eigen/tropaar-mantel-moeder-gods-hemelum.md`)

### dup-015

- `tropaar-20260921-feest-van-de-geboorte-van-de-moeder-gods-20260921-ma-liturgie-geboorte-moeder-gods-n04.vsa` (bron: `samenstellingen/20260921-ma-liturgie-geboorte-moeder-gods.md`)
- `tropaar-geboorte-van-de-moeder-gods-09-08-geboorte-van-de-moeder-gods-n04.vsa` (bron: `feesteigen/09-08-geboorte-van-de-moeder-gods.md`)
- `tropaar-tropaar-v-h-feest-20260921-ma-liturgie-geboorte-moeder-gods-n05.vsa` (bron: `samenstellingen/20260921-ma-liturgie-geboorte-moeder-gods.md`)
- `tropaar-tropaar-vh-feest-vd-geb-mgods-nls-en-ksl-nl-20260924-do-liturgie-nafeest-geboorte-mg-silouan-de-athoniet-n01.vsa` (bron: `samenstellingen/20260924-do-liturgie-nafeest-geboorte-mg-silouan-de-athoniet.md`)

### dup-016

- `eer-aan-de-vader-20260828-feest-van-de-ontslaping-van-de-moeder-god-20260828-vr-liturgie-ontslapen-moeder-gods-n04.vsa` (bron: `samenstellingen/20260828-vr-liturgie-ontslapen-moeder-gods.md`)
- `eer-aan-de-vader-ontslaping-van-de-moeder-gods-08-15-ontslaping-van-de-moeder-gods-n04.vsa` (bron: `feesteigen/08-15-ontslaping-van-de-moeder-gods.md`)

### dup-017

- `tropaar-20260828-feest-van-de-ontslaping-van-de-moeder-god-20260828-vr-liturgie-ontslapen-moeder-gods-n02.vsa` (bron: `samenstellingen/20260828-vr-liturgie-ontslapen-moeder-gods.md`)
- `tropaar-ontslaping-van-de-moeder-gods-08-15-ontslaping-van-de-moeder-gods-n02.vsa` (bron: `feesteigen/08-15-ontslaping-van-de-moeder-gods.md`)
- `tropaar-tropaar-van-het-feest-nls-en-ksl-nl-20260828-vr-liturgie-ontslapen-moeder-gods-n03.vsa` (bron: `samenstellingen/20260828-vr-liturgie-ontslapen-moeder-gods.md`)
- `tropaar-tropaar-van-ontslapen-nls-en-ksl-nl-20260903-vr-liturgie-apostel-thaddeos-n01.vsa` (bron: `samenstellingen/20260903-vr-liturgie-apostel-thaddeos.md`)

### dup-018

- `tropaar-tropaar-hh-martelaren-t-4-nl-20260811-di-liturgie-n02.vsa` (bron: `samenstellingen/20260811-di-liturgie.md`)
- `tropaar-tropaar-hh-martelaren-tropaar-heilige-martelaren-hemelum-n01.vsa` (bron: `hemelum-eigen/tropaar-heilige-martelaren-hemelum.md`)

### dup-019

- `prokimen-20260828-feest-van-de-ontslaping-van-de-moeder-god-nl-20260828-vr-liturgie-ontslapen-moeder-gods-n06.vsa` (bron: `samenstellingen/20260828-vr-liturgie-ontslapen-moeder-gods.md`)
- `prokimen-ontslaping-van-de-moeder-gods-08-15-ontslaping-van-de-moeder-gods-n05.vsa` (bron: `feesteigen/08-15-ontslaping-van-de-moeder-gods.md`)

### dup-020

- `uw-heilig-kruis-nls-versie-uit-liturgikon-nl-20260814-vr-liturgie-kruisuitdraging-n05.vsa` (bron: `samenstellingen/20260814-vr-liturgie-kruisuitdraging.md`)
- `uw-heilig-kruis-uw-heilig-kruis-weekdagen-troparen-en-kondaken-hemelum-n07.vsa` (bron: `hemelum-eigen/weekdagen-troparen-en-kondaken-hemelum.md`)

### dup-021

- `tropaar-tropaar-icoon-moeder-gods-vladimir-nls-en-ksl-nl-20260908-di-liturgie-icoon-mgods-vladimir-n01.vsa` (bron: `samenstellingen/20260908-di-liturgie-icoon-mgods-vladimir.md`)
- `tropaar-tropaar-icoon-moeder-gods-vladimir-tropaar-icoon-moeder-gods-vladimir-hemelum-n01.vsa` (bron: `hemelum-eigen/tropaar-icoon-moeder-gods-vladimir-hemelum.md`)

### dup-022

- `communievers-communievers-onthoofding-johannes-de-doper-08-31-onthoofding-johannes-de-doper-n04.vsa` (bron: `feesteigen/08-31-onthoofding-johannes-de-doper.md`)
- `communievers-communievers-onthoofding-johannes-de-doper-20260911-vr-liturgie-onthoofding-johannes-de-doper-n03.vsa` (bron: `samenstellingen/20260911-vr-liturgie-onthoofding-johannes-de-doper.md`)

### dup-023

- `moeder-godslied-20260924-nafeest-vd-geboorte-vd-mgods-h-silouan-de-20260924-do-liturgie-nafeest-geboorte-mg-silouan-de-athoniet-n03.vsa` (bron: `samenstellingen/20260924-do-liturgie-nafeest-geboorte-mg-silouan-de-athoniet.md`)
- `moeder-godslied-moeder-godslied-nls-nl-20260819-wo-liturgie-transfiguratie-n09.vsa` (bron: `samenstellingen/20260819-wo-liturgie-transfiguratie.md`)
- `moeder-godslied-moeder-godslied-v-h-feest-v-d-transfiguratie-08-06-verheerlijking-op-de-berg-thabor-n06.vsa` (bron: `feesteigen/08-06-verheerlijking-op-de-berg-thabor.md`)
- `moeder-godslied-moeder-godslied-v-h-feest-v-d-transfiguratie-20260825-di-liturgie-n04.vsa` (bron: `samenstellingen/20260825-di-liturgie.md`)
- `moeder-godslied-moeder-godslied-vh-feest-kruisverheffing-20260930-wo-liturgie-n02.vsa` (bron: `samenstellingen/20260930-wo-liturgie.md`)

### dup-024

- `tropaar-20260819-feest-van-de-h-transfiguratie-vd-heer-woe-20260819-wo-liturgie-transfiguratie-n04.vsa` (bron: `samenstellingen/20260819-wo-liturgie-transfiguratie.md`)
- `tropaar-tropaar-transfiguratie-nls-en-ksl-nl-20260825-di-liturgie-n01.vsa` (bron: `samenstellingen/20260825-di-liturgie.md`)
- `tropaar-tropaar-van-het-feest-nls-en-ksl-nl-20260819-wo-liturgie-transfiguratie-n06.vsa` (bron: `samenstellingen/20260819-wo-liturgie-transfiguratie.md`)
- `tropaar-verheerlijking-op-de-berg-thabor-08-06-verheerlijking-op-de-berg-thabor-n04.vsa` (bron: `feesteigen/08-06-verheerlijking-op-de-berg-thabor.md`)

### dup-025

- `moeder-godslied-20260828-feest-van-de-ontslaping-van-de-moeder-god-20260828-vr-liturgie-ontslapen-moeder-gods-n07.vsa` (bron: `samenstellingen/20260828-vr-liturgie-ontslapen-moeder-gods.md`)
- `moeder-godslied-ontslaping-van-de-moeder-gods-08-15-ontslaping-van-de-moeder-gods-n06.vsa` (bron: `feesteigen/08-15-ontslaping-van-de-moeder-gods.md`)

### dup-026

- `kondak-kondak-h-johannes-de-doper-20260811-di-liturgie-n03.vsa` (bron: `samenstellingen/20260811-di-liturgie.md`)
- `kondak-troparen-en-kondaken-voor-de-weekdagen-hemelum-weekdagen-troparen-en-kondaken-hemelum-n04.vsa` (bron: `hemelum-eigen/weekdagen-troparen-en-kondaken-hemelum.md`)

### dup-027

- `kondak-h-nikolaas-van-myra-6-december-12-06-nikolaas-van-myra-hemelum-n02.vsa` (bron: `feesteigen/12-06-nikolaas-van-myra-hemelum.md`)
- `kondak-h-nikolaas-van-myra-6-december-12-06-nikolaas-van-myra-liturgikon-n02.vsa` (bron: `feesteigen/12-06-nikolaas-van-myra-liturgikon.md`)
- `kondak-h-nikolaas-van-myra-6-december-tropaar-kondak-nikolaas-van-myra-n02.vsa` (bron: `hemelum-eigen/tropaar-kondak-nikolaas-van-myra.md`)

### dup-028

- `tropaar-tropaar-profeet-elia-20260802-zo-liturgie-profeet-elias-n03.vsa` (bron: `samenstellingen/20260802-zo-liturgie-profeet-elias.md`)
- `tropaar-tropaar-profeet-elia-toon-4-liturgikon-p-266-267-07-20-profeet-elia-n01.vsa` (bron: `feesteigen/07-20-profeet-elia.md`)

### dup-029

- `kondak-20260911-feest-van-de-onthoofding-van-de-h-johanne-20260911-vr-liturgie-onthoofding-johannes-de-doper-n02.vsa` (bron: `samenstellingen/20260911-vr-liturgie-onthoofding-johannes-de-doper.md`)
- `kondak-onthoofing-van-h-johannes-de-doper-08-31-onthoofding-johannes-de-doper-n02.vsa` (bron: `feesteigen/08-31-onthoofding-johannes-de-doper.md`)

