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
| `validate` | Controleert bibliotheek-`.vsa` (en eventueel `.mvsa`) via de `vsa`-CLI. | [validate](validate/) |
| `check` | Preflight: validate + VSA-/MSCZ-publicatiecontrole + Coria-fingerprints + Hugo-build. | [check](check/) |
| `build` | Bouwt de site naar `generated\site`. | [build](build/) |
| `serve` | Lokale preview op http://127.0.0.1:18732/ (niet 1313, niet 18731). | [serve](serve/) |
| `vsa-products` | Maakt/vernieuwt sibling `{stam}.vsa.mxl` (Coria) bij een bibliotheek-`.vsa`. | [vsa-products](vsa-products/) |
| `mscz-products` | Maakt/vernieuwt `{stam}.mscz.pdf` + `{stam}.mscz.mxl` bij een basispartituur-`.mscz`. | [mscz-products](mscz-products/) |
| `tekstblad-products` | Maakt/vernieuwt `{stam}.tekstblad.pdf` bij een bibliotheek-`.tekstblad.md`. | [tekstblad-products](tekstblad-products/) |
| `import-mvsa` | Maakt/vernieuwt bewerkvorm `{stam}.mscz.mvsa` naast een basispartituur-`.mscz` (alleen bestaande siblings, tenzij pad/`--create`). | [import-mvsa](import-mvsa/) |
| `layout` | Past de basispartituur-standaard toe op `.mscz` of `.mxl` (tooling-layoutprofiel `partituur`). | [layout](layout/) |
| `ensure-bibliotheek-id` | Zet of controleert de colofonregel `Bibliotheek-id:` op basispartituur-`.mscz`. | [ensure-bibliotheek-id](ensure-bibliotheek-id/) |
| `opkuisen` | Herkomstanalyse + inhoudelijke opkuis (Capella/MusicXML/MuseScore); optioneel `--layout`. | [opkuisen](opkuisen/) |
| `bieb accepteer` | Partituur/tekstblad opnemen onder een bibliotheek-id. | [bieb accepteer](bieb-accepteer/) |
| `update-werkvoorraad` | Tabel in `input\werkvoorraad.md` laten aansluiten op bestanden in `input\`. | [update-werkvoorraad](update-werkvoorraad/) |

Intern (geen apart gebruikerscommando): `python scripts\fingerprint_coria_mxl.py`
maakt `/mxl/c/<hash>.musicxml` en `data/coria-fp.json` voor de Oefenen-knop.
Wordt al door `check` / `build` / `serve` aangeroepen.
`check_vsa_products.py`, `check_mscz_products.py`,
`check_tekstblad_products.py` en `check_import_mvsa.py` schrijven
status-JSON (versheid / importcontrole).

Detail: [scripts/README.md](https://github.com/orthodox-ronl/bibliotheek/blob/development/scripts/README.md)
in de repo.

## Nog niet in deze repo (komt later)

| Commando (later) | Rol |
| --- | --- |
| `bieb zoek` / `bieb hernoem` | Zoeken / hernoemen van bibliotheek-ids |
| `h` / `pdf` / ... | Console-hulp en overige VSA-demo-commando's |

Man-pages (ter voorbereiding):
[oefenhoek-index](oefenhoek-index/),
[capella-mxl-to-mscz](capella-mxl-to-mscz/), [h](h/), [pdf](pdf/),
[demo-pdf](demo-pdf/), [sync-bron-zondagen](sync-bron-zondagen/).

{{< navbuttons "Werktrajecten|/handleiding/werktrajecten/" "Check|/handleiding/scripts/check/" >}}
