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

Geen nieuwe `.print.mscz`: handmatige MuseScore-bladen = `{stam}.mscz` +
`artefacten_handmatig: true` op `index.md`.

## Publicatiecontroles

| Spoor                 | Bron                                             | Sibling                                             | Status in deze repo                                                                  |
| --------------------- | ------------------------------------------------ | --------------------------------------------------- | ------------------------------------------------------------------------------------ |
| VSA                   | `.vsa`                                           | `.vsa.mxl` + `.vsa.pdf` + `vsa-source-sha256`       | **Actief** (`vsa-products` / `check_vsa_products`)                                   |
| Lyrics (zoektekst)    | `.vsa` / `.mvsa` / `.mscz`                       | `.vsa.lyrics.txt` / `.mvsa.lyrics.txt` / `.mscz.lyrics.txt` + source-sha | **Actief** (`lyrics-products` / `check_lyrics_products`)                             |
| Partituur (mscz)      | `.mscz`                                          | `.mscz.pdf` + `.mscz.mxl` + partituur-sha           | **Actief** (`mscz-products` / `check_mscz_products`)                                 |
| Tekstblad             | `.tekstblad.md`                                  | `.tekstblad.pdf`                                    | **Actief** (`tekstblad-products` / `check_tekstblad_products`)                       |
| Import (bewerkvorm)   | `.mscz`                                          | `.mscz.mvsa` + partituur-sha (optioneel)            | **Actief** (`import-mvsa` / `check_import_mvsa`; alleen bestaande paren)             |
| mvsa (canonieke bron) | `.mvsa`                                          | `.mvsa.mxl` + `.mvsa.pdf` + source-sha              | **Actief** (`mvsa-products` / `check_mvsa_products`)                                 |
| Audio (preview)       | `.mvsa` / `.mscz` / `.vsa`                       | `.mvsa.mp3` / `.mscz.mp3` / `.vsa.mp3` + stamp      | **Actief** (`audio-products` / `check_audio_products`; zelfde bronnen als Coria-MXL) |
| Coria-contract        | bestaande `.vsa.mxl` / `.mscz.mxl` / `.mvsa.mxl` | `mxl validate` (mono / satb)                        | **Actief** (`check_mxl_playback_contract`)                                           |
| VSA-SVG (plaatje)     | `.vsa`                                           | `static/vsa/bladermap/….svg`                        | **Geen** versheidscontrole; `oefenhoek-index --svg` in check/build/CI                |

CI genereert geen MuseScore-/PDF-/audio-producten; wel bladermap-SVG uit `.vsa`
vóór Hugo. Importcontrole eist **geen** `.mscz.mvsa` bij elke partituur —
alleen dat bestaande siblings vers zijn. Audio eist wél een `.mp3` bij elke
canonieke `.mvsa` / basis-`.mscz` / `.vsa` (buiten handmatige mappen).
Contractcontrole faalt als een bestaande Coria-`.mxl` de checklist niet haalt;
fix lokaal met `scripts\products.cmd --kinds mscz,mvsa,vsa --only-invalid`.

Oude bestandsnaam: `docs/productgates.md` (stub blijft als doorverwijzing).

## Genereren (`products.cmd`)

Lokaal (niet in CI): [`scripts/products.cmd`](../scripts/products.cmd) —
wrapper over alle `sync_*_products`. Default-condities: **missing ∪ stale ∪
invalid** (`mxl validate` op Coria-siblings). Opties: `--kinds`, `--dry-run`,
`--force`, `--only-missing` / `--only-stale` / `--only-invalid`, `--reasons`.

Leesbare HOW: [handleiding — Publicatiecontrole](../content-source/handleiding/start/publicatiecontrole.md#producten-opnieuw-genereren--productscmd).
