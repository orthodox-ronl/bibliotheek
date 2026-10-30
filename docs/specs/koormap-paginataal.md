# Koormap-paginataal (hoofdlijnen)

Normatief voor wat een beheerder mag schrijven in de Markdown van een
**koormap-pagina** (typisch `index.md` onder `content-source/koormappen/…`).
Dit document beschrijft de **taal** en het **paginacontract**.
`bieb`, `pdf-…` en `kop` zijn afgesproken én geïmplementeerd.
Beheerder-spiekbriefje: handleiding *Koormap-blad schrijven*. Oude
layout-shortcodes en class `koormap-tussenkop` zijn opgeruimd (M7).

Leesbare context: handleiding
[Catalogus en koormappen](../../content-source/handleiding/start/catalogus-en-koormappen.md)
en spiekbriefje
[Koormap-blad schrijven](../../content-source/handleiding/start/koormap-blad.md).
Terminologie: zangstuk-id → variant-id → uitvoeringsvorm-id →
representatie-id
([bron glossary](https://github.com/orthodox-ronl/bron/blob/main/docs/specs/terminologie.md)).

---

## 1. Doel

Een koormap-pagina is één **getoonde pagina**: de beheerder stelt samen wat
het koor op die liturgische plek ziet en meeneemt. Dezelfde bron bepaalt:

1. de **webweergave** (onder elkaar, zonder print-bladscheidingen);
2. de **download/print van deze pagina** (A4-PDF van wat op de pagina staat,
   met eventuele bladregels die de beheerder zet).

De catalogus blijft de bron van partituren en metadata. De koormap kopieert
geen basispartituur-bestanden; zij **verwijst** en **legt uit** (titels,
volgorde, bladindeling).

---

## 2. Paginacontract

| Regel | Betekenis |
| --- | --- |
| Download / print | Altijd de **getoonde pagina** (koormap-slot of catalogus-blad). |
| Inhoud | Een koormap-pagina mag **meerdere** zangstukken, varianten en/of uitvoeringsvormen bevatten. Daar legt het systeem geen limiet op. |
| Catalogus-blad | Bevat per definitie **één** uitvoeringsvorm; download/print van het blad = die pagina (`index.md.pdf`). |
| Layout | Bladtitels en rubrieken tussen partituren: shortcode `kop` (§6). Uitleg en gewone structuur: Markdown. Catalogusmuziek: `bieb`. Geen HTML voor uitlijning of kopgrootte. |
| Navbalk | **Download pagina** en **Print pagina** horen bij de pagina (niet per `bieb`-blok). Bij elk muziekblok: tip-icoon **♪** voor oefenen/beluisteren. |

Plaatsing van Download/Print in de navigatie is onderdeel van dit contract.

---

## 3. Bestand en gewone Markdown

| Onderdeel | Afspraak |
| --- | --- |
| Bestand | Koormap-slot: `…/index.md` (of sectie-`_index.md` waar dat al de conventie is). |
| Frontmatter van de pagina | Blijft zoals nu (`title`, `linkTitle`, `weight`, `publicatiestatus`, `automatische_inhoud`, …). Dat is **pagina**-metadata van de koormap, niet de catalogus-frontmatter van een uitvoeringsvorm. Optioneel: `pdf_bestandsnaam` (zie hieronder). |
| Body | Gewone Markdown (koppen, alinea’s, lijsten, tabellen, …) plus de shortcodes in dit document. |

### Voorgestelde naam bij «Download pagina»

Het bestand naast de Markdown blijft `index.md.pdf` (Hugo page
resource). Bij **Download pagina** stelt de site een bestandsnaam voor
volgens deze volgorde (koormap-slot):

1. frontmatter `pdf_bestandsnaam` — als die gezet is;
2. anders frontmatter `title`;
3. anders de **mapnaam** van de pagina (laatste map in het pad).

Op een **catalogus**-blad geldt stap 2 als de afgeleide bladtitel
(zelfde als de H1), niet frontmatter `title`.

Zonder `.pdf` in die waarde wordt die extensie toegevoegd. Tekens die in
bestandsnamen niet mogen (`\ / : * ? " < > |`) worden door een streepje
vervangen.

Voorbeeld (expliciete downloadnaam, anders dan de paginatitel):

```yaml
---
title: "Vredeslitanie"
pdf_bestandsnaam: "Vredeslitanie NL+KSL"
weight: 1
publicatiestatus: reviewable
automatische_inhoud: false
---
```

Alles wat Hugo-Markdown al toestaat, blijft beschikbaar. Dit document
normatief alleen de **extra** koormap-taal. Markdown-`#` / `##` mag voor
**uitleg** en hiërarchie; voor de **bladlook** van titels en tussenrubrieken
(web én pagina-PDF): `kop`.

---

## 4. Overzicht van de taal

| Element | Rol |
| --- | --- |
| `bieb` (kort, met `id`) | Één uitvoeringsvorm: standaard het muzikale deel, of een genoemd onderdeel — zie §5.1. |
| `bieb` … `/bieb` (blok) | Uitvoeringsvorm als **context**; daarbinnen onderdelen zonder telkens `id` — zie §5.2. |
| Onderdelen (`titel`, `muziek`, …) | Catalogusstukjes van de context-UV, of via `bieb id=…` met expliciet onderdeel — zie §5.3. |
| `kop` … `/kop` | Bladtitel of rubriek: uitlijning en grootte — zie §6. |
| `witruimte` | Extra verticale ruimte tussen onderdelen (web én pagina-PDF) — zie §7. |
| `pdf-pagina` | In de **PDF van deze pagina**: nieuw A4-blad. Op het web geen bladscheiding — zie §8. |
| `pdf-bijelkaar` … `/pdf-bijelkaar` | In de PDF: streef naar **één** A4 voor de inhoud van het blok — zie §9. |

**PDF-directives** hebben het voorvoegsel `pdf-`, zodat een beheerder meteen
ziet: dit stuurt de download/print, niet de lopende webtekst. (Hugo-shortcodes
gebruiken een koppelteken, geen punt: dus `pdf-pagina`, niet `pdf.pagina` —
zelfde bedoeling, wel in te typen in de sitebouw.)

---

## 5. `bieb` — catalogusinhoud op de pagina

Er zijn drie manieren om catalogusinhoud te zetten. Die mogen op één pagina
door elkaar.

### 5.1 Korte vorm met `id` (alleen muziek)

```markdown
{{< bieb id="zangstuk/variant/uitvoeringsvorm" />}}
```

| Eis | Toelichting |
| --- | --- |
| `id` | **Verplicht**. Catalogus-id in drie lagen. |
| Self-close `/>` | **Verplicht** in Hugo voor deze korte vorm (dezelfde shortcode bestaat ook als blok). |
| Betekenis | Het **muzikale deel** (+ oefenacties bij dat blok). |

Hugo staat **geen** mix toe van named `id="…"` en positional `titel` /
`colofon` / `muziek` op één shortcode. Andere onderdelen: gebruik het
**blok** (§5.2) met geneste `{{< titel >}}` / `{{< colofon >}}` / enz.

Een geneste korte `bieb id="…"` **wijzigt de openstaande blok-context niet**.
Na die korte shortcode blijven volgende `{{< titel >}}` / `{{< muziek >}}`
horen bij het **buitenste** `bieb … /bieb`-blok.

### 5.2 Blokvorm (context)

```markdown
{{< bieb id="zangstuk/variant/uitvoeringsvorm" >}}
…
{{< /bieb >}}
```

| Eis | Toelichting |
| --- | --- |
| `id` | Verplicht op de openings-shortcode. |
| Context | Onderdelen **zonder** eigen `id` (§5.3) verwijzen naar **deze** uitvoeringsvorm. |
| Meerdere blokken | Op één pagina mogen meerdere `bieb`-blokken staan, elk met eigen `id`. |
| Overige Markdown | Koppen, tekst en shortcodes die géén onderdeel zijn, blijven gewone paginainhoud. |

### 5.3 Onderdelen (met of zonder `bieb`-prefix)

Twee schrijfwijzen zijn **gelijkwaardig** wanneer er een openstaande
`bieb`-blokcontext is:

| Zonder prefix | Met prefix |
| --- | --- |
| `{{< titel >}}` | `{{< bieb titel  />}}` |
| `{{< title >}}` | `{{< bieb title  />}}` |
| `{{< muziek >}}` | `{{< bieb muziek  />}}` |
| `{{< bron >}}` | `{{< bieb bron  />}}` |
| `{{< copyright >}}` | `{{< bieb copyright  />}}` |
| `{{< colofon >}}` | `{{< bieb colofon  />}}` |
| `{{< veld "…" >}}` | `{{< bieb veld "…"  />}}` |

| Situatie | Regel |
| --- | --- |
| Binnen `bieb … /bieb` | Onderdeel zonder `id` → context-UV. |
| Buiten elk `bieb`-blok | Open een `bieb`-blok met `id` en zet daarin het onderdeel (`{{< titel >}}` / `{{< colofon >}}`, …). Hugo staat **geen** mix van named `id=` en positional `titel`/`colofon` op één self-closing shortcode toe. |
| Binnen een blok, andere UV | Gebruik §5.1 met ander `id`; context van het blok blijft staan. |

#### Bekende onderdelen (fase 1 — lijst mag groeien)

| Onderdeel | Aliassen | Betekenis |
| --- | --- | --- |
| `titel` | `title` | Catalogustitel van de uitvoeringsvorm, als platte tekst (geschikt in een Markdown-kop of binnen `kop`). |
| `muziek` | — | Partituurweergave (+ tip-icoon **♪** bij dat blok). Geen paginatitel forceren. **Schermketen en look:** [schermpartituur.md](schermpartituur.md) (normatief). Kort: voorkeur ``.mvsa.from-ir.musicxml`` → OSMD; anders één tall SVG (``.mvsa.svg`` / ``.vsa.svg`` / ``.mscz.svg`` / legacy bladermap; geen ``*-N.svg``); tekstblad-md of PDF alleen als nood-fallback. Blad download/print: nav **Download/Print pagina** (`index.md.pdf`), geen score-knop naar product-PDF. Artifact Score-IR: `vsa mvsa score-ir … --musicxml` in VSA-tooling. |
| `bron` | — | Korte bronvermelding van de uitvoeringsvorm. |
| `copyright` | — | Korte copyright-/licentieregel (footer-achtig), alleen als de beheerder dit zet. Verwijst vaak naar het colofon («zie colofon»). |
| `colofon` | — | Volledige colofontekst: uit MuseScore-colofon-VBox indien aanwezig; anders opgebouwd uit copyright-notice, eredienst-kopieertoestemming, Bron en Bibliotheek-id. Scherm én `index.md.pdf`. |
| `veld` | — | Generieke frontmatter; zie §5.4. |

Welke sleutels later **ook zonder** `veld` een eigen korte naam krijgen,
komt in een uitbreidingstabel. Tot die tijd: `veld`.

#### `muziek` — latere parameters (gereserveerd)

In een volgende fase mag `muziek` parameters krijgen om delen van het
bronbestand te kiezen of op **deze pagina** bij te sturen (bijv. `@blok`,
`@tempo`, openings-`@tekst`), zonder de catalogusbron te wijzigen. Die
parameters horen op `muziek` (en eventueel later `tekst`), niet op `veld`.

### 5.4 `veld` — frontmatter van de uitvoeringsvorm

```markdown
{{< veld "bron.uitgangspunt" >}}
{{< bieb veld "bron.uitgangspunt" />}}
{{< bieb id="ektinia/vrede/hemelum" veld "bron.uitgangspunt" />}}
```

| Regel | Toelichting |
| --- | --- |
| Argument | Pad of sleutel in de frontmatter van de bedoelde uitvoeringsvorm. Canonieke sleutels: [VSA-/MVSA-frontmatter](vsa-frontmatter.md). |
| Context | Met open blok: die UV. Zonder blok: alleen met `id=` op de korte `bieb`. |
| Uitvoer | Tekst op de pagina (en in download/print van de pagina). |
| Ontbrekend | Voorspelbaar gedrag (leeg vs. fout) in het bouwplan. |
| Geen notatie | `veld` leest geen `@blok`-inhoud; daarvoor later `muziek` / `tekst`. |

---

## 6. `kop` — bladtitel en rubriek

Eén shortcode voor titels en tussenrubrieken op het blad. Geen aparte
namen (`bladkop` / `tussenkop`): defaults + optionele knoppen volstaan.

```markdown
{{< kop >}}(1a) Vredeslitanie{{< /kop >}}
{{< kop links middel >}}Toon 1{{< /kop >}}
{{< kop >}}{{< titel >}}{{< /kop >}}
```

| Eis | Toelichting |
| --- | --- |
| Blokvorm | Openen met `{{< kop … >}}`, sluiten met `{{< /kop >}}`. Inhoud = de zichtbare tekst (platte tekst, of een genest onderdeel zoals `titel`). Geen geneste Markdown-opmaak in v1 (`**vet**`); wel HTML-inline desgewenst. |
| Standaard | **Midden** uitgelijnd, grootte **groot** (typische bladtitel). |
| Knoppen | Optionele woordjes uit twee vaste sets (volgorde vrij; hoogstens één per set). Onbekende woorden: fout bij bouw. |
| Web en PDF | Zelfde look op de pagina en in de pagina-download. |
| Geen kleur (v1) | Geen kleurenknoppen en geen vrije kleurcodes. Eventuele vaste rollen (bijv. `zacht`) later via uitbreidingstabel. |

### 6.1 Knoppen

| Soort | Toegestane woorden | Betekenis |
| --- | --- | --- |
| Uitlijning | `links` · `midden` · `rechts` | Horizontale plaatsing van de tekst. |
| Grootte | `groot` · `middel` · `klein` | Visuele trap (ongeveer bladkop / rubriek / label). Geen HTML-jargon (`h1`/`h2`) in de beheerderstaal. |

Voorbeelden:

```markdown
{{< kop >}}(1a) Vredeslitanie{{< /kop >}}
{{< kop links middel >}}Toon 1{{< /kop >}}
{{< kop midden klein >}}zie ommezijde{{< /kop >}}
{{< kop rechts middel >}}Kerkslavisch{{< /kop >}}
```

Typische rubriek tussen partituren (zoals “Toon 1”): `links` + `middel`.

### 6.2 Wat `kop` niet is

| Niet | Wel |
| --- | --- |
| Vervanging van catalogus-`titel` als databron | `titel` blijft het catalogusonderdeel; `kop` is alleen presentatie eromheen. |
| Vervanging van alle Markdown-koppen | `#` / `##` blijven voor uitleg en structuur buiten bladlook. |
| HTML / CSS door de beheerder | Geen `<h1 style="…">`, geen `class="koormap-tussenkop"`. |

### 6.3 Verouderde middelen (verwijderd of niet schrijven)

| Oud / elders | Op koormap-pagina’s |
| --- | --- |
| `<h1 style="text-align: center">…</h1>` e.d. | `kop` (desgewenst met knoppen) |
| `<p class="koormap-tussenkop">…</p>` | `{{< kop links middel >}}…{{< /kop >}}` (class verwijderd) |
| Shortcodes `pagebreak`, `pagina`, `keep-together`, `print-only`, `web-only` | Verwijderd; gebruik `pdf-pagina` / `pdf-bijelkaar` |

Markdown-`#` blijft toegestaan voor uitleg; voor bladlook: `kop`.
`pdf.cmd` leest nog legacy HTML-`h1` en `#` als fallback.

---

## 7. `witruimte` — ruimte tussen onderdelen

Lege Markdown-regels tussen shortcodes geven **geen** zichtbare ruimte
(Hugo/CSS slaat ze over). Voor een bewuste tussenruimte:

```markdown
{{< witruimte >}}
{{< witruimte groot >}}
{{< witruimte klein >}}
```

| Eis | Toelichting |
| --- | --- |
| Korte vorm | Geen inhoud; optioneel één knop. |
| Standaard | **middel**. |
| Knoppen | `klein` · `middel` · `groot` (hoogstens één). |
| Web en PDF | Zelfde intentie: zichtbare verticale ruimte op de pagina en in de pagina-download. |

### 7.1 NL + KSL op één slot (conventie)

Per uitvoeringsvorm: `kop` met de titel **in de taal van de lyrics** (niet
de labels «Nederlands» / «Kerkslavisch»), daarna korte `bieb` met `/>`
wanneer alleen muziek nodig is, en `witruimte` ertussen. Zie handleiding
*Koormap-blad*. Grote stukken: `pdf-pagina` tussen de talen (elk een eigen
A4); geen `pdf-bijelkaar` om NL+KSL te forceren.

---

## 8. `pdf-pagina` — bladscheiding alleen in de PDF

```markdown
{{< pdf-pagina >}}
```

| Weergave | Gedrag |
| --- | --- |
| Web | Geen zichtbare bladscheiding; geen extra lege ruimte door deze shortcode. |
| PDF van deze pagina | Hier begint een **nieuw A4-blad**. |

De beheerder gebruikt dit wanneer blokken in de download **niet** op hetzelfde
blad mogen staan (bijv. NL en KSL elk een eigen blad).

---

## 8a. Relatie tot kale muziek-SVG en Score-IR

**Schermlook (normatief in deze repo):** [schermpartituur.md](schermpartituur.md)
— keten OSMD → SVG → PDF-fallback, titels, OSMD-cues/centreren, en wat
SVG/mscz/tekstblad wél en nog niet eisen.

Org-/tooling-richting (print vs scherm): kale tall-SVG (catalogusproduct)
voor scherm-fallback én print-bouwsteen. `pdf.cmd` bouwt `index.md.pdf` uit
die sibling-SVG + Markdown (geen catalogus-PDF-plak; geen MuseScore als de
SVG er al is). Compose snijdt op systeembrenzen, zodat rest-ruimte na
titel/proza op dezelfde A4-pagina wél met muziek wordt gevuld. Ontbreekt de
SVG: alleen lokaal opnieuw exporteren. Zie
[VSA-tooling — kale-muziek-svg-en-uitgaven](https://github.com/orthodox-ronl/VSA-tooling/blob/main/docs/plans/kale-muziek-svg-en-uitgaven.md)
§4 en [partituur-ir §7](https://github.com/orthodox-ronl/VSA-tooling/blob/main/docs/plans/partituur-ir.md).

**Catalogus-leaves** (één uitvoeringsvorm per `index.md`): body zonder
dubbele Markdown-H1; PDF-titel uit afgeleide catalogustitel wanneer de
Markdown geen `kop`/`#` meer heeft — plan
[catalogus-index-md-pdf.md](../plans/catalogus-index-md-pdf.md).

---

## 9. `pdf-bijelkaar` — streven naar één A4 in de PDF

```markdown
{{< pdf-bijelkaar >}}
…
{{< /pdf-bijelkaar >}}
```

| Weergave | Gedrag |
| --- | --- |
| Web | Geen speciale bladwerking; inhoud compact onder elkaar. |
| PDF van deze pagina (`pdf.cmd`) | Streef ernaar alles binnen het blok op **één** A4 te houden. |

Dit is een **koormap-keuze**, geen cataloguswijziging. De canonieke
catalogus-producten (`.mvsa.pdf` / `.mvsa.svg` zonder compact) blijven het
losse oefenblad. Alleen de pagina-download (en later eventueel een tijdelijke
export voor die download) mag dichter gezet worden.

### Koppeling met VSA-tooling (`--compact`)

Wanneer `pdf.cmd` muziek binnen `pdf-bijelkaar` opnieuw exporteert of
compositieert voor één A4, gebruikt die pijplijn de tooling-vlag
**`--compact`** op `vsa mvsa svg` / `vsa mvsa pdf` (dichte Style-baseline:
kleinere systeemafstand en paginamarges). Zie VSA-tooling CLI
[`mvsa svg` / `mvsa pdf`](https://github.com/orthodox-ronl/VSA-tooling/blob/main/docs/reference/cli/mvsa.md)
en [`.mscz` Style-opties](https://github.com/orthodox-ronl/VSA-tooling/blob/main/docs/formats/mscz.md).

| Laag | Rol |
| --- | --- |
| Shortcode `pdf-bijelkaar` | Intentie van de beheerder: “dit hoort op één blad”. |
| Tooling `--compact` | Concrete dichte export (marges/systeemafstand). |
| Latere fine-tuning | Optionele parameters op `pdf-bijelkaar` of aparte `pdf-…`-directives die losse Style-vlaggen doorgeven (`--min-system-distance`, marges, …). Tot die tijd: alleen `--compact`. |

**Escalatie (bedoeling):**

1. Zet de muziek in het blok dicht met `--compact` (plus koppen uit `kop` of Markdown).
2. Past het dan nog niet op één A4: alsnog een tweede blad; **geen** muziek
   afsnijden of weglaten.
3. Fijnere overrides (tussen “normaal” en `--compact`) komen later via
   shortcode-parameters, niet via een tweede catalogus-variant.

Zonder `pdf-bijelkaar` mag de PDF-flow gewoon afbreken tussen blokken en
blijft de standaard (ruimere) catalogus-layout gelden.

`pdf-pagina` binnen `pdf-bijelkaar` is tegenstrijdig; het bouwplan moet dat
weigeren of eenduidig oplossen.

Latere PDF-directives krijgen hetzelfde voorvoegsel (`pdf-…`).

---

## 10. Voorbeelden (bedoeling)

### 10.1 Vredeslitanie — NL + KSL op één PDF-blad

```markdown
---
title: "Vredeslitanie"
linkTitle: "Vredeslitanie"
weight: 1
publicatiestatus: reviewable
automatische_inhoud: false
---

{{< pdf-bijelkaar >}}

{{< kop >}}(1a) Vredeslitanie{{< /kop >}}

{{< bieb id="ektinia/vrede/hemelum" >}}

{{< muziek >}}

{{< /bieb >}}

{{< bieb id="ektinia/vrede/hemelum-ksl" >}}

{{< muziek >}}

{{< /bieb >}}

{{< /pdf-bijelkaar >}}
```

Web: beide rubrieken onder elkaar. PDF: streven naar **één** A4
(`pdf-bijelkaar` → tooling `--compact` in `pdf.cmd`). Geen `pdf-pagina`
binnen dit blok.

Wil je NL en KSL elk op een **eigen** blad: laat `pdf-bijelkaar` weg en zet
`{{< pdf-pagina >}}` tussen de twee `bieb`-blokken.

### 10.2 Eerste kleine litanie — catalogustitel in `kop`

```markdown
{{< pdf-bijelkaar >}}

{{< bieb id="ektinia/eerste-kleine/hemelum" >}}
{{< kop >}}{{< titel >}}{{< /kop >}}
{{< muziek >}}
{{< /bieb >}}

{{< bieb id="ektinia/tweede-kleine/hemelum" >}}
{{< kop >}}{{< titel >}}{{< /kop >}}
{{< muziek >}}
{{< /bieb >}}

{{< /pdf-bijelkaar >}}
```

### 10.3 Alleen muziek (korte vorm)

```markdown
{{< kop >}}Eerste kleine litanie{{< /kop >}}

{{< bieb id="ektinia/eerste-kleine/hemelum" />}}
```

### 10.4 Rubrieken tussen partituren (alleluia-achtig)

```markdown
{{< kop >}}(9b) Alleluia{{< /kop >}}

{{< pdf-bijelkaar >}}

{{< kop links middel >}}Toon 1{{< /kop >}}
{{< bieb id="alleluia/9a-toon-1/groningen" />}}

{{< kop links middel >}}Toon 2{{< /kop >}}
{{< bieb id="alleluia/9a-toon-2/groningen" />}}

{{< /pdf-bijelkaar >}}
```

### 10.5 Tussendoor een andere uitvoeringsvorm (derde antifoon-achtig)

Buitenste blok = lopende antifoon; middenin een tropaar uit een ander id;
daarna weer de context van het blok.

```markdown
{{< bieb id="derde-antifoon/zondag/hemelum" >}}

{{< kop >}}{{< titel >}}{{< /kop >}}

{{< muziek >}}

{{< kop links middel >}}Tropaar (uit de catalogus, ander id){{< /kop >}}

{{< bieb id="tropaar/zondag-toon-1/groningen" muziek />}}

{{< muziek >}}

{{< /bieb >}}
```

(Exacte id’s en of “tweede `muziek`” het vervolg van dezelfde UV is, hangt
af van latere `@blok`-selectie; het voorbeeld toont alleen het
**context**-idee.)

### 10.6 Onderdeel buiten elk blok (via `bieb`-blok)

```markdown
{{< bieb id="ektinia/vrede/hemelum" >}}

{{< kop >}}{{< titel >}}{{< /kop >}}

{{< muziek >}}

{{< /bieb >}}
```

---

## 11. Uitbreidingspunten (bewust open)

| Uitbreiding | Richting |
| --- | --- |
| Meer korte namen i.p.v. `veld` | Tabel: alias → frontmatter-pad. |
| Parameters op `muziek` / `tekst` | Selectie van `@blok` (en presentatie-overrides op deze pagina). |
| Meer `pdf-…` directives / params op `pdf-bijelkaar` | Zelfde familie; fine-tuning Style-vlaggen naast de default `--compact`. |
| Defaults van korte `bieb` zonder onderdeel | Blijft “muziek”; eventueel later andere default = aparte beslissing. |
| Catalogus-blad | Zelfde taal; context kan impliciet de enige UV van dat blad zijn. |
| `kop`: vaste kleurrollen | Eventueel later `zacht` (secundair); geen vrije kleurcodes. |
| `kop`: preset-woord | Eventueel later één woord (bijv. `tussen` = `links` + `middel`) — geen tweede shortcode. |

Niet in deze authoring-taal (bewust):

- parallelle mappen `fragmenten/` / `afdruk/` / `oefenen/` voor dezelfde
  koormap-pagina;
- een apart booklet-/YAML-compositieproduct naast `index.md`;
- layout alleen in MuseScore + PDF’s plakken als hoofdstrategie voor
  koormap-pagina’s;
- VSA-tooling-directives (`:::include`, `:::pagebreak:::`, …) als
  schrijftaal in Hemelum-koormap-`index.md` (zie §12);
- HTML/CSS voor bladtitels en tussenrubrieken (zie §6.3).

---

## 12. Relatie tot `:::include` en verwante directives

| Middel | Rol |
| --- | --- |
| Koormap-paginataal (dit document) | Wat beheerders in koormap- (en later catalogus-)`index.md` schrijven. |
| `:::include`, `:::pagebreak:::`, `:::print-only:::`, … | Blijven nuttig in **VSA-tooling**: demo’s, Markdown→PDF-bladen buiten de koormap, interne pijplijn, tests. |
| Hemelum-koormap-`index.md` | Schrijf **niet** in `:::include`-stijl; gebruik `bieb` / `kop` / `pdf-…`. |

**Opruimen?** Niet de tooling-directives zelf afschaffen. Wel:

- geen nieuwe koormap-content in die stijl beginnen;
- of de PDF-pijplijn *intern* nog `pagebreak`-achtige middelen gebruikt, is
  een bouwdetail, geen beheerderstaal;
- oude Hugo-shortcodes (`pagebreak`, `keep-together`, `pagina`, `print-only`,
  `web-only`) zijn verwijderd; schrijf `pdf-…` / `kop`.

---

## 13. Status

| Onderdeel | Status |
| --- | --- |
| Paginacontract; `bieb` kort met `id` (+ onderdeel); `bieb`-blok; onderdelen; `veld`; `pdf-pagina`; `pdf-bijelkaar` | **Afgesproken** |
| Shortcode `kop` (+ knoppen uitlijning/grootte; geen kleur v1) | **Afgesproken** |
| Shortcode `witruimte` (`klein` / `middel` / `groot`) | **Afgesproken + web/PDF** |
| Shortcode-implementatie (web) + print-CSS (`bieb` / `pdf-…`) | **Gedaan (M1)** — self-closing `bieb` schrijven met `/>` (Hugo) |
| Nav Download/Print | **Gedaan (M2)** |
| Pagina-PDF-pijplijn | **Gedaan (M3)** — `scripts\pdf.cmd` (koormap); catalogus-dekking + titel zonder `#`: [catalogus-index-md-pdf.md](../plans/catalogus-index-md-pdf.md) |
| Proefslots + docs (`bieb` / `pdf-…`) | **Gedaan (M4)** — o.a. vredeslitanie, eerste-kleine-litanie; `proef-ektinias` verwijderd |
| Shortcode `kop` + CSS; proefslots HTML → `kop` | **Gedaan (M5)** — vredeslitanie, eerste-kleine-litanie, alleluia |
| Handleiding + spiekbriefje voor beheerders | **Gedaan (M6)** — `handleiding/start/koormap-blad.md` |
| Migratie/opruiming oude layout | **Gedaan (M7)** — `kop` in `pagina_pdf`; CSS/shortcodes `pagebreak`/`keep-together`/`pagina`/`print-only`/`web-only`/`koormap-tussenkop` weg; legacy `#`/`<h1>` blijft fallback in `pagina_pdf` |
| `@blok`-selectie en presentatie-overrides | **Gereserveerd** |
