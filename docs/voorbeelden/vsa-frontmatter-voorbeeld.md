# Voorbeeld: frontmatter bij een uitvoeringsvorm

Proefschema. **Normatieve elementlijst:**
[docs/specs/vsa-frontmatter.md](../specs/vsa-frontmatter.md).

Uitgangspunt: frontmatter volgt uit gebruik; alleen **gedocumenteerde**
sleutels. Catalogus: eerst **migreren**, daarna **strippen**.

| Fase | Wat je ziet |
| ---- | ----------- |
| Werkbank | Volledig skelet; leeg = `null` |
| Catalogus | Alleen gevulde sleutels (gate stript de rest) |

| Laag | Bestand | Taak |
| ---- | ------- | ---- |
| Cataloguspagina | `index.md` | vinden, publicatiestatus |
| VSA/MVSA | `*.vsa` / `*.mvsa` | afspelen (plat), partituur (MuseScore-Engels), soort, toon, taal, bron, gelegenheid |
| Koormap-slot | koormap-`index.md` | lokale titel; `bieb id` |

---

## Werkbank-voorbeelden (openen)

1. [Tropaar Geboorte Moeder Gods](werkbank/voorbeeld-tropaar-geboorte-moeder-gods.vsa) —
   feesteigen (`gelegenheid`), `soort` + `toon`, `bron.uitgangspunt` + bewerking.
2. [Moeder Godslied Transfiguratie](werkbank/voorbeeld-moeder-godslied-transfiguratie.vsa) —
   `soorten`, `gelegenheden`, `bron.uitgangspunt` Liturgikon.

`bron.uitgangspunt` gaat bij product-export naar MusicXML `<source>` en
(via layout/`@bron`) naar MuseScore-meta `source`. Korte namen:
handleiding [Uitgave-bronnen](../../content-source/handleiding/start/uitgave-bronnen.md)
(`data/bronnen.yaml`).

Canonieke vorm bekijken (stript `null` en lege takken):

```cmd
scripts\frontmatter-canoniek.cmd docs\voorbeelden\werkbank\voorbeeld-tropaar-geboorte-moeder-gods.vsa
```

---

## Cataloguspagina (`index.md`) — zoeken & publiceren

```yaml
---
title: "Tropaar Geboorte Moeder Gods toon 4 (Meneon I — Den Haag)"
linkTitle: "Meneon I Den Haag"
publicatiestatus: reviewable
automatische_inhoud: false
---
```

Id zit in het pad, bijv. `tropaar/geboorte-mg-toon-4/meneon-i-den-haag`.

---

## Koormap-slot — lokale titel

```yaml
---
title: "Tropaar Geboorte MG (t.4)"
linkTitle: "Geboorte MG"
---

{{< bieb id="tropaar/geboorte-mg-toon-4/meneon-i-den-haag" >}}
```

---

## Gate (canonieke vorm)

- Spec + gedrag: [vsa-frontmatter.md — Canonieke-vorm-gate](../specs/vsa-frontmatter.md#canonieke-vorm-gate)
- Script: `scripts\frontmatter-canoniek.cmd` (`--check` / `--in-place`)
- Nog **niet** automatisch in `bieb accepteer`

De gate gooit overtollige frontmatter weg; de VSA-notatie blijft onaangeroerd.
