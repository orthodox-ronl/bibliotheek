---
title: "bieb kopieer"
linkTitle: "bieb kopieer"
weight: 167
---

# NAME

`bieb kopieer` — uitvoeringsvorm kopiëren naar een nieuw catalogus-id

# SYNOPSIS

```cmd
scripts\bieb.cmd kopieer <bron-id> <nieuw-id> [--dry-run]
```

Met `.\scripts` op PATH: `bieb kopieer …`. Korte hulp: `h bieb kopieer`
of `bieb kopieer -h`. Typ `?` bij een vraag voor uitleg.

# DESCRIPTION

Kopieert één **uitvoeringsvorm** (leaf) naar een nieuw id. Geen
variant- of zangstuk-kopie (nog niet).

Bron en nieuw: slash- of stam-vorm, zoals bij
[bieb hernoem](../bieb-hernoem/). Nieuw mag alleen het laatste segment
zijn (zelfde ouder), bijvoorbeeld `groningen`.

Het script:

1. Controleert dat bron een bestaande uitvoeringsvorm is.
2. Weigert als de **doelmap al bestaat**.
3. Maakt zo nodig zangstuk-/variant-`_index.md` aan.
4. Kopieert bestanden en hernoemt de publicatiestam.
5. Schrijft een nieuwe leaf-`index.md` met nieuw `bieb id` en afgeleide
   titels (bouw leidt titels verder af).
6. Kopieert bladermap-SVG’s onder het nieuwe pad (als die er zijn).
7. Maakt **geen** koormap-slot — dat blijft handwerk.

Daarna: products vernieuwen, zoekindex, `scripts\check.cmd`. Eventueel
koormap-slot met shortcode `bieb`.

# EXAMPLES

```cmd
scripts\bieb.cmd kopieer ektinia/vredes/hemelum ektinia/vredes/groningen --dry-run
scripts\bieb.cmd kopieer ektinia-vredes-hemelum groningen
scripts\bieb.cmd kopieer tropaar/zondag-toon-1/groningen tropaar/zondag-toon-2/groningen
```

# WHEN

Als je dezelfde partituur onder een **ander** uitvoeringsvorm-id nodig
hebt (andere plaats, taal-suffix, …) zonder de bron te verplaatsen. Voor
nieuw materiaal uit de werkbank: [bieb accepteer](../bieb-accepteer/).
Voor id wijzigen zonder kopie: [bieb hernoem](../bieb-hernoem/).

# SEE ALSO

[bieb accepteer](../bieb-accepteer/),
[bieb hernoem](../bieb-hernoem/),
[bieb verwijder](../bieb-verwijder/),
[check](../check/),
[h](../h/)
