# Schermpartituur (lookafspraken)

Normatief voor hoe **muziek op het scherm** eruit moet zien in de
bibliotheek-site (catalogusblad en koormap-slot via `bieb` / `muziek`).
Doel: beheerders en bouwers toetsen dezelfde checklist; QA vóór
`development` → `main` gebruikt dit document.

**Eén pakket voor beide schermgeneratoren:** OSMD (Score-IR → from-ir
MusicXML) én SVG-fallback (MuseScore/`mvsa svg`, VSA-SVG, mscz-SVG).
Semantiek + deze lookregels zijn bindend; pixel-perfecte gelijkheid tussen
de ketens is dat niet (besluit 2).

Beheerder-taal en shortcodes: [koormap-paginataal.md](koormap-paginataal.md).
Productketens: [publicatiecontrole.md](../publicatiecontrole.md),
[tooling-koppeling.md](../tooling-koppeling.md).
Implementatie OSMD: `static/js/score-osmd.js` (moet dit document volgen).
SVG-export (titel uit, Source Sans 3, cues, …): VSA-tooling-stap
`mvsa svg` / layout `muziek` — niet in deze repo.

Speelplan-syntax en prioriteiten: niet hier dupliceren; zie
[VSA-tooling — speelplan](https://github.com/orthodox-ronl/VSA-tooling/blob/main/docs/specification-mvsa/speelplan.md).
Bladvorm op scherm: §4.4 hieronder.

---

## 1. Scherm versus print/download

| Kanaal | Bedoeling |
| --- | --- |
| **Scherm** | Doorlopende partituur om mee te lezen/oefenen in de browser. Geen A4-bladkaders als primaire look. |
| **Download / Print (pagina)** | `index.pagina.pdf` van het getoonde blad (koormap of catalogus-leaf) via nav **Download pagina** / **Print pagina**. Catalogus heeft geen aparte score-knoppen meer naar product-PDF. |

Op het scherm forceert het onderdeel `muziek` **geen** paginatitel. Titels
horen bij de Hugo-pagina (catalogus-H1) of bij koormap-`kop` / Markdown.

---

## 2. Welk plaatje op het scherm (volgorde)

De site kiest in deze volgorde ([`bieb-score.html`](../../layouts/partials/bieb-score.html)):

1. **OSMD** — sibling `{stam}.mvsa.from-ir.musicxml` (Score-IR → MusicXML)
2. **Muziek-SVG** — sibling `{stam}.mvsa.svg`, `{stam}.vsa.svg` of `{stam}.mscz.svg` (anders legacy `static/vsa/bladermap/….svg` bij `.vsa`)
3. **Tekstblad** — body van sibling `{stam}.tekstblad.md` (HTML; geen product-PDF als viewer)
4. **PDF op scherm** — alleen als 1–3 ontbreken

Gevolgen:

- Waar OSMD beschikbaar is, is dat de **gewenste** schermlook (geen MuseScore-paginamodel).
- SVG is **fallback** of het schermpad voor bronnen zonder Score-IR (`.vsa`, basispartituur-`.mscz`).
- Tekstblad toont de Markdown/HTML-bron op scherm; product-PDF is geen viewer meer.
- PDF-op-scherm blijft alleen nood-fallback als SVG/OSMD/tekstblad-md ontbreken.
- Coria (`.mxl` / Oefenen) en audio horen **niet** bij de schermlook van de partituur; die knoppen blijven apart.

Beide ketens (1 en 2) volgen hetzelfde lookpakket in §4. Verschil is alleen
*hoe* de tekening tot stand komt, niet *wat* er wel/niet op mag staan.

---

## 3. Titels en pagina-chrome (site)

| Context | Eis |
| --- | --- |
| Catalogusblad | Precies **één** zichtbare hoofdtitel (template-H1 uit afgeleide catalogustitel). Geen tweede dezelfde titel via `bieb titel` of een Markdown-`#` met dezelfde tekst. |
| Koormap-slot | **Geen** template-H1. Bladtitel en rubrieken via `kop` (of afgesproken Markdown). Geen dubbele titel naast `bieb titel`. |
| In de partituurtekening | Geen titel/ondertitel/componist/lyricist/credits — alleen muziek (**OSMD én SVG**, besluit 1). Catalogus-PDF-op-scherm mag wel een titel in het PDF-blad hebben (nood-fallback = printlook). |
| Download/Print | Alleen pagina-knoppen in de **nav** (`index.pagina.pdf`). Per muziekblok: ♪-menu oefenen/beluisteren (catalogus: ook {}-menu bronnen); geen score-Download/Print naar product-PDF. |

---

## 4. Gedeeld schermpakket (OSMD én SVG)

Bindend voor elke partituurtekening op het scherm, ongeacht of de site OSMD
of SVG toont. Implementatie: OSMD in `static/js/score-osmd.js`; SVG via
VSA-tooling-export. Gaps aan de SVG-kant → ticket/PR in VSA-tooling, geen
stille versoepeling van deze regels in de site.

### 4.1 Chrome in de partituurtekening

| Onderdeel | Op het scherm |
| --- | --- |
| Partituurtitel / ondertitel / componist / lyricist / credits | Uit (besluit 1) |
| Partijnamen en partijafkortingen | Uit (besluit 4) |
| Metronoomtekens | Uit (besluit 4) |
| Maatsoort (o.a. vaste 4/4) | Uit — senza misura; geen valse 4/4 (besluit 4) |
| Maatnummers | Aan op **beide** ketens. Voorkeur: begin van elk systeem. Minimaal: minstens één maatnummer per systeem (besluit 3) |
| Lettertype (tekst/cues/lyrics-stijl) | Source Sans 3 op **beide** ketens (besluit 5) |

### 4.2 Cues (liturgische aanwijzingen boven de noten)

Zelfde wrap-/centreer-regels op SVG en OSMD (besluit 6).

| Eis | Toelichting |
| --- | --- |
| Juiste maat | Cue hoort bij de maat van de eerste noot van die aanwijzing. |
| Niet over maatstrepen | Cue-tekst blijft binnen de maat; bij noodzaak wrap naar twee regels (`t1` / `… t2`-achtig). |
| Breedte | Eerst ruimte voor twee regels; inklappen naar **één** regel alleen als die ene regel nog past. |
| Inklappen | Bij inklappen: onderste regel houden; één-regelcues op die onderste hoogte. |
| Na centreren | Cues **niet** meeschuiven met de noten; ze blijven op de (oude) eerste-noot-positie. |

### 4.3 Noten, lyrics, afstand

| Eis | Toelichting |
| --- | --- |
| Centreren | Noten (en bijbehorende lyrics/dashes) centreren in de beschikbare maatbreedte wanneer er genoeg wit links én rechts is. |
| Korte stukken | Geen nutteloos uitgerekte lege maten; cues en tekst blijven leesbaar. |
| Lange stukken | Systeemovergangen blijven kloppen (ook KSL); horizontale scroll alleen als de viewport echt te smal is. OSMD: partituur schaalt mee (`autoResize`). |
| Wit | Tussen systemen en notenbalken genoeg ruimte zodat lyrics en cues niet in elkaar lopen. |

Zelfde **informatiedichtheid** op beide ketens: noten, lyrics, cues,
speelplan-navigatie; geen chrome-ruis (besluit 7). Geen eis tot
pixel-/engraving-gelijkheid buiten deze regels (besluit 2).

### 4.4 Speelplan-bladvorm (navigatie op het blad)

Wanneer de bron een `@speelplan` heeft, moeten **beide** generatoren de
bladvorm-navigatie kunnen tonen (herhaal, volta, D.S./D.C., Fine, Coda, …)
volgens de prioriteiten in
[speelplan.md](https://github.com/orthodox-ronl/VSA-tooling/blob/main/docs/specification-mvsa/speelplan.md)
(compacte conventionele notatie; expand alleen als vangnet). Geen
blok-id-labels boven maten als navigatie genoeg is.

Kort overzicht (details en patronen blijven in speelplan.md):

| Prio | Patroon (voorbeeld) | Bladtekens |
| --- | --- | --- |
| 1 | plan = blokvolgorde | niets extra |
| 2 | `(a,b)×n+(a,c)` | herhaal + volta |
| 3 | `prefix + X×n + suffix` | `\|: … :\|` (+ times) |
| 4 | D.S./D.C. al Fine | Segno + Fine + sprong |
| 5 | D.S./D.C. al Coda | Segno / To Coda / Coda + sprong |
| 6 | rest | expand (uitgeschreven op blad) |

**Acceptatie:**

1. **VSA-tooling** — from-ir MusicXML bevat dezelfde navigatiemarkeringen als
   partituur-MusicXML (bestaande tests daar).
2. **Bibliotheek** — steekproef/`scripts\check_osmd_nav_zichtbaar.cmd` (ook in
   `check` en Pages-CI): OSMD moet die tekens **zichtbaar tekenen** (VexFlow-
   modifiers / SVG), niet alleen dat ze in `.from-ir.musicxml` staan
   (besluit 9).

Repro-voorbeeld volta: catalogus
`alleluia/9a-toon-1/groningen` (`@speelplan 1, 2, 1, 2, 1, 3`).

---

## 5. Keten-specifiek (levering, geen tweede lookwereld)

### 5.1 OSMD

| Eis | Toelichting |
| --- | --- |
| Bron | Sibling `{stam}.mvsa.from-ir.musicxml`. |
| Gedrag | Volgt §4; bron van waarheid voor clientgedrag: `static/js/score-osmd.js`. |
| Systemen | Volgens MusicXML (`newSystemFromXML`); cues niet afkappen. |

### 5.2 SVG-fallback

| Eis | Toelichting |
| --- | --- |
| Bron | Sibling `{stam}.mvsa.svg` of `{stam}.vsa.svg` (preferred); legacy bladermap-SVG alleen zolang de sibling ontbreekt. |
| Rol | Primair schermpad voor **VSA** (nog geen Score-IR/OSMD). Voor **mvsa** alleen als from-ir ontbreekt. |
| Look | Zelfde pakket als §4 (titel/chrome uit, Source Sans 3, maatnummers, cues, speelplan-nav). Export: VSA-tooling layout `muziek` / MuseScore 4. |
| Kolom | Breedte volgt de contentkolom; geen horizontale overflow buiten de kolom op oefenhoek-pagina’s (`overflow-x` begrensd). |
| Site-titel | Het onderdeel `muziek` zet geen extra HTML-titel. |

Als MuseScore een §4-regel nog niet haalt: documenteer de gap of open een
VSA-tooling-ticket — versoepel de eis hier niet stilzwijgend.

---

## 6. Basispartituur-`.mscz` op het scherm

| Eis | Toelichting |
| --- | --- |
| Voorkeur keten | Zelfde volgorde als §2: als er een canonieke `.mvsa` + from-ir is, wint OSMD; anders SVG; anders PDF van het mscz-spoor. |
| Alleen `.mscz` (+ PDF) | Scherm toont vaak de catalogus-PDF als blad — dat is **nood-fallback**, niet de eindlook. |
| Titel | Geen tweede Hugo-titel; PDF mag wel eigen bladkop hebben. SVG van dit spoor volgt §4 zodra die export er is. |

**Nog niet normatief:** wanneer elke mscz-UV Score-IR/OSMD móet hebben vóór
publicatie. Publicatiecontrole eist nu from-ir voor canonieke `.mvsa`, niet
voor elke losse `.mscz`.

---

## 7. Tekstblad (`.tekstblad.md`)

| Eis | Toelichting |
| --- | --- |
| Scherm | Body van sibling `{stam}.tekstblad.md` (HTML via `bieb-score`). Er is geen OSMD/SVG-keten. |
| Inhoud | Leesbare liturgische tekst/dialoog. |
| Titel | Zelfde paginaregels als §3. |
| Print | Blad = `index.pagina.pdf` (nav); product-`.tekstblad.pdf` is geen schermviewer. |

---

## 8. Checklist voor steekproef / review

Per geopende catalogus- of koormap-URL:

1. Juiste keten (§2): zie je OSMD waar from-ir bestaat, anders SVG, anders tekstblad-md / PDF?
2. Titels (§3): geen dubbele hoofdtitel; geen titel/credits **in** de partituurtekening?
3. Chrome gedeeld (§4.1): geen partijnamen, metronoom, maatsoort; Source Sans 3; maatnummers (minstens één per systeem, bij voorkeur begin systeem) — **op OSMD én SVG**?
4. Cues / centreren / wit (§4.2–4.3): leesbaar, niet afgekapt, niet over maatstrepen?
5. Speelplan (§4.4): bij bron met `@speelplan` — zichtbare herhaal/volta/D.S./… (niet alleen in het MusicXML-bestand)? Steekproef minstens `alleluia/9a-toon-1/groningen`.
6. Kolom / fallback (§5–7): SVG/mscz/tekstblad zichtbaar in de kolom; geen extra site-titel door `muziek`?
7. Download/Print: nav-pagina-PDF; knoppen doen wat ze zeggen?

Neem in een steekproef **korte én lange** stukken mee (en bij mvsa bij voorkeur
ook een multi-`bieb`-pagina NL+KSL).

---

## 9. Wat dit document niet regelt

- CoriB (latere oefen-UI); Coria-knop blijft externe `coria.nl`
- Inhoud/validiteit van VSA/MVSA-bronnen (validate / tooling)
- Layoutprofielen van MuseScore-print (`layout.cmd`, A4-PDF)
- Pixel-perfecte gelijkheid tussen SVG-fallback en OSMD (bewust niet verplicht)
- From-ir / speelplan-MusicXML-generatie (VSA-tooling)

**Niet meer «SVG open»:** Source Sans 3, cue-wrap/centreer, chrome uit
(titel/partijnamen/metronoom/maatsoort), maatnummers — dat is §4 voor beide
ketens. Open implementatiegaps horen in VSA-tooling, niet als stille
site-uitzondering.

Wijzigingen aan lookregels: PR op dit bestand; OSMD-gedrag in
`score-osmd.js` synchroon houden.
