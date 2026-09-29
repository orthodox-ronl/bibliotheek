---
title: "audio-products"
linkTitle: "audio-products"
weight: 107
---

# NAME

`scripts\audio-products.cmd` — preview-`.mp3` maken bij een bibliotheek-bron

# SYNOPSIS

```cmd
scripts\audio-products.cmd [pad] [--force] [--dry-run]
```

# DESCRIPTION

Maakt naast een bibliotheek-bron een **afspeelbaar mp3-bestand** zodat
koorleden op de site op **Beluisteren** kunnen klikken. Per brontype een
eigen sibling:

| Bron | Audio-product |
| --- | --- |
| `{stam}.mvsa` | `{stam}.mvsa.mp3` |
| `{stam}.mscz` (basispartituur) | `{stam}.mscz.mp3` |
| `{stam}.vsa` | `{stam}.vsa.mp3` |

Het script schrijft een **herkomststempel** in het mp3-bestand (zelfde
velden als bij PDF/MXL: hash van de bron, wanneer gemaakt). Zo ziet
`check` later of de bron is gewijzigd terwijl het mp3 nog oud is.

Zoekt onder het opgegeven pad (of, zonder pad, onder
`content-source\bibliotheek`). Overgeslagen: `input\`, mappen met
`artefacten_handmatig: true`, import-siblings `*.mscz.mvsa`, en
`.print.mscz`.

Onder de motorkap: tooling-CLI `vsa audio` (MuseScore 4). CI genereert
**geen** audio; jij wel lokaal, daarna committen.

**Belangrijk:** elke bibliotheek-`.mvsa` / basis-`.mscz` / `.vsa` (buiten
handmatige mappen) hoort een passende `.mp3` te hebben — dezelfde scope
als de Coria-`.mxl`. Ontbreekt of veroudert die, dan faalt
`check --strict` / CI. Maak ze lokaal met dit script (of
[all-products](../all-products/)); CI genereert geen MuseScore-audio.

# OPTIONS

| Optie | Betekenis |
| --- | --- |
| `--force` | Bestaande mp3’s overschrijven |
| `--dry-run` | Alleen tonen wat er zou gebeuren |

# EXAMPLES

```cmd
scripts\audio-products.cmd content-source\bibliotheek\9-alleluia\9a-toon-1\groningen
scripts\audio-products.cmd content-source\bibliotheek\tropaar\maandag-toon-4\hemelum --force
```

# WHEN

Als je Beluisteren wilt tonen op een bladermap, of als `check --strict`
meldt dat een bestaand `.mp3` verouderd is.

# SEE ALSO

- [check](../check/)
- [Publicatiecontrole](/handleiding/start/publicatiecontrole/)
- Werktraject: [audio](/handleiding/werktrajecten/audio/)
