# Plan: blad-PDF’s — lokaal-eerst, R2-fallback

Status: **lokaal-eerst + één R2-set (`production/`)**. Preview-map op R2
is afgeschaft. Geen history-rewrite in dit traject.

## Model

1. **Downloadknop:** staat de PDF in de site-build (lokaal/WIP) → die URL;
   anders → R2 `production/{pad-onder-content-source}/…`.
2. **R2:** alleen `production/…` (stabiele set).
3. **Git:** op `main` geen getrackte blad-PDF’s (CI-guard). Op
   `development`/feature: mag bij WIP.
4. **Opschonen:** lokale PDF met dezelfde SHA-256 als R2 → wissen
   (`r2-pdf-opschonen --apply`).

## Commando’s

| Commando | Rol |
| --- | --- |
| `scripts\pdf.cmd` | Blad-PDF lokaal maken |
| `scripts\r2-pdf-upload.cmd` | Naar R2 `production/` (+ metadata `sha256`) |
| `scripts\r2-pdf-opschonen.cmd [--apply]` | Gelijke lokale PDF’s weg |
| `r2-pdf-upload --purge-prefix preview --apply-purge` | Eenmalig oude R2-`preview/` legen |
| `r2-pdf-upload --restamp-metadata [--only-missing-sha]` | SHA-256 op bestaande R2-PDF’s (zonder lokale bestanden) |

Credentials: `scripts\r2-env.cmd` / `.ps1` (gitignore; zie `*.example`).
EU-bucket: `R2_JURISDICTION=eu`.

## Hugo / CI

| Overlay | Gedrag |
| --- | --- |
| `hugo.toml` + lokaal serve | `preferLocal=true`, R2-fallback |
| `hugo.pdf-assets.preview.toml` | WIP-PDF’s mee; rest → R2 |
| `hugo.pdf-assets.production.toml` | negeert `*.pdf` in build; downloads → R2 |

## Terugkeerpad

Tag `pre-r2-pdfs` (oude dual-mode met PDF’s in git). Of overlays uit en
PDF’s weer committen. History-opschoning alleen na expliciete OK.

## Eenmalig: R2-prefix `preview/` legen

Na omschakeling naar één set:

```powershell
.\scripts\r2-pdf-upload.ps1 --purge-prefix preview
.\scripts\r2-pdf-upload.ps1 --purge-prefix preview --apply-purge
```
