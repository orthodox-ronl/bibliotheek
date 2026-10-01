---
title: "Catalogus en koormappen"
linkTitle: "Catalogus en koormappen"
weight: 25
aliases:
  - "/handleiding/start/bibliotheek-en-koormappen/"
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
velden op elke catalogus- en koormap-pagina. Mis je `publicatiestatus`,
dan ontbreekt de statusbadge; de build faalt daar niet op.

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

## Klaar als

Je kunt uitleggen waarom een Zwolle-cherubijn eerst in de catalogus hoort;
waarom de Hemelum-liturgiemap géén tweede opslag van PDF’s is; en wanneer je
een **sectie** (boom) kiest versus een **compositieblad** (meerdere
shortcodes op één pagina).

## Naamgevingsbeleid (nieuwe ids)

1. **Nieuwe** `zangstuk-id`s krijgen **geen** sorteerprefix (`tropaar`, niet
   `tropaar`). Liturgienummers horen in de koormap-titel en in Hugo-
   `weight`.
2. Spelling voor *nieuwe* ids: `johannes`, `alleluia`; liever voluit dan
   `mg` of `zo-wk-mg`.
3. Genummerde top-level `zangstuk-id`s zijn hernoemd (zie
   [Zangstuk-soorten](/handleiding/start/zangstuk-soorten/)). Nieuwe
   hernoemingen: [`bieb hernoem`](/handleiding/scripts/bieb-hernoem/).
4. Echte naamsynoniemen van dezelfde variant: `alias_van`. Spelling- en
   woordvolgorde-varianten: zoekindex + [`data/zoek-synoniemen.yaml`](https://github.com/orthodox-ronl/bibliotheek/blob/development/data/zoek-synoniemen.yaml).

Zie [Zangstuk-soorten](/handleiding/start/zangstuk-soorten/) voor de
inventaristabel en resterende vervolgstappen.

{{< navbuttons "Waar ligt wat|/handleiding/start/waar-ligt-wat/" "Zangstuk-soorten|/handleiding/start/zangstuk-soorten/" >}}
