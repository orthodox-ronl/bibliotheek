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
4. Coria-fingerprints (`python scripts\fingerprint_coria_mxl.py`)
5. Hugo-build naar `generated\site`

Zonder `--strict` waarschuwen de publicatiecontroles lokaal maar falen
niet (behalve op `main` of met `BIBLIOTHEEK_PRODUCTS_STRICT=1`). Met
`--strict`, en altijd in CI, is een stale of missing product een fout.
Vernieuw dan lokaal met [vsa-products](../vsa-products/) of
[mscz-products](../mscz-products/) en commit de siblings mee. CI genereert
geen MuseScore-/MusicXML-producten.

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
- [serve](../serve/)
- [build](../build/)
- [Wat heb je nodig](/handleiding/start/wat-heb-je-nodig/)
- [Status en check](/handleiding/publiceren/2-status-en-check/)
- [Publicatiecontrole](/handleiding/start/publicatiecontrole/)
