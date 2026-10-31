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
scripts\products.cmd [pad] [--kinds LIST] [--force] [--dry-run] [--verbose]
                     [--only-missing|--only-stale|--only-invalid]
scripts\all-products.cmd [opties]
```

`[pad]` = catalogusmap of één bronbestand (default:
`content-source\catalogus`). `--kinds` is een komma-lijst of `all`
(default). Alias `all-products` = `--kinds all`.

Kinds: `vsa`, `mscz`, `tekstblad`, `import`, `mvsa`, `audio`, `lyrics`.

# DESCRIPTION

Bouwt de bestanden die de site en Coria nodig hebben naast de bron in de
catalogus. Elk kind toont preflight op de echte todo-lijst; korte runs
(minder dan 100 items of geschat klaar binnen ongeveer een halve minuut)
starten zonder vraag; bij 100+ items volgt de dubbele zekerheidsvraag.
`-y` is vooral nodig zonder interactieve terminal. Na een geslaagde run
(niet `--dry-run`) schrijft de tooling voor vsa/mvsa/mscz
`{bron}.products-meta.json` (snelle versheid; bladreeks-SVG als `svg-1`…).
Die export is **kaal**: lyrics en preview-mp3 krijgen daarbij nog geen
bibliotheek-herkomststempel. Direct daarna zet `products` die stempels
wél (zelfde regels als `--kinds lyrics` / `--kinds audio`) en werkt de
hashes in de meta bij. Bij vsa/mscz worden gewijzigde MXL/SVG-hashes
gemerged zonder andere meta-keys te wissen. Daarna vernieuwt het de
zoekindex en Coria-fingerprints.

**Logging:** standaard beknopt (voortgang + fouten met `Oplossing: …`).
Mislukt er iets over meerdere kinds, dan eindigt de run met
`=== Samenvatting products ===`. Gebruik `-v` / `--verbose` voor
per-stap detail; zonder die vlag krijgt de VSA-tooling `--quiet`.

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
[pdf](../pdf/). Alleen git-gewijzigde bronnen (plus koormap-pdf):
[products-changed](../products-changed/).

Bij een **map** pakt `products` alleen canonieke bronnen (`.vsa` /
`.mvsa` / basis-`.mscz`). Afgeleide `*.mvsa.mscz` / `*.vsa.mscz` worden
overgeslagen, zodat er geen kettingnamen zoals `*.mvsa.mscz.mp3` ontstaan.
Wil je wél vanaf zo’n afgeleide werken: geef dat bestand expliciet als
pad. Bestaande kettingrommel:
[cleanup-chained-products](../cleanup-chained-products/).

# EXAMPLES

```cmd
scripts\products.cmd
scripts\products.cmd content-source\catalogus\trisagion --kinds mscz,audio
scripts\products.cmd --kinds vsa --dry-run
scripts\products.cmd --kinds mscz,mvsa,vsa --only-invalid
scripts\products.cmd --verbose
```

# SEE ALSO

- [products-changed](../products-changed/) — alleen git-gewijzigde bronnen
- [all-products](../all-products/)
- [cleanup-chained-products](../cleanup-chained-products/)
- [check](../check/)
- [Publicatiecontrole](../../start/publicatiecontrole/)
