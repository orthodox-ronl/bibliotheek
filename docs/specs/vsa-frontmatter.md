# VSA-/MVSA-frontmatter (proefschema)

Normatief voor **gedocumenteerde** sleutels. Alleen deze sleutels
mogen in `.vsa` / `.mvsa` (ook in de werkbank). Ongedocumenteerd =
weigeren of wegstrippen bij de canonieke-vorm-gate.

## Werkbank versus catalogus

| Fase | Frontmatter |
| ---- | ----------- |
| **Werkbank** | Volledig **skelet**: alle gedocumenteerde sleutels zichtbaar; leeg = `null`. Zo zie je wat je mag vullen. |
| **Catalogus** (canonieke vorm) | Alleen sleutels mét bruikbare inhoud. Lege/`null`-sleutels en import-rommel weg. |

## Migratie, daarna strippen

Op bestaande catalogusbestanden:

1. **Eerst migreren** — oude sleutels hernoemen/overzetten naar dit
   schema (zie [Migratiekaart](#migratiekaart-oude--nieuwe-sleutels));
   controleren dat afspelen/export nog klopt.
2. **Daarna strippen** — `scripts\frontmatter-canoniek.cmd` gooit
   lege en ongedocumenteerde sleutels weg.

Geen “strip-only” op de catalogus vóór stap 1.

## Canonieke-vorm-gate

Doel: bronbestanden **kleiner** maken door overtollige frontmatter weg
te gooien — **geen** notatie herschrijven.

| Actie | Wat |
| ----- | --- |
| Weg | `null`, `""`, lege mapping/lijst |
| Weg | Sleutels die niet in dit document staan (o.a. ruwe `herkomst_vsa_demo`, `stap2_*`, `extractie`, oude `template`) |
| Behouden | Gedocumenteerde sleutels met inhoud die aan het criterium voldoet |
| Controleren | `corpus_id` (als aanwezig): moet overeenkomen met de afgesproken identifier van dit stuk |

Tooling (lokaal):

1. Migreren: `scripts\migrate-vsa-frontmatter.cmd` (legacy +
   `herkomst_vsa_demo` → canonieke sleutels; daarna strip)
2. Alleen strippen: `scripts\frontmatter-canoniek.cmd`
   (`--check` melden; zonder vlag stdout of `--in-place`)

Koppeling aan `bieb accepteer`: nog te doen.

## Lagen (herinnering)

| Laag | Bestand | Taak |
| ---- | ------- | ---- |
| Cataloguspagina | `index.md` | vinden, publicatiestatus |
| VSA/MVSA | `*.vsa` / `*.mvsa` | afspelen, partituur, soort, toon, taal, bron, gelegenheid |
| Koormap-slot | koormap-`index.md` | lokale titel; `bieb id` |

---

## Elementcatalogus

Elk element: **criterium** (wanneer is de inhoud bruikbaar genoeg?) +
**voorbeelden** (zo verschillend mogelijk).

### Platte afspeel-sleutels (tijdelijk)

Waarvoor: huidige tooling/Coria leest nog plat `do` / `mode` / `tempo`.

| Sleutel | Criterium | Voorbeelden |
| ------- | --------- | ----------- |
| `do` | Toonhoogte-anker (notatienaam + octaaf). | `F4` · `D4` |
| `mode` | Toonsoortlabel dat de toolchain kent. | `major` · `minor` |
| `tempo` | Positief geheel; metronoomgetal. | `120` · `90` |

**Later:** onder `afspelen:` groeperen zodra tooling dat leest. Tot die
tijd: **plat houden** bij migratie (`muziek.do` → top-level `do`, niet
alleen naar `afspelen`).

### `afspelen` (mapping, optioneel / toekomst)

Zelfde inhoud als de platte sleutels, genest. Nu nog niet verplicht;
mag naast plat staan tijdens de overgang.

| Sleutel | Criterium | Voorbeelden |
| ------- | --------- | ----------- |
| `afspelen.do` | Zie `do`. | `F4` · `D4` |
| `afspelen.mode` | Zie `mode`. | `major` · `minor` |
| `afspelen.tempo` | Zie `tempo`. | `120` · `90` |

### `partituur` (mapping) — MuseScore-Engels

Waarvoor: velden die naar de **partituurkop / MuseScore-metadata**
gaan. Sleutelnamen volgen **nu** de Engelse MuseScore-termen (niet
vertalen). Latere wens: Nederlandse namen + expliciete mapping-tabel
naar MuseScore; voorlopig is de Engelse naam zelf de mapping.

| Sleutel | MuseScore (richting) | Criterium | Voorbeelden |
| ------- | -------------------- | --------- | ----------- |
| `partituur.title` | work / score title | Zinvolle kop op een los blad; geen pad-id. | `"Tropaar — H. Nikolaas (toon 4)"` · `"Derde antifoon — Geboorte Moeder Gods"` |
| `partituur.subtitle` | subtitle | Optioneel; uitvoeringsvorm/traditie zonder de hoofdtitel te herhalen. | `"Hemelum"` · `"Liturgikon"` |
| `partituur.composer` | composer | Menselijke toeschrijving of `Traditioneel`. | `"Traditioneel"` · `"V. Jewsewy"` |
| `partituur.arranger` | arranger | Wie de lokale zetting maakte/aanpaste. | `"Hemelum"` · `"Groningen"` |
| `partituur.layout` | (export, geen standaard meta) | Alleen als export het leest; anders weglaten. | `{ formaat: A4 }` |

**Niet** onder `partituur:`: `taal` — dat is een eigenschap van de VSA
zelf (zie hieronder).

### `titel` (string)

Waarvoor: korte naam in tooling/UI van het bronbestand (downloadcontext).

**Criterium:** herkenbaar zonder mapstructuur; mag afwijken van
`index.md` title en van `partituur.title`.

**Migratie:** als er een oude `title` / `identificatie.title` is → vul
**zowel** `titel` als `partituur.title` (zelfde tekst mag; later
bijschaven).

**Voorbeelden:** `"Nikolaas van Myra — tropaar toon 4"` ·
`"Wij verheerlijken U, bisschop Gregorios"`

### `taal` (string)

Waarvoor: taal van de gezongen tekst in **dit** bestand (ook bij
latere transliteratie: eigenschap van de VSA, niet van de partituurkop).

**Criterium:** korte code die de toolchain kent.

**Voorbeelden:** `nl` · `ksl`

### `toon` (geheel, optioneel)

Waarvoor: Oktoëchos-toon van dit stuk (eigenschap van de VSA).

**Criterium:** geheel getal **1 t/m 8**. Geen vrije labels (`"Toon 4"` →
`4`).

**Voorbeelden:** `4` · `1`

### `soort` (string)

Waarvoor: liturgische/genre-context in het bestand zelf.

**Criterium:** één canonieke term uit de org-glossary / catalogus-boom
(`tropaar`, `kondak`, `derde-antifoon`, `prijslied`, `moeder-godslied`,
…). Geen vrije synoniemen (`troparion` → `tropaar`). Oude `genre:` →
`soort`.

**Voorbeelden:** `tropaar` · `derde-antifoon`

### `soorten` (lijst, optioneel)

Waarvoor: zeldzame gevallen met meer dan één passende hoofdsoort.

**Criterium:** minstens twee geldige soort-termen; `soort` blijft de
**primaire**. Niet gebruiken om zoekaliases te proppen.

**Voorbeelden:** `[ tropaar, kleine-intocht ]` (hypothetisch) · weglaten

### `gelegenheid` (mapping of lijst van mappings, optioneel)

Waarvoor: als het stuk **inhoudelijk** aan één of meer
feesten/gebeurtenissen hangt (feesteigen), zodat titel, id of download
dat nog “weet”. Zelfde schema mag in frontmatter van bijbehorende
`.md`-bestanden staan als die dezelfde context vastleggen.

**Vorm:**

| Vorm | Wanneer |
| ---- | ------- |
| Eén mapping | Het stuk hangt aan precies één gelegenheid |
| Lijst van mappings | Meerdere gelegenheden (primair + secundair, of structureel bij meer dagen) |
| Platte string (oud) | Nog toegestaan; voorkeur is mapping met `naam` |

**Regel:** staat `gelegenheid` in de frontmatter, dan is **`naam`
verplicht** op elke mapping-entry. Die `naam` mag later in een titel of
id worden gebruikt. Weekdagliederen die alleen via de koormap worden
gepland: **geen** `gelegenheid` hier — dat is koormap.

| Deelveld | Verplicht? | Criterium | Voorbeelden |
| -------- | ---------- | --------- | ----------- |
| `naam` | **ja** (bij mapping) | Herkenbare aanduiding van de gelegenheid; bruikbaar in titel/id | `Kruisverheffing` · `Geboorte van de Moeder Gods` |
| `type` | nee | Soort dag of viering; vrije maar herhaalbare term | `feest` · `heiligendag` · `zondag` · `dinsdag` · `doordeweekse dag` |
| `datum` | nee | Kalenderdatum zonder jaartal; maand kort of lang; `oct` en `okt` beide ok | `26 sept` · `14 september` · `6 okt` · `6 oct` |
| `periode` | nee | Liturgische periode i.p.v. (of naast) een vaste kalenderdatum | `Grote Vasten` · `Paastijd` |
| `bron` | nee | Waar de gegevens over **deze gelegenheid** vandaan komen (niet hetzelfde als top-level `bron` van het zangstuk) | `Liturgikon` · `Meneon I` · `koortraditie Hemelum` |

**Voorbeelden:**

```yaml
gelegenheid:
  - naam: Kruisverheffing
  type: feest
  datum: 14 sept
  bron: Liturgikon
```

```yaml
gelegenheid:
  - naam: Verheerlijking op de berg Thabor
    type: feest
    datum: 6 aug
    bron: Liturgikon
  - naam: nafeest Transfiguratie
    type: feest
```

```yaml
# Oude platte vorm (nog ok):
gelegenheid: "8 sep — Geboorte van de Moeder Gods"
```

### `gelegenheden` (lijst van strings, optioneel)

Waarvoor: oudere/eenvoudige vorm voor meerdere platte labels.
**Voorkeur:** meerdere entries onder `gelegenheid` (lijst van mappings
met verplichte `naam`).

**Criterium:** elke string is een vaste, herhaalbare labelvorm.
Weekdagliederen alleen via koormap: niet hier.

**Voorbeelden:**
`[ "6 aug — Verheerlijking op de berg Thabor", "nafeest Transfiguratie" ]`

### `bron` (mapping)

Waarvoor: **herkomstspoor** — waarom dit bestand zo is (en een lichte
copyright-trace). Niet te zwaar tillen, wél niet weglaten.

Model:

1. **Uitgangspunt** — vaste, herkenbare bron (“waar kwam het vandaan?”).
2. **Afwijkingen** — alleen noemen als ze er toe doen (andere streepjes,
   herschikte tekstregel).
3. **Optioneel splitsen** — tekst vs melodie alleen als die echt van
   *andere* uitgaven komen.

Korte labels (`Liturgikon`, `Meneon I`, `Koormap Groningen`) worden
toegelicht op de pagina
[Uitgave-bronnen](/handleiding/start/uitgave-bronnen/)
(`data/bronnen.yaml`).

| Sleutel | Criterium | Voorbeelden |
| ------- | --------- | ----------- |
| `bron.uitgangspunt` | De standaardzin die als bronvermelding mag verschijnen (boek + plek, of koormap). Zelfde tekst gaat naar MusicXML `<source>` en MuseScore-meta `source`. | `"Liturgikon, p.58"` · `"Koormap Groningen"` · `"Meneon I, p.12-13"` |
| `bron.tekst` | Alleen als de **woorden** een andere bron hebben dan het uitgangspunt. | `"Liturgikon, p.271"` · `"Meneon I, p.12-13"` |
| `bron.melodie` | Alleen als de **melodie/zetting** een andere bron heeft dan het uitgangspunt. | `"Hemelum (Jewsewy)"` · `"VOKN-25"` |
| `bron.bewerking` | Wat er t.o.v. het uitgangspunt is aangepast (tekst en/of melodie). | `"tekst: Red, Heer, Uw volk i.p.v. Heer, red Uw volk"` · `"melodie: streepjes anders geplaatst"` |
| `bron.korte_vermelding` | Eén regel voor colofon als de deelveelden te lang zijn; **niet** als vervanging van `uitgangspunt` als die er wél is. | `"Liturgikon / praktijk Hemelum"` |

Lege deelveelden in catalogus weglaten; in werkbank `null` laten staan.

**Export:** `bron.uitgangspunt` → MusicXML
`<identification><source>` en MuseScore `metaTag name="source"`
(plus colofonregel “Bron: …” bij MSCZ-layout). Zie ook
[Migratiekaart](#migratiekaart-oude--nieuwe-sleutels).

### `corpus_id` (string, optioneel)

Waarvoor: vaste identifier van het stuk in een corpus/reeks (als die
er is).

**Criterium:** niet-lege string die **klopt** met de afgesproken id voor
dit zangstuk/deze uitvoeringsvorm. De gate mag controleren (niet
raden).

**Voorbeelden:** `"T4-11"` · `"VOKN-25"`

### `gebruikt-in` (lijst van catalogus-ids, optioneel)

Waarvoor: dit zangstuk/deze uitvoeringsvorm komt **ook** voor als
onderdeel van een ander catalogusstuk (typisch: een tropaar of kondak
dat in een feest-antifoon meekomt). De losse leaf blijft de canonieke
plaats; `gebruikt-in` wijst naar de samengestelde leaf(s).

**Regel:** staat een tropaar (of kondak) in een antifoon, dan moet die
ook als **zelfstandige** catalogus-leaf bestaan, mét `gebruikt-in` naar
die antifoon.

**Criterium:** elke entry is een volledig catalogus-id
`zangstuk/variant/uitvoeringsvorm` dat bestaat of bewust wordt
aangekondigd. Geen vrije tekst, geen bestandsnamen.

**Voorbeelden:**
`[ "derde-antifoon/geboorte-moeder-gods/liturgikon" ]` ·
`[ "derde-antifoon/kruisverheffing/liturgikon" ]`

### `zoek` (mapping, optioneel)

Waarvoor: alleen als pagina/zoekindex dit later uit VSA leest.
**Voorkeur:** synoniemen in `data/zoek-synoniemen.yaml` of op `index.md`.

| Sleutel | Criterium | Voorbeelden |
| ------- | --------- | ----------- |
| `zoek.aliases` | Alternatieve namen die iemand intikt. | `[ "Nicolaas", "Sinterklaas-tropaar" ]` |
| `zoek.tags` | Korte facetlabels, geen zinnen. | `[ "6-dec", "feestdag" ]` |

---

## Migratiekaart (oude → nieuwe sleutels)

| Oud (catalogus nu) | Nieuw | Opmerking |
| ------------------ | ----- | --------- |
| `do` / `mode` / `tempo` (plat) | ongewijzigd | Tijdelijk plat houden |
| `muziek.do` / `.mode` / `.tempo` | plat `do` / `mode` / `tempo` | Niet alleen naar `afspelen` |
| `title` / `identificatie.title` | `titel` **én** `partituur.title` | Beide vullen |
| `identificatie.composer` | `partituur.composer` | Engels |
| `identificatie.language` | `taal` | Top-level, Nederlands sleutelwoord |
| `identificatie.tone` / top-`tone` | `toon` | Geheel 1–8 |
| `genre` | `soort` | |
| `corpus_id` | `corpus_id` | Behouden; gate mag valideren |
| `template` | — | Weg (oud artefact) |
| `identificatie.bron` / `sources[]` / `bronnen[]` (duidelijke boek/koormap) | `bron.uitgangspunt` | Eerste bruikbare string; rest handmatig of → `bewerking` |
| Praktijk-/aanpassingszin | `bron.bewerking` | Bijv. “Praktijk in Groningen…” |
| Onduidelijk / gemengd | `bron.korte_vermelding` of handmatig | Liever niet raden naar tekst vs melodie |
| `herkomst_vsa_demo` | — | Weg na nuttige migratie; strip-fase |
| `alias` / `based-on` | — | **Uitgesteld** tot na afronden VSA-demo-import |
| MVSA `@bron "…"` | zelfde rol als `bron.uitgangspunt` | Blijft geldig in `.mvsa`-body; inhoud gelijk houden |

### Uitgesteld: `alias` / `based-on`

Opnieuw bekijken **nadat** de VSA-demo-import (stappen 3–5) is
afgerond. Herinnering vastgelegd voor die fase.

---

## Werkbank-skelet (alle sleutels)

Zie de voorbeeldbestanden:

- [`werkbank/voorbeeld-tropaar-geboorte-moeder-gods.vsa`](../voorbeelden/werkbank/voorbeeld-tropaar-geboorte-moeder-gods.vsa)
- [`werkbank/voorbeeld-moeder-godslied-transfiguratie.vsa`](../voorbeelden/werkbank/voorbeeld-moeder-godslied-transfiguratie.vsa)

Narratief: [`vsa-frontmatter-voorbeeld.md`](../voorbeelden/vsa-frontmatter-voorbeeld.md).
