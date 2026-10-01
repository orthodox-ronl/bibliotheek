---
title: "tekstblad-products"
linkTitle: "tekstblad-products"
weight: 115
---

# NAME

`scripts\tekstblad-products.cmd` — A4-PDF maken bij een catalogus-`.tekstblad.md`

# SYNOPSIS

```cmd
scripts\tekstblad-products.cmd [pad] [--force] [--dry-run]
```

# DESCRIPTION

Zoekt canonieke bronnen `{stam}.tekstblad.md` onder het opgegeven pad
(of, zonder pad, onder `content-source\catalogus`) en schrijft ernaast
`{stam}.tekstblad.pdf` via `vsa pdf`. In de PDF komt een stamp
(`vsa-source-sha256`, `vsa-source-kind=tekstblad`) zodat `check` kan zien
of de PDF nog bij de bron past.

Bestanden in `input\` en mappen met `artefacten_handmatig: true` worden
overgeslagen. CI genereert deze PDF’s niet; jij wel lokaal (Chrome of Edge
nodig voor `vsa pdf`), daarna bron + PDF samen committen.

# OPTIONS

| Optie | Betekenis |
| --- | --- |
| `--force` | Bestaande PDF overschrijven |
| `--dry-run` | Alleen tonen wat er zou gebeuren |

# EXAMPLES

```cmd
scripts\tekstblad-products.cmd
scripts\tekstblad-products.cmd content-source\catalogus\7d-dialoog-met-diaken --force
```

# WHEN

Als de `.tekstblad.md` klaar is voor publicatie-PDF, of als `check --strict`
meldt dat de PDF ontbreekt, zonder stamp is, of verouderd.

# SEE ALSO

- [check](../check/)
- [pdf](../pdf/) — generieke markdown ? PDF
- Workflow: [Tekstblad](/handleiding/werktrajecten/tekstblad/)
- [Publicatiecontrole](/handleiding/start/publicatiecontrole/)
