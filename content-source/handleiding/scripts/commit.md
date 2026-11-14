---
title: "commit"
linkTitle: "commit"
weight: 106
---

# NAME

`scripts\commit.cmd` — commit alleen gewijzigde bronbestanden onder
catalogus en koormappen (geen afgeleiden)

# SYNOPSIS

```cmd
scripts\commit.cmd [--vsa] [--mvsa] [--mscz] [--md] [--tekstblad | --all]
                   [-m "bericht"] [--dry-run] [--base REF]
```

# DESCRIPTION

Lost het probleem op dat een gewone `git add` op catalogus of koormappen
meteen alle afgeleiden meeneemt (SVG, MXL, mp3, Score-IR, …). Die
bestanden zijn groot; je wilt ze vaak nog lokaal houden terwijl je
tussendoor alleen de bronnen als WIP vastlegt. Dit commando zoekt
**gewijzigde bronnen** onder `content-source\catalogus\` en
`content-source\koormappen\` (t.o.v. `HEAD`, plus nieuwe bestanden) en
commit **alleen die paden**. Afgeleiden blijven op schijf staan als
ongecommitte wijziging; je hoeft ze niet te wissen en later opnieuw te
genereren.

**Wat telt als bron?**

| Soort | Bestanden |
| ----- | --------- |
| Markdown | `index.md`, `_index.md`, overige `.md` |
| Tekstblad | `{stam}.tekstblad.md` |
| VSA | kale `{stam}.vsa` en `{stam}.syl.vsa` |
| MVSA | kale `{stam}.mvsa` (niet `.vsa.mvsa` / `.mscz.mvsa`) |
| MSCZ | basis-`{stam}.mscz` en `{stam}.print.mscz` |

Alles met een tweede extensie na `.vsa` / `.mvsa` / `.mscz` (bijvoorbeeld
`.vsa.svg`, `.mvsa.mxl`, `.mscz-1.svg`) blijft buiten de commit.
`index.md.pdf` staat al in `.gitignore`.

**Vlags:** zonder vlag gaan alle bronsoorten mee. Met één of meer
`--vsa` / `--mvsa` / `--mscz` / `--md` / `--tekstblad` alleen die
soort(en). Combineerbaar: `commit --mscz --mvsa` commit alleen die
gewijzigde partituurbronnen.

**`--all`:** neemt gewijzigde bestanden in de **hele repo** mee: catalogus-
en koormapbronnen plus bijvoorbeeld scripts, layouts en handleiding.
Nog steeds **niet:** notatie-afgeleiden (SVG, MXL, mp3, …) en JSON die
uit producten of `check` komen (`*.products-meta.json`,
`data\*-status.json`, `data\check-fixlist.json`, `static\zoek\index.json`,
…). Niet combineren met de bronsoort-vlags.

**Bericht:** `-m "…"` zet het commitbericht. Zonder `-m` opent git de
editor (net als bij een gewone `git commit`).

**Dry-run:** `--dry-run` toont welke paden mee zouden gaan en schrijft
niets.

Andere al gestagede bestanden buiten deze selectie komen **niet** in
deze commit (git commit met padlijst).

**Let op publicatiecontrole:** wijzig je een `.vsa`, `.mvsa` of `.mscz`
en commit je de siblings nog niet, dan kan `check` / CI rood worden tot
een latere commit de bijgewerkte producten bevat. Commits die alleen
Markdown of koormaptekst vastleggen blijven daarvoor veilig. Producten
bijwerken: [products-changed](../products-changed/).

# EXAMPLES

```cmd
REM Eerst kijken
scripts\commit.cmd --dry-run

REM Alle gewijzigde bronnen
scripts\commit.cmd -m "wip: catalogus en koormap"

REM Alleen VSA-bronnen
scripts\commit.cmd --vsa -m "wip: vsa"

REM Alleen .mscz en .mvsa
scripts\commit.cmd --mscz --mvsa -m "wip: partituur"

REM Alleen Markdown (inclusief tekstblad)
scripts\commit.cmd --md -m "wip: teksten"

REM Hele repo minus afgeleiden/product-JSON
scripts\commit.cmd --all -m "wip: scripts en bronnen"
```

# WHEN

Tussendoor WIP vastleggen terwijl afgeleiden lokaal (of verouderd)
blijven staan. Niet als vervanging van een complete
bron+product-commit vóór merge naar een branch waar `check` groen moet
zijn.

# SEE ALSO

- [stage](../stage/) —zelfde selectie, alleen `git add`
- [products-changed](../products-changed/)
- [products](../products/)
- [Publicatiecontrole](../../start/publicatiecontrole/)
- [check](../check/)
