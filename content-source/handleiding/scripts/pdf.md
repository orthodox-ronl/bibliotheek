---
title: "pdf"
linkTitle: "pdf"
weight: 52
---

# NAME

`scripts\pdf.cmd` — PDF van een koormap- of cataloguspagina
samenstellen uit kale blad-SVG’s en Markdown-koppen (geen
catalogus-product-PDF’s plakken)

# SYNOPSIS

```cmd
scripts\pdf.cmd <pad\naar\index.md|map> [--force]
scripts\pdf.cmd --all-koormappen [--force]
```

# DESCRIPTION

Maakt de PDF achter de knop **Download pagina**: één
bestand `index.md.pdf` naast de Markdown van een bladermap-pagina (Hugo
page resource). Dat is de PDF van de **getoonde pagina** (koormap-slot of
catalogus-uitvoeringsvorm), niet hetzelfde als de losse catalogus-product-PDF
van één uitvoeringsvorm.

Dit commando hoort niet bij `products`, `all-products`, `check` of de
Pages-build. Die keten maakt en controleert catalogus-siblings
(`.mvsa.pdf`, `.mvsa.svg`, `.vsa.svg`, en de rest). De pagina-PDF maak je
lokaal uit de **notatiebronnen** (`.mvsa` / `.vsa` / `.mscz`) plus de
Markdown-layout, en commit je mee. `check` meldt niet of de pagina-PDF
ontbreekt. MuseScore 4 is nodig voor `.mvsa`/`.mscz`-SVG-export (en dus
zodra de pagina zulke bronnen of `pdf-bijelkaar` gebruikt).

Catalogus-leaves: ontwerp en restmijlpalen in
`docs/plans/catalogus-index-md-pdf.md`.

**Download pagina** gebruikt die PDF. De site stelt een bestandsnaam voor:
frontmatter `pdf_bestandsnaam`; anders op een koormap `title`, op een catalogus-blad
de afgeleide bladtitel; anders de mapnaam — zie
`docs\specs\koormap-paginataal.md`. Zonder dit bestand tonen de knoppen
niet. Er is geen aparte browser-HTML-afdruk meer via de navigatie (dat
was hetzelfde als Ctrl+P).

Invoer volgt [bestand of map](../invoer-bestand-of-map/): één `.md` of een
map (recursief alle `index.md`). `--all-koormappen` is suiker voor het pad
`content-source\koormappen`. Bij meerdere pagina’s: preflight met geschatte
duur en bevestiging (of `-y`).

**Contract (doelmodel):** de pagina-PDF volgt de koormap-Markdown. Shortcode
`pdf-bijelkaar` betekent: streef naar **één A4** voor de inhoud van dat blok.
Daarvoor exporteert de pijplijn de muziek in dat blok opnieuw met VSA-tooling
**`--compact`** (dichtere systeemafstand en marges), en zet koppen uit de
Markdown bij de notatie. De canonieke catalogus-`.mvsa.pdf` / `.mvsa.svg`
blijven het losse oefenblad zonder die compact-override. Zie de specificatie
`docs\specs\koormap-paginataal.md` (§9).

**Afspraak (org):** kale muziek = SVG zonder catalogus-/titel-chrome;
koormap-`index.md.pdf` mag **niet** gebouwd worden door catalogus-PDF’s
te plakken (metadata-dubbeling). Richting: blad-SVG’s + Markdown-layout.
Later: tall scherm-SVG of Score-IR. Plan in VSA-tooling:
[kale-muziek-svg-en-uitgaven](https://github.com/orthodox-ronl/VSA-tooling/blob/main/docs/plans/kale-muziek-svg-en-uitgaven.md).

**Huidige implementatie:** kale blad-SVG’s + koppen uit de Markdown op A4
(`index.md.pdf`). Bron: `.mvsa` / `.vsa` / `.mscz` in de catalogusmap —
**geen** plakken van catalogus-product-PDF’s. Binnen `pdf-bijelkaar`: opnieuw
exporteren met `mvsa svg --compact`. Meerdere MuseScore-pagina’s worden als
bladreeks (`stem-1.svg`, …) onder elkaar gezet. Vereist MuseScore 4 (bij
`.mvsa`/`.mscz`) en `pymupdf`.

Catalogus-leaf **zonder** notatie (stub / `voorzien`, geen tekstblad): één
A4 met de afgeleide titel en de tekst dat het blad voorzien is. Zelfde
bestand `index.md.pdf`, zodat **Download pagina** werkt.
`bieb accepteer --stub` maakt die PDF meteen mee.

Catalogus-leaf met alleen een **tekstblad** (`.tekstblad.pdf`): titel uit
het tekstblad-frontmatter, toelichting uit gewone alinea’s in de leaf-`index.md`,
daarna de getrimde inhoud van het tekstblad-PDF (onderste witruimte weg),
idealiter op één A4.

# OPTIONS

| Optie | Betekenis |
| --- | --- |
| `--all-koormappen` | Suiker: zelfde als pad `content-source\koormappen` |
| `--force` | Opnieuw schrijven, ook als de PDF nieuwer lijkt dan de bronnen |
| `-y`, `--yes` | Batch zonder bevestigingsvraag |

# EXAMPLES

Vredeslitanie (NL + KSL in `pdf-bijelkaar`):

```cmd
scripts\pdf.cmd content-source\koormappen\hemelum\liturgie-zondag\vredeslitanie\index.md
```

Hele zondagsliturgie-map:

```cmd
scripts\pdf.cmd content-source\koormappen\hemelum\liturgie-zondag
```

# WHEN

Je hebt de shortcodes op een slot-pagina gezet of gewijzigd en wilt de
knop **Download pagina** een actuele pagina-PDF geven. Ook vóór
push/PR: `check` (en CI) eist die PDF bij bladen met `bieb`/`muziek`
waar een notatiebron bestaat — zie [check](../check/).

# SEE ALSO

- [Koormap-blad schrijven](/handleiding/start/koormap-blad/) — spiekbriefje voor shortcodes
- [Catalogus en koormappen](/handleiding/start/catalogus-en-koormappen/)
- Spec: `docs\specs\koormap-paginataal.md` in de repository
- Plan catalogus-leaves: `docs\plans\catalogus-index-md-pdf.md`
