---
title: "all-products"
linkTitle: "all-products"
weight: 108
---

# NAME

`scripts\all-products.cmd` — alle ontbrekende of verouderde bibliotheek-producten
in één keer bijwerken

# SYNOPSIS

```cmd
scripts\all-products.cmd [pad] [--force] [--dry-run] [-y]
```

# DESCRIPTION

Roept achter elkaar **alle** product-sporen aan (zelfde als
`products.cmd --kinds all`) die siblings maken naast bibliotheek-bronnen
onder `content-source\catalogus` (of onder een opgegeven pad). Het pad is
één bronbestand of een map — zie
[Invoer: bestand of map](../invoer-bestand-of-map/). Bij een map of
meerdere kinds: preflight met bevestiging (of `-y`); per kind volgt een
eigen duur-schatting. Audio en lyrics horen daar gewoon bij; ze zijn geen
aparte uitzondering. Mappen met `artefacten_handmatig: true` en bestanden
in `input\` worden overgeslagen. Past het brontype niet bij een spoor, dan
skip (geen fout).

Volgorde:

1. [vsa-products](../vsa-products/) — `{stam}.vsa.mxl` + `{stam}.vsa.pdf` + `{stam}.vsa.svg`
2. [mscz-products](../mscz-products/) — `{stam}.mscz.pdf` + `{stam}.mscz.mxl`
3. [tekstblad-products](../tekstblad-products/) — `{stam}.tekstblad.pdf`
4. [mvsa-products](../mvsa-products/) — `{stam}.mvsa.mxl` + `{stam}.mvsa.pdf` + `{stam}.mvsa.svg` + Score-IR + from-ir MusicXML
5. [import-mvsa](../import-mvsa/) — alleen **bestaande** `{stam}.mscz.mvsa`
6. [audio-products](../audio-products/) — `{stam}.mvsa.mp3` / `.mscz.mp3` / `.vsa.mp3`
7. [lyrics-products](../lyrics-products/) — `{stam}.vsa.lyrics.txt` / `.mvsa.lyrics.txt` / `.mscz.lyrics.txt`

Daarna (tenzij `--dry-run`): Coria-fingerprints voor de Oefenen-knop
(`fingerprint_coria_mxl.py`, via `products.cmd`), en
`static\zoek\index.json` opnieuw bouwen zodat zoeken lyrics, status en
audio-paden volgt. Op GitHub Pages gebeurt die indexstap opnieuw in de
deploy (ook voor `/preview/` en branch-previews).

Elk spoor vernieuwt alleen wat ontbreekt of waarvan de herkomststempel
niet meer bij de bron past (tenzij `--force`).

Dit commando maakt **geen** koormap-blad. Het bestand `index.pagina.pdf`
(knoppen Download pagina en Print pagina) bouw je daarna met
[pagina-pdf](../pagina-pdf/), als de catalogus-PDF’s al vers zijn.
`pdf-bijelkaar` exporteert dan een tijdelijke compacte SVG; die
overschrijft `{stam}.mvsa.svg` niet.

**MuseScore 4** is nodig voor PDF en audio. Zonder MuseScore stoppen die
stappen met een foutmelding. CI draait dit script **niet**; jij wel
lokaal, daarna committen. Audio voor de hele bibliotheek kan tientallen
minuten duren.

Opties (`--force`, `--dry-run`, `-y`, pad) gaan door naar elk onderliggend
script.

# EXAMPLES

```cmd
scripts\all-products.cmd
scripts\all-products.cmd content-source\catalogus\alleluia
scripts\all-products.cmd --dry-run
```

# WHEN

Na het toevoegen of wijzigen van bronnen, of als `check --strict` meerdere
productsporen tegelijk als missing/stale meldt. Voor één spoor: het
specifieke `*-products.cmd`.

# SEE ALSO

- [check](../check/)
- [pagina-pdf](../pagina-pdf/)
- [audio-products](../audio-products/)
- [Publicatiecontrole](/handleiding/start/publicatiecontrole/)
