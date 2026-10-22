---
title: "pagina-pdf"
linkTitle: "pagina-pdf"
weight: 52
---

# NAME

`scripts\pagina-pdf.cmd` — PDF van een koormap- of cataloguspagina
samenstellen uit catalogus-product-PDF’s

# SYNOPSIS

```cmd
scripts\pagina-pdf.cmd <pad\naar\index.md|map> [--force]
scripts\pagina-pdf.cmd --all-koormappen [--force]
```

# DESCRIPTION

Maakt de PDF achter de knoppen **Download pagina** en **Print pagina**: één
bestand `index.pagina.pdf` naast de Markdown van een bladermap-pagina (Hugo
page resource). Dat is de PDF van de **getoonde pagina**, niet van één los
catalogusblad.

Dit commando hoort niet bij `products`, `all-products`, `check` of de
Pages-build. Die keten maakt en controleert catalogus-siblings
(`.mvsa.pdf`, `.mvsa.svg`, `.vsa.svg`, en de rest). De blad-PDF maak je
lokaal, nadat die siblings vers zijn, en commit je mee. `check` meldt
niet of de blad-PDF ontbreekt. MuseScore 4 is nodig zodra de pagina
`pdf-bijelkaar` bevat.

Beide knoppen gebruiken die PDF (opslaan respectievelijk afdrukken). Bij
**Download pagina** stelt de site een bestandsnaam voor: frontmatter
`pdf_bestandsnaam`, anders `title`, anders de mapnaam — zie
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
koormap-`index.pagina.pdf` mag **niet** gebouwd worden door catalogus-PDF’s
te plakken (metadata-dubbeling). Richting: blad-SVG’s + Markdown-layout.
Later: tall scherm-SVG of Score-IR. Plan in VSA-tooling:
[kale-muziek-svg-en-uitgaven](https://github.com/orthodox-ronl/VSA-tooling/blob/main/docs/plans/kale-muziek-svg-en-uitgaven.md).

**Huidige implementatie:** altijd kale blad-SVG’s + koppen uit de Markdown
op A4 (`index.pagina.pdf`). Bron: `.mvsa` / `.vsa` / `.mscz` in de
catalogusmap — **geen** plakken van catalogus-product-PDF’s. Binnen
`pdf-bijelkaar`: opnieuw exporteren met `mvsa svg --compact`. Meerdere
MuseScore-pagina’s worden als bladreeks (`stem-1.svg`, …) onder elkaar
gezet. Vereist MuseScore 4 (bij `.mvsa`/`.mscz`) en `pymupdf`.

# OPTIONS

| Optie | Betekenis |
| --- | --- |
| `--all-koormappen` | Suiker: zelfde als pad `content-source\koormappen` |
| `--force` | Opnieuw schrijven, ook als de PDF nieuwer lijkt dan de bronnen |
| `-y`, `--yes` | Batch zonder bevestigingsvraag |

# EXAMPLES

Vredeslitanie (NL + KSL in `pdf-bijelkaar`):

```cmd
scripts\pagina-pdf.cmd content-source\koormappen\hemelum\liturgie-zondag\vredeslitanie\index.md
```

Hele zondagsliturgie-map:

```cmd
scripts\pagina-pdf.cmd content-source\koormappen\hemelum\liturgie-zondag
```

# WHEN

Je hebt de shortcodes op een slot-pagina gezet of gewijzigd en wilt de
knoppen Download/Print pagina een actuele pagina-PDF geven.

# SEE ALSO

- [Koormap-blad schrijven](/handleiding/start/koormap-blad/) — spiekbriefje voor shortcodes
- [Catalogus en koormappen](/handleiding/start/catalogus-en-koormappen/)
- Spec: `docs\specs\koormap-paginataal.md` in de repository
