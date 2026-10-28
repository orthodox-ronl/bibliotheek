# Publicatiecontrole (bibliotheek)

Normatief consumer-beleid voor deze repo. Leesbare vorm voor beheerders:
[handleiding — Publicatiecontrole](../content-source/handleiding/start/publicatiecontrole.md)
(op de site na build/preview).

Tooling-conventie (naamgeving conversies):
[VSA-tooling — bestandsnaamgeving](https://orthodox-ronl.github.io/VSA-tooling/formats/canonical-checklists/#bestandsnaamgeving-conventie).

Ownership: sibling-namen, publicatie-/importcontroles en Hugo-CI horen
**hier**; geldigheid/conversie/layoutprofielen in
[VSA-tooling](https://github.com/orthodox-ronl/VSA-tooling). Zie
[tooling-koppeling.md](tooling-koppeling.md).

## Terminologie

| Term                | Betekenis                                                              |
| ------------------- | ---------------------------------------------------------------------- |
| Versheidscontrole   | Sibling bestaat + herkomststempel past bij bron; meet/meldt alleen     |
| Publicatiecontrole  | Versheidscontrole op site-producten                                    |
| Importcontrole      | Versheidscontrole op bewerk-/importvorm                                |
| Contractcontrole    | Bestaande Coria-`.mxl` voldoet aan playback-checklist (`mxl validate`) |
| Geldigheidscontrole | `vsa validate` / `mvsa validate` / …                                   |
| Strengheid          | warn vs `--strict` / CI fail                                           |

## Naamgeving (doel)

| Rol       | Patroon                                                                                                    |
| --------- | ---------------------------------------------------------------------------------------------------------- |
| Bron      | `{stam}.{ext}` met één echte extensie: `.vsa` / `.mscz` / `.mvsa`                                          |
| Afgeleide | `{stam}.{bron-ext}.{doel-ext}` — bijv. `.vsa.mxl`, `.vsa.pdf`, `.mscz.pdf`, `.mscz.mxl`, `.vsa.lyrics.txt`, `.mscz.lyrics.txt` |
| Tekstblad | uitzondering: `{stam}.tekstblad.md` → `{stam}.tekstblad.pdf`                                               |

**Geen product-van-product:** uit één bron komt hoogstens één laag
afgeleiden (`….mvsa.mp3`, `….mscz.mxl`, optioneel `….mvsa.mscz`). Niet
`….mvsa.mscz.mp3`, `….mscz.mscz…`, of Score-IR/from-ir op `.mscz`/`.vsa`
(die horen alleen bij canonieke `.mvsa`). Bulk-`products` slaat afgeleide
`*.vsa.mscz` / `*.mvsa.mscz` over; een expliciet CLI-bestandspad mag wél.
Rommel opruimen: [`scripts/cleanup-chained-products.cmd`](../scripts/cleanup-chained-products.cmd).

Geen nieuwe `.print.mscz`: handmatige MuseScore-bladen = `{stam}.mscz` +
`manueel: true` op `index.md`.

## Publicatiecontroles

| Spoor                 | Bron                                             | Sibling                                             | Status in deze repo                                                                  |
| --------------------- | ------------------------------------------------ | --------------------------------------------------- | ------------------------------------------------------------------------------------ |
| VSA                   | `.vsa`                                           | `.vsa.mxl` + `.vsa.svg` + `vsa-source-sha256` (geen verplichte `.vsa.pdf`) | **Actief** (`products --kinds vsa` / `check_vsa_products`)                                   |
| Lyrics (zoektekst)    | `.vsa` / `.mvsa` / `.mscz`                       | `.vsa.lyrics.txt` / `.mvsa.lyrics.txt` / `.mscz.lyrics.txt` + source-sha | **Actief** (`products --kinds lyrics` / `check_lyrics_products`)                             |
| Partituur (mscz)      | `.mscz`                                          | `.mscz.mxl` + `.mscz.svg` (scherm) + partituur-sha (geen verplichte `.mscz.pdf`) | **Actief** (`products --kinds mscz` / `check_mscz_products`)                                 |
| Tekstblad             | `.tekstblad.md`                                  | geen verplichte product-PDF; blad = `index.md.pdf` uit de `.md` | **Actief** (`check_tekstblad_products` = bron aanwezig; `pdf.cmd`)                |
| Import (bewerkvorm)   | `.mscz`                                          | `.mscz.mvsa` + partituur-sha (optioneel)            | **Actief** (`import-mvsa` / `check_import_mvsa`; alleen bestaande paren)             |
| mvsa (canonieke bron) | `.mvsa`                                          | `.mvsa.mxl` + `.score-ir.json` + `.from-ir.musicxml` + source-sha; `.mvsa.svg` optioneel als from-ir er is (geen verplichte `.mvsa.pdf`) | **Actief** (`products --kinds mvsa` / `check_mvsa_products`)                                 |
| Score-IR scherm (OSMD) | `.mvsa`                                        | `.mvsa.score-ir.json` + `.mvsa.from-ir.musicxml` | **Actief** (`products --kinds mvsa` / `check`). Scherm: OSMD. `.mvsa.svg` alleen scherm-fallback; check eist die SVG niet als from-ir geldig is. |
| Audio (preview)       | `.mvsa` / `.mscz` / `.vsa`                       | `.mvsa.mp3` / `.mscz.mp3` / `.vsa.mp3` + stamp      | **Actief** (`products --kinds audio` / `check_audio_products`; zelfde bronnen als Coria-MXL) |
| Coria-contract        | bestaande `.vsa.mxl` / `.mscz.mxl` / `.mvsa.mxl` | `mxl validate` (mono / satb)                        | **Actief** (`check_mxl_playback_contract`)                                           |
| VSA-SVG (legacy pad)  | `.vsa`                                           | `static/vsa/bladermap/….svg`                        | **Legacy**; scherm gebruikt sibling `.vsa.svg` (zie VSA hierboven). Optioneel nog `oefenhoek-index --svg` |

CI genereert geen MuseScore-/PDF-/audio-producten en geen sibling-SVG
(`.vsa.svg` / `.mvsa.svg`). Wel, vóór Hugo, een legacy bladermap-plaatje
uit `.vsa` (`oefenhoek-index --svg`) voor het geval de sibling-SVG nog
ontbreekt. Het scherm gebruikt de sibling. Koormap-blad
`index.md.pdf` hoort niet bij `products.cmd`: lokaal
`scripts/pdf.cmd`, daarna committen. Wel in `check`
(`check_index_md_pdf.py`): ontbrekend of ouder dan Markdown/notatiebron
is een waarschuwing lokaal, een fout met `--strict` / in CI / op `main`.
Importcontrole eist **geen** `.mscz.mvsa` bij elke partituur —
alleen dat bestaande siblings vers zijn. Audio eist wél een `.mp3` bij elke
canonieke `.mvsa` / basis-`.mscz` / `.vsa` (buiten handmatige mappen).
Contractcontrole faalt als een bestaande Coria-`.mxl` de checklist niet haalt;
fix lokaal met `scripts\products.cmd --kinds mscz,mvsa,vsa --only-invalid`.

Oude bestandsnaam: `docs/productgates.md` (stub blijft als doorverwijzing).

## Genereren (`products.cmd`)

Lokaal (niet in CI): [`scripts/products.cmd`](../scripts/products.cmd) —
wrapper over alle product-sporen (vsa, mscz, tekstblad, mvsa, import, audio,
lyrics). Default-condities: **missing ∪ stale ∪ invalid** (`mxl validate` op
Coria-siblings). Ontbreekt het brontype voor een spoor, dan skip (geen fout).
Map-scan gebruikt alleen canonieke bronnen (geen `*.mvsa.mscz` als
basis-`.mscz`). `--kinds` is focus/uitsluiting, geen “vertel welke bronnen
bestaan”. Opties:
`--dry-run`, `--force`, `--only-missing` / `--only-stale` / `--only-invalid`,
`--reasons`. Na een geslaagde run (niet `--dry-run`) vernieuwt `products.cmd`
ook de Coria-fingerprints (`fingerprint_coria_mxl.py`) voor **Oefenen** (tip-icoon **♪**).

### Architectuur (orthogonaal)

Alle sporen delen één schil in [`scripts/product_kind.py`](../scripts/product_kind.py)
(`run_kind`: collect → `need_regen` → MuseScore-gate → sync). Per kind blijft
alleen bron-selectie en generatie in `sync_*_products` / `sync_import_mvsa`.
Gebruikerscommando: alleen [`scripts/products.cmd`](../scripts/products.cmd)
(`--kinds …`); geen aparte `*-products.cmd`. Na vsa/mvsa/mscz ook
`{bron}.products-meta.json` (snelle versheid; stamp-fallback zonder meta).
`check_*` blijft apart (status-JSON) maar hergebruikt `collect` en productpaden.

Leesbare HOW: [handleiding — Publicatiecontrole](../content-source/handleiding/start/publicatiecontrole.md#producten-opnieuw-genereren--productscmd).
