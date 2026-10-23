# Schermpartituur (lookafspraken)

Normatief voor hoe **muziek op het scherm** eruit moet zien in de
bibliotheek-site (catalogusblad en koormap-slot via `bieb` / `muziek`).
Doel: beheerders en bouwers toetsen dezelfde checklist; QA vóór
`development` → `main` gebruikt dit document.

Beheerder-taal en shortcodes: [koormap-paginataal.md](koormap-paginataal.md).
Productketens: [publicatiecontrole.md](../publicatiecontrole.md),
[tooling-koppeling.md](../tooling-koppeling.md).
Implementatie OSMD: `static/js/score-osmd.js` (moet dit document volgen).

---

## 1. Scherm versus print/download

| Kanaal | Bedoeling |
| --- | --- |
| **Scherm** | Doorlopende partituur om mee te lezen/oefenen in de browser. Geen A4-bladkaders als primaire look. |
| **Download / Print (catalogus)** | A4-product-PDF van de uitvoeringsvorm (`.vsa.pdf` / `.mscz.pdf` / `.mvsa.pdf` / `.tekstblad.pdf`). Mag titel, id, colofon bevatten. |
| **Download / Print (pagina)** | `*.pagina.pdf` van het getoonde blad (koormap of catalogus); zie koormap-paginataal. |

Op het scherm forceert het onderdeel `muziek` **geen** paginatitel. Titels
horen bij de Hugo-pagina (catalogus-H1) of bij koormap-`kop` / Markdown.

---

## 2. Welk plaatje op het scherm (volgorde)

De site kiest in deze volgorde ([`bieb-score.html`](../../layouts/partials/bieb-score.html)):

1. **OSMD** — sibling `{stam}.mvsa.from-ir.musicxml` (Score-IR → MusicXML)
2. **Muziek-SVG** — sibling `{stam}.mvsa.svg` of `{stam}.vsa.svg` (anders legacy `static/vsa/bladermap/….svg` bij `.vsa`)
3. **PDF op scherm** — alleen als 1 en 2 ontbreken (typisch tekstblad of mscz zonder SVG/OSMD)

Gevolgen:

- Waar OSMD beschikbaar is, is dat de **gewenste** schermlook (geen MuseScore-paginamodel).
- SVG en PDF-op-scherm zijn **fallback** of het enige pad voor bronnen zonder Score-IR (nu vooral `.vsa` en veel `.mscz`).
- Coria (`.mxl` / Oefenen) en audio horen **niet** bij de schermlook van de partituur; die knoppen blijven apart.

---

## 3. Titels en pagina-chrome (alle brontypen)

| Context | Eis |
| --- | --- |
| Catalogusblad | Precies **één** zichtbare hoofdtitel (template-H1 uit afgeleide catalogustitel). Geen tweede dezelfde titel via `bieb titel` of een Markdown-`#` met dezelfde tekst. |
| Koormap-slot | **Geen** template-H1. Bladtitel en rubrieken via `kop` (of afgesproken Markdown). Geen dubbele titel naast `bieb titel`. |
| In de partituur zelf | OSMD tekent geen titel/ondertitel/componist/lyricist. Catalogus-PDF-op-scherm mag wel een titel in het PDF-blad hebben (dat is printlook als nood-fallback). |
| Download/Print | Pagina-knoppen in de **nav**; per muziekblok op de koormap alleen oefenacties (compact menu). Op het catalogusblad mogen score-Download/Print naar de product-PDF. |

---

## 4. OSMD-look (`.mvsa` met from-ir) — bindend

Geldt wanneer de pagina OSMD toont. Bron van waarheid voor gedrag:
`static/js/score-osmd.js`; dit hoofdstuk is de leesbare norm.

### 4.1 Wat wel en niet zichtbaar is

| Onderdeel | Op het scherm |
| --- | --- |
| Partituurtitel / ondertitel / componist / lyricist / credits | Uit |
| Partijnamen en partijafkortingen | Uit |
| Metronoomtekens | Uit |
| Maatsoort (o.a. vaste 4/4) | Uit (MusicXML senza misura; OSMD mag geen valse 4/4 tonen) |
| Maatnummers | Aan (niet alleen aan het begin van een systeem) |
| Lettertype (tekst/cues/lyrics-stijl in OSMD) | Source Sans 3 |
| Systeemovergangen | Volgens MusicXML (`newSystemFromXML`); leesbaar, geen afgekapte cues |

### 4.2 Cues (liturgische aanwijzingen boven de noten)

| Eis | Toelichting |
| --- | --- |
| Juiste maat | Cue hoort bij de maat van de eerste noot van die aanwijzing. |
| Niet over maatstrepen | Cue-tekst blijft binnen de maat; bij noodzaak wrap naar twee regels (`t1` / `… t2`-achtig). |
| Breedte | Eerst ruimte voor twee regels; inklappen naar **één** regel alleen als die ene regel nog past. |
| Inklappen | Bij inklappen: onderste regel houden; één-regelcues op die onderste hoogte. |
| Na centreren | Cues **niet** meeschuiven met de noten; ze blijven op de (oude) eerste-noot-positie. |

### 4.3 Noten en lyrics in de maat

| Eis | Toelichting |
| --- | --- |
| Centreren | Noten (en bijbehorende lyrics/dashes) centreren in de beschikbare maatbreedte wanneer er genoeg wit links én rechts is. |
| Korte stukken | Geen nutteloos uitgerekte lege maten; cues en tekst blijven leesbaar. |
| Lange stukken | Systeemovergangen blijven kloppen (ook KSL); horizontale scroll alleen als de viewport echt te smal is; partituur schaalt mee (`autoResize`). |

### 4.4 Afstand en leesbaarheid

Tussen systemen en notenbalken genoeg wit zodat lyrics en cues niet in
elkaar lopen (OSMD engraving-regels in de implementatie). Lyrics-hoogte
blijft leesbaar op desktop en gangbare laptopbreedte.

---

## 5. SVG-look (`.vsa` en mvsa-SVG-fallback)

| Eis | Toelichting |
| --- | --- |
| Bron | Sibling `{stam}.vsa.svg` of `{stam}.mvsa.svg` (preferred); legacy bladermap-SVG alleen zolang de sibling ontbreekt. |
| Rol | Primair schermpad voor **VSA** (nog geen Score-IR/OSMD). Voor **mvsa** alleen als from-ir ontbreekt. |
| Titel | Het onderdeel `muziek` zet geen extra HTML-titel; als de SVG zelf een MuseScore-bladkop bevat, is dat een product van de SVG-export, geen tweede Hugo-H1. |
| Pagina | Breedte volgt de contentkolom; geen horizontale overflow buiten de kolom op oefenhoek-pagina’s (`overflow-x` begrensd). |

**Nog niet normatief (bewust open):** pixel-identieke look met OSMD
(cues, centreren, lettertype). Tot Score-IR/OSMD ook voor VSA bestaat, geldt
voor SVG: **zichtbaar, schaalbaar in de kolom, geen dubbele site-titel**.
Verdere SVG-lookregels alleen via PR op dit document.

---

## 6. Basispartituur-`.mscz` op het scherm

| Eis | Toelichting |
| --- | --- |
| Voorkeur keten | Zelfde volgorde als §2: als er een canonieke `.mvsa` + from-ir is, wint OSMD; anders SVG; anders PDF van het mscz-spoor. |
| Alleen `.mscz` (+ PDF) | Scherm toont vaak de catalogus-PDF als blad — dat is **nood-fallback**, niet de eindlook. |
| Titel | Geen tweede Hugo-titel; PDF mag wel eigen bladkop hebben. |

**Nog niet normatief:** wanneer elke mscz-UV Score-IR/OSMD móet hebben vóór
publicatie. Publicatiecontrole eist nu from-ir voor canonieke `.mvsa`, niet
voor elke losse `.mscz`.

---

## 7. Tekstblad (`.tekstblad.md`)

| Eis | Toelichting |
| --- | --- |
| Scherm | Sibling `{stam}.tekstblad.pdf` (PDF-op-scherm). Er is geen OSMD/SVG-keten. |
| Inhoud | Leesbare liturgische tekst/dialoog; layout volgt het tekstblad-product. |
| Titel | Zelfde paginaregels als §3. |

---

## 8. Checklist voor steekproef / review

Per geopende catalogus- of koormap-URL:

1. Juiste keten (§2): zie je OSMD waar from-ir bestaat, anders SVG, anders PDF?
2. Titels (§3): geen dubbele hoofdtitel?
3. Bij OSMD (§4): cues, maatnummers, geen partijnamen/metronoom/4/4, Source Sans 3, centreren, systeemovergangen bij lange stukken?
4. Bij SVG/mscz/tekstblad (§5–7): zichtbaar, in de kolom, geen extra site-titel door `muziek`?
5. Download/Print: nav-pagina-PDF; op catalogus eventueel score-PDF — knoppen doen wat ze zeggen?

Neem in een steekproef **korte én lange** stukken mee (en bij mvsa bij voorkeur
ook een multi-`bieb`-pagina NL+KSL).

---

## 9. Wat dit document niet regelt

- CoriB (latere oefen-UI); Coria-knop blijft externe `coria.nl`
- Inhoud/validiteit van VSA/MVSA-bronnen (dat is validate / tooling)
- Layoutprofielen van MuseScore-print (`layout.cmd`, A4-PDF)
- Pixel-perfecte gelijkheid tussen SVG-fallback en OSMD (open, §5)

Wijzigingen aan lookregels: PR op dit bestand; OSMD-gedrag in
`score-osmd.js` synchroon houden.
