---
title: "Script-referentie"
linkTitle: "Scripts"
weight: 50
hide_page_list: true
---

# Script-referentie (man-pages)

Deze sectie beschrijft Windows-commando's (`.cmd`) in de repository-map
`bibliotheek`. Zet `.\scripts` op PATH, of roep `scripts\<naam>.cmd` aan
vanuit de repo-root.

## Nu beschikbaar in deze repo

| Commando | Wat het doet | Man-page |
| --- | --- | --- |
| `check` | Preflight: Coria-fingerprints + Hugo-build (CI-spiegel). | [check](check/) |
| `build` | Bouwt de site naar `generated\site`. | [build](build/) |
| `serve` | Lokale preview op http://127.0.0.1:18732/ (niet 1313, niet 18731). | [serve](serve/) |

Intern (geen apart gebruikerscommando): `python scripts\fingerprint_coria_mxl.py`
maakt `/mxl/c/<hash>.musicxml` en `data/coria-fp.json` voor de Oefenen-knop.
Wordt al door `check` / `build` / `serve` aangeroepen.

Detail: [scripts/README.md](https://github.com/orthodox-ronl/bibliotheek/blob/development/scripts/README.md)
in de repo.

## Nog niet in deze repo (komt later)

Product- en beheerpipelines die `vsa` of MuseScore-CLI nodig hebben, staan
**nog niet** als `.cmd` in `bibliotheek`. De HOW-pagina's hieronder
beschrijven het *bedoelde* werktraject; paden zijn al op deze repo
afgestemd. Tot de tooling aansluit: die stappen tijdelijk in
[VSA-demo](https://github.com/orthodox-ronl/VSA-demo) uitvoeren, of wachten.

| Commando (later) | Rol |
| --- | --- |
| `bieb-accepteer` | Partituur/tekstblad opnemen onder een bibliotheek-id |
| `opkuisen` / `layout` | Inhoudsfixes + basispartituur-normalisatie |
| `mscz-products` / `vsa-products` / `tekstblad-products` | PDF/Coria-afgeleiden |
| `ensure-bibliotheek-id` / `update-werkvoorraad` | Colofon-id / werkvoorraadtabel |
| `h` / `pdf` / ... | Console-hulp en overige VSA-demo-commando's |

Man-pages (ter voorbereiding):
[bieb-accepteer](bieb-accepteer/), [opkuisen](opkuisen/), [layout](layout/),
[mscz-products](mscz-products/), [vsa-products](vsa-products/),
[tekstblad-products](tekstblad-products/), [ensure-bibliotheek-id](ensure-bibliotheek-id/),
[update-werkvoorraad](update-werkvoorraad/), [oefenhoek-index](oefenhoek-index/),
[capella-mxl-to-mscz](capella-mxl-to-mscz/), [h](h/), [pdf](pdf/),
[demo-pdf](demo-pdf/), [sync-bron-zondagen](sync-bron-zondagen/).

{{< navbuttons "Werktrajecten|/handleiding/werktrajecten/" "Check|/handleiding/scripts/check/" >}}
