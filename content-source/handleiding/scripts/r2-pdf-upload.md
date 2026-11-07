---
title: "r2-pdf-upload"
linkTitle: "r2-pdf-upload"
weight: 53
---

# NAME

`scripts\r2-pdf-upload.cmd` — blad-PDF’s naar Cloudflare R2 `production/`

# SYNOPSIS

```cmd
scripts\r2-pdf-upload.cmd [--dry-run] [pad ...]
scripts\r2-pdf-upload.cmd --list-buckets
scripts\r2-pdf-upload.cmd --purge-prefix preview [--apply-purge]
scripts\r2-pdf-upload.cmd --restamp-metadata [--only-missing-sha] [--dry-run]
```

# DESCRIPTION

Zet `index.md.pdf` / translit-PDF’s in R2 onder
`production/{pad-onder-content-source}/…`. Zet metadata `sha256` voor
[r2-pdf-opschonen](../r2-pdf-opschonen/). Alleen **production/**;
`--env preview` wordt geweigerd.

Laadt `scripts\r2-env.cmd` / `.ps1` automatisch. EU:
`R2_JURISDICTION=eu`.

`--purge-prefix preview --apply-purge` wist de afgeschafte preview-map
op R2 (eerst zonder `--apply-purge` om te tellen).

`--restamp-metadata` zet of vernieuwt de `sha256`-metadata op alle
PDF’s die al onder `production/` staan (download + herschrijven). Nodig
als objecten zonder vingerafdruk zijn geüpload, of na een eenmalige
migratie. Met `--only-missing-sha` sla je objecten over die al
`sha256` hebben.

# EXAMPLES

```cmd
scripts\r2-pdf-upload.cmd --dry-run catalogus\alleluia
scripts\r2-pdf-upload.cmd
scripts\r2-pdf-upload.cmd --purge-prefix preview --apply-purge
scripts\r2-pdf-upload.cmd --restamp-metadata --only-missing-sha
```

# SEE ALSO

[pdf](../pdf/) · [r2-pdf-opschonen](../r2-pdf-opschonen/) ·
[Blad-PDF op R2](../../publiceren/blad-pdf-op-r2/)
