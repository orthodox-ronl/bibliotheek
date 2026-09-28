---
title: "check"
linkTitle: "check"
weight: 20
---

# NAME

`scripts\check.cmd` — controleren of de repository klaar is om te delen

# SYNOPSIS

```cmd
check
```

Of: `scripts\check.cmd` vanuit de repo-root.

# DESCRIPTION

`check` is de preflight voor deze repo (CI-spiegel):

1. `validate` — `vsa validate` op `content-source\bibliotheek` (en
   `mvsa validate` als daar `.mvsa`-bestanden staan)
2. Coria-fingerprints (`python scripts\fingerprint_coria_mxl.py`)
3. Hugo-build naar `generated\site`

Productpipelines (sibling PDF/MSCZ, freshness-gates) horen hier nog niet
bij; die komen later als aparte `check_*`-stappen in deze repo.

# EXAMPLES

```cmd
cd /d C:\Git\orthodox-ronl\bibliotheek
check
```

# WHEN

Vóór je commit of push. Tussendoor alleen markdown bekijken: `serve` is
genoeg (die runt fingerprints + Hugo-server, zonder validate).

# SEE ALSO

- [validate](../validate/)
- [serve](../serve/)
- [build](../build/)
- [Wat heb je nodig](/handleiding/start/wat-heb-je-nodig/)
- [Status en check](/handleiding/publiceren/2-status-en-check/)
