---
title: "vsa-products"
linkTitle: "vsa-products"
weight: 110
---

# NAME

`scripts\vsa-products.cmd` — Coria-`.vsa.mxl`, A4-`.vsa.pdf` en muziek-`.vsa.svg`
maken bij een catalogus-`.vsa`

# SYNOPSIS

```cmd
scripts\vsa-products.cmd [pad] [--force] [--dry-run]
```

`[pad]` = één `.vsa` of een map (recursief) — zie
[Invoer: bestand of map](../invoer-bestand-of-map/). Bij meerdere bronnen
die bijgewerkt moeten worden: preflight met geschatte duur (of `-y`).

# DESCRIPTION

Maakt naast een catalogus-`.vsa` drie siblings (zelfde productrol als bij
`.mvsa` via `mvsa-products`):

| Product | Waartoe |
| --- | --- |
| `{stam}.vsa.mxl` | Coria-afspelen (**Oefenen**) |
| `{stam}.vsa.pdf` | A4-blad (**Downloaden** / **Printen**; mag titel uit `index.md`) |
| `{stam}.vsa.svg` | Alleen notatie op het **scherm** (shortcode `muziek`) |

Voor de `.mxl`:

1. syllabificeert in een tijdelijk bestand (canonieke `.vsa` blijft ongewijzigd);
2. exporteert via `vsa musicxml --musicxml-profile playback`;
3. saniteert voor Coria;
4. zet een `vsa-source-sha256`-stempel van de canonieke `.vsa`.

Voor de `.pdf`: tijdelijke Markdown met alleen de VSA-notatie (de
YAML-frontmatter van de `.vsa` eraf, zodat die niet als tekst op het blad
komt) in `::: vsa-notatie` → `vsa pdf` (Chrome of Edge nodig). De titel
bovenaan komt uit de bladermap-`index.md`. Daarna dezelfde
herkomststempel in de PDF. Zonder PDF blijven **Downloaden** en
**Printen** op VSA-only bladermappen weg.

Voor de `.svg`: `vsa svg` (native VSA-renderer, muziek-only) +
herkomststempel in XML-commentaren. Zonder SVG toont de site de PDF als
fallback op het scherm (met titel) — daarom hoort de SVG bij dit
productcommando, net als `.mvsa.svg` bij `mvsa-products`.

Mappen met `artefacten_handmatig: true` in de frontmatter worden
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
meldt dat de `.vsa.mxl`, `.vsa.pdf` of `.vsa.svg` verouderd of zonder stamp is.

# SEE ALSO

- [check](../check/)
- [validate](../validate/)
- [mvsa-products](../mvsa-products/) — dezelfde drie producten voor `.mvsa`
- Workflow: [VSA → SVG en Coria](/handleiding/werktrajecten/vsa/)
