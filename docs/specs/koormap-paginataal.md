# Koormap-paginataal (hoofdlijnen)

Normatief voor wat een beheerder mag schrijven in de Markdown van een
**koormap-pagina** (typisch `index.md` onder `content-source/koormappen/…`).
Dit document beschrijft de **taal** en het **paginacontract**. Het is nog
geen bouwplan: implementatie, shortcode-techniek en productpijplijn volgen
in een latere stap.

Leesbare context: handleiding
[Catalogus en koormappen](../../content-source/handleiding/start/catalogus-en-koormappen.md).
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
| Catalogus-blad | Bevat per definitie **één** uitvoeringsvorm; dezelfde knoppenidee: download/print = die pagina. |
| Layout | Titels, nummers, tussenkoppen en uitleg zet de beheerder in Markdown. Verwijzingen naar catalogusmuziek gaan via `bieb` (alleen het muzikale deel, plus expliciet gekozen metadata-onderdelen). |
| Navbalk | **Download** en **Print** horen bij de pagina (niet per `bieb`-blok). Bij elk muziekblok mogen **oefenacties** (Coria, audio, …) blijven staan. |

Plaatsing van Download/Print in de navigatie is onderdeel van dit contract;
de exacte UI volgt in het bouwplan.

---

## 3. Bestand en gewone Markdown

| Onderdeel | Afspraak |
| --- | --- |
| Bestand | Koormap-slot: `…/index.md` (of sectie-`_index.md` waar dat al de conventie is). |
| Frontmatter van de pagina | Blijft zoals nu (`title`, `linkTitle`, `weight`, `publicatiestatus`, `automatische_inhoud`, …). Dat is **pagina**-metadata van de koormap, niet de catalogus-frontmatter van een uitvoeringsvorm. |
| Body | Gewone Markdown (koppen, alinea’s, lijsten, tabellen, …) plus de shortcodes in dit document. |

Alles wat Hugo-Markdown al toestaat, blijft beschikbaar. Dit document
normatief alleen de **extra** koormap-taal.

---

## 4. Overzicht van de taal

| Element | Rol |
| --- | --- |
| `bieb` (kort, met `id`) | Één uitvoeringsvorm: standaard het muzikale deel, of een genoemd onderdeel — zie §5.1. |
| `bieb` … `/bieb` (blok) | Uitvoeringsvorm als **context**; daarbinnen onderdelen zonder telkens `id` — zie §5.2. |
| Onderdelen (`titel`, `muziek`, …) | Catalogusstukjes van de context-UV, of via `bieb id=…` met expliciet onderdeel — zie §5.3. |
| `pdf-pagina` | In de **PDF van deze pagina**: nieuw A4-blad. Op het web geen bladscheiding — zie §6. |
| `pdf-bijelkaar` … `/pdf-bijelkaar` | In de PDF: streef naar **één** A4 voor de inhoud van het blok — zie §7. |

**PDF-directives** hebben het voorvoegsel `pdf-`, zodat een beheerder meteen
ziet: dit stuurt de download/print, niet de lopende webtekst. (Hugo-shortcodes
gebruiken een koppelteken, geen punt: dus `pdf-pagina`, niet `pdf.pagina` —
zelfde bedoeling, wel in te typen in de sitebouw.)

---

## 5. `bieb` — catalogusinhoud op de pagina

Er zijn drie manieren om catalogusinhoud te zetten. Die mogen op één pagina
door elkaar.

### 5.1 Korte vorm met `id` (overal toegestaan)

```markdown
{{< bieb id="zangstuk/variant/uitvoeringsvorm" />}}
{{< bieb id="zangstuk/variant/uitvoeringsvorm" muziek />}}
{{< bieb id="zangstuk/variant/uitvoeringsvorm" titel />}}
{{< bieb id="zangstuk/variant/uitvoeringsvorm" veld "bron.uitgangspunt" />}}
```

| Eis | Toelichting |
| --- | --- |
| `id` | **Verplicht** in de korte vorm. Catalogus-id in drie lagen. |
| Self-close `/>` | **Verplicht** in Hugo voor de korte vorm (dezelfde shortcode bestaat ook als blok). |
| Zonder onderdeelnaam | Betekenis = het **muzikale deel** (+ oefenacties bij dat blok), gelijk aan expliciet `muziek`. |
| Met onderdeelnaam | Zelfde onderdelen als in §5.3 (`titel` / `title`, `muziek`, `bron`, `copyright`, `veld`, …). |
| Waar | **Buiten** én **binnen** een `bieb`-blok. Binnen een blok mag je zo “tussendoor” een **andere** uitvoeringsvorm tonen (bijvoorbeeld een tropaar uit een ander id midden in een derde-antifoon-blad), zonder de omringende context te veranderen. |

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
| `{{< veld "…" >}}` | `{{< bieb veld "…"  />}}` |

| Situatie | Regel |
| --- | --- |
| Binnen `bieb … /bieb` | Onderdeel zonder `id` → context-UV. |
| Buiten elk `bieb`-blok | Onderdeel **moet** via de korte vorm met `id` (§5.1), bijv. `{{< bieb id="…" titel />}}`. Kale `{{< titel >}}` is dan ongeldig. |
| Binnen een blok, andere UV | Gebruik §5.1 met ander `id`; context van het blok blijft staan. |

#### Bekende onderdelen (fase 1 — lijst mag groeien)

| Onderdeel | Aliassen | Betekenis |
| --- | --- | --- |
| `titel` | `title` | Catalogustitel van de uitvoeringsvorm, als platte tekst (geschikt in een Markdown-kop). |
| `muziek` | — | Partituurweergave (+ oefenacties bij dat blok). Geen paginatitel forceren. |
| `bron` | — | Korte bronvermelding van de uitvoeringsvorm. |
| `copyright` | — | Copyright-/licentieregel(s), alleen als de beheerder dit zet. |
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

## 6. `pdf-pagina` — bladscheiding alleen in de PDF

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

## 7. `pdf-bijelkaar` — streven naar één A4 in de PDF

```markdown
{{< pdf-bijelkaar >}}
…
{{< /pdf-bijelkaar >}}
```

| Weergave | Gedrag |
| --- | --- |
| Web | Geen speciale bladwerking; inhoud compact onder elkaar. |
| PDF | Streef ernaar alles binnen het blok op **één** A4 te houden. |

**Escalatie (bedoeling; details in bouwplan):**

1. Normale layout op één blad.
2. Indien nodig: beperkt verkleinen tot een vaste ondergrens.
3. Past het dan nog niet: alsnog een tweede blad; **geen** muziek
   afsnijden of weglaten.

Zonder `pdf-bijelkaar` mag de PDF-flow gewoon afbreken tussen blokken.
`pdf-pagina` binnen `pdf-bijelkaar` is tegenstrijdig; het bouwplan moet dat
weigeren of eenduidig oplossen.

Latere PDF-directives krijgen hetzelfde voorvoegsel (`pdf-…`).

---

## 8. Voorbeelden (bedoeling)

### 8.1 Vredeslitanie — metadata + bladscheiding in de PDF

```markdown
---
title: "Vredeslitanie"
linkTitle: "Vredeslitanie"
weight: 1
publicatiestatus: reviewable
automatische_inhoud: false
---

{{< bieb id="ektinia/vrede/hemelum" >}}

# (1) {{< titel >}}

{{< muziek >}}

{{< /bieb >}}

{{< pdf-pagina >}}

{{< bieb id="ektinia/vrede/hemelum-ksl" >}}

# (1) {{< bieb title />}}

{{< bieb bron />}}

{{< bieb muziek />}}

{{< /bieb >}}
```

Web: beide rubrieken onder elkaar. PDF: blad 1 NL, blad 2 KSL.

### 8.2 Eerste kleine litanie — geen bladscheiding, wél bij elkaar

(KSL-uitvoeringsvorm ontbreekt; `ektinia/tweede-kleine/hemelum` als stand-in.)

```markdown
{{< pdf-bijelkaar >}}

{{< bieb id="ektinia/eerste-kleine/hemelum" >}}
# {{< titel >}}
{{< muziek >}}
{{< /bieb >}}

{{< bieb id="ektinia/tweede-kleine/hemelum" >}}
# {{< title >}}
{{< muziek >}}
{{< /bieb >}}

{{< /pdf-bijelkaar >}}
```

### 8.3 Alleen muziek (korte vorm)

```markdown
# Eerste kleine litanie

{{< bieb id="ektinia/eerste-kleine/hemelum" />}}
```

### 8.4 Tussendoor een andere uitvoeringsvorm (derde antifoon-achtig)

Buitenste blok = lopende antifoon; middenin een tropaar uit een ander id;
daarna weer de context van het blok.

```markdown
{{< bieb id="derde-antifoon/zondag/hemelum" >}}

# {{< titel >}}

{{< muziek >}}

## Tropaar (uit de catalogus, ander id)

{{< bieb id="tropaar/zondag-toon-1/groningen" muziek />}}

{{< muziek >}}

{{< /bieb >}}
```

(Exacte id’s en of “tweede `muziek`” het vervolg van dezelfde UV is, hangt
af van latere `@blok`-selectie; het voorbeeld toont alleen het
**context**-idee.)

### 8.5 Onderdeel buiten elk blok (altijd met `id`)

```markdown
# {{< bieb id="ektinia/vrede/hemelum" titel />}}

{{< bieb id="ektinia/vrede/hemelum" muziek />}}
```

---

## 9. Uitbreidingspunten (bewust open)

| Uitbreiding | Richting |
| --- | --- |
| Meer korte namen i.p.v. `veld` | Tabel: alias → frontmatter-pad. |
| Parameters op `muziek` / `tekst` | Selectie van `@blok` (en presentatie-overrides op deze pagina). |
| Meer `pdf-…` directives | Zelfde familie als `pdf-pagina` / `pdf-bijelkaar`. |
| Defaults van korte `bieb` zonder onderdeel | Blijft “muziek”; eventueel later andere default = aparte beslissing. |
| Catalogus-blad | Zelfde taal; context kan impliciet de enige UV van dat blad zijn. |

Niet in deze authoring-taal (bewust):

- parallelle mappen `fragmenten/` / `afdruk/` / `oefenen/` voor dezelfde
  koormap-pagina;
- een apart booklet-/YAML-compositieproduct naast `index.md`;
- layout alleen in MuseScore + PDF’s plakken als hoofdstrategie voor
  koormap-pagina’s;
- VSA-tooling-directives (`:::include`, `:::pagebreak:::`, …) als
  schrijftaal in Hemelum-koormap-`index.md` (zie §10).

---

## 10. Relatie tot `:::include` en verwante directives

| Middel | Rol |
| --- | --- |
| Koormap-paginataal (dit document) | Wat beheerders in koormap- (en later catalogus-)`index.md` schrijven. |
| `:::include`, `:::pagebreak:::`, `:::print-only:::`, … | Blijven nuttig in **VSA-tooling**: demo’s, Markdown→PDF-bladen buiten de koormap, interne pijplijn, tests. |
| Hemelum-koormap-`index.md` | Schrijf **niet** in `:::include`-stijl; gebruik `bieb` / `pdf-…`. |

**Opruimen?** Niet de tooling-directives zelf afschaffen. Wel:

- geen nieuwe koormap-content in die stijl beginnen;
- of de PDF-pijplijn *intern* nog `pagebreak`-achtige middelen gebruikt, is
  een bouwdetail, geen beheerderstaal.

---

## 11. Status

| Onderdeel | Status |
| --- | --- |
| Paginacontract; `bieb` kort met `id` (+ onderdeel); `bieb`-blok; onderdelen; `veld`; `pdf-pagina`; `pdf-bijelkaar` | **Afgesproken** |
| Shortcode-implementatie (web) + print-CSS | **Gedaan (M1)** — self-closing `bieb` schrijven met `/>` (Hugo) |
| Nav Download/Print | **Gedaan (M2)** |
| Pagina-PDF-pijplijn | **Gedaan (M3)** — `scripts\pagina-pdf.cmd` |
| Proefslots + docs | **Gedaan (M4)** — o.a. vredeslitanie, eerste-kleine-litanie; `proef-ektinias` verwijderd |
| `@blok`-selectie en presentatie-overrides | **Gereserveerd** |
