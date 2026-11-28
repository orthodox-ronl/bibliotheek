---
title: "Blad-PDF op R2"
linkTitle: "Blad-PDF op R2"
weight: 50
---

# Blad-PDF op Cloudflare R2

Stabiele blad-PDF’s (`index.md.pdf` en translit) staan op **Cloudflare R2**
onder `production/…`. Op de branch `development` gaan alleen de PDF’s die
**anders** zijn dan op productie naar `development/…` (geen dubbele
volledige set). De downloadknop gebruikt eerst een **lokale** PDF (als die
in de build zit), anders R2 (`development/` als override, anders
`production/`).

Blad-PDF’s horen **niet in git** (lokaal wel op schijf voor `serve`).

## Wat jij doet

Voor het publiceren hoef je niets met R2 te doen. Wijzig het blad, bekijk het
met `serve` en leg de bron vast op `development`. GitHub doet daarna het
volgende vanzelf:

- Na een wijziging op `development` bouwt GitHub de blad-PDF's en zet de
  gewijzigde PDF's op R2 `development/`.
- Na een samenvoeging van `development` naar `main` bouwt GitHub alle
  blad-PDF's en zet ze op R2 `production/`. Mislukt het bouwen of uploaden,
  dan verandert de echte site niet. De mislukte publicatie staat dan op
  GitHub onder het tabblad **Actions**.

GitHub gebruikt hiervoor de R2-sleutels die in de instellingen van de
repository staan (**Settings**, **Secrets and variables**, **Actions**).

De scripts [r2-pdf-upload](../../scripts/r2-pdf-upload/) en
[r2-pdf-promote](../../scripts/r2-pdf-promote/) zijn alleen nog een
noodmiddel, voor als GitHub het niet kan. Die scripts lezen de sleutels uit
`scripts\r2-env.cmd` of `r2-env.ps1` (niet in git).

## Wanneer wat

| Situatie | Gedrag |
| -------- | ------ |
| PDF lokaal aanwezig | Download = bestand op de site |
| Preview + pad in manifest | Download = R2 `development/…` |
| Anders / main-build | Download = R2 `production/…` |
| Preview-banier | Verschijnt als het manifest niet leeg is |

## Wat je moet bewaren (niet in git)

In `scripts\r2-env.cmd` of `scripts\r2-env.ps1`:

| Variabele | Wat het is |
| --------- | ---------- |
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

### Manifest klopt niet met R2

```cmd
scripts\r2-pdf-upload.cmd --write-manifest-from-r2
```

### SHA-256 ontbreekt op R2 (opschonen kan niet vergelijken)

```cmd
scripts\r2-pdf-upload.cmd --restamp-metadata --only-missing-sha
```

### Publieke URL 404

Bestand geüpload onder `production/…` of `development/…`? Public
Development URL nog aan? Basis-URL in `hugo.toml` / overlays nog juist?

Meer detail: [docs/plans/pdf-r2.md](https://github.com/orthodox-ronl/bibliotheek/blob/development/docs/plans/pdf-r2.md).

{{< navbuttons "pdf|/handleiding/scripts/pdf/" "r2-pdf-upload|/handleiding/scripts/r2-pdf-upload/" >}}
