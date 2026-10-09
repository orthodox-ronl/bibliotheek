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
| `h` | Overzicht van commando’s; `h <naam>` = `<naam> -h`. | [h](h/) |
| `validate` | Controleert catalogus-`.vsa` (en eventueel `.mvsa`) via de `vsa`-CLI. | [validate](validate/) |
| `check` | Preflight: validate + VSA-/MSCZ-publicatiecontrole + Coria-fingerprints + Hugo-build. | [check](check/) |
| `build` | Bouwt de site naar `generated\site`. | [build](build/) |
| `serve` | Lokale preview op http://127.0.0.1:18732/ (niet 1313, niet 18731). | [serve](serve/) |
| `vsa-products` | Maakt/vernieuwt `{stam}.vsa.mxl` (Coria) + `{stam}.vsa.pdf` (A4) bij een catalogus-`.vsa`. | [vsa-products](vsa-products/) |
| `mscz-products` | Maakt/vernieuwt `{stam}.mscz.pdf` + `{stam}.mscz.mxl` bij een basispartituur-`.mscz`. | [mscz-products](mscz-products/) |
| `tekstblad-products` | Maakt/vernieuwt `{stam}.tekstblad.pdf` bij een catalogus-`.tekstblad.md`. | [tekstblad-products](tekstblad-products/) |
| `import-mvsa` | Maakt/vernieuwt bewerkvorm `{stam}.mscz.mvsa` naast een basispartituur-`.mscz` (alleen bestaande siblings, tenzij pad/`--create`). | [import-mvsa](import-mvsa/) |
| `mvsa-products` | Maakt/vernieuwt `{stam}.mvsa.mxl` + `{stam}.mvsa.pdf` bij een catalogus-`.mvsa`. | [mvsa-products](mvsa-products/) |
| `audio-products` | Maakt/vernieuwt preview-`{stam}.{bron}.mp3` bij `.mvsa` / `.mscz` / `.vsa` (Beluisteren). | [audio-products](audio-products/) |
| `lyrics-products` | Maakt/vernieuwt `{stam}.vsa.lyrics.txt` / `.mvsa.lyrics.txt` / `.mscz.lyrics.txt` (zoektekst). | [lyrics-products](lyrics-products/) |
| `all-products` | Roept alle `*-products` (+ import-mvsa) achter elkaar aan voor ontbrekende/stale siblings. | [all-products](all-products/) |
| `layout` | Past de basispartituur-standaard toe op `.mscz` of `.mxl` (tooling-layoutprofiel `partituur`). | [layout](layout/) |
| `ensure-bibliotheek-id` | Zet of controleert de colofonregel `Bibliotheek-id:` op basispartituur-`.mscz`. | [ensure-bibliotheek-id](ensure-bibliotheek-id/) |
| `bump-vsa-tooling-pin` | Zet `vsa-tooling.pin` op de tip van VSA-tooling (productie-pin); commit/PR zelf. | [bump-vsa-tooling-pin](bump-vsa-tooling-pin/) |
| `opkuisen` | Herkomstanalyse + inhoudelijke opkuis (Capella/MusicXML/MuseScore); optioneel `--layout`. | [opkuisen](opkuisen/) |
| `bieb accepteer` | Partituur/tekstblad opnemen onder een catalogus-id (Werkbank → Catalogus). | [bieb accepteer](bieb-accepteer/) |
| `bieb hernoem` | Zangstuk-id hernoemen (map, stam, refs, koormap-slots). | [bieb hernoem](bieb-hernoem/) |
| `update-werkvoorraad` | Tabel in `input\werkvoorraad.md` laten aansluiten op bestanden in `input\`. | [update-werkvoorraad](update-werkvoorraad/) |
| `werkbank-status` | Overzicht open werkbank-cases; schrijft `data\werkbank-status.json`. | [werkbank-status](werkbank-status/) |
| `lifecycle-grenzen` | Spaties/ruwe formats in catalogusmappen melden (optioneel `--fail`). | [lifecycle-grenzen](lifecycle-grenzen/) |
| `oefenhoek-index` | SVG-plaatjes uit catalogus-`.vsa` naar `static\vsa\bladermap\` (geen stamp); optioneel legacy-strip. | [oefenhoek-index](oefenhoek-index/) |

Intern (geen apart gebruikerscommando): `python scripts\fingerprint_coria_mxl.py`
maakt `/mxl/c/<hash>.musicxml` en `data/coria-fp.json` voor de Oefenen-knop.
Wordt al door `check` / `build` / `serve` aangeroepen.
`check_koormap_slot_links.py` controleert relatieve links in koormappen
(onderdeel van `check` / CI). `check_vsa_products.py`,
`check_mscz_products.py`, `check_tekstblad_products.py`,
`check_import_mvsa.py`, `check_mvsa_products.py`,
`check_audio_products.py` en `check_lyrics_products.py` schrijven
status-JSON (versheid / importcontrole).

Detail: [scripts/README.md](https://github.com/orthodox-ronl/bibliotheek/blob/development/scripts/README.md)
in de repo.

## Nog niet in deze repo (komt later)

| Commando (later) | Rol |
| --- | --- |
| `bieb zoek` | Zoeken van catalogus-ids op de commandoregel |

Man-pages (ter voorbereiding / andere repo):
[capella-mxl-to-mscz](capella-mxl-to-mscz/), [pdf](pdf/),
[demo-pdf](demo-pdf/), [sync-bron-zondagen](sync-bron-zondagen/).

{{< navbuttons "Werktrajecten|/handleiding/werktrajecten/" "Check|/handleiding/scripts/check/" >}}
