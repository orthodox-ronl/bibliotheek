---
title: "products — audio"
linkTitle: "products (audio)"
weight: 107
---

# NAME

`scripts\products.cmd --kinds audio` — preview-`.mp3` maken bij een bibliotheek-bron
(gewoon product-spoor; ook via `products` / `all-products`)

# SYNOPSIS

```cmd
scripts\products.cmd --kinds audio [pad] [--force] [--dry-run]
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
`products --kinds mvsa` / `vsa` / `mscz` zet die stempel ook als tooling
eerst een kaal mp3 schreef — anders zou `check` `unstamped_mp3` melden.

Zoekt onder het opgegeven pad (of, zonder pad, onder
`content-source\catalogus`). Overgeslagen: `input\`, mappen met
`manueel: true`, import-siblings `*.mscz.mvsa`, `.print.mscz`, en
afgeleide `*.vsa.mscz` / `*.mvsa.mscz` (die maken anders
`*.mvsa.mscz.mp3`). Zo’n afgeleide wél als bron: geef het bestand
expliciet als pad op de commandoregel.

Onder de motorkap: tooling-CLI `vsa audio` (MuseScore 4). Bij `.vsa`
syllabificeert het script eerst in een **tijdelijk** bestand (zelfde als
`products --kinds vsa` voor Coria), zodat Beluisteren dezelfde lettergreep-noten
heeft als Oefenen; de canonieke `.vsa` blijft ongewijzigd. CI genereert
**geen** audio; jij wel lokaal, daarna committen.

**Belangrijk:** elke catalogus-`.mvsa` / basis-`.mscz` / `.vsa` (buiten
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
scripts\products.cmd --kinds audio content-source\catalogus\alleluia\9a-toon-1\groningen
scripts\products.cmd --kinds audio content-source\catalogus\tropaar\maandag-toon-4\hemelum --force
```

# WHEN

Als je Beluisteren wilt tonen op een bladermap, of als `check --strict`
meldt dat een bestaand `.mp3` verouderd is.

# SEE ALSO

- [check](../check/)
- [Publicatiecontrole](/handleiding/start/publicatiecontrole/)
- Werktraject: [audio](/handleiding/werktrajecten/audio/)
