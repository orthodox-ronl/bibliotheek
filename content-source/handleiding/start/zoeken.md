---
title: "Zoeken in de catalogus"
linkTitle: "Zoeken"
weight: 85
nav_sort: weight
---

Met **Zoeken** vind je een uitvoeringsvorm in de catalogus: op titel, op
catalogus-id, of op een stukje gezongen tekst. Je opent Zoeken via de knop
in de site-kop, of via [Catalogus → Zoeken](/catalogus/zoeken/).

Deze pagina legt eerst uit wat een bezoeker mag verwachten. Daarna volgt
de technische specificatie, zodat je kunt beoordelen of het zoeken nog
past bij wat jullie nodig hebben.

{{< cue >}}
- Ingang voor koorleden: knop **Zoeken** in de kop, of `/catalogus/zoeken/`
- Korte tip: klik op **?** naast de knop Zoeken
- Indexbestand: `static\zoek\index.json` (bij Pages-deploy opnieuw gebouwd)
- Synoniemen: [`data/zoek-synoniemen.yaml`](https://github.com/orthodox-ronl/bibliotheek/blob/development/data/zoek-synoniemen.yaml)
- Gezongen tekst: sibling `{stam}.vsa.lyrics.txt` / `.mvsa.lyrics.txt` /
  `.mscz.lyrics.txt` — zie [lyrics-products](/handleiding/scripts/lyrics-products/)
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
   tijdens het bouwen van de index).

Daarnaast:

- **Hoofdletters** doen niet mee.
- **Leestekens** worden genegeerd.
- **Synoniemen** uit `data\zoek-synoniemen.yaml` (bijv. *alleluja* →
  *alleluia*, *litanie* → *ektinia*) worden op zoekterm én op
  geïndexeerde tekst toegepast.
- **Omgewisselde woorden** kunnen nog matchen via een gesorteerde
  tokensleutel (zelfde woorden, andere volgorde).

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
- Geen server-side ranking of typfout-correctie buiten de synoniemenlijst.

## Specificatie (detail)

### Bouwen van de index

Script: `python scripts\build_zoek_index.py` (ook via `lyrics-products`,
`products` / `all-products`, en bij elke Pages-deploy vóór Hugo).

Bronnen: elke uitvoeringsvorm-leaf
`content-source\catalogus\<zangstuk>\<variant>\<uitvoeringsvorm>\index.md`
(uitsluiting: paden onder `input\`). Mappen met
`artefacten_handmatig: true` doen **wél** mee in de zoekindex (alleen
productscripts slaan die over). Gezongen tekst wordt toegevoegd als er in
die bladermap een canonieke `.vsa`, `.mvsa` of basispartituur-`.mscz` is
(lyrics-sibling of live `vsa text` / MusicXML).
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
| `title` / `linkTitle` | Uit leaf-frontmatter (fallback variant / id) |
| `zangstukTitle` / `variantTitle` | Titels van de bovenliggende `_index.md` |
| `status` | `publicatiestatus` van de leaf |
| `text` | Genormaliseerde zoekblob (titels + id-woorden + gezongen tekst) |
| `tokens` | Gesorteerde unieke tokens van `text` (woordvolgorde-varianten) |
| `incipit` | Eerste ~12 woorden van de platte brontekst (niet genormaliseerd voor weergave) |
| `audio` | Site-absoluut pad naar voorkeurs-`.mp3` in de bladermap, of leeg |

Audio-voorkeur in de bladermap: `.mvsa.mp3`, dan `.mscz.mp3`, dan
`.vsa.mp3`, dan overige `.mp3`.

### Normalisatie

Zowel bij indexeren als bij de zoekterm in de browser:

1. `casefold` / lowercase.
2. Leestekens → spatie.
3. Tokens opsplitsen; elk token via synoniemenmap (zo aanwezig).
4. Weer samenvoegen tot één string (`text`) of gesorteerde unieke tokens
   (`tokens` / `tokenSort` in JS).

### Scoring in de browser (`static/js/catalogus-zoek.js`)

Globale index één keer laden per pagina (gedeeld door kop-zoeken en
pagina-formulier). Per entry een score > 0 om als treffer te tonen
(max. 40 getoond, hoogste score eerst, dan id).

Indicatie van de gewichten (kan wijzigen; dit is de huidige code):

- Treffer in titel/linkTitle: zwaar
- Treffer in id (met `/` en `-` als spaties): middel
- Treffer in genormaliseerde `text`: middel
- Exacte match op gesorteerde tokens: bonus
- Deelmatches op query-woorden: lichte bonus naar verhouding

Synoniemen uit de JSON worden op de zoekterm toegepast vóór scoren.

### UI-ingangen

| Plek | Template / script |
| --- | --- |
| Catalogus-zoekpagina | shortcode `zoek-formulier` |
| Site-kop | partial `site-zoek` |
| Tip **?** | partial `zoek-help-tip` → deze handleidingpagina |
| Gedrag | `static/js/catalogus-zoek.js` |

`data-base` op `.catalogus-zoek` is het pad van `site.BaseURL` (eindigend
op `/`), zodat links onder preview/branch kloppen.

### Beheer: synoniemen en lyrics bijwerken

1. Pas `data\zoek-synoniemen.yaml` aan (lowercase sleutels).
2. Vernieuw lyrics waar nodig: `scripts\lyrics-products.cmd`.
3. Of alleen de index: `python scripts\build_zoek_index.py`.
4. Commit `static\zoek\index.json` als je lokaal wilt spiegelen; op Pages
   wordt de index sowieso opnieuw gebouwd.

## Zie ook

- [lyrics-products](/handleiding/scripts/lyrics-products/) — gezongen tekst als sibling
- [Catalogus en koormappen](/handleiding/start/catalogus-en-koormappen/) — model en `bieb`
- [Publicatiestatus](/handleiding/publiceren/2-status-en-check/) — betekenis van statuslabels
- [Zangstuk-soorten](/handleiding/start/zangstuk-soorten/) — o.a. synoniem litanie/ektinia

{{< navbuttons "Catalogus|/handleiding/start/catalogus/" "Catalogus en koormappen|/handleiding/start/catalogus-en-koormappen/" >}}
