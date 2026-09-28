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

Zelfde keten als `check`: Coria-fingerprints + Hugo-build naar
`generated\site`. Commit `generated\` en `static\mxl\` niet (gitignore).

# WHEN

Als je het site-artifact nodig hebt zonder een preview-server te starten.

# SEE ALSO

- [check](../check/)
- [serve](../serve/)
