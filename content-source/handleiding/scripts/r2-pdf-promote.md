---
title: "r2-pdf-promote"
linkTitle: "r2-pdf-promote"
weight: 54
---

# NAME

`scripts\r2-pdf-promote.cmd` — R2 `development/` naar `production/`

# SYNOPSIS

```cmd
scripts\r2-pdf-promote.cmd [--dry-run]
```

# DESCRIPTION

Leest alle blad-PDF’s onder R2 `development/`, schrijft ze naar hetzelfde
relatieve pad onder `production/` (met `sha256`-metadata), wist daarna
`development/`, en maakt `data\pdf-r2-development.json` leeg.

Dit hoort **na een merge van `development` naar `main`**, zodat preview-
overrides niet blijven hangen en main alleen `production/` gebruikt.

Laadt `scripts\r2-env.cmd` / `.ps1`. Commit het lege manifest mee.

# EXAMPLES

```cmd
scripts\r2-pdf-promote.cmd --dry-run
scripts\r2-pdf-promote.cmd
```

# SEE ALSO

[r2-pdf-upload](../r2-pdf-upload/) ·
[Blad-PDF op R2](../../publiceren/blad-pdf-op-r2/)
