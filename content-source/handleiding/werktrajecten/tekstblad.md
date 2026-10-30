---
title: "Tekstblad → PDF"
linkTitle: "Tekstblad"
weight: 55
---

# Tekstblad

Dit werktraject houdt een bibliotheek-bron **`{stam}.tekstblad.md`**
bij (vooral tekst, eventueel HTML en `::: vsa-notatie`). Representatie-id:
`tekstblad`. Op het scherm toont `bieb` die inhoud; blokken
`::: vsa-notatie` worden als SVG getekend via
`{stam}.tekstblad.scherm.html`. Download/Print gebruikt `index.md.pdf`
(via `pdf.cmd`).

{{< cue >}}
Na een `{stam}.tekstblad.md` met `::: vsa-notatie` in de bladermap:
```cmd
scripts\products.cmd --kinds tekstblad content-source\catalogus\<zangstuk>
scripts\pdf.cmd content-source\catalogus\<zangstuk>
scripts\check.cmd --strict
```
Commit de `.tekstblad.md` samen met `.tekstblad.scherm.html` en de
block-SVG’s; commit `index.md.pdf` na `pdf.cmd`.
{{< /cue >}}

## Waartoe

Liturgische tekst of dialoog (bijvoorbeeld ustav met de diaken) hoort in de
**bibliotheek**, net als een basispartituur of een `.vsa`. Koorleden zien
het blad via shortcode `bieb` en downloaden via **Download pagina** —
niet een tweede kopie van de tekst in de koormap.

## Eindresultaat en criteria

| Bestand (in de bladermap) | Rol |
| --- | --- |
| `{stam}.tekstblad.md` | Canonieke bron (nooit een Hugo-pagina) |
| `{stam}.tekstblad.scherm.html` + `…-block-N.svg` | Scherm: VSA-blokken als tekening (`products --kinds tekstblad`) |
| `index.md.pdf` | Blad voor Download/Print (`pdf.cmd`) |

**Klaar** als: de bron frontmatter `build: render: never` (en `list: never`)
heeft; bij `::: vsa-notatie` de scherm-HTML/SVG’s bij de bron passen;
`bieb` toont leesbare tekst met gerenderde notatie; **Download pagina**
werkt via `index.md.pdf`. Geen verplichte product-`.tekstblad.pdf` meer;
geen Coria uit dit spoor.

Voorbeeld:
`content-source\catalogus\dialoog-met-diaken\default\hemelum\`.

## Wanneer wel / wanneer niet

| Wel | Niet |
| --- | --- |
| Ustav, dialoog, liturgische proza met korte VSA-regels | Vierstemmig MuseScore → [Basispartituur](../basispartituur/) |
| Tekst die je als A4-blad wilt downloaden/printen | Alleen schermtekst op een gewone `index.md` (geen product) |
| | Een koormap-blad met meerdere stukken → [pdf](../../scripts/pdf/) |

## Volgorde (bestanden)

1. Schrijf of herstel `{stam}.tekstblad.md` (HTML en `::: vsa-notatie` mogen).
2. Neem op met [Opnemen](../opnemen-in-catalogus/) /
   `bieb accepteer` (zet indien nodig de `build:`-frontmatter).
3. Bouw scherm-SVG’s (alleen nodig bij `::: vsa-notatie`):

```cmd
scripts\products.cmd --kinds tekstblad content-source\catalogus\dialoog-met-diaken
```

4. Bouw het blad voor Download/Print:

```cmd
scripts\pdf.cmd content-source\catalogus\dialoog-met-diaken
```

5. Koormap-slot: alleen intro + `bieb` (geen tweede kopie van de tekst).
6. [Site-build](../site-build/) / `scripts\check.cmd --strict`.

## Automatisch (CI)

- **Wel:** `check_tekstblad_products.py` controleert of de `.tekstblad.md`
  bestaat (statusbestand).
- **Niet:** scherm-SVG’s of `index.md.pdf` opnieuw genereren op GitHub
  Actions. Maak die **lokaal** (`products --kinds tekstblad`, `pdf.cmd`)
  en commit ze samen met de bron.

## Handmatig

| Situatie | Commando | Man-page |
| --- | --- | --- |
| Scherm-SVG’s bij `::: vsa-notatie` | `scripts\products.cmd --kinds tekstblad` `[map]` | [products (tekstblad)](../../scripts/tekstblad-products/) |
| Blad `index.md.pdf` | `scripts\pdf.cmd` | [pdf](../../scripts/pdf/) |
| Opnemen | `bieb accepteer` | [bieb accepteer](../../scripts/bieb-accepteer/) |
| Alles vóór commit | `scripts\check.cmd --strict` | [check](../../scripts/check/) |

## Zie ook

- Namen/publicatiecontrole: [Publicatiecontrole](/handleiding/start/publicatiecontrole/)
- [Markdown naar PDF](../markdown-naar-pdf/) (generiek / demo)
- [Opnemen](../opnemen-in-catalogus/)

{{< navbuttons "Site-build|/handleiding/werktrajecten/site-build/" "Markdown naar PDF|/handleiding/werktrajecten/markdown-naar-pdf/" >}}
