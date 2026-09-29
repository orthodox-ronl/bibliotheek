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

1. `validate` — `vsa validate` op `content-source\bibliotheek` (en
   `mvsa validate` als daar `.mvsa`-bestanden staan)
2. VSA-publicatiecontrole — of elke bibliotheek-`.vsa` (behalve
   `artefacten_handmatig`) een passende sibling `{stam}.vsa.mxl` heeft
   met `vsa-source-sha256`
3. MSCZ-publicatiecontrole — of elke basispartituur-`.mscz` (behalve
   handmatig/print) passende siblings `{stam}.mscz.pdf` en
   `{stam}.mscz.mxl` heeft met `vsa-partituur-sha256`
4. Tekstblad-publicatiecontrole — of elke `{stam}.tekstblad.md` een
   passende `{stam}.tekstblad.pdf` heeft met `vsa-source-sha256`
5. Importcontrole — of elke **bestaande** `{stam}.mscz.mvsa` bij de
   bijbehorende basispartituur-`.mscz` past (`vsa-partituur-sha256`);
   ontbrekende import-siblings zijn geen fout
6. MVSA-publicatiecontrole — of elke canonieke bibliotheek-`.mvsa`
   (geen `.mscz.mvsa`) passende siblings `{stam}.mvsa.mxl` en
   `{stam}.mvsa.pdf` heeft met `vsa-source-sha256`
7. Bibliotheek-id — of elke basispartituur-`.mscz` in het colofon de
   regel `Bibliotheek-id:` heeft die bij het bladermap-pad past
8. Coria-fingerprints (`python scripts\fingerprint_coria_mxl.py`)
9. Bladermap-SVG (`oefenhoek-index --svg`) — plaatjes uit `.vsa`; geen
   stamp-publicatiecontrole
10. Hugo-build naar `generated\site`

Zonder `--strict` waarschuwen de publicatie-, import- en id-controles
lokaal maar falen niet (behalve op `main` of met
`BIBLIOTHEEK_PRODUCTS_STRICT=1` / `BIBLIOTHEEK_ID_STRICT=1`). Met
`--strict`, en altijd in CI, is een stale of missing product, een
verouderde import-sibling, of een id-mismatch een fout. Vernieuw
producten lokaal met [vsa-products](../vsa-products/),
[mscz-products](../mscz-products/),
[tekstblad-products](../tekstblad-products/) of
[mvsa-products](../mvsa-products/); vernieuw
import-siblings met [import-mvsa](../import-mvsa/); herstel id’s met
[ensure-bibliotheek-id](../ensure-bibliotheek-id/) of
[layout](../layout/). CI genereert geen MuseScore-/PDF-producten.

# EXAMPLES

```cmd
cd /d C:\Git\orthodox-ronl\bibliotheek
check
check --strict
```

# WHEN

Vóór je commit of push. Tussendoor alleen markdown bekijken: `serve` is
genoeg (die runt fingerprints + Hugo-server, zonder validate/publicatiecontrole).

# SEE ALSO

- [validate](../validate/)
- [vsa-products](../vsa-products/)
- [mscz-products](../mscz-products/)
- [tekstblad-products](../tekstblad-products/)
- [import-mvsa](../import-mvsa/)
- [mvsa-products](../mvsa-products/)
- [oefenhoek-index](../oefenhoek-index/)
- [layout](../layout/)
- [ensure-bibliotheek-id](../ensure-bibliotheek-id/)
- [serve](../serve/)
- [build](../build/)
- [Wat heb je nodig](/handleiding/start/wat-heb-je-nodig/)
- [Status en check](/handleiding/publiceren/2-status-en-check/)
- [Publicatiecontrole](/handleiding/start/publicatiecontrole/)
