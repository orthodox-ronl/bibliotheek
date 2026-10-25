---
title: "VSA → SVG en Coria"
linkTitle: "VSA"
weight: 30
---

# VSA → SVG en Coria

Dit werktraject maakt uit een canonieke **`.vsa`** in de catalogus
drie siblings: een scherm-SVG, een A4-PDF en een Coria-bestand
`{stam}.vsa.mxl`. Representatie-id: `vsa`.

{{< cue >}}
Na een werkende `{stam}.vsa` in de bladermap:
```cmd
scripts\products.cmd --kinds vsa content-source\catalogus\<zangstuk>\<variant>\<uitvoeringsvorm>
check --strict
```
{{< /cue >}}
## Waartoe

Eenstemmige notatie (antifoon, communievers, tropaar-regels, …) moet op
de cataloguspagina als plaatje verschijnen en via **Oefenen** in Coria
afspeelbaar zijn — zonder een volledige MuseScore-basispartituur.

## Eindresultaat en criteria

| Output | Rol |
| --- | --- |
| `{stam}.vsa` in de bladermap | Canonieke bron (YAML: `do`, `mode`, `tempo`) |
| `{stam}.vsa.svg` naast de `.vsa` | Alleen notatie op het scherm; stamp `vsa-source-sha256` |
| `{stam}.vsa.mxl` naast de `.vsa` | Coria; dezelfde stamp |
| `{stam}.vsa.pdf` naast de `.vsa` | A4 voor **Downloaden** / **Printen**; dezelfde stamp |
| `static\vsa\bladermap\…\*.svg` | Legacy fallback, alleen zolang `{stam}.vsa.svg` ontbreekt (`oefenhoek-index --svg`; geen stamp) |

**Klaar** als: `vsa validate` stil is; de sibling-SVG zichtbaar is via shortcode `bieb`;
`check_vsa_products` (onder `check --strict`) is groen voor MXL, PDF én SVG.

**Waarom geen lettergreepstreepjes in de canonieke `.vsa`?** Orthografische
`-` (Pyphen) helpt Coria én preview-audio (één kwartnoot per lettergreep),
maar hoort niet op het gepubliceerde SVG. `products --kinds vsa` roept
tooling `vsa products` aan (tijdelijke syllabify + Coria-MXL + SVG); audio
syllabify’t apart tijdelijk. Die tekst wordt niet teruggeschreven naar
`{stam}.vsa`. Een experimentele sidecar `{stam}.syl.vsa` is **geen** bron
voor SVG, `products --kinds vsa` of `products --kinds audio`.

## Wanneer wel / wanneer niet

| Wel | Niet |
| --- | --- |
| Eenstemmige tekst op bekende melodie | Vierstemmig blad → [Basispartituur](../basispartituur/) |
| catalogus-uitvoeringsvorm met `.vsa` | VSA alleen op een demo-/handleidingpagina → [Ingebedde VSA](../ingebedde-vsa/) |
| | Printvel met handmatige PDF → [Print-vel](../print-vel/) |
| | Map met `manueel: true` (pipeline slaat auto-producten over) |

## Volgorde (bestanden)

1. Schrijf of herstel `{stam}.vsa`. HOW:
   [.vsa schrijven](../../vsa/1-vsa-schrijven/).
2. Neem op in de catalogus indien nodig:
   [Opnemen](../opnemen-in-catalogus/) (`bieb accepteer`).
3. Coria-`.vsa.mxl`, A4-`.vsa.pdf` en scherm-`.vsa.svg`:

```cmd
scripts\products.cmd --kinds vsa content-source\catalogus\eniggeboren-zoon
```

4. Controleer: `check --strict` (validate + publicatiecontrole + Hugo).
5. Site bekijken: `serve` → http://127.0.0.1:18732/

Bibliotheek-**Oefenen** gebruikt `{stam}.vsa.mxl`. Het scherm toont
`{stam}.vsa.svg`. **Downloaden** en **Printen** gebruiken `{stam}.vsa.pdf`.

## Automatisch (CI)

- **Wel:** `check_vsa_products.py` controleert of `{stam}.vsa.mxl`,
  `{stam}.vsa.pdf` en `{stam}.vsa.svg` bij de canonieke `.vsa` passen
  (sha-stamp). Pages-CI faalt bij missing/stale.
- **Wel:** `oefenhoek-index --svg` vernieuwt het legacy-plaatje vóór
  Hugo (geen stamp). Dat plaatje telt alleen als de sibling-SVG er
  nog niet is.
- **Niet:** stilzwijgend verouderde producten herschrijven zonder commit.
  Vernieuw lokaal met `products --kinds vsa` en commit `.vsa.mxl`, `.vsa.pdf`
  en `.vsa.svg` mee. `check` maakt die bestanden niet.

## Handmatig

| Situatie | Commando | Man-page |
| --- | --- | --- |
| Coria-`.vsa.mxl` + A4-`.vsa.pdf` + `.vsa.svg` | `scripts\products.cmd --kinds vsa` `[map]` | [products (vsa)](../../scripts/vsa-products/) |
| Alles vóór commit | `scripts\check.cmd --strict` | [check](../../scripts/check/) |

## Zie ook

- Optioneel tropaar toon 4: [Template SATB](../../vsa/2-template-satb/)
- [validate](../../scripts/validate/) · [check](../../scripts/check/)

{{< navbuttons "Basispartituur|/handleiding/werktrajecten/basispartituur/" "Print-vel|/handleiding/werktrajecten/print-vel/" >}}
