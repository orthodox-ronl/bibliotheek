---
title: "VSA → SVG en Coria"
linkTitle: "VSA"
weight: 30
---

# VSA → SVG en Coria

Dit werktraject maakt uit een canonieke **`.vsa`** in de catalogus
een SVG-plaatje op de site en een Coria-bestand `{stam}.vsa.mxl`.
Representatie-id: `vsa`.

{{< cue >}}
Na een werkende `{stam}.vsa` in de bladermap:
```cmd
scripts\vsa-products.cmd content-source\catalogus\<zangstuk>\<variant>\<uitvoeringsvorm>
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
| `static\vsa\bladermap\…\*.svg` | Plaatje voor de site als er (nog) geen PDF is; **geen** publicatiecontrole (vernieuwd door `oefenhoek-index --svg`) |
| `{stam}.vsa.mxl` naast de `.vsa` | Coria; stamp `vsa-source-sha256` van de canonieke `.vsa` |
| `{stam}.vsa.pdf` naast de `.vsa` | A4 voor **Downloaden** / **Printen**; zelfde stamp |

**Klaar** als: `vsa validate` stil is; SVG of PDF zichtbaar via shortcode `bieb`;
`check_vsa_products` (onder `check --strict`) is groen voor MXL én PDF.

**Waarom geen lettergreepstreepjes in de canonieke `.vsa`?** Orthografische
`-` (Pyphen) helpt Coria én preview-audio (één kwartnoot per lettergreep),
maar hoort niet op het gepubliceerde SVG. `vsa-products` en `audio-products`
syllabify’t alleen in een **tijdelijk** bestand tijdens export en schrijft
die tekst niet terug naar `{stam}.vsa`. Een experimentele sidecar
`{stam}.syl.vsa` is **geen** bron voor SVG, `vsa-products` of
`audio-products`.

## Wanneer wel / wanneer niet

| Wel | Niet |
| --- | --- |
| Eenstemmige tekst op bekende melodie | Vierstemmig blad → [Basispartituur](../basispartituur/) |
| catalogus-uitvoeringsvorm met `.vsa` | VSA alleen op een demo-/handleidingpagina → [Ingebedde VSA](../ingebedde-vsa/) |
| | Printvel met handmatige PDF → [Print-vel](../print-vel/) |
| | Map met `artefacten_handmatig: true` (pipeline slaat auto-producten over) |

## Volgorde (bestanden)

1. Schrijf of herstel `{stam}.vsa`. HOW:
   [.vsa schrijven](../../vsa/1-vsa-schrijven/).
2. Neem op in de catalogus indien nodig:
   [Opnemen](../opnemen-in-catalogus/) (`bieb accepteer`).
3. Coria-`.vsa.mxl` en A4-`.vsa.pdf`:

```cmd
scripts\vsa-products.cmd content-source\catalogus\eniggeboren-zoon
```

4. Controleer: `check --strict` (validate + publicatiecontrole + Hugo).
5. Site bekijken: `serve` → http://127.0.0.1:18732/

Bibliotheek-**Oefenen** gebruikt `{stam}.vsa.mxl`; **Downloaden** /
**Printen** gebruiken `{stam}.vsa.pdf`.

## Automatisch (CI)

- **Wel:** `check_vsa_products.py` controleert of `{stam}.vsa.mxl` en
  `{stam}.vsa.pdf` bij de canonieke `.vsa` passen (sha-stamp). Pages-CI
  faalt bij missing/stale.
- **Wel:** `oefenhoek-index --svg` vernieuwt bladermap-SVG vóór Hugo
  (geen stamp; geen “stale SVG”-fout; op de pagina zie je de PDF als die
  er is, anders de SVG).
- **Niet:** stilzwijgend verouderde producten herschrijven zonder commit.
  Vernieuw lokaal met `vsa-products` en commit `.vsa.mxl` + `.vsa.pdf`
  mee. CI heeft geen MuseScore/Chrome-PDF-run voor producten.

## Handmatig

| Situatie | Commando | Man-page |
| --- | --- | --- |
| Coria-`.vsa.mxl` + A4-`.vsa.pdf` | `scripts\vsa-products.cmd` `[map]` | [vsa-products](../../scripts/vsa-products/) |
| Alles vóór commit | `scripts\check.cmd --strict` | [check](../../scripts/check/) |

## Zie ook

- Optioneel tropaar toon 4: [Template SATB](../../vsa/2-template-satb/)
- [validate](../../scripts/validate/) · [check](../../scripts/check/)

{{< navbuttons "Basispartituur|/handleiding/werktrajecten/basispartituur/" "Print-vel|/handleiding/werktrajecten/print-vel/" >}}
