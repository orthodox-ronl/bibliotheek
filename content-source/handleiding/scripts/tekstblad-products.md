---
title: "products — tekstblad"
linkTitle: "products (tekstblad)"
weight: 115
---

# NAME

`scripts\products.cmd --kinds tekstblad` — scherm-SVG’s bij catalogus-`.tekstblad.md` met `::: vsa-notatie`

# SYNOPSIS

```cmd
scripts\products.cmd --kinds tekstblad [pad] [--force] [--dry-run]
```

# DESCRIPTION

Zoekt canonieke bronnen `{stam}.tekstblad.md` onder het opgegeven pad
(of, zonder pad, onder `content-source\catalogus`). Als de bron
`::: vsa-notatie`-blokken heeft, schrijft het script ernaast:

- `{stam}.tekstblad.scherm.html` — dezelfde HTML/tekst, met elk VSA-blok
  als `<img>` naar een sibling-SVG;
- `{stam}-…-block-N.svg` — de getekende notatie voor schermweergave
  (shortcode `bieb`).

Zonder `::: vsa-notatie` doet dit kind niets. Pagina-PDF (Download/Print)
hoort bij `scripts\pdf.cmd` (`index.md.pdf`), niet bij dit product-kind.
Bestanden in `input\` en mappen met `manueel: true` worden overgeslagen.

# OPTIONS

| Optie | Betekenis |
| --- | --- |
| `--force` | Bestaande scherm-HTML/SVG’s overschrijven |
| `--dry-run` | Alleen tonen wat er zou gebeuren |

# EXAMPLES

```cmd
scripts\products.cmd --kinds tekstblad
scripts\products.cmd --kinds tekstblad content-source\catalogus\dialoog-met-diaken --force
```

# WHEN

Als je `::: vsa-notatie` in een tekstblad hebt gezet of gewijzigd, of als
Hugo waarschuwt dat `.tekstblad.scherm.html` ontbreekt (ruwe VSA op
scherm). Commit de `.tekstblad.md` samen met de scherm-HTML en de
block-SVG’s.

# SEE ALSO

- [check](../check/)
- [pdf](../pdf/) — blad `index.md.pdf` uit tekstblad of notatiebron
- Workflow: [Tekstblad](/handleiding/werktrajecten/tekstblad/)
- [Publicatiecontrole](/handleiding/start/publicatiecontrole/)
