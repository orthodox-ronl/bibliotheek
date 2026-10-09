---
title: "build"
linkTitle: "build"
weight: 30
---

# NAME

`scripts\build.cmd` — hele website bouwen naar `generated\site`

# SYNOPSIS

```cmd
build
```

# DESCRIPTION

Maakt Coria-fingerprints, schrijft de bouwtijd naar `data\build.yaml`
(footer «Gegenereerd» op de homepage; niet committen), en bouwt de site
naar `generated\site`. Anders dan `check` draait `build` **geen**
`vsa validate`. Commit `generated\` en `static\mxl\` niet (gitignore).

# WHEN

Als je het site-artifact nodig hebt zonder een preview-server te starten.

# SEE ALSO

- [check](../check/)
- [serve](../serve/)
