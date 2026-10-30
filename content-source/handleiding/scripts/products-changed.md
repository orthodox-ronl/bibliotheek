---
title: "products-changed"
linkTitle: "products-changed"
weight: 105
---

# NAME

`scripts\products-changed.cmd` — catalogus-producten en koormap-blad-PDF’s
alleen voor bestanden die in git gewijzigd zijn onder `content-source`

# SYNOPSIS

```cmd
scripts\products-changed.cmd [--dry-run]
                             [--since-main | --since-development | --base REF]
                             [--force] [-y] [--verbose]
```

`--since-dev` is een alias voor `--since-development`.

# DESCRIPTION

Lost het probleem op dat een volle `products`-run de hele catalogus scant
(inclusief de dure contractcheck **invalid**) terwijl je vaak alleen een
paar bronnen hebt aangepast. Dit commando kijkt naar **git**: welke
bestanden onder `content-source` zijn gewijzigd t.o.v. een referentie
(default: `HEAD`, dus jouw lokale wijzigingen t.o.v. de laatste commit),
inclusief nieuwe (nog niet getrackte) bestanden.

**Welke basis?**

| Optie | Vergelijkt met | Wanneer |
| --- | --- | --- |
| (geen) | `HEAD` | Lokale, nog niet gecommitte edits |
| `--since-development` / `--since-dev` | `development` (of `origin/development`) | Feature-branch die op `development` landt |
| `--since-main` | `main` (of `origin/main`) | Alles t.o.v. productie vóór merge naar `main` |

Op de branch `development` zelf is `--since-development` ongeveer hetzelfde
als `HEAD` (zelfde tip). Op een feature-branch is het wél smal: alleen jouw
delta t.o.v. `development`. `--since-main` kan dan juist **te breed** zijn
(alles wat al op `development` staat maar nog niet op `main`). Eerst altijd
`--dry-run`. Ontbreekt de gekozen tak lokaal én als `origin/…`, dan stopt
het commando met een fout.

Alleen **productbronnen** tellen mee:

| Gewijzigd bestand | Wat er gebeurt |
| --- | --- |
| Catalogus-`.mvsa` (geen import-`.mscz.mvsa`) | `products` op dat bestand met kinds `mvsa,audio,lyrics` |
| Catalogus-`.vsa` | kinds `vsa,audio,lyrics` |
| Basispartituur-`.mscz` | kinds `mscz,audio,lyrics` |
| Import-`.mscz.mvsa` | kind `import` |
| `.tekstblad.md` | kind `tekstblad` |
| Koormap-`index.md` onder `content-source\koormappen\` | [pdf](../pdf/) voor die pagina (`index.md.pdf`) |

Afgeleiden (`.mxl`, `.svg`, `.mp3`, `.lyrics.txt`, `products-meta.json`,
enz.) en andere Markdown worden **overgeslagen**. Zo blijven de
geschreven bestanden — en dus je volgende commit — klein.

**Condities:** alleen **missing** en **stale** (ontbreekt of
herkomststempel past niet). **Invalid** (`mxl validate` over de boom)
draait hier bewust niet mee. Heb je juist contractfouten te herstellen:
gebruik [products](../products/) met `--only-invalid` op een smal pad.

Na een geslaagde run (niet bij `--dry-run`), en alleen als er minstens
één productbron is afgehandeld: zoekindex en Coria-fingerprints **één
keer** aan het eind. Koormap-pdf alleen telt daar niet voor mee.

`--force` gaat door naar de onderliggende aanroepen. Bij een lege run
t.o.v. `HEAD` (alles al gecommit) geeft het commando tips voor
`--since-development` en `--since-main`.

# EXAMPLES

```cmd
REM Eerst kijken wat zou draaien (schrijft niets)
scripts\products-changed.cmd --dry-run

REM Alleen voor jouw huidige wijzigingen t.o.v. HEAD
scripts\products-changed.cmd

REM Feature-branch t.o.v. development (eerst dry-run)
scripts\products-changed.cmd --since-development --dry-run
scripts\products-changed.cmd --since-dev

REM Alles t.o.v. productie-main (vaak breder; eerst dry-run)
scripts\products-changed.cmd --since-main --dry-run
```

# WHEN

Na het wijzigen van één of enkele catalogusbronnen of koormap-pagina’s,
vóór je commit — wanneer een volle `products` of `all-products` te breed
(en te langzaam) is. Na commits op een feature-branch: meestal
`--since-development`; pas `--since-main` als je echt t.o.v. productie
wilt. Niet als vervanging van `check`, en niet als je bewust de hele boom
of alleen contract-ongeldige MXL’s wilt aanpakken.

# SEE ALSO

- [products](../products/)
- [all-products](../all-products/)
- [pdf](../pdf/)
- [check](../check/)
- [Publicatiecontrole](../../start/publicatiecontrole/)
