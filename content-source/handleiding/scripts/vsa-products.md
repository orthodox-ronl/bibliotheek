---
title: "products — vsa"
linkTitle: "products (vsa)"
weight: 110
---

# NAME

`scripts\products.cmd --kinds vsa` — Coria-`.vsa.mxl`, A4-`.vsa.pdf` en muziek-`.vsa.svg`
maken bij een catalogus-`.vsa`

# SYNOPSIS

```cmd
scripts\products.cmd --kinds vsa [pad] [--force] [--dry-run]
```

`[pad]` = één `.vsa` of een map (recursief) — zie
[Invoer: bestand of map](../invoer-bestand-of-map/). Bij meerdere bronnen
die bijgewerkt moeten worden: preflight met geschatte duur (of `-y`).

# DESCRIPTION

Maakt naast een catalogus-`.vsa` drie siblings (zelfde productrol als bij
`.mvsa` via `products --kinds mvsa`):

| Product | Waartoe |
| --- | --- |
| `{stam}.vsa.mxl` | Coria-afspelen (**Oefenen**) |
| `{stam}.vsa.pdf` | A4-blad (**Downloaden** / **Printen**; mag titel uit `index.md`) |
| `{stam}.vsa.svg` | Alleen notatie op het **scherm** (shortcode `muziek`) |

Onder de motorkap: tooling `vsa products` maakt Coria-`.mxl` (tijdelijke
syllabify + playback + finalize) en scherm-`.svg`, en schrijft
`*.products-meta.json` (schema 2: bron- + product-hashes), plus eventueel
kale lyrics/mp3. Versheid van mxl/svg voor check/regen komt uit die meta.
Lyrics- en Beluisteren-stempels zet dit script daarna zelf (anders klaagt
`check` over `unstamped_lyrics` / `unstamped_mp3`). Optioneel zet het nog
een Coria-bronvermelding in de MXL (geen versheidstempel).

Product-PDF is geen vast sync-slot meer (blad = `index.md.pdf` via
`pdf.cmd`). Zonder scherm-SVG kan de site nog een PDF als fallback tonen.

Mappen met `manueel: true` in de frontmatter worden
overgeslagen. Zonder pad werkt het onder `content-source\catalogus`.

Lokaal vernieuw je producten met dit commando. CI genereert **niet** —
`check_vsa_products` faalt bij ontbrekende of verouderde siblings.

# OPTIONS

| Optie | Betekenis |
| --- | --- |
| `--force` | Bestaande `.vsa.mxl` / `.vsa.pdf` / `.vsa.svg` overschrijven |
| `--dry-run` | Alleen tonen wat er zou gebeuren |

# WHEN

Na een wijziging aan een `.vsa` in de catalogus, of als `check --strict`
meldt dat `.vsa.mxl` / `.vsa.svg` of de products-meta ontbreekt of verouderd is.

# SEE ALSO

- [check](../check/)
- [validate](../validate/)
- [products (mvsa)](../mvsa-products/) — dezelfde drie producten voor `.mvsa`
- Workflow: [VSA → SVG en Coria](/handleiding/werktrajecten/vsa/)
