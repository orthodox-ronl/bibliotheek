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

**Bestand of map:** commando’s die op bronbestanden werken, nemen meestal
óf één bestand óf een map (recursief passende bestanden). Zie
[Invoer: bestand of map](invoer-bestand-of-map/).

## Nu beschikbaar in deze repo

| Commando | Wat het doet | Man-page |
| --- | --- | --- |
| *(conventie)* | Pad = één bronbestand of een map (recursief). | [Bestand of map](invoer-bestand-of-map/) |
| `h` | Overzicht van commando’s; `h <naam>` = `<naam> -h`. | [h](h/) |
| `validate` | Controleert catalogus-`.vsa` (en eventueel `.mvsa`) via de `vsa`-CLI. | [validate](validate/) |
| `check` | Preflight: validate + publicatiecontroles + Coria-fingerprints + Hugo-build. Maakt geen catalogusproducten en geen blad-PDF. | [check](check/) |
| `build` | Bouwt de site naar `generated\site`. | [build](build/) |
| `serve` | Lokale preview op http://127.0.0.1:18732/ (niet 1313, niet 18731). | [serve](serve/) |
| `products` | Catalogus-afgeleiden bouwen (`--kinds vsa,mvsa,mscz,audio,lyrics,…` of `all`). | [products](products/) |
| `products --kinds vsa` | `{stam}.vsa.mxl` + `{stam}.vsa.svg` bij catalogus-`.vsa`. | [products (vsa)](vsa-products/) |
| `products --kinds mscz` | `{stam}.mscz.mxl` + `{stam}.mscz.svg` bij basispartituur-`.mscz`. | [products (mscz)](mscz-products/) |
| `products --kinds tekstblad` | Tekstblad-kind (blad-PDF via [pdf](pdf/)). | [products (tekstblad)](tekstblad-products/) |
| `import-mvsa` | Maakt/vernieuwt bewerkvorm `{stam}.mscz.mvsa` naast een basispartituur-`.mscz` (alleen bestaande siblings, tenzij pad/`--create`). | [import-mvsa](import-mvsa/) |
| `products --kinds mvsa` | MXL, Score-IR, from-ir (+ optioneel SVG) bij catalogus-`.mvsa`. | [products (mvsa)](mvsa-products/) |
| `products --kinds audio` | Preview-`{stam}.{bron}.mp3` (Beluisteren). | [products (audio)](audio-products/) |
| `products --kinds lyrics` | `{stam}.….lyrics.txt` (zoektekst). | [products (lyrics)](lyrics-products/) |
| `all-products` | Alias voor `products --kinds all` (inclusief import-mvsa). | [all-products](all-products/) |
| `layout` | Past de basispartituur-standaard toe op `.mscz` of `.mxl` (tooling-layoutprofiel `partituur`). | [layout](layout/) |
| `ensure-bibliotheek-id` | Zet of controleert de colofonregel `Bibliotheek-id:` op basispartituur-`.mscz`. | [ensure-bibliotheek-id](ensure-bibliotheek-id/) |
| `bump-vsa-tooling-pin` | Zet `vsa-tooling.pin` op de tip van VSA-tooling (productie-pin); commit/PR zelf. | [bump-vsa-tooling-pin](bump-vsa-tooling-pin/) |
| `opkuisen` | Herkomstanalyse + inhoudelijke opkuis (Capella/MusicXML/MuseScore); optioneel `--layout`. | [opkuisen](opkuisen/) |
| `bieb accepteer` (`accept`) | Partituur/tekstblad opnemen onder een catalogus-id (Werkbank → Catalogus). | [bieb accepteer](bieb-accepteer/) |
| `bieb hernoem` (`rename`) | Catalogus-id hernoemen (zangstuk/variant/uitvoeringsvorm; map, stam, refs, koormap-slots). Id-vormen: slash, dash, pad, unieke suffix. | [bieb hernoem](bieb-hernoem/) |
| `bieb verwijder` (`delete`) | Catalogus-id wissen; dangling refs en koormap-slots rapporteren. | [bieb verwijder](bieb-verwijder/) |
| `bieb kopieer` (`copy`) | Uitvoeringsvorm kopiëren naar nieuw id (geen koormap-slot). | [bieb kopieer](bieb-kopieer/) |
| `update-werkvoorraad` | Tabel in `input\werkvoorraad.md` laten aansluiten op bestanden in `input\`. | [update-werkvoorraad](update-werkvoorraad/) |
| `werkbank-status` | Overzicht open werkbank-cases; schrijft `data\werkbank-status.json`. | [werkbank-status](werkbank-status/) |
| `lifecycle-grenzen` | Spaties/ruwe formats in catalogusmappen melden (optioneel `--fail`). | [lifecycle-grenzen](lifecycle-grenzen/) |
| `oefenhoek-index` | Legacy SVG uit `.vsa` naar `static\vsa\bladermap\` (geen stamp). Het scherm gebruikt `{stam}.vsa.svg` zodra `products --kinds vsa` die heeft gemaakt. | [oefenhoek-index](oefenhoek-index/) |
| `pdf.cmd` | Maakt `index.md.pdf` voor Download/Print pagina uit kale blad-SVG’s + Markdown-koppen (`pdf-bijelkaar` → compact). | [pdf](pdf/) |

Intern (geen apart gebruikerscommando): `python scripts\fingerprint_coria_mxl.py`
maakt `/mxl/c/<hash>.musicxml` en `data/coria-fp.json` voor **Oefenen** (♪).
Wordt al door `check` / `build` / `serve` aangeroepen.
`check_koormap_slot_links.py` controleert relatieve links in koormappen
(onderdeel van `check` / CI). `check_vsa_products.py`,
`check_mscz_products.py`, `check_tekstblad_products.py`,
`check_import_mvsa.py`, `check_mvsa_products.py`,
`check_audio_products.py` en `check_lyrics_products.py` schrijven
status-JSON (versheid / importcontrole).

Detail: [scripts/README.md](https://github.com/orthodox-ronl/bibliotheek/blob/development/scripts/README.md)
in de repo.

## Nog niet in deze repo

| Commando (later) | Rol |
| --- | --- |
| `bieb zoek` | Zoeken van catalogus-ids op de commandoregel |

Een los Markdownblad naar PDF (`pdf` / `demo-pdf`), Capella-batch
(`capella-mxl-to-mscz`) en een zondag-sync uit `bron` zijn geen
commando’s van deze repository. Een koormap-blad is
[pdf](pdf/). Een catalogus-tekstblad is
[products (tekstblad)](tekstblad-products/). Een generieke `vsa pdf` hoort
in VSA-tooling.

{{< navbuttons "Werktrajecten|/handleiding/werktrajecten/" "Check|/handleiding/scripts/check/" >}}
