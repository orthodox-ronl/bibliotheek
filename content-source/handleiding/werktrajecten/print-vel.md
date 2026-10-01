---
title: "Print-vel"
linkTitle: "Print-vel"
weight: 40
---

# Print-vel (legacy-naam)

Dit werktraject houdt een **handmatig MuseScore-blad** en een **handmatige
PDF** bij buiten de basispartituur-keten.

**Doelvorm** (zie [Publicatiecontrole](/handleiding/start/publicatiecontrole/)): het
bestand heet `{stam}.mscz` (geen `.print.` in de naam) en de bladermap heeft
`artefacten_handmatig: true`. Afgeleide PDF: `{stam}.mscz.pdf`.

**Legacy:** bestandsnaam eindigend op `.print.mscz` blijft herkend tot
migratie.

{{< cue >}}
Zet op de catalogus-`index.md` `artefacten_handmatig: true`. Geen
`scripts\layout.cmd`, geen `mscz-products`. Exporteer de PDF zelf in
MuseScore 4. Nieuwe bladen: `{stam}.mscz` + `{stam}.mscz.pdf`. Oude bladen
mogen nog `*.print.mscz` heten.
{{< /cue >}}

## Waartoe

Soms heb je één A4-vel voor de koormap met layout of tekstregels die de
basispartituur-normalisatie zou vernielen, of een template-SATB-blad dat
jij zelf bijhoudt. Dat hoort **niet** door `layout` / `mscz-products` te
lopen.

## Eindresultaat en criteria

| Bestand (in de bladermap) | Rol |
| --- | --- |
| `{stam}.print.mscz` | MuseScore-bron; scripts laten dit met rust |
| `{stam}.print.pdf` of korte `{stam}.pdf` | Handmatige A4-export |
| Optioneel: Coria-`.mxl` / `.vsa` | Alleen als jij die zelf neerzet en bijhoudt |

**Klaar** als: `artefacten_handmatig: true` op de catalogus-`index.md`;
PDF staat naast het print-bestand; shortcode `bieb` toont de PDF; gele
beheerdersbanner op de cataloguspagina.

## Wanneer wel / wanneer niet

| Wel | Niet |
| --- | --- |
| Bewust buiten de basispartituur-spoor | Gewoon oefenmateriaal met automatische Coria → [Basispartituur](../basispartituur/) |
| Gecombineerd printvel, template-SATB | Eenstemmige notatie alleen → [VSA](../vsa/) |

Voorbeelden in de catalogus:
`kleine-intocht/zo-wk-mg/hemelum`,
`tropaar/nikolaas-van-myra-toon-4/hemelum`,
`moeder-godslied/ontslapen-moeder-gods/hemelum`.

## Volgorde (bestanden)

1. Maak of bewerk `{stam}.print.mscz` in MuseScore 4 (naam moet op
   `.print.mscz` eindigen).
2. Neem op via [Opnemen](../opnemen-in-catalogus/)
   (`bieb accepteer`), of leg het bestand handmatig in de bladermap.
3. Exporteer PDF in MuseScore (Bestand → Exporteren → PDF) naar dezelfde
   map.
4. Zet frontmatter op `index.md`:

```yaml
artefacten_handmatig: true
```

5. Eventueel koormap-slot met `bieb`. HOW:
   [Print-.mscz](../../partituur/7-print-mscz/).
6. [Site-build](../site-build/).

## Automatisch (CI)

Geen automatische PDF/Coria uit `.print.mscz`. CI en `check` eisen geen
`partituur-sha256`-keten voor dit spoor. Maps met
`artefacten_handmatig: true` worden door `mscz-products` /
`vsa-products` overgeslagen.

## Handmatig

| Situatie | Actie |
| --- | --- |
| Layout / PDF / Coria | MuseScore 4 met de hand — **geen** `layout` / `mscz-products` |
| Opnemen | `bieb accepteer` — [bieb accepteer](../../scripts/bieb-accepteer/) |
| Controle | `scripts\check.cmd --strict` — [check](../../scripts/check/) |

## Zie ook

- HOW: [Print-.mscz](../../partituur/7-print-mscz/)
- Namen/publicatiecontrole: [Publicatiecontrole](/handleiding/start/publicatiecontrole/)

{{< navbuttons "VSA|/handleiding/werktrajecten/vsa/" "Site-build|/handleiding/werktrajecten/site-build/" >}}
