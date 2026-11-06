---
title: "bieb hernoem"
linkTitle: "bieb hernoem"
weight: 165
---

# NAME

`bieb hernoem` — catalogus-id hernoemen (zangstuk, variant of
uitvoeringsvorm: map, publicatiestam, id-verwijzingen, koormap-slots)

# SYNOPSIS

```cmd
scripts\bieb.cmd hernoem <oud> <nieuw> [--dry-run]
scripts\bieb.cmd rename <oud> <nieuw> [--dry-run]
```

Met `.\scripts` op PATH: `bieb hernoem …`. Engelse alias: `rename`.
Korte hulp: `h bieb hernoem` of `bieb hernoem -h`. Typ `?` bij een vraag
voor uitleg met voorbeelden.

# DESCRIPTION

Hernoemt één catalogus-id. Je hoeft niet te kiezen welk “niveau” het is:
de vorm van het id bepaalt dat. Oud en nieuw moeten **hetzelfde niveau**
zijn (zangstuk, variant of uitvoeringsvorm). De doelmap mag nog niet
bestaan.

## Toegestane id-vormen (oud en nieuw)

| Invoer | Betekenis |
| --- | --- |
| `ektinia` | zangstuk-id |
| `ektinia/vredes` of `ektinia-vredes` | variant |
| `ektinia/vredes/hemelum` of `ektinia-vredes-hemelum` | uitvoeringsvorm |
| `ektinia\vredes\hemelum` | zelfde, met Windows-backslashes |
| `content-source\catalogus\ektinia\vredes\hemelum` | pad t.o.v. de repository-map |
| `vredes/hemelum` of `vredes-hemelum` | alleen als dat **uniek** is in de hele catalogus |
| alleen `hemelum` | alleen als die uitvoeringsvorm-naam **uniek** is |

Nieuw id mag **korter** t.o.v. de bron (zelfde ouder):

| Nieuw (kort) | Voorbeeld | Wordt |
| --- | --- | --- |
| Alleen uitvoeringsvorm | `groningen` of `hemelum-ksl` | `…/vredes/groningen` |
| `variant/uv` of `variant\uv` | `vredes\groningen` | `ektinia/vredes/groningen` |
| `variant-uv` | `vredes-groningen` | `ektinia/vredes/groningen` |

## Ambiguïteit

Past de invoer op meer dan één bestaand id, dan toont het script
**genummerde voorstellen**. Enter kiest nummer 1; je mag ook een nummer
of een eenduidige slash-vorm typen. `?` toont de hulptekst.

## Wat het script doet

1. Verplaatst de catalogusmap.
2. Hernoemt bestanden met de oude publicatiestam
   (`.vsa`, `.vsa.mxl`, `.lyrics.txt`, `.mp3`, …).
3. Verplaatst bladermap-SVG’s onder `static\vsa\bladermap\catalogus\`.
4. Hernoemt **koormap-mappen** waarvan de naam gelijk is aan het oude
   zangstuk-id (bij zangstuk-hernoem) of aan de oude stam (bij
   variant/uitvoeringsvorm), zodat TOC-links niet 404 geven.
5. Werkt id-verwijzingen bij (`bieb id=…`, `alias_van`, paden, stam in
   docs). Catalogus-titels hoeven niet herschreven: die leidt de bouw
   af uit het (nieuwe) id; zie
   [Catalogus en koormappen](../../start/catalogus-en-koormappen/) (§ Titels).

Twijfelgevallen (bijv. oude id alleen in een `title:`-regel) worden
getoond, niet stil herschreven.

Hugo-`aliases` voor oude URL’s worden **niet** gezet.

Daarna: producten vernieuwen waar de colofon/stam mee moet, daarna
`python scripts\build_zoek_index.py` en `scripts\check.cmd`.

**Let op:** koormap-slots met een bewuste andere pleknaam (bijvoorbeeld
litanie-map terwijl het catalogus-id `ektinia` is) worden niet hernoemd
op mapnaam — wel worden `bieb id=`-verwijzingen bijgewerkt.

# EXAMPLES

Eerst altijd dry-run:

```cmd
scripts\bieb.cmd hernoem ektinia litanie --dry-run
scripts\bieb.cmd hernoem ektinia/vredes ektinia/vredeslitanie --dry-run
scripts\bieb.cmd hernoem ektinia-vredes-hemelum groningen --dry-run
scripts\bieb.cmd hernoem ektinia\vredes\hemelum vredes\groningen --dry-run
scripts\bieb.cmd rename ektinia litanie --dry-run
scripts\bieb.cmd hernoem ektinia litanie
scripts\check.cmd --strict
```

# WHEN

Als je een catalogus-id wilt wijzigen en mappen, publicatiestam en
id-verwijzingen (inclusief koormappen) mee moeten. Niet voor alleen
cosmetische `title`/`linkTitle` — die komen uit het id.

Werktraject: [Catalogus-id hernoemen](../../werktrajecten/zangstuk-hernoemen/).

# SEE ALSO

[bieb accepteer](../bieb-accepteer/),
[bieb verwijder](../bieb-verwijder/),
[bieb kopieer](../bieb-kopieer/),
[check](../check/),
[Catalogus-id hernoemen](../../werktrajecten/zangstuk-hernoemen/),
[Catalogus en koormappen](../../start/catalogus-en-koormappen/),
[h](../h/)
