# Productgates (bibliotheek)

Normatief consumer-beleid voor deze repo. Leesbare vorm voor beheerders:
[handleiding — Productgates](../content-source/handleiding/start/productgates.md)
(op de site na build/preview).

Tooling-conventie (naamgeving conversies):
[VSA-tooling — bestandsnaamgeving](https://orthodox-ronl.github.io/VSA-tooling/formats/canonical-checklists/#bestandsnaamgeving-conventie).

Ownership: sibling-namen, freshness-gates en Hugo-CI horen **hier**;
geldigheid/conversie/layoutprofielen in
[VSA-tooling](https://github.com/orthodox-ronl/VSA-tooling). Zie
[tooling-koppeling.md](tooling-koppeling.md).

## Naamgeving (doel)

| Rol | Patroon |
| --- | --- |
| Bron | `{stam}.{ext}` met één echte extensie: `.vsa` / `.mscz` / `.mvsa` |
| Afgeleide | `{stam}.{bron-ext}.{doel-ext}` — bijv. `.vsa.mxl`, `.mscz.pdf`, `.mscz.mxl` |
| Tekstblad | uitzondering: `{stam}.tekstblad.md` → `{stam}.tekstblad.pdf` |

Geen nieuwe `.print.mscz`: handmatige MuseScore-bladen = `{stam}.mscz` +
`artefacten_handmatig: true` op `index.md`.

## Gates

| Gate | Bron | Sibling | Status in deze repo |
| ---- | ---- | ------- | ------------------- |
| VSA | `.vsa` | `.vsa.mxl` + `vsa-source-sha256` | **Actief** (`vsa-products` / `check_vsa_products`) |
| Partituur (mscz) | `.mscz` | `.mscz.pdf` + `.mscz.mxl` + partituur-sha | Voorzien |
| Tekstblad | `.tekstblad.md` | `.tekstblad.pdf` | Voorzien |
| mvsa | `.mvsa` | naar gelang traject | Voorzien |

CI genereert geen producten; alleen validate + actieve gates + Hugo.
