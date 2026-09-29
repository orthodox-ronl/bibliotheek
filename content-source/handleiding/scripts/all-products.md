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
scripts\all-products.cmd [pad] [--force] [--dry-run]
```

# DESCRIPTION

Roept achter elkaar de product-scripts aan die siblings maken naast
bibliotheek-bronnen onder `content-source\bibliotheek` (of onder een
opgegeven pad). Mappen met `artefacten_handmatig: true` en bestanden in
`input\` worden door die scripts overgeslagen.

Volgorde:

1. [vsa-products](../vsa-products/) — `{stam}.vsa.mxl`
2. [mscz-products](../mscz-products/) — `{stam}.mscz.pdf` + `{stam}.mscz.mxl`
3. [tekstblad-products](../tekstblad-products/) — `{stam}.tekstblad.pdf`
4. [mvsa-products](../mvsa-products/) — `{stam}.mvsa.mxl` + `{stam}.mvsa.pdf`
5. [import-mvsa](../import-mvsa/) — alleen **bestaande** `{stam}.mscz.mvsa`
6. [audio-products](../audio-products/) — `{stam}.mvsa.mp3` / `.mscz.mp3` / `.vsa.mp3`

Elk spoor vernieuwt alleen wat ontbreekt of waarvan de herkomststempel
niet meer bij de bron past (tenzij `--force`).

**MuseScore 4** is nodig voor PDF en audio. Zonder MuseScore stoppen die
stappen met een foutmelding. CI draait dit script **niet**; jij wel
lokaal, daarna committen. Audio voor de hele bibliotheek kan tientallen
minuten duren.

Opties (`--force`, `--dry-run`, pad) gaan door naar elk onderliggend
script.

# EXAMPLES

```cmd
scripts\all-products.cmd
scripts\all-products.cmd content-source\bibliotheek\9-alleluia
scripts\all-products.cmd --dry-run
```

# WHEN

Na het toevoegen of wijzigen van bronnen, of als `check --strict` meerdere
productsporen tegelijk als missing/stale meldt. Voor één spoor: het
specifieke `*-products.cmd`.

# SEE ALSO

- [check](../check/)
- [audio-products](../audio-products/)
- [Publicatiecontrole](/handleiding/start/publicatiecontrole/)
