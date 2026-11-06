---
title: "Markdown naar PDF"
linkTitle: "Markdown naar PDF"
weight: 60
---

# Markdown naar PDF

Deze repository heeft geen commando `pdf` of `demo-pdf`. Een los
Markdownblad met `::: vsa-notatie` zet je niet om via een script in
`scripts\`.

Wat wél in de bibliotheek staat:

| Wat je wilt | Commando |
| --- | --- |
| Liturgische tekst in de catalogus (`{stam}.tekstblad.md` → `{stam}.tekstblad.pdf`) | [products (tekstblad)](../../scripts/tekstblad-products/) |
| PDF van een koormap- of cataloguspagina (`index.md.pdf`) | [pdf](../../scripts/pdf/) |
| A4-blad bij een `.vsa` of `.mvsa` | [products (vsa)](../../scripts/vsa-products/) / [products (mvsa)](../../scripts/mvsa-products/) |

Een generieke export `vsa pdf` hoort in VSA-tooling, niet in deze
commandolijst. `check` en de Pages-build controleren geen demo-PDF en
draaien geen `check_demo_pdf_fresh`.

{{< navbuttons "Tekstblad|/handleiding/werktrajecten/tekstblad/" "pdf|/handleiding/scripts/pdf/" >}}
