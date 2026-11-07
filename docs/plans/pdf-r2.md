# Plan: blad-PDF’s op Cloudflare R2

Status: **fase 2 — dual mode**. CI bouwt met R2-download-URL’s
(`hugo.pdf-assets.*.toml`); blad-PDF’s worden genegeerd bij de Hugo-build
én uit de publishmap gehouden, maar blijven dual mode nog in git. Lokaal
`serve`/`build` blijft standaard **zonder** R2. Terugdraaien: overlays uit
CI + tag `pre-r2-pdfs`.

**CI-list tegen dikke sync/timeout:** preview- en branch-deploys gebruiken
`keep_files=false` (subdirectory wordt schoon vervangen — geen oude PDF’s
meer op `gh-pages/preview/`). Productie-root houdt `keep_files=true` zodat
`preview/` en branch-mappen niet weggevaagd worden.

Gerelateerd: downloadknop = blad-PDF
([schermpartituur.md](../specs/schermpartituur.md) §1);
bouw lokaal met [`scripts/pdf.cmd`](../../scripts/pdf.cmd).

---

## Wat we willen

| Onderdeel | Keuze |
| --- | --- |
| Welke bestanden | Blad-PDF’s: `index.md.pdf` en `index.md.translit-*.pdf` |
| Opslag | Cloudflare R2, **één** account, **één** bucket |
| Productie vs preview | **Altijd aparte mappen** `production/…` en `preview/…` |
| Site | GitHub Pages blijft HTML; downloadknop wijst naar R2 als de schakelaar aan staat |
| Terug naar nu | Schakelaar uit + PDF’s uit tag `pre-r2-pdfs` (of opnieuw `pdf.cmd`) |

---

## Pad in de bucket

Object-sleutel = `{omgeving}/{pad-onder-content-source}/{bestandsnaam}`

Voorbeelden:

- `production/catalogus/…/uitvoeringsvorm/index.md.pdf`
- `preview/koormappen/hemelum/…/index.md.translit-nls.pdf`

Branch-previews gebruiken dezelfde **`preview/`**-map als development
(niet-productie). Productie (`main`) alleen `production/`.

---

## Gratis limieten (R2, peildatum docs Cloudflare)

- 10 GB opslag / maand gratis; daarna ~$0,015 per GB
- Uploads/wijzigingen: 1 miljoen / maand gratis
- Downloads: 10 miljoen / maand gratis
- Verkeer naar internet (egress): **altijd gratis**
- Betaalmethode nodig om R2 te activeren; onder de limiet blijf je $0

Met volle productie- **én** preview-spiegel (~2×): gratis tot grofweg
4–5× huidige PDF-omvang; bij ~10× nog centen/dimes, geen GitHub-muur.

---

## Jij: Cloudflare eenmalig (fase 1)

1. Account: [https://dash.cloudflare.com/sign-up](https://dash.cloudflare.com/sign-up)
2. Billing → betaalmethode toevoegen.
3. **Storage & databases → R2 → Overview** → R2-abonnement afronden (gratis laag).
4. Bucket aanmaken, bijvoorbeeld `orthodox-ronl-bibliotheek-pdf`.
5. Publieke toegang: voor de proef mag `r2.dev`; voor productie later een
   eigen subdomein (niet blijvend op `r2.dev` leunen).
6. Publieke basis-URL (proef, `r2.dev`):
   `https://pub-16acc8d1bd9b47b684ae5c7aa3215f1d.r2.dev/`
   (staat in de overlays `hugo.pdf-assets.*.toml`). Voor productie later
   liever een eigen subdomein i.p.v. blijvend `r2.dev`.

**S3-endpoint:** deze bucket staat in jurisdiction **EU**. Uploads moeten
naar `https://<ACCOUNT_ID>.eu.r2.cloudflarestorage.com` (niet het
standaard-endpoint zonder `.eu.`). In PowerShell:

```powershell
$env:R2_ENDPOINT = "https://$($env:R2_ACCOUNT_ID).eu.r2.cloudflarestorage.com"
```

Diagnose: `python scripts\r2_pdf_upload.py --list-buckets`

**Credentials lokaal** (niet in git):

1. Kopieer `scripts/r2-env.ps1.example` → `scripts/r2-env.ps1` (of `.cmd`),
   vul Account ID / keys / bucket in. Die bestanden staan in `.gitignore`.
2. Scripts die naar Cloudflare **schrijven** laden die env zelf:
   - `scripts\r2-pdf-upload.cmd` → `call r2-env.cmd` eerst
   - `scripts\r2-pdf-upload.ps1` → dot-source `r2-env.ps1` eerst
   - `r2_pdf_upload.py` laadt `r2-env.cmd` / `.ps1` als vars nog ontbreken

**Bulk-upload:**

```powershell
.\scripts\r2-pdf-upload.ps1 --env preview
.\scripts\r2-pdf-upload.ps1 --env production
```

Of: `scripts\r2-pdf-upload.cmd --env preview` (enz.).

Eerst preview, dan production. Duurt even (~1 GB per omgeving).
Daarna pas pushen van de CI-wijziging, anders ontbreken downloads.

---

## Repo-schakelaar (omkeerbaar)

In [`hugo.toml`](../../hugo.toml):

- `params.pdfAssets.enabled = false` → **huidige situatie** (relatieve PDF op de site).
- `enabled = true` + gevulde `base` + `env` → download-URL’s naar R2.

CI/lokaal met overlay:

```cmd
hugo --config hugo.toml,hugo.pdf-assets.production.toml …
hugo --config hugo.toml,hugo.pdf-assets.preview.toml …
```

---

## Terugkeerpad

1. Tag/branch **`pre-r2-pdfs`**: moment met alle blad-PDF’s nog in git.
2. Schakelaar uit → downloads weer vanaf de site.
3. PDF’s terug uit die tag (of opnieuw genereren met `pdf.cmd` + committen).
4. R2-upload stoppen; bucket mag leeg of blijven.
5. **Git-geschiedenis herschrijven** doen we **niet** tot jij expliciet OK
   geeft dat R2 bevalt.

---

## Fasen

| Fase | Inhoud |
| --- | --- |
| 1 | Account/bucket (jij); schakelaar + padschema + upload-commando (repo); tag `pre-r2-pdfs` |
| 2 | Uploads vullen; CI/download-URL’s aan; dual mode (PDF nog in git + op R2) |
| 3 | Korte beheerder-handleiding |
| 4 | Pas na jouw OK: PDF’s uit tracking / eventueel history-opschoning |
