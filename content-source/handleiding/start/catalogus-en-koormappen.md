---
title: "Catalogus en koormappen"
linkTitle: "Catalogus en koormappen"
weight: 25
---

# Catalogus en koormappen

{{< cue >}}
- **Bibliotheek** = alles wat jullie *hebben* (uitvoeringsvorm + id + partituur)
- **Koormap** = geordende *view* voor één gelegenheid of thema (navigatie + leesbladen)
- Een uitvoeringsvorm mag in de catalogus staan **zonder** koormap
- In een koormap is een liturgische plek vaak een **hoofdstuk** (sectie) met
  kindpagina’s of een **compositieblad** (markdown + shortcodes)
{{< /cue >}}

**Wat je nu doet:** het model kennen waarmee de bibliotheek-site werkt, zodat
publicatie, ids en navigatie niet door elkaar lopen.

## Drie invalshoeken

| Wie | Vraag | Ingang |
| --- | --- | --- |
| Beheerder | Wat hebben we? Welk id gebruik ik? | [Bibliotheek](/catalogus/), [Id-register](/catalogus/id-register/), special pages |
| Koor (in situ) | Wat zingen we in welke volgorde? | Koormap, nu vooral [liturgie zondag](/koormappen/hemelum/liturgie-zondag/) / [weekdagen](/koormappen/hemelum/liturgie-weekdagen/) |
| Individueel koorlid | Wat moet / wil ik oefenen? | Koormap *of* bibliotheek (ook stukken die nog in geen map zitten) |

## Kernregel

De bibliotheek is de **bron van waarheid**. Koormappen zijn **views**: ze
bevatten geen tweede kopie van de basispartituur-bestanden, maar verwijzen met
`bieb` naar `zangstuk/variant/uitvoeringsvorm`.

Een uitvoeringsvorm mag publiek in de catalogus staan terwijl **geen
enkele** koormap ernaar wijst. Dat is bewust: ontdekking en latere opname in
een map (feest, collectie, parochiekeuze) komen daarna.

## Bouwstenen in een koormap

Een koormap is geen platte lijst “één zangstuk = één pagina”. De
[liturgiemappen Hemelum](/koormappen/hemelum/liturgie/) (zondag /
weekdagen) zijn een
**inhoudsopgave van liturgische plekken**. Een titel in die inhoudsopgave
kan naar één zangstuk wijzen, of naar een **hoofdstuk** met meerdere
keuzes (bijvoorbeeld eerste antifoon: weekdagen, zondag, later feestdagen).

| Bouwsteen | Bestand | Rol |
| --- | --- | --- |
| **Koormap-root** | `koormappen/hemelum/liturgie-zondag\_index.md` (of `liturgie-weekdagen`) | Handmatige inhoudsopgave van die map |
| **Koormap-sectie** | map met `_index.md` | Liturgische plek / hoofdstuk; tekst plus kindlijst, of eigen TOC |
| **Slot-pagina** | map met `index.md` | Lees- of oefenblad: markdown plus `bieb` (geen catalogus/`lokaal/`-include) |

**Sectie** (`_index.md`): zet `automatische_inhoud: true` als de layout de
kindpagina’s mag tonen (voorbeeld:
`koormappen/hemelum/liturgie-zondag\eerste-antifoon\`). Zet `false` als je zelf de
inhoudsopgave van dat hoofdstuk schrijft (zoals de root van een liturgiemap).
Gebruik in sectie-`_index.md` geen `#`-titel in de body; die titel komt uit
de layout.

**Slot-pagina** (`index.md`): gewone markdown. Daartussen kun je één of
meer shortcodes `bieb` zetten. Elke shortcode zet eerst de knoppen
**Oefenen** / **Beluisteren** / **Downloaden** / **Printen** voor die
uitvoeringsvorm, en
daarna de PDF of VSA-SVG. De partituur blijft in de catalogus; de
slot-pagina is alleen de view. Navigatie naar Bibliotheek of Koormap loopt
via de sticky broodkruimelregel bovenaan de pagina.

### Boom of compositieblad?

Twee manieren om meerdere uitvoeringsvormen op **één liturgische plek** te
tonen —zelfde mechaniek, andere leeservaring:

| Patroon | Wanneer | Voorbeeld |
| --- | --- | --- |
| **Boom** | De zanger kiest één variant (of bladert per kind) | Cherubijnenhymne: sectie → 15b, 15c, …; antifoon: weekdagen / zondag |
| **Compositieblad** | Eén pagina bundelt een set (proza + scores) | Prokimens voor de hele week op één `index.md`, met shortcode per weekdag |

Voorbeeld compositieblad (schets):

```markdown
# Prokimen weekdagen (Kiev, Groningen)

## Maandag
{{</* bieb id="prokimen/9a-maandag/groningen" */>}}

## Dinsdag
{{</* bieb id="prokimen/9a-dinsdag/groningen" */>}}
```

**Let op:** elke `bieb` op dezelfde pagina heeft een **eigen** knoppenrij
direct boven de partituur van die uitvoeringsvorm. Je hoeft geen aparte
kindpagina’s te maken alleen om knoppen te scheiden.

### Alias-varianten

Soms heeft **dezelfde variant** meerdere namen. Voorbeeld: de tropaar-variant
`maandag-toon-4` is dezelfde variant als `heilige-engelen-toon-4` (de tropaar
van de Heilige Engelen, gezongen op maandag). Dat is een alias op
**variant-niveau**, niet een tweede uitvoeringsvorm.

Dan:

- partituren (`.vsa`, PDF, …) staan **alleen** bij de canonieke variant, hier
  de uitvoeringsvorm `tropaar/maandag-toon-4/hemelum`;
- de alias-variant heeft alleen een `_index.md` met frontmatter
  `alias_van: tropaar/maandag-toon-4` — geen map `hemelum/`, geen `index.md`,
  geen partituur;
- de bibliotheek-index van het zangstuk (`tropaar/`, `kondak/`, …) noemt
  **beide** varianten; achter de alias-naam staat dat het een alias is.

Shortcode `bieb` krijgt een uitvoeringsvorm-id (drie lagen). Wie de
alias-variant in dat id zet, bijvoorbeeld
`tropaar/heilige-engelen-toon-4/hemelum`, wordt herschreven naar de canonieke
uitvoeringsvorm. Product-tools (`vsa-products`, basispartituur-producten) slaan
alias-varianten over: daar is niets te genereren.

`check` weigert een alias-variant die toch een uitvoeringsvorm-map of
partituur bevat. Dat patroon mag voor elk zangstuk waarvan een variant
onder meerdere namen bekend is.

## Titels en frontmatter in de catalogus

Elke catalogus-pagina (`_index.md` of leaf-`index.md`) heeft minstens:

| Veld | Rol |
| --- | --- |
| `title` | Volledige, leesbare paginatitel (vaak de H1) |
| `linkTitle` | Korte naam in navigatie, kindlijsten en broodkruimels |
| `publicatiestatus` | Wat koorleden mogen verwachten (`voorzien` / `concept` / `reviewable` / `productie`) |
| `automatische_inhoud` | Sectie: meestal `true` (kindlijst). Leaf: altijd `false` (score via `bieb`) |

Ids komen uit het **pad** (`zangstuk/variant/uitvoeringsvorm`), niet uit
`title` of `linkTitle`. Tooling en shortcode `bieb` gebruiken het pad.

### Naamgeving per laag

| Laag | `title` | `linkTitle` |
| --- | --- | --- |
| **Zangstuk** | Liturgisch nummer + naam, bijv. `11 Dringende litanie` | Zelfde of iets korter voor de hoofdnavigatie |
| **Variant** | Leesbare variantnaam, bijv. `Alleluia toon 1 (Kiev)` of `Kondak zondag toon 1` | Kort voor de kindlijst: `Toon 1`, of de folder-id zoals `zondag-toon-1` |
| **Uitvoeringsvorm (leaf)** | Volledige titel mét herkomst, bijv. `Alleluia toon 1 (Kiev, Groningen)` | Label van de uitvoeringsvorm met hoofdletter: `Groningen`, `Hemelum`, `Liturgikon` — **niet** de mapnaam in kleine letters en **niet** alleen een slug |

`title` en `linkTitle` mogen verschillen: lange titel op de pagina, korte
label in de navigatie. Dat is bewust (alleluia’s, prokimens, troparen).

### Variant-id `default`

Als er nog maar één variant is, heet de map vaak `default`. Op die
variant-`_index.md` mag `title` / `linkTitle` tijdelijk `default` blijven;
de leaf draagt dan de echte liturgische titel. Zodra er een tweede variant
komt, geef je `default` een echte naam of hernoem je de map.

### Wat `check` (nog) niet doet

`scripts\check.cmd` controleert **geen** frontmatter-schema (geen verplichte
velden, geen capitalisatie van `linkTitle`). Wel verwacht de handleiding die
velden op elke catalogus- en koormap-pagina. Mis je `publicatiestatus` op
een **leaf**, dan ontbreekt de `?` naast de titel; de build faalt daar niet
op. Op sectie-overzichten en hulppagina’s (zoals zoeken) zie je die tip
niet, ook al staat het veld wel in de frontmatter.

## Soorten koormap (classificatie)

Zelfde mechaniek, andere bedoeling — geen nieuwe id-laag:

| Type | Ordening | Voorbeeld |
| --- | --- | --- |
| Liturgisch | Volgorde in de dienst | Liturgiemap Hemelum |
| Feest / kalender | Orde van die dag of cyclus | Pasen, 15 augustus |
| Collectie | Thematisch | Alle cherubijnen, troparen toon 1–8 |
| Parochiekeuze | Wat *dit* koor deze periode zingt | “Hemelum najaar”, “Zwolle-cherubijn” |

Optioneel later: frontmatter `type:` op de koormap-`_index` (`liturgie`,
`feest`, `collectie`, `parochie`).

«Collectie» hier is dus een *view* in de koormap, geen extra maplaag boven
zangstukken in de catalogus. Zie besluit 5 in
[Zangstuk-soorten](/handleiding/start/zangstuk-soorten/).

## Wat de catalogus-root toont

De root van de catalogus is **geen** sitemap van alle stubs. Koorleden zien
daar vooral **oefenbare** zangstukken (nette titel, liturgienummer-volgorde).
Voorzien-items en technische registers staan onder
[Speciaal](/catalogus/speciaal/) en het
[Id-register](/catalogus/id-register/).

## Special pages

Automatisch bijgehouden (bij elke sitebuild):

| Pagina | Inhoud |
| --- | --- |
| [Voorzien](/catalogus/speciaal/voorzien/) | Zangstukken zonder oefenbare inhoud |
| [Ongerefereerd](/catalogus/speciaal/ongerefereerd/) | In de catalogus, nog niet in een koormap |
| [Oefenbaar](/catalogus/speciaal/oefenbaar/) | Platte lijst van linkbare uitvoeringsvormen + id |
| [Handmatig](/catalogus/speciaal/handmatig/) | Uitvoeringsvormen met `artefacten_handmatig: true` |

## Taalvarianten op de uitvoeringsvorm

Nederlands en kerkslavisch zijn **aparte uitvoeringsvormen**. De taal
hoort in het derde padsegment (de leaf-map), niet in een vierde maplaag
en niet als aparte map per bestandsformaat. Markeer de taal met suffix
`-nl` of `-ksl` op de uitvoeringsvorm-id — alleen waar nodig.

### Wanneer wel, wanneer niet

| Situatie | Wat je doet |
| --- | --- |
| Alleen Nederlands voor die herkomst (geen kerkslavisch-sibling) | Geen taalsuffix: leaf `hemelum` |
| Zelfde herkomst in **beide** talen | Twee leaves: `hemelum-nl` en `hemelum-ksl` |
| Alleen kerkslavisch (Cyrillisch) | Suffix `-ksl` op de uitvoeringsvorm-id |
| Mengvorm NL + kerkslavisch in één partituur | Suffix `-nl-ksl` (zeldzaam) |

Gebruik `-nl` **alleen waar nodig**: als er een `-ksl`-sibling is (of komt),
zodat beide leaves even duidelijk zijn. Zet geen `-nl` op elke
Nederlandse leaf «voor de zekerheid».

**Voorkeursconventie** voor nieuw werk: taal via suffix op de
**uitvoeringsvorm-id** (`-nl` / `-ksl`). Zet de taal **niet** in de
variant-id.

**Legacy / alternatief:** sommige oudere stukken houden taal in de
variant, bijvoorbeeld `trisagion/8a-nederlands/hemelum` naast
`trisagion/8a-slav/hemelum`. Die maps niet hernoemen tot een aparte
migratie; voor **nieuwe** ids volg je de suffix op de uitvoeringsvorm.

Getranslitereerde producten (Latijns schrift naast Cyrillisch) horen
later; die conventie staat nog niet vast in dit padmodel.

### Pad, catalogus-id en bestandsstam

| Begrip | Vorm | Voorbeeld (schets) |
| --- | --- | --- |
| Cataloguspad | `catalogus\<zangstuk>\<variant>\<uitvoeringsvorm>\` | `catalogus\prijslied\bisschop-gregorios\hemelum-nl\` |
| Catalogus-id (`bieb`) | `zangstuk/variant/uitvoeringsvorm` | `prijslied/bisschop-gregorios/hemelum-nl` |
| Publicatiestam | `{zangstuk}-{variant}-{uitvoeringsvorm}` | `prijslied-bisschop-gregorios-hemelum-nl` |

Voorbeeld-paar (nog niet per se in de catalogus; richting voor nieuw werk):

```text
content-source\catalogus\prijslied\bisschop-gregorios\hemelum-nl\
content-source\catalogus\prijslied\bisschop-gregorios\hemelum-ksl\
```

Catalogus-ids: `prijslied/bisschop-gregorios/hemelum-nl` en
`prijslied/bisschop-gregorios/hemelum-ksl`. Bestandsstam van de
Nederlandse leaf:
`prijslied-bisschop-gregorios-hemelum-nl` (plus extensie van de bron).

Precedent in het [Id-register](/catalogus/id-register/): o.a.
`cherubijnenhymne/15c-kastorski/hemelum-ksl-trlat` (stub) en bestaande
`-ksl`-leaves zoals `tropaar/uw-heilig-kruis/groningen-ksl`.

### Canonieke bron vs afgeleiden

In **elke** leaf-map liggen bron en afgeleiden naast elkaar (siblings):

| Soort | Voorbeelden | Rol |
| --- | --- | --- |
| **Canonieke bron** | `{stam}.vsa`, `{stam}.mscz`, `{stam}.mvsa`, `{stam}.tekstblad.md` | Hier bewerk je |
| **Afgeleiden** | `{stam}.vsa.mxl`, `{stam}.vsa.pdf`, `{stam}.mp3`, `{stam}.mscz.pdf`, … | Regenereren met productscripts |

Formaat is **geen** id-laag: geen aparte map `pdf/` of `mxl/` onder de
leaf. PDF, MusicXML en audio blijven siblings van de bron in dezelfde
uitvoeringsvorm-map. Detail:
[Publicatiecontrole](publicatiecontrole/).

### Koormap: alleen `bieb`

Koormap-slots bevatten **geen** kopie van de partituur. Ze verwijzen
met shortcode `bieb` naar het catalogus-id, inclusief het taalsuffix
wanneer dat in de leaf-naam zit:

```markdown
{{</* bieb id="prijslied/bisschop-gregorios/hemelum-nl" */>}}
{{</* bieb id="prijslied/bisschop-gregorios/hemelum-ksl" */>}}
```

Korte woordenlijst: [Woorden](woorden/) (regel **Taal-suffix**). Concrete
ids: [Id-register](/catalogus/id-register/).

## Naamgevingsbeleid (nieuwe ids)

1. **Nieuwe** `zangstuk-id`s krijgen **geen** sorteerprefix (`tropaar`, niet
   `tropaar`). Liturgienummers horen in de koormap-titel en in Hugo-
   `weight`.
2. Spelling voor *nieuwe* ids: `johannes`, `alleluia`; liever voluit dan
   `mg` of `zo-wk-mg`.
3. Genummerde top-level `zangstuk-id`s zijn hernoemd (zie
   [Zangstuk-soorten](/handleiding/start/zangstuk-soorten/)). Nieuwe
   hernoemingen: werktraject
   [Zangstuk hernoemen](/handleiding/werktrajecten/zangstuk-hernoemen/)
   ([`bieb hernoem`](/handleiding/scripts/bieb-hernoem/)).
4. Echte naamsynoniemen van dezelfde variant: `alias_van`. Spelling- en
   woordvolgorde-varianten: zoekindex + [`data/zoek-synoniemen.yaml`](https://github.com/orthodox-ronl/bibliotheek/blob/development/data/zoek-synoniemen.yaml).
5. Taal (NL / kerkslavisch): suffix op de **uitvoeringsvorm** (`-nl` /
   `-ksl`), alleen waar nodig — zie
   [Taalvarianten](#taalvarianten-op-de-uitvoeringsvorm).

Zie [Zangstuk-soorten](/handleiding/start/zangstuk-soorten/) voor de
inventaristabel en resterende vervolgstappen.

## Klaar als

Je kunt uitleggen waarom een Zwolle-cherubijn eerst in de catalogus hoort;
waarom de Hemelum-liturgiemap géén tweede opslag van PDF’s is; wanneer je
een **sectie** (boom) kiest versus een **compositieblad** (meerdere
shortcodes op één pagina); en hoe je een NL/kerkslavisch-paar als twee
uitvoeringsvormen met `-nl` / `-ksl` aanmaakt.

{{< navbuttons "Waar ligt wat|/handleiding/start/waar-ligt-wat/" "Zangstuk-soorten|/handleiding/start/zangstuk-soorten/" >}}
