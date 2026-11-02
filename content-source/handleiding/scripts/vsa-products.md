---
title: "products — vsa"
linkTitle: "products (vsa)"
weight: 110
---

# NAME

`scripts\products.cmd --kinds vsa` — Coria-`.vsa.mxl`, muziek-`.vsa.svg`
(+ optioneel translit-SVG) maken bij een catalogus-`.vsa`

# SYNOPSIS

```cmd
scripts\products.cmd --kinds vsa [pad] [--force] [--dry-run]
```

`[pad]` = één `.vsa` of een map (recursief) — zie
[Invoer: bestand of map](../invoer-bestand-of-map/). Bij meerdere bronnen
die bijgewerkt moeten worden: preflight met geschatte duur (of `-y`).

# DESCRIPTION

Maakt naast een catalogus-`.vsa` de siblings voor Coria en scherm:

| Product                       | Waartoe                                                        |
| ----------------------------- | -------------------------------------------------------------- |
| `{stam}.vsa.mxl`              | Coria-afspelen (**Oefenen**)                                   |
| `{stam}.vsa.svg`              | Notatie op het **scherm** (Translit uit)                       |
| `{stam}.vsa.translit-nls.svg` | Scherm met Latijnse hulpregel (alleen bij kerkslavische bron)  |
| `{stam}.vsa.translit-ksl.svg` | Scherm met Cyrillische hulpregel (alleen bij Nederlandse bron) |

Hybride tekst (nl + ksl in één bron) krijgt beide translit-SVG’s.
`check` eist de translit-bestanden nog niet; wél `.vsa.mxl` + `.vsa.svg`.

Onder de motorkap: alleen wat nodig is. Coria-`.mxl` via
`vsa musicxml --syllabify`, scherm-`.svg` via `vsa svg` (niet het atomische
`vsa products`, dat ook mp3/pdf/Score-IR zou meenemen). Beide schrijven mee
in `*.products-meta.json`. Translit-SVG’s komen apart via
`vsa svg --translit-modus`. Bestaande lyrics-/Beluisteren-stempels worden
desnoods bijgewerkt. Optioneel zet het script nog een Coria-bronvermelding
in de MXL.

Pagina-download/print is **niet** `{stam}.vsa.pdf` maar `index.md.pdf`
(+ translit-pagina-PDF’s) via [pdf](../pdf/).

Mappen met `manueel: true` in de frontmatter worden
overgeslagen. Zonder pad werkt het onder `content-source\catalogus`.

Lokaal vernieuw je producten met dit commando. CI genereert **niet** —
`check_vsa_products` faalt bij ontbrekende of verouderde siblings.

# OPTIONS

| Optie       | Betekenis                                                    |
| ----------- | ------------------------------------------------------------ |
| `--force`   | Bestaande `.vsa.mxl` / `.vsa.svg` / translit-SVG’s overschrijven |
| `--dry-run` | Alleen tonen wat er zou gebeuren                             |

# WHEN

Na een wijziging aan een `.vsa` in de catalogus, of als `check --strict`
meldt dat `.vsa.mxl` / `.vsa.svg` of de products-meta ontbreekt of
verouderd is. Voor Translit op scherm: daarna ook [pdf](../pdf/) als je
de download-PDF’s wilt meenemen.

# SEE ALSO

- [check](../check/)
- [validate](../validate/)
- [products (mvsa)](../mvsa-products/) — Coria/scherm/Score-IR voor `.mvsa`
- [pdf](../pdf/) — pagina-`index.md.pdf` (+ translit-varianten)
- Workflow: [VSA → SVG en Coria](/handleiding/werktrajecten/vsa/)
