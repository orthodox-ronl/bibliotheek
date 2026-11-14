---
title: "stage"
linkTitle: "stage"
weight: 107
---

# NAME

`scripts\stage.cmd` — stage alleen gewijzigde bronbestanden onder
catalogus en koormappen (geen afgeleiden, geen commit)

# SYNOPSIS

```cmd
scripts\stage.cmd [--vsa] [--mvsa] [--mscz] [--md] [--tekstblad | --all]
                  [--dry-run] [--base REF]
```

# DESCRIPTION

Zelfde bronselectie als [commit](../commit/), maar doet alleen `git add`
op die paden. Afgeleiden (SVG, MXL, mp3, Score-IR, …) blijven unstaged
op schijf. Er is geen `-m`: je commit daarna zelf (`git commit` of
[commit](../commit/)).

**Wat telt als bron?** Zie de tabel bij [commit](../commit/).

**Vlags:** zonder vlag gaan alle bronsoorten mee. Met één of meer
`--vsa` / `--mvsa` / `--mscz` / `--md` / `--tekstblad` alleen die
soort(en). **`--all`:** hele repo minus afgeleiden en product-/check-JSON
(zelfde regel als bij [commit](../commit/)).

**Dry-run:** `--dry-run` toont welke paden gestaged zouden worden en
schrijft niets.

# EXAMPLES

```cmd
REM Eerst kijken
scripts\stage.cmd --dry-run

REM Alle gewijzigde bronnen stagen
scripts\stage.cmd

REM Alleen VSA-bronnen
scripts\stage.cmd --vsa

REM Alleen .mscz en .mvsa
scripts\stage.cmd --mscz --mvsa

REM Hele repo minus afgeleiden/product-JSON
scripts\stage.cmd --all
```

# WHEN

Wanneer je bronnen wilt klaarzetten in de index (bijvoorbeeld om daarna
een commitbericht in de editor te schrijven, of om eerst `git status` /
`git diff --cached` te bekijken) zonder meteen te committen. Voor een
directe commit met bericht: [commit](../commit/).

# SEE ALSO

- [commit](../commit/)
- [products-changed](../products-changed/)
- [Publicatiecontrole](../../start/publicatiecontrole/)
