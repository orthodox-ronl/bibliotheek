---
title: "validate"
linkTitle: "validate"
weight: 15
---

# NAME

`scripts\validate.cmd` — controleer of bibliotheek-`.vsa` (en eventueel
`.mvsa`) geldig is volgens de `vsa`-/`mvsa`-CLI

# SYNOPSIS

```cmd
validate
validate content-source\bibliotheek\tropaar
```

Of: `scripts\validate.cmd` vanuit de repo-root. Zonder argument valideert
het script de map `content-source\bibliotheek`.

# DESCRIPTION

Zet eerst `vsa-tool` klaar (`scripts\_ensure.cmd --vsa-tool`) en roept
daarna de gepubliceerde CLI aan:

1. `vsa validate` op het gekozen pad (standaard de hele bibliotheek-map)
2. Als er onder dat pad minstens één `.mvsa` staat: ook `mvsa validate`

Het script kopieert geen validatielogica uit VSA-tooling; het geeft alleen
het pad door. Ruwe dumps onder `content-source\input` horen niet bij deze
preflight — die map is geen publicatiebron.

# EXAMPLES

```cmd
cd /d C:\Git\orthodox-ronl\bibliotheek
validate
```

# WHEN

Los vóór je een `.vsa` commit, of via `check` (die `validate` eerst
aanroept). Op GitHub Actions draait dezelfde `vsa validate`-stap in de
Pages-workflow vóór de Hugo-build.

# SEE ALSO

- [check](../check/)
- [VSA schrijven](/handleiding/vsa/1-vsa-schrijven/)
- CLI: https://orthodox-ronl.github.io/VSA-tooling/reference/cli/
