---
title: "r2-pdf-opschonen"
linkTitle: "r2-pdf-opschonen"
weight: 54
---

# NAME

`scripts\r2-pdf-opschonen.cmd` — lokale blad-PDF’s wissen die gelijk zijn
aan R2

# SYNOPSIS

```cmd
scripts\r2-pdf-opschonen.cmd [--apply] [pad ...]
scripts\r2-pdf-opschonen.cmd --fail-if-tracked-on-main
```

# DESCRIPTION

Voor elke lokale `index.md.pdf` / translit: SHA-256 vergelijken met
R2-object `production/…` (metadata van [r2-pdf-upload](../r2-pdf-upload/)).
Bij gelijke inhoud: melden, of met `--apply` wissen (tracked → `git rm`).

Zonder `--apply` is het een dry-run. Op branch `main` controleert
`check` / CI dat er geen getrackte blad-PDF’s meer zijn
(`--fail-if-tracked-on-main`).

# EXAMPLES

```cmd
scripts\r2-pdf-opschonen.cmd
scripts\r2-pdf-opschonen.cmd --apply
```

# SEE ALSO

[r2-pdf-upload](../r2-pdf-upload/) · [Blad-PDF op R2](../../publiceren/blad-pdf-op-r2/)
