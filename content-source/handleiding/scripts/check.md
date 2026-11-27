---
title: "check"
linkTitle: "check"
weight: 20
---

# NAME

`scripts\check.cmd` — controleren of de repository klaar is om te delen

# SYNOPSIS

```cmd
check
check --strict
```

Of: `scripts\check.cmd` vanuit de repo-root.

# DESCRIPTION

`check` is de preflight voor deze repo (CI-spiegel):

1. `validate` — `.vsa` → `vsa validate`, `.mvsa` → `mvsa validate`
   (map: beide waar nodig)
2. VSA-publicatiecontrole — of elke catalogus-`.vsa` (behalve
   `manueel` / `manual`) passende `{stam}.vsa.svg` heeft, en — als T1
   een formule kiest — ook `{stam}.vsa.mvsa` (geen `.vsa.mxl` meer)
3. MSCZ-publicatiecontrole — of elke basispartituur-`.mscz` (behalve
   handmatig/print) passende siblings `{stam}.mscz.pdf` en
   `{stam}.mscz.mxl` heeft met `vsa-partituur-sha256`
4. Tekstblad-publicatiecontrole — of elke `{stam}.tekstblad.md` een
   passende `{stam}.tekstblad.pdf` heeft met `vsa-source-sha256`
5. Importcontrole — of elke **bestaande** `{stam}.mscz.mvsa` bij de
   bijbehorende basispartituur-`.mscz` past (`vsa-partituur-sha256`);
   ontbrekende import-siblings zijn geen fout
6. MVSA-publicatiecontrole — of elke catalogus-`.mvsa` (inclusief
   afgeleide `.vsa.mvsa`, geen `.mscz.mvsa`) passende siblings
   (o.a. `{stam}.mvsa.mxl`, score-ir/from-ir; svg optioneel bij from-ir)
   heeft met herkomststempel / products-meta
7. Audio-publicatiecontrole — of elke canonieke `.mvsa` / basis-`.mscz` /
   `.vsa` een passende preview-`.mp3` heeft met herkomststempel
8. Lyrics-publicatiecontrole — of elke catalogus-`.vsa` / `.mvsa` /
   basis-`.mscz` een passende `{stam}.….lyrics.txt` heeft met
   `vsa-source-sha256`
9. Catalogus-id — of elke basispartituur-`.mscz` in het colofon de
   regel `Bibliotheek-id:` heeft die bij het bladermap-pad past
10. Koormap-slotlinks (`python scripts\check_koormap_slot_links.py
    --fail`) — of relatieve links in koormap-markdown (inhoudsopgaven)
    naar bestaande mappen of pagina’s wijzen; vangt 404’s na een half
    uitgevoerde `bieb hernoem`
11. Catalogus-leaf-titels (`check_catalogus_leaf_titles`) — of leaf-`title`
    niet alleen het zangstuk-id is en `linkTitle` een leesbaar
    uitvoeringsvorm-label is (waarschuwing; met `--strict` fout)
12. Gebreken-markering (`python scripts\check_gebreken.py`) — geen
    `publicatiestatus: productie` samen met *effectieve* `gebreken`
    (leaf/variant/zangstuk, met overerving); waarschuwing als SVG of
    `index.md.pdf` de stempel mist terwijl de markering aan staat (fout
    met `--strict`). Handleiding:
    [Status en check](../../publiceren/2-status-en-check/)
    Stempel- en watermerkproblemen komen ook in `data\check-fixlist.json`
    (via `python scripts\check_gebreken.py --write-status`, vóór de
    fixlist-stap) en worden door `fix` afgewerkt: SVG-stempels met
    `python scripts\gebreken.py <map>`, een PDF zonder watermerk met
    `scripts\pdf.cmd <map>\index.md --force`. De stempelstap staat in de
    afwerkvolgorde vóór de pdf.
13. Coria-fingerprints (`python scripts\fingerprint_coria_mxl.py`)
14. Coria-fetch-probe (`python scripts\probe_coria_fetch.py`) — of Coria
    een steekproef (mscz/mvsa/vsa) vanaf **github.io** kan ophalen (geen
    `raw.githubusercontent.com`); zet `base` in
    `data\coria-public-base.json`. Zonder `--strict` alleen waarschuwen bij
    falen; met `--strict` exit 1
15. Legacy bladermap-SVG (`python scripts\sync_oefenhoek_index.py --svg`) — plaatje onder
   `static\vsa\bladermap\` uit `.vsa`, zonder stempel. Het scherm
   gebruikt sibling `{stam}.vsa.svg` (stap 2) zodra die er is; dit
   plaatje is alleen de fallback
16. Zoekindex (`python scripts\build_zoek_index.py` → `static\zoek\index.json`)
17. Bouwtijd-stempel (`python scripts\write_build_stamp.py` →
    `data\build.yaml`; footer «Gegenereerd» op de homepage; niet
    committen)
18. Hugo-build naar `generated\site` (footer «Bijgewerkt» via
    Git-geschiedenis van het contentbestand)

De Pages-deploy (productie, `/preview/`, branch-previews) bouwt de
zoekindex ook vóór Hugo, zodat zoeken niet afhangt van een verouderde
gecommitte `index.json`.

Zonder `--strict` waarschuwen de publicatie-, import- en id-controles
lokaal maar falen niet (behalve op `main` of met
`BIBLIOTHEEK_PRODUCTS_STRICT=1` / `BIBLIOTHEEK_ID_STRICT=1`). Met
`--strict`, en altijd in CI, is een stale of missing product, een
verouderde import-sibling, of een id-mismatch een fout. Vernieuw
producten lokaal met [products](../products/) (alles tegelijk)
of met [products (vsa)](../vsa-products/),
[products (mscz)](../mscz-products/),
[products (tekstblad)](../tekstblad-products/),
[products (mvsa)](../mvsa-products/),
[products (audio)](../audio-products/) of
[products (lyrics)](../lyrics-products/); vernieuw
import-siblings met [import-mvsa](../import-mvsa/); herstel id’s met
[ensure-bibliotheek-id](../ensure-bibliotheek-id/) of
[layout](../layout/). CI genereert geen MuseScore-/PDF-/audio-/lyrics-producten en geen
sibling-SVG (`.vsa.svg` / `.mvsa.svg`); wel de zoekindex en de legacy
bladermap-SVG bij elke site-deploy.

`pdf.cmd` genereert CI niet. `check` controleert lokale `index.md.pdf`
versheid waar die bestaat (`check_index_md_pdf.py`). Ontbreekt of
verouderd: waarschuwing; fout met `--strict`. Op **main** mag geen
blad-PDF getrackt zijn (guard). Stabiele PDF’s: R2 +
[r2-pdf-opschonen](../r2-pdf-opschonen/).

Per productcontrole zie je eerst wat er getest wordt, dan tellingen
vooraan (`  3  stale-pdf`, `  1  meta  foute sha256`), de mappen die
niet kloppen, en één fix-sjabloon met `{file}`. Details en volledige
paden alleen met `--verbose` / `BIBLIOTHEEK_VERBOSE=1`.

Na die checks schrijft `check` altijd `data\check-fixlist.json`: elk
auto-fixbaar probleem plus herstelcommando. Met `--strict` betekent
een non-zero exit: *er zijn problemen gevonden* (inventarisatie), niet
dat `fix` al is mislukt. Afwerken: [fix](../fix/)
(`fix --check --dry-run` inventariseert opnieuw en toont de lijst;
`fix --check` werkt hem af).

# EXAMPLES

```cmd
cd /d C:\Git\orthodox-ronl\bibliotheek
check
check --strict
scripts\fix.cmd --check --dry-run
```

# WHEN

Vóór je commit of push. Tussendoor alleen markdown bekijken: `serve` is
genoeg (die runt fingerprints + Hugo-server, zonder validate/publicatiecontrole).

# SEE ALSO

- [fix](../fix/)
- [validate](../validate/)
- [products (vsa)](../vsa-products/)
- [products (mscz)](../mscz-products/)
- [products (tekstblad)](../tekstblad-products/)
- [import-mvsa](../import-mvsa/)
- [products (mvsa)](../mvsa-products/)
- [products (audio)](../audio-products/)
- [products](../products/)
- `python scripts\sync_oefenhoek_index.py`
- [pdf](../pdf/)
- [layout](../layout/)
- [ensure-bibliotheek-id](../ensure-bibliotheek-id/)
- [bieb hernoem](../bieb-hernoem/)
- [h](../h/)
- [serve](../serve/)
- [build](../build/)
- [Zangstuk hernoemen](/handleiding/werktrajecten/zangstuk-hernoemen/)
- [Wat heb je nodig](/handleiding/start/wat-heb-je-nodig/)
- [Status en check](/handleiding/publiceren/2-status-en-check/)
- [Publicatiecontrole](/handleiding/start/publicatiecontrole/)
