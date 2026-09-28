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

`check` is de preflight voor deze repo (fase 1, Hugo-only):

1. Coria-fingerprints (`python scripts\fingerprint_coria_mxl.py`)
2. Hugo-build naar `generated\site`

Er is **geen** VSA-validate of `vsa build-markdown` in deze keten. Die
stappen komen later via de gepubliceerde `vsa`-CLI.

# EXAMPLES

```cmd
cd /d C:\Git\orthodox-ronl\bibliotheek
check
```

# WHEN

Vóór je commit of push. Tussendoor alleen markdown bekijken: `serve` is
genoeg (die runt fingerprints + Hugo-server).

# SEE ALSO

- [serve](../serve/)
- [build](../build/)
- [Wat heb je nodig](/handleiding/start/wat-heb-je-nodig/)
- [Status en check](/handleiding/publiceren/2-status-en-check/)
