---
title: "products — vsa"
linkTitle: "products (vsa)"
weight: 110
---

# NAME

`scripts\products.cmd --kinds vsa` — muziek-`.vsa.svg`, schets-`.vsa.mvsa`
en (via cascade) de mvsa-producten bij een catalogus-`.vsa`

# SYNOPSIS

```cmd
scripts\products.cmd --kinds vsa [pad] [--force] [--dry-run]
```

`[pad]` = één `.vsa` of een map (recursief) — zie
[Invoer: bestand of map](../invoer-bestand-of-map/). Bij meerdere bronnen
die bijgewerkt moeten worden: preflight met geschatte duur (of `-y`).

# DESCRIPTION

Maakt naast een catalogus-`.vsa` deze afgeleiden:

| Product | Waartoe |
| ------------------- | ------ |
| `{stam}.vsa.svg` | Notatie op het **scherm** (shortcode `muziek`) |
| `{stam}.….translit-….svg` | Optioneel: translit volgens de taalmatrix |
| `{stam}.vsa.mvsa` | Schets-partituur via `vsa mvsa` (T1: `formule:` / soort+toon / bestaande MVSA-template) |

**Geen** Coria-`{stam}.vsa.mxl` meer. Playback-MXL hoort bij de schets:
`{stam}.vsa.mvsa.mxl` (en score-ir / from-ir / svg / translit / lyrics /
mp3), alsof die `.vsa.mvsa` de bron is. Die cascade draait mee bij
`--kinds vsa`, zodat je niet apart `--kinds mvsa,audio,lyrics` hoeft te
zetten voor die schets.

Templatekeuze volgt
[vsa-mvsa-contract T1](https://github.com/orthodox-ronl/VSA-tooling/blob/main/docs/specification-vsa-templates/vsa-mvsa-contract.md):

- staat `formule:` in de `.vsa` en die wijst nergens naartoe → **harde fout**;
- geen passende default-formule (soort+toon) → **geen** `.vsa.mvsa` (geen
  fout; alleen zichtbaar met `--verbose`);
- bestaat er al een `.vsa.mvsa`, dan wint de template uit die frontmatter
  (`template_opgegeven` / `template`) bij hergeneratie.

Onder de motorkap: `vsa svg`, daarna `convert_vsa_to_mvsa` / cascade
`mvsa …`, plus `*.products-meta.json` (schema 2). Product-PDF is geen
sync-slot (blad = `index.md.pdf` via `pdf.cmd`).

Mappen met `manueel: true` in de frontmatter worden overgeslagen. Zonder
pad werkt het onder `content-source\catalogus`. CI genereert **niet** —
`check_vsa_products` faalt bij ontbrekende of verouderde siblings.

# OPTIONS

| Optie | Betekenis |
| ----------- | --------- |
| `--force` | Bestaande `.vsa.svg` / `.vsa.mvsa` (en cascade) overschrijven |
| `--dry-run` | Alleen tonen wat er zou gebeuren |

# WHEN

Na een wijziging aan een `.vsa` in de catalogus, of als `check --strict`
meldt dat `.vsa.svg` / `.vsa.mvsa` of de products-meta ontbreekt of
verouderd is.

# SEE ALSO

- [check](../check/)
- [validate](../validate/)
- [products (mvsa)](../mvsa-products/) — producten op een canonieke of schets-`.mvsa`
- [Publicatiecontrole](../../start/publicatiecontrole/)
