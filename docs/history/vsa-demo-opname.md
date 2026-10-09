# VSA-demo → catalogus (afgerond)

Eenmalige overzetting van oefenmateriaal uit de VSA-demo-site naar
`content-source/catalogus/`. De tussenmap
`content-source/input/vsa-demo/` is **verwijderd** na opname; dit document
is het bewaarde verslag.

## Traject

1. **Stap 1** — VSA-blokken uit demo-Markdown → `_stap1/`  
   Script: `scripts/extract-vsa-demo-md.py`
2. **Stap 2** — normaliseren + vergelijken met catalogus → `_stap2/`  
   Scripts: `scripts/stap2-vergelijk-vsa.py`, `scripts/stap2-verwerken.py`
3. **Opname** — nieuw/varianten/twijfel → catalogus (`bieb accepteer`)  
   Script: `scripts/_stap2_nieuw_accepteer.py`

Die scripts blijven in de repo als historisch hulpmiddel. Zonder de
inputmap doen ze niets nuttigs meer.

## Stap-2-vergelijking (samenvatting)

- Catalogus-VSA destijds: 62 · Stap1-VSA: 138
- **al in bieb** (notatie gelijk na normalisatie): 52
- **mogelijke variant**: 19
- **twijfel**: 2
- **nieuw**: 65
- **duplicaatgroepen** binnen stap1: 29

## Stap-2-verwerking (eindstand)

- Catalogus verrijkt (al-in-bieb, daarna weg uit `_stap2`): **29**
- Varianten: **13**
- Twijfel: **2** → opgenomen:
  - `tropaar/heer-red-uw-volk/hemelum`
  - `tropaar/gregorios-van-utrecht-toon-4/hemelum`
- Nieuw: **48** → opgenomen (5 near-dups liturgie geschrapt t.g.v.
  feesteigen); map leeg
- Fouten: **0**
- Duplicaatgroepen samengevoegd: **29**

Prijslied icoon Vladimir: bestaande uitvoeringsvorm hernoemd
`…/hemelum` → `…/meneon-1`; nieuw Hemelum-prijslied als `…/hemelum`.

Import-YAML (`herkomst_vsa_demo`, `stap2_*`) is later gestript via
`scripts/migrate_vsa_frontmatter.py` naar het schema in
[vsa-frontmatter.md](../specs/vsa-frontmatter.md).

## Wat nog open kan staan

Veel opgenomen bladen staan op `publicatiestatus: reviewable` en kunnen
nog een **inhoudelijke opkuisronde** nodig hebben (Liturgikon-pagina’s in
body-commentaar, structuur derde antifoon, MVSA-ektinia, enz.). Dat is
geen herstel van de dump: de canonieke bron staat in de catalogus.
