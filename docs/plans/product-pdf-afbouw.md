# Besluit: catalogus-product-PDF afbouwen

Status: **afbouw rond** — VSA/mvsa/mscz/tekstblad: product-PDF niet meer
verplicht. Tekstblad-`pagina-pdf` uit `.md` via `vsa pdf` (tijdelijke
body). Geen bulk-delete van bestaande product-PDF’s.

Gerelateerd printpad (pagina, niet product):
[catalogus-pagina-pdf.md](catalogus-pagina-pdf.md).
Norm scherm vs print: [schermpartituur.md](../specs/schermpartituur.md) §1.
Publicatieproducten nu: [publicatiecontrole.md](../publicatiecontrole.md).

---

## 1. Besluit

**Catalogus-product-PDF’s** (`.vsa.pdf`, `.mscz.pdf`, `.mvsa.pdf`,
`.tekstblad.pdf` als A4-uitgave van één uitvoeringsvorm) vervullen geen
goede eigen rol meer naast `index.pagina.pdf`.

- **Print en download van “wat je op het blad ziet”** hoort bij
  **Download pagina / Print pagina** (`index.pagina.pdf`).
- **Score-Download / Score-Print** naar de product-PDF op het catalogusblad
  is overlapping / erfenis en wordt **afgebouwd**.
- Afbouw gebeurt **niet stil** en **niet in één keer**: eerst inventaris,
  dan UI, dan pas generatie/`check` — zie §2.

**Buiten dit besluit** (blijven of apart traject):

| Onderdeel | Waarom |
| --- | --- |
| `index.pagina.pdf` | Canonieke print van koormap- of catalogusblad |
| Handmatige print-PDF naast `*.print.mscz` | Ander publicatiespoor (MuseScore → zelf exporteren) |
| Coria-`.mxl`, audio, SVG, Score-IR / from-ir MusicXML | Oefenen / scherm; geen A4-product-PDF |
| Optionele “archief-PDF met colofon” later | Alleen als apart, bewust opt-in — niet als default product |

---

## 2. Volgorde (harde tussenstops)

| Stap | Wat | Wanneer klaar genoeg om door te gaan |
| --- | --- | --- |
| **1 — Inventaris** | Welke catalogus-leaves hebben de product-PDF nog **echt** nodig? (zie §3) | **Gedaan** (§3.1–3.3) |
| **2 — UI** | Score-Download/Print naar product-PDF weg op catalogus; nav-pagina-knoppen blijven | **Gedaan** (`oefenhoek-score-acties` + schermpartituur) |
| **3 — Generatie + `check`** | Product-PDF niet meer verplicht; `*-products` slaat PDF over | **Gedaan** (ook tekstblad; zie §3.5) |

Stap 3: geen stille delete van bestaande product-PDF’s in de catalogus.

---

## 3. Inventaris (stap 1)

Vragen (afgevinkt in §3.1):

1. **Scherm-fallback** — `bieb` toont product-PDF omdat OSMD (from-ir)
   én sibling-muziek-SVG (`.mvsa.svg` / `.vsa.svg`) ontbreken?
   (Legacy `static/vsa/bladermap/….svg` telt wél als scherm-SVG.)
2. **Geen `index.pagina.pdf`** terwijl print wél nodig is?
3. **Andere noodzaak** die pagina-PDF niet dekt?
4. **Niet meenemen** — handmatige print-PDF; `voorzien` zonder notatiebron.

Scan: 195 catalogus-leaves (`content-source/catalogus/…/…/…/`), datum
van deze inventaris. Methode: sibling-bestanden + keten zoals
`layouts/partials/bieb-score.html`.

### 3.1 Uitkomst

| Groep | Aantal | Scherm nu | Product-PDF nodig voor scherm? | Voor stap 2 / 3 |
| --- | ---: | --- | --- | --- |
| `.mvsa` + from-ir → OSMD | 59 | OSMD | Nee | Alleen download-knop erfenis |
| `.vsa` + sibling `.vsa.svg` | 112 | SVG | Nee | Idem |
| `.vsa` zonder sibling-SVG, wél legacy static SVG | 2 | Legacy SVG | Nee | Idem; PDF heet hier `{stam}.pdf` (niet `.vsa.pdf`) |
| Basispartituur-`.mscz` (scherm was product-PDF) | 7 | Was PDF; nu **`.mscz.svg`** | Nee (na schermfix) | Alle catalogus-`.mscz` (9) hebben SVG via `mscz-products` |
| Tekstblad (alleen `.tekstblad.md` + `.tekstblad.pdf`) | 1 | Was PDF; nu **`.tekstblad.md`-body** | Nee (na schermfix) | Print blijft `index.pagina.pdf` |
| Alleen `*.print.mscz` + handmatige PDF | 1 | Handmatige PDF | Buiten besluit | Blijft print-spoor |
| `voorzien` zonder notatiebron | 13 | Geen partituur | Nee (geen product-PDF) | Stub-`index.pagina.pdf` voldoende |

**Pagina-PDF:** alle 195 leaves hebben `index.pagina.pdf` (inclusief
voorzien-stubs). Geen gat “print nodig maar geen pagina-PDF”.

**Andere noodzaak (archief/extern):** in de repo geen apart spoor
gevonden dat pagina-PDF niet dekt. Score-Download/Print is de enige
overige consument van product-PDF’s (171 leaves hebben product-PDF
alleen daarvoor, niet als scherm).

### 3.2 Leaves waar product-PDF nu wél scherm is

**Basispartituur-`.mscz` (7)** — geen `.mscz.svg` / from-ir in de map;
scherm = `.mscz.pdf`:

| Pad |
| --- |
| `catalogus/communievers/moeder-gods/pancakescrawlspace` |
| `catalogus/eerste-antifoon/zondag/hemelum` |
| `catalogus/eucharistische-canon/19a-feofan/hemelum` |
| `catalogus/moeder-godslied/20d-in-waarheid/hemelum` |
| `catalogus/moeder-godslied/verhef-o-mijn-ziel-met-jubelzang/pancakescrawlspace` |
| `catalogus/onder-uwe-hoede/default/groningen` |
| `catalogus/vriendelijk-licht/default/groningen` |

**Tekstblad (1):**
`catalogus/dialoog-met-diaken/default/hemelum`
(`.tekstblad.pdf` op scherm; heeft wél `index.pagina.pdf`).

**Print-spoor (1, niet afbouwen als product-PDF-keten):**
`catalogus/kleine-intocht/zo-wk-mg/hemelum`
(`*.print.mscz` + handmatige `{stam}.pdf`).

**Geen echte PDF-scherm-fallback (legacy SVG voldoende):**

| Pad | Opmerking |
| --- | --- |
| `catalogus/moeder-godslied/ontslapen-moeder-gods/hemelum` | `.vsa` + static bladermap-SVG; ook `.print.mscz` |
| `catalogus/tropaar/nikolaas-van-myra-toon-4/hemelum` | Idem |

### 3.3 Gevolg voor volgende stappen

- **Stap 2 (UI):** **gedaan** — catalogus toont geen Score-Download/Print
  naar product-PDF meer; nav-pagina-knoppen blijven.
- **Stap 3 (`check` / generatie):** product-PDF mag uit de verplichte
  productketen zodra je dat besluit (schermpad is al zonder product-PDF).
  Print-mscz blijft handmatig.

### 3.4 Keuze schermvervanger (licht)

**Gekozen: lichte vorm** — geen verplichte migratie `.mscz` → `.mvsa`
vóór scherm zonder product-PDF.

| Groep | Schermvervanger | Catalogusbron |
| --- | --- | --- |
| 7× basispartituur-`.mscz` | Sibling `{stam}.mscz.svg` via `mvsa svg` in `mscz-products` (check eist stamp) | `.mscz` mag blijven |
| 1× tekstblad | Scherm: body van `.tekstblad.md` in `bieb-score` (HTML); print = `index.pagina.pdf` | `.tekstblad.md` blijft |

**Koninklijke route:** nieuwe of blijvende bron bij voorkeur **`.mvsa`**
(één keten met SVG/OSMD). Omzetten van bestaande MuseScore-bronnen mag
wanneer het nuttig blijkt — vastgelegd als automatische lijst
[MuseScore (.mscz)](../../content-source/overzichten/speciaal/mscz-bron.md)
onder Speciaal.

**Snel ophangen:** een aangeleverde `.mscz` mag in de catalogus zonder
eerst naar `.mvsa` te converteren. Verplicht converteren is géén
publicatie-eis.

Niet gekozen (zwaarder): alle 7 meteen naar `.mvsa` als enige bron —
strategisch netjes, te zwaar als enige voorwaarde voor product-PDF-afbouw.

### 3.5 Stap 3 — status

| Soort | Product-PDF in `check`/`products` | Toelichting |
| --- | --- | --- |
| `.vsa` / `.mvsa` / basis-`.mscz` | **Uit** | Bestaande `*.….pdf` mogen in git blijven; scripts vernieuwen ze niet meer |
| `.tekstblad.md` | **Uit** | `pagina-pdf` rendert body uit `.md` (`vsa pdf` tijdelijk); scherm = `.md` |
| `*.print.mscz` + handmatige PDF | Buiten besluit | Ongewijzigd |

Optioneel later: oude catalogus-product-PDF’s opruimen (geen eis).

---

## 4. Wat dit plan níet is

- Geen bulk-delete van bestaande `*.….pdf` in de catalogus in deze fase.
- Geen wijziging aan VSA-tooling-export zolang bibliotheek die PDF nog
  eist of als fallback toont.
- Geen vervanging van het pagina-PDF-traject; dat blijft leidend voor print.
