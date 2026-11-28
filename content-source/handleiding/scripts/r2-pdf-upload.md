---
title: "r2-pdf-upload"
linkTitle: "r2-pdf-upload"
weight: 53
---

# NAME

`scripts\r2-pdf-upload.cmd` — blad-PDF’s naar Cloudflare R2

# SYNOPSIS

```cmd
scripts\r2-pdf-upload.cmd [--env production|development] [--dry-run] [pad ...]
scripts\r2-pdf-upload.cmd --list-buckets
scripts\r2-pdf-upload.cmd --purge-prefix development [--apply-purge]
scripts\r2-pdf-upload.cmd --restamp-metadata [--only-missing-sha] [--dry-run]
scripts\r2-pdf-upload.cmd --write-manifest-from-r2
```

# DESCRIPTION

Zet `index.md.pdf` / translit-PDF’s in R2. Metadata `sha256` gaat mee.

| `--env` | Gedrag |
| ------- | ------ |
| `production` (default) | Upload naar `production/…` |
| `development` | Alleen PDF’s die afwijken van (of ontbreken op) `production/` → `development/…`; werkt `data\pdf-r2-development.json` bij |

`--env preview` wordt geweigerd (gebruik `development`).

Laadt `scripts\r2-env.cmd` / `.ps1` automatisch. EU:
`R2_JURISDICTION=eu`.

GitHub uploadt na elke publicatie van `development` en `main` zelf; zie
[Blad-PDF op R2](../../publiceren/blad-pdf-op-r2/).

# EXAMPLES

```cmd
scripts\r2-pdf-upload.cmd --dry-run catalogus\alleluia
scripts\r2-pdf-upload.cmd --env development
scripts\r2-pdf-upload.cmd --env production
scripts\r2-pdf-upload.cmd --write-manifest-from-r2
```

# SEE ALSO

[pdf](../pdf/) · [r2-pdf-promote](../r2-pdf-promote/) ·
[r2-pdf-opschonen](../r2-pdf-opschonen/) ·
[Blad-PDF op R2](../../publiceren/blad-pdf-op-r2/)
