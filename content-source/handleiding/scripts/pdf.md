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
scripts\pdf.cmd <pad\naar\index.md|map> [--force] [--verbose]
scripts\pdf.cmd --all-koormappen [--force] [--verbose]
```

# DESCRIPTION

Maakt de PDF achter het **download-icoon** in de navigatie: eerst altijd
`index.md.pdf` naast de Markdown van een bladermap-pagina (Hugo page
resource). Dat is de PDF van de **getoonde pagina** (koormap-slot of
catalogus-uitvoeringsvorm), niet hetzelfde als een losse
catalogus-product-PDF van één uitvoeringsvorm.

Zelfde run schrijft waar nodig ook translit-pagina-PDF’s (§5a), uit de
translit-SVG-siblings:

| Broninhoud op het blad | Extra bestanden naast `index.md.pdf` |
| ---------------------- | ------------------------------------ |
| Puur Nederlands        | `index.md.translit-ksl.pdf`          |
| Puur kerkslavisch      | `index.md.translit-nls.pdf`          |
| Hybride (nl + ksl)     | beide                                |

Ontbreekt de bijbehorende `{bron}.translit-*.svg`, dan exporteert
`pdf.cmd` die SVG onderweg (MuseScore bij `.mvsa`). Op de site volgt
het **download-icoon** de translit-knoppen (geen knop → basis-PDF;
**ФЛД→FLD**/Nls of **FLD→ФЛД**/Ksl → translit-PDF). `check --strict`
eist de translit-PDF’s nog niet; wél de basis-`index.md.pdf`.

Dit commando hoort niet bij `products`, `products --kinds all` of de
Pages-build. **Volgorde:** eerst catalogus-siblings vernieuwen met
[products](../products/) (`.mvsa.svg` / `.vsa.svg` / `.mscz.svg` en
eventuele translit-SVG’s), daarna pas `pdf.cmd`. Zo gebruikt de
pagina-PDF de verse product-SVG’s. Ontbreekt of is een sibling-SVG
verouderd (herkomststempel past niet bij de bron), dan exporteert
`pdf.cmd` die SVG nog lokaal opnieuw — dat is noodhulp, geen vervanging
van `products`. Gewijzigde koormap-`index.md` meenemen na een git-edit:
[products-changed](../products-changed/). De pagina-PDF maak je lokaal
uit de **notatiebronnen**, de sibling-SVG’s en de Markdown-layout, en
commit je mee. MuseScore 4 is nodig voor `.mvsa`/`.mscz`-SVG-export (en
dus zodra de pagina zulke bronnen of `pdf-bijelkaar` gebruikt).

**Uitvoer:** standaard `OK …` per gemaakte PDF en een slotregel
`Klaar: …`. Tussenstappen (bron, SVG, schaal, …) alleen met `--verbose`.

Catalogus-leaves: ontwerp en restmijlpalen in
`docs/plans/catalogus-index-md-pdf.md`.

Het **download-icoon** gebruikt die PDF’s. De site stelt een bestandsnaam voor:
frontmatter `pdf_bestandsnaam`; anders op een koormap `title`, op een catalogus-blad
de afgeleide bladtitel; anders de mapnaam — zie
`docs\specs\koormap-paginataal.md`. Bij actieve translit-knop krijgt de
voorgestelde naam het achtervoegsel « (translit Nls)» of « (translit Ksl)»;
op schijf blijven de namen `index.md.pdf` / `index.md.translit-*.pdf`.
Zonder basis-`index.md.pdf` (en zonder enige translit-PDF) blijft het
download-icoon weg. Er is geen aparte browser-HTML-afdruk meer via de
navigatie (dat was hetzelfde als Ctrl+P).

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
(`index.md.pdf`, plus optioneel translit-varianten). Bron: `.mvsa` /
`.vsa` / `.mscz` in de catalogusmap — **geen** plakken van
catalogus-product-PDF’s. Translit-varianten gebruiken
`*.translit-nls.svg` / `*.translit-ksl.svg`. Binnen `pdf-bijelkaar`: opnieuw
exporteren met `mvsa svg --compact`. Vereist MuseScore 4 (bij `.mvsa`/`.mscz`)
en `pymupdf`.

Catalogus-leaf **zonder** notatie (stub / `voorzien`, geen tekstblad): één
A4 met de afgeleide titel en de tekst dat het blad voorzien is. Zelfde
bestand `index.md.pdf`, zodat het **download-icoon** werkt.
`bieb accepteer --stub` maakt die PDF meteen mee.

Catalogus-leaf met alleen een **tekstblad** (`.tekstblad.pdf`): titel uit
het tekstblad-frontmatter, toelichting uit gewone alinea’s in de leaf-`index.md`,
daarna de getrimde inhoud van het tekstblad-PDF (onderste witruimte weg),
idealiter op één A4.

# OPTIONS

| Optie              | Betekenis                                                      |
| ------------------ | -------------------------------------------------------------- |
| `--all-koormappen` | Suiker: zelfde als pad `content-source\koormappen`             |
| `--force`          | Opnieuw schrijven, ook als de PDF nieuwer lijkt dan de bronnen |
| `-y`, `--yes`      | Batch zonder bevestigingsvraag                                 |

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
**download-icoon** een actuele pagina-PDF geven. Ook vóór
push/PR: `check` (en CI) eist die PDF bij bladen met `bieb`/`muziek`
waar een notatiebron bestaat — zie [check](../check/). Na een
notatiewijziging: eerst [products](../products/) voor die bronnen, dan
`pdf.cmd` voor de bladermap-pagina’s die ernaar verwijzen.

# SEE ALSO

- [products](../products/) — sibling-SVG’s en andere catalogus-afgeleiden
- [Koormap-blad schrijven](/handleiding/start/koormap-blad/) — spiekbriefje voor shortcodes
- [Catalogus en koormappen](/handleiding/start/catalogus-en-koormappen/)
- Spec: `docs\specs\koormap-paginataal.md` in de repository
- Plan catalogus-leaves: `docs\plans\catalogus-index-md-pdf.md`
