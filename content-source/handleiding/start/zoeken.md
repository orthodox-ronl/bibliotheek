---
title: "Zoeken in de catalogus"
linkTitle: "Zoeken"
weight: 85
nav_sort: weight
---

Met **Zoeken** vind je een uitvoeringsvorm in de catalogus: op titel, op
catalogus-id, of op een stukje gezongen tekst. Je opent Zoeken via de knop
in de site-kop, of via [Catalogus → Zoeken](/overzichten/zoeken/).

Deze pagina legt eerst uit wat een bezoeker mag verwachten. Daarna volgt
de technische specificatie, zodat je kunt beoordelen of het zoeken nog
past bij wat jullie nodig hebben.

**Wie leest wat?**

| Jij bent … | Lees … |
| --- | --- |
| Koorlid dat een stuk zoekt | De korte tips op de zoekpagina [Zoeken](/overzichten/zoeken/), en hieronder *Waarop matcht een zoekterm?* en *Hoe staan de treffers op volgorde?* |
| Beheerder van de catalogus | *Hoofdlijnen* en *Beheer: iets wordt niet gevonden*; het script staat bij [zoek-index](/handleiding/scripts/zoek-index/) |
| Ontwikkelaar of AI-assistent | *Specificatie (detail)*; de logica staat in `static/js/catalogus-zoek-kern.js` en `scripts/build_zoek_index.py` |

{{< cue >}}
- Ingang voor koorleden: knop **Zoeken** in de kop, of `/overzichten/zoeken/`
- Korte tip: ga met de muis over de knop **Zoeken** in de kop (popover);
  in het zoekvenster zelf staat nog een **?** bij het zoekveld
- Indexbestand: `static\zoek\index.json` (bij Pages-deploy opnieuw gebouwd)
- Synoniemen: [`data/zoek-synoniemen.yaml`](https://github.com/orthodox-ronl/bibliotheek/blob/development/data/zoek-synoniemen.yaml)
- Gezongen tekst: sibling `{stam}.vsa.lyrics.txt` / `.mvsa.lyrics.txt` /
  `.mscz.lyrics.txt` — zie [products (lyrics)](/handleiding/scripts/lyrics-products/)
- Zoeklogica: `static\js\catalogus-zoek-kern.js`; test:
  `node --test tests\zoek-kern.test.mjs` (draait ook mee in `pytest`)
{{< /cue >}}

## Hoofdlijnen

### Wat zit er in de zoekindex?

Elke **uitvoeringsvorm** in `content-source\catalogus\` (bladermap met
`index.md`) kan in de index komen. Per treffer zie je onder meer de titel,
de publicatiestatus, soms een stukje begrotekst (incipit uit lyrics van
`.vsa` / `.mvsa` / `.mscz`), het catalogus-id, en soms een beluister-knop.

Zoeken is **client-side**: de browser laadt één JSON-bestand en filtert
lokaal. Er is geen aparte zoekserver.

### Waarop matcht een zoekterm?

Je mag zoeken op:

1. **Titel** van de uitvoeringsvorm, en titels van variant en zangstuk
   erboven.
2. **Catalogus-id** in de vorm `zangstuk/variant/uitvoeringsvorm` (streepjes
   en schuine strepen worden als spaties behandeld).
3. **Gezongen tekst** uit de lyrics-sibling van een `.vsa` / `.mvsa` /
   basis-`.mscz` (of, als die sibling nog ontbreekt, een verse tekst-export
   tijdens het bouwen van de index). Staat er naast een partituur ook een
   canonieke `.vsa` of `.mvsa`, dan wint die notatie — niet de (vaak
   langere) `.mscz`-lyrics met foute lettergreep-koppeling.

Daarnaast geldt:

- **Hoofdletters** doen niet mee.
- **Accenten en trema's** doen niet mee: *mysterien* vindt *Mysteriën*.
- **Leestekens** worden genegeerd.
- **Streepjes binnen een woord** doen niet mee. Je mag zoeken op
  *eeuwige*, *eeu-wige* of *eeu-wi-ge*: alle drie geven hetzelfde
  resultaat. Dat geldt ook voor echte samenstellingen: *Drie-eenheid*,
  *drieeenheid* en *drie eenheid* vinden dezelfde uitvoeringsvormen.
- **Een zoekwoord matcht vanaf het begin van een woord.** *eeuw* vindt
  *eeuwige*; *wige* vindt dat woord niet.
- **Synoniemen** uit `data\zoek-synoniemen.yaml` (bijv. *alleluja* →
  *alleluia*, *litanie* → *ektinia*) worden op zoekterm én op
  geïndexeerde tekst toegepast.

### Hoe staan de treffers op volgorde?

1. Bovenaan staan de uitvoeringsvormen waarin **alle** woorden uit je
   zoekterm voorkomen.
2. Daaronder, na de tussenkop *Ook gevonden, maar niet met alle
   woorden*, staan de uitvoeringsvormen met **zoveel mogelijk** van je
   woorden. Bij een zoekterm van twee woorden telt één woord al mee; bij
   langere zoektermen moet minstens de helft van de woorden voorkomen.
   Een zoekterm met alleen korte woordjes als *de* of *u* levert geen
   deeltreffers op.
3. Bij evenveel gevonden woorden komt vóór wie je woorden **aaneen** en
   **in de gezochte volgorde** bevat, en daarna wie ze in de titel of het
   id heeft.

De lijst toont telkens 40 treffers. Met de knop *Toon meer* zie je de
volgende 40.

### Wat toont een treffer?

| Onderdeel | Bedoeling |
| --- | --- |
| Titel (link) | Gaat naar de cataloguspagina van die uitvoeringsvorm |
| Publicatiestatus + **?** | Wat *concept* / *reviewable* / … betekent; feedback-links |
| Incipit | Eerste woorden van de gezongen tekst |
| ▶ | Preview-audio beluisteren (als er een `.mp3` bij de bladermap staat) |
| Snelheid | Afspeelsnelheid voor zoektreffers in dit tabblad |
| Catalogus-id + **?** | Klik op het id om `{{</* bieb id="…" */>}}` te kopiëren voor een koormap |

Op GitHub Pages (productie, preview en branch-previews) moeten trefferlinks
onder de site-baseURL blijven — zie de Cursor-regel *interne links ×
baseURL*.

### Wat zoeken niet doet (nu)

- Geen full-text over koormappen of handleidingpagina’s.
- Geen typfout-correctie buiten de synoniemenlijst.

## Specificatie (detail)

### Bouwen van de index

Script: `python scripts\build_zoek_index.py` (ook via `products --kinds lyrics`,
`products` / `products --kinds all`, en bij elke Pages-deploy vóór Hugo).

Bronnen: elke uitvoeringsvorm-leaf
`content-source\catalogus\<zangstuk>\<variant>\<uitvoeringsvorm>\index.md`
(uitsluiting: paden onder `input\`). Mappen met
`manueel: true` doen **wél** mee in de zoekindex (alleen
productscripts slaan die over). Gezongen tekst wordt toegevoegd als er in
die bladermap een canonieke `.vsa`, `.mvsa` of basispartituur-`.mscz` is
(lyrics-sibling of live `vsa text` / MusicXML). Bij meerdere bronnen in
dezelfde bladermap: eerst `.mvsa`, dan `.vsa`, dan `.mscz`; binnen die
keuze de langste bruikbare tekst. **Afgeleide notatie telt nooit als
tekstbron:** `{stam}.vsa.mvsa` (de schets die uit een `.vsa` wordt
gemaakt) en `{stam}.mscz.mvsa` (de importvorm van een `.mscz`) worden
overgeslagen. Daarin stonden woorden soms in stukjes (*on wankelbare*),
waardoor zoeken op het hele woord misliep. Zie
[Catalogus: één canonieke notatiebron](https://github.com/orthodox-ronl/bibliotheek/blob/development/docs/catalogus-notatiebron.md).
Uitvoer: `static\zoek\index.json` met o.a.:

| Veld | Inhoud |
| --- | --- |
| `generated_at` | Tijdstempel (UTC) |
| `count` | Aantal entries |
| `synonyms` | Map uit `data/zoek-synoniemen.yaml` (ook naar de client) |
| `entries[]` | Zie hieronder |

### Velden per entry

| Veld | Betekenis |
| --- | --- |
| `id` | `zangstuk/variant/uitvoeringsvorm` |
| `url` | Site-absoluut pad `/catalogus/<id>/` (client plakt `data-base` ervoor) |
| `title` / `linkTitle` | Afgeleid uit bron/id (zelfde algoritme als de site) |
| `zangstukTitle` / `variantTitle` | Afgeleid uit de bovenliggende mapnamen |
| `status` | `publicatiestatus` van de leaf |
| `text` | Genormaliseerde zoekblob (titels + id-woorden + gezongen tekst) |
| `incipit` | Eerste ~12 woorden van de platte brontekst (niet genormaliseerd voor weergave) |
| `audio` | Site-absoluut pad naar voorkeurs-`.mp3` in de bladermap, of leeg |

Audio-voorkeur in de bladermap: `.mvsa.mp3`, dan `.mscz.mp3`, dan
`.vsa.mp3`, dan overige `.mp3`.

### Normalisatie

Zowel bij indexeren (`scripts\build_zoek_index.py`, functie
`normalize_text`) als in de browser (`static/js/catalogus-zoek-kern.js`,
functie `norm`) gelden dezelfde stappen. Een test legt vast dat ze
hetzelfde resultaat geven.

1. Kleine letters.
2. Accenten en trema's weg (*mysteriën* → *mysterien*).
3. `_` weg (het melisma-streepje in *verhoor_*).
4. Een woord met harde streepjes (*Drie-eenheid*) wordt los én aaneen
   opgeslagen: *drie eenheid drieeenheid*.
5. Overige leestekens → spatie.
6. Per woord de synoniemenmap (zo aanwezig).
7. Alles weer samenvoegen tot één string (`text`).

De zoekterm doorloopt dezelfde stappen, met één verschil: een woord met
streepjes in de zoekterm (*eeu-wi-ge*) wordt aaneen gezocht (*eeuwige*)
én als losse woorden (*eeu wi ge*), zodat je ook een id of een echte
samenstelling kunt plakken.

### Zoeken en rangschikken in de browser

De logica staat in `static/js/catalogus-zoek-kern.js` (zonder
schermcode, zodat ze getest kan worden); `static/js/catalogus-zoek.js`
toont de uitkomst. De index wordt één keer per pagina geladen (gedeeld
door kop-zoeken en pagina-formulier).

Een zoekwoord telt als gevonden als een woord in de titel, het id of de
gezongen tekst ermee **begint**. Een uitvoeringsvorm is een treffer als
alle woorden gevonden zijn, of — bij meer dan één woord — als minstens
de helft gevonden is (en dan niet alleen korte woordjes). Sorteervolgorde:
aantal gevonden woorden, dan aaneen-in-volgorde, dan gevonden woorden in
de gezochte volgorde, dan treffer in titel boven id boven tekst, dan het
id.

### UI-ingangen

| Plek | Template / script |
| --- | --- |
| Catalogus-zoekpagina | shortcode `zoek-formulier` |
| Site-kop | partial `site-zoek` |
| Tip **?** | partial `zoek-help-tip` → deze handleidingpagina |
| Zoeklogica (normaliseren, scoren) | `static/js/catalogus-zoek-kern.js` |
| Gedrag en weergave | `static/js/catalogus-zoek.js` |

`data-base` op `.catalogus-zoek` is het pad van `site.BaseURL` (eindigend
op `/`), zodat links onder preview/branch kloppen.

### Beheer: iets wordt niet gevonden

Zoek je als beheerder een stuk dat niet verschijnt, loop dan deze punten
na, in deze volgorde:

1. **Staat de uitvoeringsvorm in de index?** Open `static\zoek\index.json`
   en zoek op het id. Ontbreekt het? Draai `python scripts\build_zoek_index.py`
   (of `check`) en kijk of het id nu wel verschijnt.
2. **Staat het woord in de gezongen tekst?** Open het bestand
   `{stam}.vsa.lyrics.txt` of `{stam}.mvsa.lyrics.txt` naast de bron. Staat
   het woord daar in stukjes (*on wankelbare*) of niet, dan zit de fout in
   de bron of in tooling, niet in de zoekfunctie. Vernieuw de lyrics met
   `scripts\products.cmd --kinds lyrics`.
3. **Welke bron wordt gelezen?** Alleen de canonieke bron: `.mvsa`, `.vsa`
   of basis-`.mscz`. Afgeleide bestanden als `{stam}.vsa.mvsa` tellen nooit mee.
4. **Het veld `zoektekst` bovenin een `.vsa` of `.mvsa`** is bedoeld voor
   zoeken in de editor (bijvoorbeeld Ctrl+Shift+F in VS Code). De
   zoekfunctie op de site leest dat veld niet; die leest de lyrics-bestanden.
5. **Spelling- of naamvarianten** (*alleluja*/*alleluia*, *litanie*/*ektinia*)
   los je op met een regel in `data\zoek-synoniemen.yaml`.

### Beheer: synoniemen en lyrics bijwerken

1. Pas `data\zoek-synoniemen.yaml` aan (lowercase sleutels).
2. Vernieuw lyrics waar nodig: `scripts\products.cmd --kinds lyrics`.
3. Of alleen de index: `python scripts\build_zoek_index.py`.
4. Commit `static\zoek\index.json` als je lokaal wilt spiegelen; op Pages
   wordt de index sowieso opnieuw gebouwd.

## Zie ook

- [products (lyrics)](/handleiding/scripts/lyrics-products/) — gezongen tekst als sibling
- [Catalogus en koormappen](/handleiding/start/catalogus-en-koormappen/) — model en `bieb`
- [Publicatiestatus](/handleiding/publiceren/2-status-en-check/) — betekenis van statuslabels
- [Zangstuk-soorten](/handleiding/start/zangstuk-soorten/) — o.a. synoniem litanie/ektinia

{{< navbuttons "Catalogus|/handleiding/start/catalogus/" "Catalogus en koormappen|/handleiding/start/catalogus-en-koormappen/" >}}
