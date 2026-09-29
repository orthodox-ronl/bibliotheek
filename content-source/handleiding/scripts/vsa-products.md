---
title: "vsa-products"
linkTitle: "vsa-products"
weight: 110
---

# NAME

`scripts\vsa-products.cmd` — Coria-`.vsa.mxl` en A4-`.vsa.pdf` maken bij een
bibliotheek-`.vsa`

# SYNOPSIS

```cmd
scripts\vsa-products.cmd [pad] [--force] [--dry-run]
```

# DESCRIPTION

Maakt naast een bibliotheek-`.vsa` twee siblings:

| Product | Waartoe |
| --- | --- |
| `{stam}.vsa.mxl` | Coria-afspelen (**Oefenen**) |
| `{stam}.vsa.pdf` | A4-blad (**Downloaden** / **Printen**) |

Voor de `.mxl`:

1. syllabificeert in een tijdelijk bestand (canonieke `.vsa` blijft ongewijzigd);
2. exporteert via `vsa musicxml --musicxml-profile playback`;
3. saniteert voor Coria;
4. zet een `vsa-source-sha256`-stempel van de canonieke `.vsa`.

Voor de `.pdf`: tijdelijke Markdown met `::: vsa-notatie` → `vsa pdf`
(Chrome of Edge nodig), daarna dezelfde herkomststempel in de PDF.
Zonder PDF blijven **Downloaden** en **Printen** op VSA-only bladermappen weg.

Mappen met `artefacten_handmatig: true` in de frontmatter worden
overgeslagen. Zonder pad werkt het onder `content-source\bibliotheek`.

Lokaal vernieuw je producten met dit commando. CI genereert **niet** —
`check_vsa_products` faalt bij ontbrekende of verouderde siblings.

# OPTIONS

| Optie | Betekenis |
| --- | --- |
| `--force` | Bestaande `.vsa.mxl` / `.vsa.pdf` overschrijven |
| `--dry-run` | Alleen tonen wat er zou gebeuren |

# WHEN

Na een wijziging aan een `.vsa` in de bibliotheek, of als `check --strict`
meldt dat de `.vsa.mxl` of `.vsa.pdf` verouderd of zonder stamp is.

# SEE ALSO

- [check](../check/)
- [validate](../validate/)
- Workflow: [VSA → SVG en Coria](/handleiding/werktrajecten/vsa/)
