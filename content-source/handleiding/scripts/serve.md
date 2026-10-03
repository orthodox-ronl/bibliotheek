---
title: "serve"
linkTitle: "serve"
weight: 40
---

# NAME

`scripts\serve.cmd` — lokale website-preview in de browser

# SYNOPSIS

```cmd
serve
```

# DESCRIPTION

Maakt Coria-fingerprints, schrijft de bouwtijd naar `data\build.yaml`
(footer «Gegenereerd» op de homepage), en start de Hugo-development
server. Open daarna **http://127.0.0.1:18732/**. Niet poort **1313**
(lokaal gereserveerd), niet **18731** (VSA-demo).

# EXAMPLES

```cmd
cd /d C:\Git\orthodox-ronl\bibliotheek
serve
```

# WHEN

Als je in de browser wilt zien hoe bibliotheek, koormappen en handleiding
eruitzien tijdens beheerwerk.

# SEE ALSO

- [check](../check/)
- [build](../build/)
