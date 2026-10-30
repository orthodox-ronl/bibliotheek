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

1. `validate` — `vsa validate` op `content-source\catalogus` (en
   `mvsa validate` als daar `.mvsa`-bestanden staan)
2. VSA-publicatiecontrole — of elke catalogus-`.vsa` (behalve
   `manueel` / `manual`) passende siblings `{stam}.vsa.mxl`,
   `{stam}.vsa.pdf` en `{stam}.vsa.svg` heeft met `vsa-source-sha256`
3. MSCZ-publicatiecontrole — of elke basispartituur-`.mscz` (behalve
   handmatig/print) passende siblings `{stam}.mscz.pdf` en
   `{stam}.mscz.mxl` heeft met `vsa-partituur-sha256`
4. Tekstblad-publicatiecontrole — of elke `{stam}.tekstblad.md` een
   passende `{stam}.tekstblad.pdf` heeft met `vsa-source-sha256`
5. Importcontrole — of elke **bestaande** `{stam}.mscz.mvsa` bij de
   bijbehorende basispartituur-`.mscz` past (`vsa-partituur-sha256`);
   ontbrekende import-siblings zijn geen fout
6. MVSA-publicatiecontrole — of elke canonieke catalogus-`.mvsa`
   (geen `.mscz.mvsa`) passende siblings `{stam}.mvsa.mxl`,
   `{stam}.mvsa.pdf` en `{stam}.mvsa.svg` heeft met `vsa-source-sha256`
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
12. Coria-fingerprints (`python scripts\fingerprint_coria_mxl.py`)
13. Coria-fetch-probe (`python scripts\probe_coria_fetch.py`) — of Coria
    een steekproef (mscz/mvsa/vsa) vanaf **github.io** kan ophalen (geen
    `raw.githubusercontent.com`); zet `base` in
    `data\coria-public-base.json`. Zonder `--strict` alleen waarschuwen bij
    falen; met `--strict` exit 1
14. Legacy bladermap-SVG (`oefenhoek-index --svg`) — plaatje onder
   `static\vsa\bladermap\` uit `.vsa`, zonder stempel. Het scherm
   gebruikt sibling `{stam}.vsa.svg` (stap 2) zodra die er is; dit
   plaatje is alleen de fallback
15. Zoekindex (`python scripts\build_zoek_index.py` → `static\zoek\index.json`)
16. Bouwtijd-stempel (`python scripts\write_build_stamp.py` →
    `data\build.yaml`; footer «Gegenereerd» op de homepage; niet
    committen)
17. Hugo-build naar `generated\site` (footer «Bijgewerkt» via
    Git-geschiedenis van het contentbestand)

De Pages-deploy (productie, `/preview/`, branch-previews) bouwt de
zoekindex ook vóór Hugo, zodat zoeken niet afhangt van een verouderde
gecommitte `index.json`.

Zonder `--strict` waarschuwen de publicatie-, import- en id-controles
lokaal maar falen niet (behalve op `main` of met
`BIBLIOTHEEK_PRODUCTS_STRICT=1` / `BIBLIOTHEEK_ID_STRICT=1`). Met
`--strict`, en altijd in CI, is een stale of missing product, een
verouderde import-sibling, of een id-mismatch een fout. Vernieuw
producten lokaal met [all-products](../all-products/) (alles tegelijk)
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

`pdf.cmd` genereert CI niet. Het blad `index.md.pdf` maak je
lokaal (ná de catalogusproducten) en commit je mee. `check` controleert
of die PDF er is en niet ouder is dan de Markdown of notatiebron
(`check_index_md_pdf.py`). Ontbreekt of verouderd: waarschuwing lokaal;
fout met `--strict`, in CI, of op `main`. Zonder die PDF tonen
Download pagina en Print pagina niet.

Na de product-/pdf-/contract-checks schrijft `check` altijd
`data\check-fixlist.json`: elk auto-fixbaar probleem plus het
eenvoudigste herstelcommando. Afwerken: [fix](../fix/)
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
- [all-products](../all-products/)
- [oefenhoek-index](../oefenhoek-index/)
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
