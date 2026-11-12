---
title: "Formules"
linkTitle: "Formules"
weight: 5
nav_sort: weight
publicatiestatus: concept
automatische_inhoud: false
---

# Formules (VSA-templates)

Hier staan de **melodieformules** waarmee een `.vsa` naar een SATB-`.mvsa`
wordt gezet (`vsa mvsa`). Een formule-id heeft de vorm
`{soort}-toon-{n}-{bron}` (bijvoorbeeld `kondak-toon-8-hemelum`).

De machinebron staat in VSA-tooling
(`docs/specification-vsa-templates/library/` + `aliases.yaml`).
Deze catalogus-pagina’s zijn het **register** voor beheerders.

## Canonieke formules

| Id | Soort | Toon | Bron | same_as |
| --- | --- | --- | --- | --- |
| [`kondak-toon-1-groningen`](kondak-toon-1-groningen/) | kondak | 1 | groningen | — |
| [`kondak-toon-2-groningen`](kondak-toon-2-groningen/) | kondak | 2 | groningen | — |
| [`kondak-toon-5-groningen`](kondak-toon-5-groningen/) | kondak | 5 | groningen | — |
| [`kondak-toon-6-groningen`](kondak-toon-6-groningen/) | kondak | 6 | groningen | — |
| [`kondak-toon-7-groningen`](kondak-toon-7-groningen/) | kondak | 7 | groningen | — |
| [`kondak-toon-8-groningen`](kondak-toon-8-groningen/) | kondak | 8 | groningen | — |
| [`kondak-toon-8-hemelum`](kondak-toon-8-hemelum/) | kondak | 8 | hemelum | — |
| [`stichier-toon-5-pdf`](stichier-toon-5-pdf/) | stichier | 5 | pdf | — |
| [`tropaar-toon-1-groningen`](tropaar-toon-1-groningen/) | tropaar | 1 | groningen | — |
| [`tropaar-toon-2-groningen`](tropaar-toon-2-groningen/) | tropaar | 2 | groningen | `kondak-toon-2-groningen` |
| [`tropaar-toon-3-groningen`](tropaar-toon-3-groningen/) | tropaar | 3 | groningen | — |
| [`tropaar-toon-4-groningen`](tropaar-toon-4-groningen/) | tropaar | 4 | groningen | — |
| [`tropaar-toon-4-hemelum`](tropaar-toon-4-hemelum/) | tropaar | 4 | hemelum | — |
| [`tropaar-toon-5-groningen`](tropaar-toon-5-groningen/) | tropaar | 5 | groningen | `kondak-toon-5-groningen` |
| [`tropaar-toon-6-groningen`](tropaar-toon-6-groningen/) | tropaar | 6 | groningen | `kondak-toon-6-groningen` |
| [`tropaar-toon-7-groningen`](tropaar-toon-7-groningen/) | tropaar | 7 | groningen | `kondak-toon-7-groningen` |
| [`tropaar-toon-8-groningen`](tropaar-toon-8-groningen/) | tropaar | 8 | groningen | `kondak-toon-8-groningen` |
| [`tropaar-toon-8-hemelum`](tropaar-toon-8-hemelum/) | tropaar | 8 | hemelum | `kondak-toon-8-hemelum` |
| [`vers-toon-1-groningen`](vers-toon-1-groningen/) | vers | 1 | groningen | — |
| [`vers-toon-5-groningen`](vers-toon-5-groningen/) | vers | 5 | groningen | — |

## Aliassen

Een alias is een andere naam voor dezelfde library-map. Liturgikon telt
vooralsnog als Hemelum. Oude ids zonder bron-suffix blijven werken.
Ontbrekende Hemelum-formules vallen via de aliaslijst terug op Groningen.

| Alias | Canonieke id |
| --- | --- |
| `groningen-kondak-toon-4` | `tropaar-toon-4-groningen` |
| `groningen-tropaar-toon-4` | `tropaar-toon-4-groningen` |
| `hemelum-kondak-toon-1` | `kondak-toon-1-groningen` |
| `hemelum-kondak-toon-2` | `kondak-toon-2-groningen` |
| `hemelum-kondak-toon-3` | `tropaar-toon-3-groningen` |
| `hemelum-kondak-toon-4` | `tropaar-toon-4-groningen` |
| `hemelum-kondak-toon-5` | `kondak-toon-5-groningen` |
| `hemelum-kondak-toon-6` | `kondak-toon-6-groningen` |
| `hemelum-kondak-toon-7` | `kondak-toon-7-groningen` |
| `hemelum-kondak-toon-8` | `kondak-toon-8-hemelum` |
| `hemelum-toon-4` | `tropaar-toon-4-hemelum` |
| `hemelum-tropaar-toon-1` | `tropaar-toon-1-groningen` |
| `hemelum-tropaar-toon-2` | `tropaar-toon-2-groningen` |
| `hemelum-tropaar-toon-3` | `tropaar-toon-3-groningen` |
| `hemelum-tropaar-toon-4` | `tropaar-toon-4-hemelum` |
| `hemelum-tropaar-toon-5` | `tropaar-toon-5-groningen` |
| `hemelum-tropaar-toon-6` | `tropaar-toon-6-groningen` |
| `hemelum-tropaar-toon-7` | `tropaar-toon-7-groningen` |
| `hemelum-tropaar-toon-8` | `tropaar-toon-8-hemelum` |
| `kondak-toon-1` | `kondak-toon-1-groningen` |
| `kondak-toon-1-liturgikon` | `kondak-toon-1-groningen` |
| `kondak-toon-2` | `kondak-toon-2-groningen` |
| `kondak-toon-2-liturgikon` | `kondak-toon-2-groningen` |
| `kondak-toon-3-liturgikon` | `tropaar-toon-3-groningen` |
| `kondak-toon-4-groningen` | `tropaar-toon-4-groningen` |
| `kondak-toon-4-hemelum` | `tropaar-toon-4-hemelum` |
| `kondak-toon-4-liturgikon` | `tropaar-toon-4-groningen` |
| `kondak-toon-5` | `kondak-toon-5-groningen` |
| `kondak-toon-5-liturgikon` | `kondak-toon-5-groningen` |
| `kondak-toon-6` | `kondak-toon-6-groningen` |
| `kondak-toon-6-liturgikon` | `kondak-toon-6-groningen` |
| `kondak-toon-7` | `kondak-toon-7-groningen` |
| `kondak-toon-7-liturgikon` | `kondak-toon-7-groningen` |
| `kondak-toon-8` | `kondak-toon-8-groningen` |
| `kondak-toon-8-liturgikon` | `kondak-toon-8-hemelum` |
| `liturgikon-kondak-toon-1` | `kondak-toon-1-groningen` |
| `liturgikon-kondak-toon-2` | `kondak-toon-2-groningen` |
| `liturgikon-kondak-toon-3` | `tropaar-toon-3-groningen` |
| `liturgikon-kondak-toon-4` | `tropaar-toon-4-groningen` |
| `liturgikon-kondak-toon-5` | `kondak-toon-5-groningen` |
| `liturgikon-kondak-toon-6` | `kondak-toon-6-groningen` |
| `liturgikon-kondak-toon-7` | `kondak-toon-7-groningen` |
| `liturgikon-kondak-toon-8` | `kondak-toon-8-hemelum` |
| `liturgikon-tropaar-toon-1` | `tropaar-toon-1-groningen` |
| `liturgikon-tropaar-toon-2` | `tropaar-toon-2-groningen` |
| `liturgikon-tropaar-toon-3` | `tropaar-toon-3-groningen` |
| `liturgikon-tropaar-toon-4` | `tropaar-toon-4-hemelum` |
| `liturgikon-tropaar-toon-5` | `tropaar-toon-5-groningen` |
| `liturgikon-tropaar-toon-6` | `tropaar-toon-6-groningen` |
| `liturgikon-tropaar-toon-7` | `tropaar-toon-7-groningen` |
| `liturgikon-tropaar-toon-8` | `tropaar-toon-8-hemelum` |
| `stichier-toon-5` | `stichier-toon-5-pdf` |
| `tropaar-toon-1` | `tropaar-toon-1-groningen` |
| `tropaar-toon-1-liturgikon` | `tropaar-toon-1-groningen` |
| `tropaar-toon-2` | `tropaar-toon-2-groningen` |
| `tropaar-toon-2-liturgikon` | `tropaar-toon-2-groningen` |
| `tropaar-toon-3` | `tropaar-toon-3-groningen` |
| `tropaar-toon-3-liturgikon` | `tropaar-toon-3-groningen` |
| `tropaar-toon-4` | `tropaar-toon-4-hemelum` |
| `tropaar-toon-4-liturgikon` | `tropaar-toon-4-hemelum` |
| `tropaar-toon-5` | `tropaar-toon-5-groningen` |
| `tropaar-toon-5-liturgikon` | `tropaar-toon-5-groningen` |
| `tropaar-toon-6` | `tropaar-toon-6-groningen` |
| `tropaar-toon-6-liturgikon` | `tropaar-toon-6-groningen` |
| `tropaar-toon-7` | `tropaar-toon-7-groningen` |
| `tropaar-toon-7-liturgikon` | `tropaar-toon-7-groningen` |
| `tropaar-toon-8` | `tropaar-toon-8-groningen` |
| `tropaar-toon-8-liturgikon` | `tropaar-toon-8-hemelum` |
| `vers-toon-1` | `vers-toon-1-groningen` |
| `vers-toon-5` | `vers-toon-5-groningen` |

Zie ook de handleiding [template SATB](../../handleiding/vsa/2-template-satb/).
