# Plan: blad-PDF’s — lokaal + duale R2

Status: **lokaal bewaren; git negeert blad-PDF’s; `production/` = main;
`development/` = alleen de diff t.o.v. production.**

## Model

1. **Lokaal:** `scripts\pdf.cmd` / `fix --strict` maakt blad-PDF’s; die
   blijven op schijf voor `serve`. Niet in git (`.gitignore`).
2. **Downloadknop:** lokaal bestand in de build wint; anders R2.
   Op preview: als het pad in
   [`data/pdf-r2-development.json`](../../data/pdf-r2-development.json)
   staat → `development/…`, anders → `production/…`.
   Op main-build: altijd `production/…`.
3. **R2 `production/`:** volledige stabiele set (main).
4. **R2 `development/`:** alleen PDF’s waarvan de lokale SHA-256 afwijkt
   van (of ontbreekt op) `production/` — geen dubbele volledige set.
5. **Automatisch (branch `development`):** de Pages-workflow bouwt alle
   blad-PDF’s, zet de diff op `development/` (ongewijzigde worden
   overgeslagen) en schrijft het manifest voor die build; niets te
   committen. Vereist de repository-secrets `R2_ACCOUNT_ID`,
   `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET` en
   `R2_JURISDICTION`; zonder secrets gebeurt er niets. Andere branches
   uploaden niet (er is één `development/`).
6. **Automatisch (branch `main`):** de Pages-workflow bouwt alle blad-PDF’s
   uit `main` en zet ze op `production/` (ongewijzigde worden overgeslagen).
   Mislukt dat, dan verandert de echte site niet. Na de publicatie haalt
   `scripts/opruim_productie.py` verouderde bestanden van de echte site.
   Handmatig promoveren is daardoor niet meer nodig.
7. **Alleen als noodmiddel na merge naar main:** `r2-pdf-promote` kopieert `development/` →
   `production/`, wist `development/`, leegt het manifest.

Naast `index.md.pdf` en `index.md.translit-*.pdf` horen ook
`index.md.weergave-*.pdf` (keuze VSA / partituur,
[schermpartituur.md §2.1](../specs/schermpartituur.md)) bij de blad-PDF’s.

## Commando’s

| Commando | Rol |
| -------- | --- |
| `scripts\pdf.cmd` | Blad-PDF lokaal maken |
| `scripts\r2-pdf-upload.cmd --env production` | Naar R2 `production/` (+ `sha256`) |
| `scripts\r2-pdf-upload.cmd --env development` | Alleen diff → `development/` + manifest |
| `scripts\r2-pdf-promote.cmd` | Diff promoveren + `development/` legen |
| `scripts\r2-pdf-opschonen.cmd [--apply]` | Optioneel: lokale PDF wissen als gelijk aan `production/` |

Credentials: `scripts\r2-env.cmd` / `.ps1` (gitignore; zie `*.example`).
EU-bucket: `R2_JURISDICTION=eu`.

## Hugo / CI

| Overlay | Gedrag |
| ------- | ------ |
| `hugo.toml` + lokaal serve | `preferLocal=true`; overrides uit manifest |
| `hugo.pdf-assets.preview.toml` | idem + preview-banier bij niet-lege overrides |
| `hugo.pdf-assets.production.toml` | negeert `*.pdf` in build; alleen `production/` |

Op `main`: CI weigert getrackte blad-PDF’s.

## Preview-waarschuwing

Niet-leeg manifest → banier op preview: er staan N preview-PDF’s op R2
`development/`; na merge naar main horen die gepromoveerd en gewist.
