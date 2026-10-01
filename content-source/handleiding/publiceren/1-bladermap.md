---
title: "Catalogus en koormap"
linkTitle: "Catalogus en koormap"
weight: 10
---

# Catalogus en koormap

{{< cue >}}
Nieuwe partituur in de catalogus zetten:
[Opnemen in de catalogus](../1-opnemen-in-catalogus/)
(`bieb accepteer`).

Slot-pagina in de koormap:
`content-source\koormappen\hemelum\liturgie-zondag\…\index.md` (of
`liturgie-weekdagen`) met
shortcode `bieb` (parameter `id` = catalogus-id) en
`automatische_inhoud: false`. Geen basispartituur-bestanden in de koormap-map.

Een **alias-variant** (andere naam voor dezelfde variant) krijgt geen
uitvoeringsvorm-map. Zet `alias_van` op de variant-`_index.md`; zie
[Catalogus en koormappen](../../start/catalogus-en-koormappen/).

Koormap-sectie (hoofdstuk): map met `_index.md` — kindlijst of eigen TOC;
zie [Catalogus en koormappen](../../start/catalogus-en-koormappen/).

Id-lijst: [Id-register](/catalogus/id-register/).
{{< /cue >}}

**Wat je nu doet:** na het opnemen van bestanden in de **catalogus** de
**koormap** laten verwijzen, zodat koorleden de liturgiemap kunnen volgen.
De partituur blijft in de catalogus; de koormap is de route.

**Wanneer:** nadat [opnemen in de catalogus](../1-opnemen-in-catalogus/)
klaar is (of de leaf al bestaat). Familie met meerdere varianten op één
liturgische plek: zie
[Catalogus en koormappen](../../start/catalogus-en-koormappen/).

## Catalogus: kort

Gebruik **bieb accepteer** voor mappen, `index.md` en de juiste
bestandsnamen. Handmatig kopiëren van voorbeelden is alleen nog nodig bij
uitzonderingen. Details en voorbeelden van commando’s:
[Opnemen in de catalogus](../1-opnemen-in-catalogus/).

Titels en `linkTitle` (zangstuk / variant / leaf): zie
[Catalogus en koormappen](../../start/catalogus-en-koormappen/)
(sectie *Titels en frontmatter*).

Pad na acceptatie:
`content-source\catalogus\<zangstuk>\<variant>\<uitvoeringsvorm>\`
met `index.md` + oefenbestanden (publicatiestam zonder spaties).

Een **alias-variant** (andere naam voor dezelfde variant) krijgt geen
uitvoeringsvorm-map. Zet `alias_van` op de variant-`_index.md`; zie
[Catalogus en koormappen](../../start/catalogus-en-koormappen/).

## Stap voor stap (slot-pagina in de koormap)

1. Open of maak de slot-pagina (bijvoorbeeld
   `koormappen/hemelum/liturgie-zondag\trisagion\8a-trisagion\index.md`).
2. Zorg dat alleen **`index.md`** in die slotmap staat — geen `.mscz` meer
   in de koormap.
3. Frontmatter: `automatische_inhoud: false`, `publicatiestatus` passend
   bij wat koorleden zien.
4. In de body: titel + shortcode `bieb` met jouw id (voorbeeld:
   `trisagion/8a-nederlands/hemelum`).

| Situatie | Koormap-voorbeeld |
| --- | --- |
| Basispartituur via catalogus | `koormappen/hemelum/liturgie-zondag\trisagion\8a-trisagion\index.md` |
| VSA via catalogus | `koormappen/hemelum/liturgie-weekdagen\eerste-antifoon\weekdagen\index.md` |
| Sectie (boom van keuzes) | `koormappen/hemelum/liturgie-zondag\cherubijnenhymne\_index.md` + kindmappen |
| Compositieblad (meerdere scores) | Eén `index.md` met markdown en meerdere `bieb`-shortcodes — zie [Catalogus en koormappen](../../start/catalogus-en-koormappen/) |
| Troparen / kondaken / losse gezangen | Bijv. `tropaar/…`, `kondak/…`, `tropaar/uw-heilig-kruis/hemelum` — altijd `bieb`, geen `:::include` |

5. Hoort het stuk in het liturgie-overzicht? Controleer
   `koormappen/hemelum/liturgie-zondag\_index.md` of
   `liturgie-weekdagen\_index.md` (handmatige inhoudsopgave).

### Meerdere shortcodes op één slot-pagina

Op een compositieblad mag je **meerdere** `bieb`-shortcodes
zetten (elk met een eigen catalogus-id). Elke shortcode zet eerst de
knoppen **Oefenen** / **Downloaden** / **Printen** voor die uitvoeringsvorm,
en daarna de PDF of VSA-SVG. Zo heeft elke score op dezelfde pagina een
eigen knoppenrij.

## Oude migratie (alleen historisch)

De eenmalige verhuizing van basispartituren uit de liturgiemap naar de catalogus is
al gedaan. Nieuwe stukken gaan via
[opnemen in de catalogus](../1-opnemen-in-catalogus/). Het oude script
`migrate_oefenhoek_bibliotheek.py` is geen dagelijkse tool meer.

## Klaar als

Na `check --strict` toont de preview de slot-pagina met PDF/**Oefenen**/VSA
via `bieb`. De catalogus heeft de bestanden; de
koormap-map heeft geen basispartituur meer. Je weet wanneer je een sectie (boom)
gebruikt en wanneer een compositieblad.

{{< navbuttons "Vorige: opnemen in de catalogus|/handleiding/publiceren/1-opnemen-in-catalogus/" "Volgende: status en check|/handleiding/publiceren/2-status-en-check/" >}}
