---
title: "Blad-PDF op R2"
linkTitle: "Blad-PDF op R2"
weight: 50
---

# Blad-PDF op Cloudflare R2

De dikke blad-PDF’s (`index.md.pdf` en translit-varianten) staan voor
bezoekers van de **gepubliceerde** site in Cloudflare R2, niet meer in
de GitHub Pages-map. Zo blijft de repo en de Pages-deploy lichter. Lokaal
op je pc maak en bekijk je die PDF’s nog gewoon naast de Markdown.

## Wat jij blijft doen

1. Blad maken of wijzigen (Markdown + notatie).
2. PDF vernieuwen: `scripts\pdf.cmd` (zoals nu).
3. Naar Cloudflare zetten: `scripts\r2-pdf-upload.cmd` of
   `.\scripts\r2-pdf-upload.ps1`, met `--env preview` of
   `--env production`.
4. Bronnen committen/pushen. De PDF mag dual mode nog in git staan; de
   site-download knop op Pages wijst al naar R2.

Credentials eenmalig in `scripts\r2-env.cmd` of `r2-env.ps1` (niet in
git). Het upload-script laadt die bestanden zelf. Zie
[r2-pdf-upload](../../scripts/r2-pdf-upload/).

## Productie versus preview

| Omgeving | R2-map | Site |
| --- | --- | --- |
| Productie (`main`) | `production/…` | https://orthodox-ronl.github.io/bibliotheek/ |
| Preview (`development` e.d.) | `preview/…` | …/bibliotheek/preview/ |

Upload nooit per ongeluk preview-bestanden naar `production` of
omgekeerd: de mappen zijn bewust gescheiden.

## Gratis limiet (kort)

R2: ongeveer **10 GB** opslag gratis per maand. Met productie **én**
preview vol telt de opslag ~dubbel. Downloadverkeer is gratis. Onder de
limiet betaal je niets; er staat wel een betaalmethode op het
Cloudflare-account. Detail: [pdf-r2.md](https://github.com/orthodox-ronl/bibliotheek/blob/development/docs/plans/pdf-r2.md).

## Wat je moet bewaren (niet in git)

In `scripts\r2-env.cmd` of `scripts\r2-env.ps1` (alleen op jouw pc):

| Variabele | Wat het is |
| --- | --- |
| `R2_ACCOUNT_ID` | Account ID in het Cloudflare-dashboard (rechts / in de URL). **Niet** de `pub-…`-tekst uit de publieke download-URL. |
| `R2_ACCESS_KEY_ID` | Access Key van een **R2 API-token** (S3), niet een gewone Cloudflare API-token. |
| `R2_SECRET_ACCESS_KEY` | Secret van datzelfde R2-token. Cloudflare toont die secret **maar één keer** bij aanmaken. |
| `R2_BUCKET` | Exacte bucketnaam, bij ons: `orthodox-ronl-bibliotheek-pdf`. |
| `R2_JURISDICTION` | Bij deze bucket: `eu` (European Union). Zonder dit faalt upload vaak met “bucket bestaat niet”. |

Bewaar een kopie van die waarden op een veilige plek (wachtwoordkluis).
Verlies je de secret, dan kun je die niet terugkijken in Cloudflare — je
maakt een **nieuw** token (zie hieronder).

## Zeldzame situaties: wat te doen

### Token of secret kwijt

De secret van een R2 API-token is niet opnieuw op te vragen.

1. Cloudflare → **R2** → **Manage R2 API Tokens**.
2. Oude token **revoke** / verwijderen (veiliger als hij zoekraakte).
3. **Create API token**: rechten minstens **Object Read & Write** (of
   Admin Read & Write) op bucket `orthodox-ronl-bibliotheek-pdf`.
4. Nieuwe Access Key ID + Secret meteen overnemen in
   `scripts\r2-env.cmd` / `r2-env.ps1` **en** in je kluis.
5. Test: `scripts\r2-pdf-upload.cmd --list-buckets` — je moet de
   bucketnaam zien.

### Token verlopen, ingetrokken, of “Access Denied”

Zelfde remedie als hierboven: nieuw R2 API-token, `r2-env` bijwerken,
`--list-buckets` ter controle. Controleer ook of het token nog aan
**deze** bucket hangt (niet per ongeluk een andere bucket of alleen
leesrechten).

Gebruik altijd tokens onder **R2 → Manage R2 API Tokens**. Een token
vanuit het algemene Cloudflare “API Tokens”-menu is een ander soort
sleutel en werkt niet voor dit upload-script.

### “Bucket bestaat niet” / 404 bij HeadBucket

Meestal één van deze drie:

1. **Verkeerd Account ID** — je hebt `pub-…` uit de publieke URL
   gebruikt, of het ID van een ander Cloudflare-account. Haal het
   Account ID opnieuw uit het dashboard.
2. **EU vergeten** — zet `R2_JURISDICTION=eu` (of
   `R2_ENDPOINT=https://<ACCOUNT_ID>.eu.r2.cloudflarestorage.com`).
3. **Typfout in `R2_BUCKET`** — naam moet exact kloppen, inclusief
   streepjes.

Diagnose: `scripts\r2-pdf-upload.cmd --list-buckets`. Lege lijst of
fout → credentials/account/endpoint. Bucket in de lijst met pijltje →
env klopt; dan was het een ander probleem.

### Publieke download-URL doet het niet (browser)

1. Bestand wel geüpload? Pad moet zijn
   `{production|preview}/…pad-onder-content-source…/index.md.pdf`.
2. **Public Development URL** nog aan op de bucket? (Settings → Public
   Development URL → Allowed.) Voor latere productie liever een eigen
   subdomein i.p.v. blijvend `r2.dev`.
3. Basis-URL in de site-overlays
   (`hugo.pdf-assets.production.toml` /
   `hugo.pdf-assets.preview.toml`) nog gelijk aan de huidige publieke
   host?

Handmatige test-URL (voorbeeld):

`https://pub-….r2.dev/preview/catalogus/…/index.md.pdf`

### Per ongeluk naar de verkeerde omgeving geüpload

Upload hetzelfde pad opnieuw met het **andere** `--env`. Bestanden in
de verkeerde map kun je in het Cloudflare-dashboard (R2 → bucket →
objecten) wissen; ze overschrijven de andere omgeving niet automatisch.

### Nieuw Cloudflare-account of bucket verhuisd

Pas `R2_ACCOUNT_ID`, eventueel `R2_BUCKET`, token en de **publieke
basis-URL** in beide `hugo.pdf-assets.*.toml`-bestanden aan. Daarna
opnieuw bulk-uploaden naar `preview` en `production`. De oude bucket
mag leeg of weg als niets er meer naar wijst.

### Betaalmethode / R2 “uit”

R2 vraagt een betaalmethode op het account, ook onder de gratis laag.
Ontbreekt die of is de kaart afgewezen, dan kunnen uploads of het
abonnement stoppen. Dashboard → Billing controleren; daarna opnieuw
`--list-buckets`.

### Upload onderbroken (laptop dicht, netwerk weg)

Gewoon opnieuw draaien met hetzelfde `--env`. Bestaande objecten worden
overschreven; wat al klaar was, hoeft niet handmatig opgeschoond.

## Terug naar “alles via GitHub”

1. Tag/branch **`pre-r2-pdfs`** in git (terugkeerpunt met PDF’s in de
   repo).
2. CI/overlays uitzetten zodat download weer naar bestanden op de site
   wijst (of vraag de beheerder/agent om de schakelaar terug te zetten).
3. PDF’s desnoods terugzetten uit die tag, of opnieuw maken met
   `pdf.cmd` en committen.
4. R2-upload stoppen. Git-geschiedenis opschonen doen we **alleen** als
   jij later expliciet akkoord geeft.

{{< navbuttons "pdf|/handleiding/scripts/pdf/" "r2-pdf-upload|/handleiding/scripts/r2-pdf-upload/" >}}
