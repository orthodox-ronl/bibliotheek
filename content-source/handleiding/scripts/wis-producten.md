---
title: "wis-producten"
linkTitle: "wis-producten"
weight: 176
---

# NAME

`wis-producten` — alle gegenereerde bestanden uit catalogus en koormappen
melden of verwijderen, voor een schone start

# SYNOPSIS

```cmd
scripts\wis-producten.cmd [map|bestand ...] [--apply]
```

Met `.\scripts` op PATH: `wis-producten …`. Korte hulp:
`h wis-producten` of `wis-producten -h`.

# DESCRIPTION

Wist alles wat [products](../products/) en [pdf](../pdf/) opnieuw kunnen
maken. Daarna genereer je alles vers.

**Wat gewist wordt** (de naam heeft een bronextensie en daarachter nog een
extensie; dezelfde definitie als bij [seed-repo](../seed-repo/)):

- producten naast een bron: `{stam}.vsa.svg`, `{stam}.vsa.mp3`,
  `{stam}.vsa.mxl`, `{stam}.vsa.mscz`, `{stam}.vsa.mvsa`,
  `{stam}.mvsa.mxl`, `{stam}.mvsa.score-ir.json`, `{stam}.mscz.svg`, …
- bijbehorende `*.products-meta.json` en `*.lyrics.txt`
- blad-PDF’s: `index.md.pdf` en `index.md.translit-*.pdf` (ook als git ze
  negeert)

**Wat altijd blijft staan:**

- bronnen: `.vsa`, `.mvsa`, `.mscz`, `.md`, losse `.svg` en `.mxl`
- `{stam}.print.mscz` en `{stam}.mscz.mvsa` (import-bewerkvorm)
- de map `formules`
- ‘handmatige’ mappen: een `index.md` met `manueel: true` (of
  `manual: true`), en mappen met een `*.tekstblad.md` (tekstbladen, zoals
  `dialoog-met-diaken`). Die worden met reden in de uitvoer genoemd.

Standaardmappen: `content-source\catalogus` én `content-source\koormappen`.
Zonder `--apply` alleen tonen (dry-run); met `--apply` echt wissen.

# EXAMPLES

```cmd
scripts\wis-producten.cmd
scripts\wis-producten.cmd --apply
scripts\wis-producten.cmd content-source\catalogus\kondak --apply
```

# WHEN

Voor een volledige verversing: eerst `wis-producten --apply`, daarna
`products` en `pdf`. Bestanden die git volgt, kun je terughalen met
`git checkout`; niet-gevolgde (zoals `index.md.pdf`) komen alleen terug door
opnieuw te genereren.

Een handmatige map wil je niet laten wissen? Zet `manueel: true` in de
`index.md` van die map.

# SEE ALSO

[products](../products/), [pdf](../pdf/),
[cleanup-chained-products](../cleanup-chained-products/),
[Publicatiecontrole](../../start/publicatiecontrole/)
