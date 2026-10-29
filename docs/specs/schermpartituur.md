# Schermpartituur (lookafspraken)

Normatief voor hoe **muziek op het scherm** eruit moet zien in de
bibliotheek-site (catalogusblad en koormap-slot via `bieb` / `muziek`).
Doel: beheerders en bouwers toetsen dezelfde checklist; QA vóór
`development` → `main` gebruikt dit document.

**Eén pakket voor beide schermgeneratoren:** SVG (default; MuseScore/
`mvsa svg`, VSA-SVG, mscz-SVG) én OSMG/OSMD (Score-IR → from-ir MusicXML),
geschakeld via het **{}**-menu. Semantiek + deze lookregels zijn bindend;
pixel-perfecte gelijkheid tussen de ketens is dat niet (besluit 2).
Tijdelijk: enkele cue-/centreer-regels zijn alleen voor OSMD bindend zolang
scherm-SVG via MuseScore loopt (§4.2–4.3); daarna weer voor beide.

Beheerder-taal en shortcodes: [koormap-paginataal.md](koormap-paginataal.md).
Productketens: [publicatiecontrole.md](../publicatiecontrole.md),
[tooling-koppeling.md](../tooling-koppeling.md).
Print-/export-contracten (S8, melisma, layout): VSA-tooling
[contract-index](https://github.com/orthodox-ronl/VSA-tooling/blob/main/docs/formats/contract-index.md)
— hier geen parallelle checklist.
Implementatie OSMD: `static/js/score-osmd.js` (moet dit document volgen).
Console-check (klembord → chat, geen jargon):
[OSMD diagnose](../guides/schermpartituur-osmd-diagnose.md).
SVG-export (titel uit, Source Sans 3, cues, …): VSA-tooling-stap
`mvsa svg` / layout `muziek` — niet in deze repo.

Speelplan-syntax en prioriteiten: niet hier dupliceren; zie
[VSA-tooling — speelplan](https://github.com/orthodox-ronl/VSA-tooling/blob/main/docs/specification-mvsa/speelplan.md).
Bladvorm op scherm: §4.4 hieronder.

---

## 1. Scherm versus print/download

| Kanaal                        | Bedoeling                                                                                                                                                                             |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Scherm**                    | Doorlopende partituur om mee te lezen/oefenen in de browser. Geen A4-bladkaders als primaire look.                                                                                    |
| **Download / Print (pagina)** | `index.md.pdf` van het getoonde blad (koormap of catalogus-leaf) via nav **Download pagina** / **Print pagina**. Catalogus heeft geen aparte score-knoppen meer naar product-PDF. |

Op het scherm forceert het onderdeel `muziek` **geen** paginatitel. Titels
horen bij de Hugo-pagina (catalogus-H1) of bij koormap-`kop` / Markdown.

---

## 2. Welk plaatje op het scherm

In het **{}**-menu staan onder elkaar **Bronnen** en één wisselknop:
**OSMG** (als je nu SVG ziet) of **SVG** (als je nu OSMG ziet). Default is
SVG. Keuze in `localStorage` (`bibliotheek-schermstand`), sitebreed in die
browser ([`bieb-score.html`](../../layouts/partials/bieb-score.html) +
`static/js/score-schermstand.js`).

| Stand | Bron op scherm |
| ----- | -------------- |
| **SVG** (default) | Sibling `{stam}.mvsa.svg` / `.vsa.svg` / `.mscz.svg` (geen ketting `*.mvsa.mscz.svg`); anders legacy bladermap-SVG |
| **OSMG** | Sibling `{stam}.mvsa.from-ir.musicxml` via OpenSheetMusicDisplay (`score-osmd.js`) |

Geen automatische wissel tussen SVG en OSMG (ook niet bij S8-recite). Ontbreekt
het product voor de gekozen stand, dan een korte melding op dat blad — niet
stiekem de andere keten.

Alleen als **beide** schermproducten ontbreken:

1. **Tekstblad** — body van sibling `{stam}.tekstblad.md`
2. **PDF op scherm** — nood-fallback

Coria (`.mxl` / Oefenen) en audio horen **niet** bij de schermlook; die zitten
in tip-icoon **♪**.

Beide ketens volgen hetzelfde lookpakket in §4. Verschil is alleen *hoe* de
tekening tot stand komt — met één **tijdelijke** uitzondering: een paar
cue-/centreer-regels zijn nu alleen bindend voor OSMD (§4.2–4.3), zolang
scherm-SVG via MuseScore loopt.

---

## 3. Titels en pagina-chrome (site)

| Context                 | Eis                                                                                                                                                                                          |
| ----------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Catalogusblad           | Precies **één** zichtbare hoofdtitel (template-H1 uit afgeleide catalogustitel). Geen tweede dezelfde titel via `bieb titel` of een Markdown-`#` met dezelfde tekst.                         |
| Koormap-slot            | **Geen** template-H1. Bladtitel en rubrieken via `kop` (of afgesproken Markdown). Geen dubbele titel naast `bieb titel`.                                                                     |
| In de partituurtekening | Geen titel/ondertitel/componist/lyricist/credits — alleen muziek (**OSMD én SVG**, besluit 1). Catalogus-PDF-op-scherm mag wel een titel in het PDF-blad hebben (nood-fallback = printlook). |
| Download/Print          | Alleen pagina-knoppen in de **nav** (`index.md.pdf`). Per muziekblok: ♪-menu oefenen/beluisteren (catalogus: ook {}-menu bronnen); geen score-Download/Print naar product-PDF.           |

---

## 4. Gedeeld schermpakket (OSMD én SVG)

Bindend voor elke partituurtekening op het scherm, ongeacht of de site OSMD
of SVG toont. Implementatie: OSMD in `static/js/score-osmd.js`; SVG via
VSA-tooling-export. Gaps aan de SVG-kant → ticket/PR in VSA-tooling, geen
stille versoepeling van deze regels in de site.

### 4.1 Chrome in de partituurtekening

| Onderdeel                                                    | Op het scherm                                                                                                       |
| ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------- |
| Partituurtitel / ondertitel / componist / lyricist / credits | Uit (besluit 1)                                                                                                     |
| Partijnamen en partijafkortingen                             | Uit (besluit 4)                                                                                                     |
| Metronoomtekens                                              | Uit (besluit 4)                                                                                                     |
| Maatsoort (o.a. vaste 4/4)                                   | Uit — senza misura; geen valse 4/4 (besluit 4)                                                                      |
| Maatnummers                                                  | Aan op **beide** ketens. Voorkeur: begin van elk systeem. Minimaal: minstens één maatnummer per systeem (besluit 3) |
| Lettertype (tekst/cues/lyrics-stijl)                         | Source Sans 3 op **beide** ketens (besluit 5)                                                                       |

### 4.2 Cues (liturgische aanwijzingen boven de noten)

Doel blijft besluit 6: dezelfde wrap-/centreer-look op beide ketens. **Nu**
zijn enkele regels alleen bindend voor OSMD; MuseScore-SVG (`mvsa svg` /
layout `muziek`) is daar best-effort — zie de tijdelijke uitzondering
onderaan deze paragraaf.

| Eis                                 | Keten              | Toelichting                                                                                                                                             |
| ----------------------------------- | ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Juiste maat                         | Beide              | Cue hoort bij de maat van de eerste noot van die aanwijzing.                                                                                            |
| Niet over maatstrepen / wrap        | Beide              | Cue-tekst blijft binnen de maat; bij noodzaak wrap naar twee regels (`t1` / `… t2`-achtig; MuseScore-SVG: wrap op `...`).                               |
| Breedte / inklappen naar één regel  | **OSMD-only** (nu) | Eerst ruimte voor twee regels; inklappen naar **één** regel alleen als die ene regel nog past (`score-osmd.js`). MuseScore-SVG doet dat inklappen niet. |
| Inklappen: onderste hoogte          | **OSMD-only** (nu) | Bij inklappen: onderste regel houden; één-regelcues op die onderste hoogte.                                                                             |
| Na centreren: cues niet meeschuiven | **OSMD-only** (nu) | Cues blijven op de (oude) eerste-noot-positie; niet meeschuiven met de noten. Op MuseScore-SVG geen gelijk mechanisme.                                  |

**Tijdelijke uitzondering (MuseScore-SVG):** zolang scherm-SVG via
**MuseScore** (`mvsa svg` / layout `muziek`) wordt gegenereerd, zijn de
rijen hierboven gemarkeerd **OSMD-only** een bewuste keten-uitzondering —
niet geschrapt uit de norm. **Zodra** MuseScore niet meer de
SVG-generator voor het scherm is, gelden die regels weer **voor beide**
ketens (zelfde informatiedichtheid én dezelfde cue-/centreer-look), tenzij
een nieuw productbesluit anders zegt. Versoepel ze niet stilzwijgend als
«voor altijd open».

### 4.3 Noten, lyrics, afstand

| Eis                          | Keten              | Toelichting                                                                                                                                                                                                                      |
| ---------------------------- | ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Centreren in maatbreedte     | **OSMD-only** (nu) | Noten (en bijbehorende lyrics/dashes) centreren in de beschikbare maatbreedte wanneer er genoeg wit links én rechts is. MuseScore-SVG: alleen `measureSpacing`, geen OSMD-centreer.                                              |
| Korte stukken                | Beide              | Geen nutteloos uitgerekte lege maten; cues en tekst blijven leesbaar.                                                                                                                                                            |
| Lange stukken                | Beide              | Systeemovergangen blijven kloppen (ook KSL); horizontale scroll alleen als de viewport echt te smal is. OSMD: past mee bij echte breedtewijziging (eigen resize-handler; geen OSMD-`autoResize`, anders knippert centreren weg). |
| Wit                          | Beide              | Tussen systemen en notenbalken genoeg ruimte zodat lyrics en cues niet in elkaar lopen.                                                                                                                                          |
| Lettergrepen over maatstreep | **OSMD-only** (nu) | Laatste lettergreep vóór een maatstreep en eerste erna blijven visueel gescheiden (geen «wordtte-»). OSMD: `LyricOverlapAllowedIntoNextMeasure` laag + lyric-x-padding in `score-osmd.js`.                                       |

Zelfde **informatiedichtheid** op beide ketens: noten, lyrics, cues,
speelplan-navigatie; geen chrome-ruis (besluit 7). Lange recite en
same-pitch melisma volgen de print-eindvorm (S8/S13) in from-ir MusicXML
zodat OSMD niet “één noot per lettergreep” meer toont waar het blad
collapse heeft — zie VSA-tooling [partituur-ir](https://github.com/orthodox-ronl/VSA-tooling/blob/main/docs/plans/partituur-ir.md).
Geen eis tot pixel-/engraving-gelijkheid buiten deze regels (besluit 2).
De OSMD-only-rijen in §4.2–4.3 vallen onder dezelfde tijdelijke uitzondering
als in §4.2 (weer beide ketens zodra scherm-SVG niet meer via MuseScore
loopt).

### 4.4 Speelplan-bladvorm (navigatie op het blad)

Wanneer de bron een `@speelplan` heeft, moeten **beide** generatoren de
bladvorm-navigatie kunnen tonen (herhaal, volta, D.S./D.C., Fine, Coda, …)
volgens de prioriteiten in
[speelplan.md](https://github.com/orthodox-ronl/VSA-tooling/blob/main/docs/specification-mvsa/speelplan.md)
(compacte conventionele notatie; expand alleen als vangnet). Geen
blok-id-labels boven maten als navigatie genoeg is.

Kort overzicht (details en patronen blijven in speelplan.md):

| Prio | Patroon (voorbeeld)     | Bladtekens                      |
| ---- | ----------------------- | ------------------------------- |
| 1    | plan = blokvolgorde     | niets extra                     |
| 2    | `(a,b)×n+(a,c)`         | herhaal + volta                 |
| 3    | `prefix + X×n + suffix` | `\|: … :\|` (+ times)           |
| 4    | D.S./D.C. al Fine       | Segno + Fine + sprong           |
| 5    | D.S./D.C. al Coda       | Segno / To Coda / Coda + sprong |
| 6    | rest                    | expand (uitgeschreven op blad)  |

**Acceptatie:**

1. **VSA-tooling** — from-ir MusicXML bevat dezelfde navigatiemarkeringen als
   partituur-MusicXML (bestaande tests daar).
2. **Bibliotheek** — steekproef/`scripts\check_osmd_nav_zichtbaar.cmd` (ook in
   `check` en Pages-CI): OSMD moet die tekens **zichtbaar tekenen** (VexFlow-
   modifiers / SVG), niet alleen dat ze in `.from-ir.musicxml` staan
   (besluit 9). S8 A1-adapter-check volgt op de S8-experimentbranch.

Repro-voorbeeld volta: catalogus
`alleluia/9a-toon-1/groningen` (`@speelplan 1, 2, 1, 2, 1, 3`).

---

## 5. Keten-specifiek (levering, geen tweede lookwereld)

### 5.1 OSMD

| Eis       | Toelichting                                                                                                                                                                                                                                                                                                                                                          |
| --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Bron      | Sibling `{stam}.mvsa.from-ir.musicxml`.                                                                                                                                                                                                                                                                                                                              |
| Gedrag    | Volgt §4; bron van waarheid voor clientgedrag: `static/js/score-osmd.js`.                                                                                                                                                                                                                                                                                            |
| S8-recite | From-ir mag spacer-markering (`<notehead>none</notehead>`) blijven houden voor product/CI. Op het **scherm** beslist alleen de {}-stand SVG/OSMG — geen S8-bypass meer. Tooling: [osmd-s8-recite](https://github.com/orthodox-ronl/VSA-tooling/blob/main/docs/plans/osmd-s8-recite.md). |
| Systemen  | Volgens MusicXML (`newSystemFromXML`); cues niet afkappen.                                                                                                                                                                                                                                                                                                           |

### 5.2 SVG (default-schermstand)

| Eis        | Toelichting                                                                                                                                                                                                                                                                                                                |
| ---------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Bron       | Sibling `{stam}.mvsa.svg` of `{stam}.vsa.svg` (preferred); legacy bladermap-SVG alleen zolang de sibling ontbreekt.                                                                                                                                                                                                        |
| Rol        | **Default** schermstand via {}-menu. Ook bruikbaar zonder from-ir (`.vsa`, basispartituur-`.mscz`).                                                                                                                                                                                                                         |
| Look       | Zelfde pakket als §4 (titel/chrome uit, Source Sans 3, maatnummers, cues, speelplan-nav). Export: VSA-tooling layout `muziek` / MuseScore 4. Cue-inklappen / cues-niet-meeschuiven / noten-centreren: nu **best-effort** t.o.v. OSMD (§4.2–4.3); weer verplicht voor beide zodra scherm-SVG niet meer via MuseScore loopt. |
| Kolom      | Breedte volgt de contentkolom; geen horizontale overflow buiten de kolom op oefenhoek-pagina’s (`overflow-x` begrensd).                                                                                                                                                                                                    |
| Site-titel | Het onderdeel `muziek` zet geen extra HTML-titel.                                                                                                                                                                                                                                                                          |

**Steekproef (chrome OK):** catalogus
`alleluia/9a-toon-1/groningen` — `.mvsa.svg` zonder zichtbare
partituurtitel/componist, zonder valse 4/4 (`TimeSig`); wel maatnummers +
volta. Enige `<title>mvsa-…</title>` is SVG-meta, geen bladkop. Technische
gap-audit: VSA-tooling
[`docs/plans/schermeisen-vereniging.md`](https://github.com/orthodox-ronl/VSA-tooling/blob/main/docs/plans/schermeisen-vereniging.md).

**Steekproef (S8 / schermstand):** catalogus `alleluia/9a-toon-8/groningen` —
default **SVG** toont sibling `.mvsa.svg`; via {} kun je **OSMG** (from-ir)
kiezen om te vergelijken. OSMD+adapter-doelbeeld blijft peilbaar met
`s8-alleluia-hide-check.mjs` op de S8-experimentbranch.

Als MuseScore een §4-regel die **wel** voor beide ketens bindend is nog
niet haalt: documenteer de gap of open een VSA-tooling-ticket — versoepel
de eis hier niet stilzwijgend. De tijdelijke OSMD-only-rijen (§4.2–4.3)
zijn géén vrijbrief om besluit 6 voor altijd af te zwakken.

---

## 6. Basispartituur-`.mscz` op het scherm

| Eis                    | Toelichting                                                                                                              |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Voorkeur keten         | Zelfde volgorde als §2: als er een canonieke `.mvsa` + from-ir is, wint OSMD; anders SVG; anders PDF van het mscz-spoor. |
| Alleen `.mscz` (+ PDF) | Scherm toont vaak de catalogus-PDF als blad — dat is **nood-fallback**, niet de eindlook.                                |
| Titel                  | Geen tweede Hugo-titel; PDF mag wel eigen bladkop hebben. SVG van dit spoor volgt §4 zodra die export er is.             |

**Nog niet normatief:** wanneer elke mscz-UV Score-IR/OSMD móet hebben vóór
publicatie. Publicatiecontrole eist nu from-ir voor canonieke `.mvsa`, niet
voor elke losse `.mscz`.

---

## 7. Tekstblad (`.tekstblad.md`)

| Eis    | Toelichting                                                                                |
| ------ | ------------------------------------------------------------------------------------------ |
| Scherm | Body van sibling `{stam}.tekstblad.md` (HTML via `bieb-score`). Er is geen OSMD/SVG-keten. |
| Inhoud | Leesbare liturgische tekst/dialoog.                                                        |
| Titel  | Zelfde paginaregels als §3.                                                                |
| Print  | Blad = `index.md.pdf` (nav); product-`.tekstblad.pdf` is geen schermviewer.            |

---

## 8. Checklist voor steekproef / review

Per geopende catalogus- of koormap-URL:

1. Juiste keten (§2): zie je OSMD waar from-ir bestaat, anders SVG, anders tekstblad-md / PDF?
2. Titels (§3): geen dubbele hoofdtitel; geen titel/credits **in** de partituurtekening?
3. Chrome gedeeld (§4.1): geen partijnamen, metronoom, maatsoort; Source Sans 3; maatnummers (minstens één per systeem, bij voorkeur begin systeem) — **op OSMD én SVG**?
4. Cues / centreren / wit (§4.2–4.3): leesbaar, niet afgekapt, niet over maatstrepen? Op OSMD: inklappen / cues niet meeschuiven / noten centreren. Op MuseScore-SVG: wrap + juiste maat volstaan nu; centreer/inklappen is best-effort tot scherm-SVG niet meer via MuseScore loopt.
5. Speelplan (§4.4): bij bron met `@speelplan` — zichtbare herhaal/volta/D.S./… (niet alleen in het MusicXML-bestand)? Steekproef minstens `alleluia/9a-toon-1/groningen`.
6. Kolom / fallback (§5–7): SVG/mscz/tekstblad zichtbaar in de kolom; geen extra site-titel door `muziek`?
7. Download/Print: nav-pagina-PDF; tip-icoon **♪** (en op catalogus **{}**) werken?

Neem in een steekproef **korte én lange** stukken mee (en bij mvsa bij voorkeur
ook een multi-`bieb`-pagina NL+KSL).

---

## 9. Wat dit document niet regelt

- CoriB (latere oefen-UI); **Oefenen** (♪) blijft externe `coria.nl`
- Inhoud/validiteit van VSA/MVSA-bronnen (validate / tooling)
- Layoutprofielen van MuseScore-print (`layout.cmd`, A4-PDF)
- Pixel-perfecte gelijkheid tussen SVG-fallback en OSMD (bewust niet verplicht)
- From-ir / speelplan-MusicXML-generatie (VSA-tooling)

**Niet meer «SVG open» (beide ketens):** Source Sans 3, cue-wrap op `...` /
juiste maat, chrome uit (titel/partijnamen/metronoom/maatsoort),
maatnummers — dat blijft §4 voor OSMD én MuseScore-SVG.

**Tijdelijk OSMD-only (niet «voor altijd open»):** cue-inklappen naar één
regel, cues niet meeschuiven na centreren, noten+lyrics centreren in de
maatbreedte — zie §4.2–4.3. Die regels blijven in de norm; MuseScore-SVG
mag ze nu missen. Zodra scherm-SVG niet meer via MuseScore loopt, gelden
ze weer voor beide ketens. Overige gaps: ticket/PR in VSA-tooling, geen
stille site-uitzondering.

Wijzigingen aan lookregels: PR op dit bestand; OSMD-gedrag in
`score-osmd.js` synchroon houden.
