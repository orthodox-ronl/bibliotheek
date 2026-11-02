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
scripts\products.cmd --kinds all [opties]
```

`[pad]` = catalogusmap of één bronbestand (default:
`content-source\catalogus`). Korte paden mogen: t.o.v. `content-source`,
`catalogus` of `koormappen` — zie
[bestand of map](../invoer-bestand-of-map/). `--kinds` is een komma-lijst
of `all` (default).

Kinds: `vsa`, `mscz`, `tekstblad`, `import`, `mvsa`, `audio`, `lyrics`.

# DESCRIPTION

Bouwt de bestanden die de site en Coria nodig hebben naast de bron in de
catalogus. Elk kind toont preflight op de echte todo-lijst; korte runs
(minder dan 100 items of geschat klaar binnen ongeveer een halve minuut)
starten zonder vraag; bij 100+ items volgt de dubbele zekerheidsvraag.
`-y` is vooral nodig zonder interactieve terminal.

Per notatie-kind (vsa/mscz/mvsa) worden alleen **stale slots** opnieuw
gemaakt (bijv. alleen `.mxl`, of alleen `.svg`), via aparte tooling-CLI’s —
niet één atomische `… products`-run die ook mp3/pdf meeneemt. Die CLI’s
werken `{bron}.products-meta.json` bij (snelle versheid). Audio en lyrics
zijn aparte kinds. Bestaan er nog kale lyrics/mp3 van een oude run, dan
krijgen die na slot-export opnieuw een bibliotheek-stempel. Daarna
vernieuwt `products` de zoekindex en Coria-fingerprints.

**Volgorde kinds** (bij `all`): vsa → mscz → tekstblad → mvsa → import →
audio → lyrics, zodat notatie-siblings er zijn vóór audio/lyrics. Lyrics
op `.mscz` maakt zonodig zelf eerst `.mscz.mxl`.

**Logging:** standaard alleen wat wél gebeurt (`>>> kind: N van M
bijwerken`) plus fouten met `Oplossing: …`. Paden in die regels zijn
kort (onder `content-source` zonder die prefix). Kinds die al
up-to-date zijn blijven stil (detail achter `-v` / `--verbose`).
Mislukt er iets over meerdere kinds, dan eindigt de run met
`=== Samenvatting products ===`.

Dit is het **enige** gebruikerscommando voor die producten. Er zijn geen
aparte `vsa-products.cmd`-wrappers meer. Per kind staat detail op de
man-page van dat kind (zelfde map):

- [products (vsa)](../vsa-products/)
- [products (mvsa)](../mvsa-products/)
- [products (mscz)](../mscz-products/)
- [products (audio)](../audio-products/)
- [products (lyrics)](../lyrics-products/)
- [products (tekstblad)](../tekstblad-products/)

Bij `vsa` / `mvsa` schrijft sync ook optionele translit-SVG’s
(`{bron}.translit-nls.svg` / `.translit-ksl.svg`) volgens de taal van de
bron. Bij `mvsa` bovendien `{bron}.translit.mxl` (Coria + hulp-parts).
`check` eist de translit-SVG’s nog niet. Zie
[products (vsa)](../vsa-products/) en [products (mvsa)](../mvsa-products/).

Koormap-/catalogusblad `index.md.pdf` (en `index.md.translit-*.pdf`)
hoort hier **niet** bij — dat is [pdf](../pdf/). Na `products` (verse
sibling-SVG’s) draai je `pdf.cmd` voor de pagina’s die die bronnen
tonen. Alleen git-gewijzigde bronnen (plus koormap-pdf):
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
scripts\products.cmd trisagion --kinds mscz,audio
scripts\products.cmd tweede-antifoon\weekdagen\hemelum --kinds vsa
scripts\products.cmd --kinds vsa --dry-run
scripts\products.cmd --kinds mscz,mvsa,vsa --only-invalid
scripts\products.cmd --verbose
```

# SEE ALSO

- [pdf](../pdf/) — `index.md.pdf` ná verse sibling-SVG’s uit products
- [products-changed](../products-changed/) — alleen git-gewijzigde bronnen
- [cleanup-chained-products](../cleanup-chained-products/)
- [check](../check/)
- [Publicatiecontrole](../../start/publicatiecontrole/)
