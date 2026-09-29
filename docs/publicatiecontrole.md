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

| Term | Betekenis |
| --- | --- |
| Versheidscontrole | Sibling bestaat + herkomststempel past bij bron; meet/meldt alleen |
| Publicatiecontrole | Versheidscontrole op site-producten |
| Importcontrole | Versheidscontrole op bewerk-/importvorm |
| Geldigheidscontrole | `vsa validate` / `mvsa validate` / … |
| Strengheid | warn vs `--strict` / CI fail |

## Naamgeving (doel)

| Rol | Patroon |
| --- | --- |
| Bron | `{stam}.{ext}` met één echte extensie: `.vsa` / `.mscz` / `.mvsa` |
| Afgeleide | `{stam}.{bron-ext}.{doel-ext}` — bijv. `.vsa.mxl`, `.mscz.pdf`, `.mscz.mxl` |
| Tekstblad | uitzondering: `{stam}.tekstblad.md` → `{stam}.tekstblad.pdf` |

Geen nieuwe `.print.mscz`: handmatige MuseScore-bladen = `{stam}.mscz` +
`artefacten_handmatig: true` op `index.md`.

## Publicatiecontroles

| Spoor | Bron | Sibling | Status in deze repo |
| ----- | ---- | ------- | ------------------- |
| VSA | `.vsa` | `.vsa.mxl` + `vsa-source-sha256` | **Actief** (`vsa-products` / `check_vsa_products`) |
| Partituur (mscz) | `.mscz` | `.mscz.pdf` + `.mscz.mxl` + partituur-sha | **Actief** (`mscz-products` / `check_mscz_products`) |
| Tekstblad | `.tekstblad.md` | `.tekstblad.pdf` | **Actief** (`tekstblad-products` / `check_tekstblad_products`) |
| Import (bewerkvorm) | `.mscz` | `.mscz.mvsa` + partituur-sha (optioneel) | **Actief** (`import-mvsa` / `check_import_mvsa`; alleen bestaande paren) |
| mvsa (canonieke bron) | `.mvsa` | `.mvsa.mxl` + `.mvsa.pdf` + source-sha | **Actief** (`mvsa-products` / `check_mvsa_products`) |
| Audio (preview) | `.mvsa` / `.mscz` / `.vsa` | `.mvsa.mp3` / `.mscz.mp3` / `.vsa.mp3` + stamp | **Actief, opt-in** (`audio-products` / `check_audio_products`; alleen bestaande siblings) |
| VSA-SVG (plaatje) | `.vsa` | `static/vsa/bladermap/….svg` | **Geen** versheidscontrole; `oefenhoek-index --svg` in check/build/CI |

CI genereert geen MuseScore-/PDF-/audio-producten; wel bladermap-SVG uit `.vsa`
vóór Hugo. Importcontrole eist **geen** `.mscz.mvsa` bij elke partituur —
alleen dat bestaande siblings vers zijn. Audio-controle eist **geen** mp3
bij elke bron — alleen dat bestaande `.mp3`-siblings vers zijn.

Oude bestandsnaam: `docs/productgates.md` (stub blijft als doorverwijzing).
