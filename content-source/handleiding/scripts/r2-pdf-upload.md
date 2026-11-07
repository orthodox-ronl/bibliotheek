---
title: "r2-pdf-upload"
linkTitle: "r2-pdf-upload"
weight: 53
---

# NAME

`scripts\r2-pdf-upload.cmd` / `scripts\r2-pdf-upload.ps1` — blad-PDF’s
naar Cloudflare R2 zetten (downloadmagazijn voor de site)

# SYNOPSIS

```cmd
scripts\r2-pdf-upload.cmd --env production|preview [--dry-run] [pad ...]
scripts\r2-pdf-upload.cmd --list-buckets
```

```powershell
.\scripts\r2-pdf-upload.ps1 --env preview
.\scripts\r2-pdf-upload.ps1 --env production
```

# DESCRIPTION

Zet de PDF achter het **download-icoon** (`index.md.pdf` en eventuele
`index.md.translit-*.pdf`) in Cloudflare R2. Op de gepubliceerde site
wijst die knop naar R2; productie en preview hebben **aparte mappen**
(`production/…` en `preview/…`), zodat die omgevingen elkaar niet
raken.

Het objectpad in R2 volgt de map onder `content-source`. Voorbeeld:
`preview/catalogus/…/uitvoeringsvorm/index.md.pdf`.

Zonder pad: alle blad-PDF’s onder `content-source`. Met een map of
bestand: alleen die selectie. `--dry-run` toont alleen de sleutels; dan
zijn geen credentials nodig.

**Credentials:** vul eenmalig `scripts\r2-env.cmd` of
`scripts\r2-env.ps1` in (sjabloon: `r2-env.*.example`; die bestanden
staan in `.gitignore`). Dit upload-commando laadt die env **zelf** vóór
het schrijven naar Cloudflare. Deze bucket gebruikt jurisdiction **EU**
(`R2_JURISDICTION=eu` in r2-env).

Eerst lokaal de PDF maken met [pdf](../pdf/), daarna uploaden. Lokaal
`serve` blijft de PDF van schijf gebruiken; alleen de GitHub
Pages-build wijst downloads naar R2.

Plan, limieten en terugkeerpad:
[docs/plans/pdf-r2.md](https://github.com/orthodox-ronl/bibliotheek/blob/development/docs/plans/pdf-r2.md).

Zeldzame problemen (token kwijt, verlopen, Access Denied, verkeerd
Account ID, EU-endpoint, publieke URL stuk): zie
[Blad-PDF op R2 — Zeldzame situaties](../../publiceren/blad-pdf-op-r2/#zeldzame-situaties-wat-te-doen).

# EXAMPLES

```cmd
scripts\r2-pdf-upload.cmd --list-buckets
scripts\r2-pdf-upload.cmd --env preview --dry-run catalogus\alleluia
scripts\r2-pdf-upload.cmd --env preview
scripts\r2-pdf-upload.cmd --env production
```

# DIAGNOSTICS

| Symptoom | Eerste stap |
| --- | --- |
| Access Denied | Nieuw R2 API-token (Read & Write); `r2-env` bijwerken |
| NoSuchBucket / 404 | Account ID, `R2_JURISDICTION=eu`, exacte bucketnaam |
| Geen credentials | `r2-env.cmd` / `.ps1` invullen (niet de `.example`) |
| Bucket wel/niet zichtbaar | `--list-buckets` |

Uitgebreid: [Blad-PDF op R2](../../publiceren/blad-pdf-op-r2/).

# SEE ALSO

[pdf](../pdf/) · [Publiceren: blad-PDF op R2](../../publiceren/blad-pdf-op-r2/)
