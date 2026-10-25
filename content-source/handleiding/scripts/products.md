---
title: "products"
linkTitle: "products"
weight: 100
---

# NAME

`scripts\products.cmd` — catalogus-afgeleiden (MXL, SVG, Score-IR, audio,
lyrics, …) opnieuw maken onder een map of voor één bronbestand

# SYNOPSIS

```cmd
scripts\products.cmd [pad] [--kinds LIST] [--force] [--dry-run] [--only-missing|--only-stale|--only-invalid]
scripts\all-products.cmd [opties]
```

`[pad]` = catalogusmap of één bronbestand (default:
`content-source\catalogus`). `--kinds` is een komma-lijst of `all`
(default). Alias `all-products` = `--kinds all`.

Kinds: `vsa`, `mscz`, `tekstblad`, `import`, `mvsa`, `audio`, `lyrics`.

# DESCRIPTION

Bouwt de bestanden die de site en Coria nodig hebben naast de bron in de
catalogus. Bij een map of meerdere kinds vraagt het **één keer** om
bevestiging (of `-y`); de kind-sporen vragen daarna niet opnieuw. Na een
geslaagde run (niet `--dry-run`) schrijft de tooling voor vsa/mvsa/mscz
`{bron}.products-meta.json` (snelle versheid; bladreeks-SVG als `svg-1`…).
Bibliotheek herschrijft die meta niet meer uit siblings; bij mscz wordt
alleen de MXL-hash gemerged als de Coria-bron-id de MXL wijzigt. Daarna
vernieuwt het de zoekindex en Coria-fingerprints.

Dit is het **enige** gebruikerscommando voor die producten. Er zijn geen
aparte `vsa-products.cmd`-wrappers meer. Per kind staat detail op de
man-page van dat kind (zelfde map):

- [products (vsa)](../vsa-products/)
- [products (mvsa)](../mvsa-products/)
- [products (mscz)](../mscz-products/)
- [products (audio)](../audio-products/)
- [products (lyrics)](../lyrics-products/)
- [products (tekstblad)](../tekstblad-products/)

Koormap-/catalogusblad `index.md.pdf` hoort hier **niet** bij — dat is
[pdf](../pdf/).

# EXAMPLES

```cmd
scripts\products.cmd
scripts\products.cmd content-source\catalogus\trisagion --kinds mscz,audio
scripts\products.cmd --kinds vsa --dry-run
scripts\products.cmd --kinds mscz,mvsa,vsa --only-invalid
```

# SEE ALSO

- [all-products](../all-products/)
- [check](../check/)
- [Publicatiecontrole](../../start/publicatiecontrole/)
