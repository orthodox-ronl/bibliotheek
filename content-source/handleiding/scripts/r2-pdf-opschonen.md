---
title: "r2-pdf-opschonen"
linkTitle: "r2-pdf-opschonen"
weight: 55
---

# NAME

`scripts\r2-pdf-opschonen.cmd` — optioneel lokale blad-PDF’s wissen

# SYNOPSIS

```cmd
scripts\r2-pdf-opschonen.cmd [--apply] [pad ...]
scripts\r2-pdf-opschonen.cmd --fail-if-tracked-on-main
```

# DESCRIPTION

Voor elke lokale `index.md.pdf` / translit: SHA-256 vergelijken met R2
`production/…`. Bij gelijke inhoud: melden, of met `--apply` wissen.

**Normale workflow bewaart lokale PDF’s** voor `serve`. Dit commando is
alleen voor schijfruimte. Op branch `main` controleert `check` / CI dat er
geen getrackte blad-PDF’s meer zijn (`--fail-if-tracked-on-main`).

Zonder `--apply` is het een dry-run.

# EXAMPLES

```cmd
scripts\r2-pdf-opschonen.cmd
scripts\r2-pdf-opschonen.cmd --apply
```

# SEE ALSO

[r2-pdf-upload](../r2-pdf-upload/) · [r2-pdf-promote](../r2-pdf-promote/) ·
[Blad-PDF op R2](../../publiceren/blad-pdf-op-r2/)
