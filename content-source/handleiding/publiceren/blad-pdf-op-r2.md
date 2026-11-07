---
title: "Blad-PDF op R2"
linkTitle: "Blad-PDF op R2"
weight: 50
---

# Blad-PDF op Cloudflare R2

Stabiele blad-PDF’s (`index.md.pdf` en translit) staan op **Cloudflare R2**
in één map: `production/…`. De downloadknop gebruikt eerst een **lokale**
PDF (als die in de build zit — typisch WIP), en anders R2.

## Wat jij doet

1. Blad wijzigen → `scripts\pdf.cmd` (PDF staat lokaal).
2. Testen op preview: de PDF mag op `development`/feature **in git** zolang
   je eraan rommelt.
3. Stabiel: uploaden en opschonen:

```cmd
scripts\r2-pdf-upload.cmd
scripts\r2-pdf-opschonen.cmd --apply
```

4. Op **`main`** horen geen blad-PDF’s in git (CI weigert dat). Lokaal op
   main ook leeg houden via opschonen.

Credentials: `scripts\r2-env.cmd` of `r2-env.ps1` (niet in git). Zie
[r2-pdf-upload](../../scripts/r2-pdf-upload/) en
[r2-pdf-opschonen](../../scripts/r2-pdf-opschonen/).

## Wanneer wat

| Situatie | Gedrag |
| --- | --- |
| PDF lokaal aanwezig (WIP) | Download = bestand op de site |
| Geen lokale PDF | Download = R2 `production/…` |
| Lokale PDF = zelfde hash als R2 | `r2-pdf-opschonen --apply` wist lokaal |

## Wat je moet bewaren (niet in git)

In `scripts\r2-env.cmd` of `scripts\r2-env.ps1`:

| Variabele | Wat het is |
| --- | --- |
| `R2_ACCOUNT_ID` | Account ID in het dashboard — **niet** `pub-…` uit de publieke URL |
| `R2_ACCESS_KEY_ID` / `R2_SECRET_ACCESS_KEY` | R2 API-token (S3); secret maar één keer zichtbaar |
| `R2_BUCKET` | Exacte bucketnaam |
| `R2_JURISDICTION` | Bij ons: `eu` |

## Zeldzame situaties

### Token of secret kwijt / Access Denied

1. R2 → **Manage R2 API Tokens** → nieuw token (Object Read & Write op de
   bucket); oude intrekken.
2. Waarden in `r2-env` zetten.
3. Test: `scripts\r2-pdf-upload.cmd --list-buckets`.

### “Bucket bestaat niet”

Account ID, `R2_JURISDICTION=eu`, exacte bucketnaam. Diagnose:
`--list-buckets`.

### Oude R2-map `preview/` nog vol

Die map gebruiken we niet meer. Eenmalig legen:

```cmd
scripts\r2-pdf-upload.cmd --purge-prefix preview
scripts\r2-pdf-upload.cmd --purge-prefix preview --apply-purge
```

### SHA-256 ontbreekt op R2 (opschonen kan niet vergelijken)

Normale upload zet de vingerafdruk mee. Ontbreekt die op bestaande
objecten (bijv. na de eerste migratie), dan:

```cmd
scripts\r2-pdf-upload.cmd --restamp-metadata --only-missing-sha
```

### Publieke URL 404

Bestand geüpload onder `production/…`? Public Development URL nog aan?
Basis-URL in `hugo.toml` / overlays nog juist?

Meer detail: [docs/plans/pdf-r2.md](https://github.com/orthodox-ronl/bibliotheek/blob/development/docs/plans/pdf-r2.md).

## Terug naar “alles via GitHub”

1. Tag **`pre-r2-pdfs`** of PDF’s opnieuw committen.
2. R2-fallback in Hugo uitzetten / overlays aanpassen.
3. History opschonen alleen na jouw expliciete OK.

{{< navbuttons "pdf|/handleiding/scripts/pdf/" "r2-pdf-upload|/handleiding/scripts/r2-pdf-upload/" >}}
