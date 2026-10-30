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
| Beheerder | Wat hebben we? Welk id gebruik ik? | Bestaand: [Catalogus](/overzichten/) / [Zoeken](/overzichten/zoeken/). Hemelum-naslag of reservering: [Id-register](/overzichten/id-register/) |
| Koor (in situ) | Wat zingen we in welke volgorde? | Koormap, nu vooral [liturgie zondag](/koormappen/hemelum/liturgie-zondag/) / [weekdagen](/koormappen/hemelum/liturgie-weekdagen/) |
| Individueel koorlid | Wat moet / wil ik oefenen? | Koormap *of* catalogus (ook stukken die nog in geen map zitten) |

### Catalogus bladeren (referentie)

De catalogus is bedoeld als **repertorium**, niet alleen als inhoudsopgave
van één liturgie. Via het menu **Catalogus** (startpagina
[Catalogus](/overzichten/)):

- [Zoeken](/overzichten/zoeken/) — op titel, id of gezongen tekst
- [Alfabetisch](/overzichten/alfabetisch/) — boom op zangstuk (A–Z)
- [Per herkomst](/overzichten/herkomst/) — boom op herkomst (Hemelum, Groningen, …); taalsuffix (`-ksl` e.d.) is géén aparte herkomst — NL en Ksl van dezelfde stam staan onder elkaar

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

**Slot-pagina** (`index.md`): gewone markdown plus shortcodes. Titels en
uitleg zet je zelf; `bieb` haalt muziek (en desgewenst titel/bron) uit de
catalogus; bladtitels met `kop`; bladindeling in de download met
`pdf-pagina` / `pdf-bijelkaar`. Bovenaan de pagina: **Download pagina**
als `index.md.pdf` bestaat (niet de browserafdruk van de HTML). De
voorgestelde bestandsnaam bij downloaden komt uit frontmatter
`pdf_bestandsnaam`; anders op een
**koormap** uit `title` en op een **catalogus**-blad uit de afgeleide
bladtitel; anders uit de mapnaam. Bij elk muziekblok: tip-icoon **♪** voor
**Oefenen** / **Beluisteren** van **dat** stuk. Pagina-PDF bouwen:
[pdf](../scripts/pdf/).

**Spiekbriefje voor beheerders:** [Koormap-blad schrijven](koormap-blad/).
Normatieve specificatie in de repository:
[koormap-paginataal](https://github.com/orthodox-ronl/bibliotheek/blob/development/docs/specs/koormap-paginataal.md).

### Boom of compositieblad?

Twee manieren om meerdere uitvoeringsvormen op **één liturgische plek** te
tonen —zelfde mechaniek, andere leeservaring:

| Patroon | Wanneer | Voorbeeld |
| --- | --- | --- |
| **Boom** | De zanger kiest één variant (of bladert per kind) | Cherubijnenhymne: sectie → 15b, 15c, …; antifoon: weekdagen / zondag |
| **Compositieblad** | Eén pagina bundelt een set (proza + scores) | Prokimens voor de hele week op één `index.md`, met shortcode per weekdag |

Voorbeeld compositieblad (schets):

```markdown
# Prokimen weekdagen (Kiev)

## Maandag
{{</* bieb id="prokimen/9a-maandag/groningen" */>}}

## Dinsdag
{{</* bieb id="prokimen/9a-dinsdag/groningen" */>}}
```

**Let op:** elke `bieb` op dezelfde pagina heeft een **eigen** tip-icoon
**♪** bij de partituur van die uitvoeringsvorm. Je hoeft geen aparte
kindpagina’s te maken alleen om oefenacties te scheiden.

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
uitvoeringsvorm. Product-tools (`products --kinds vsa`, basispartituur-producten) slaan
alias-varianten over: daar is niets te genereren.

`check` weigert een alias-variant die toch een uitvoeringsvorm-map of
partituur bevat. Dat patroon mag voor elk zangstuk waarvan een variant
onder meerdere namen bekend is.

## Titels en frontmatter in de catalogus

Getoonde namen in de catalogus (paginatitel, navigatie, zoeken) worden
**afgeleid bij de bouw** uit het pad/id, en bij een leaf optioneel uit de
bron (VSA/mvsa-`titel:`). Handmatige redactionele titels horen in
**koormappen**, niet in de catalogus. Agent-contract in de repo:
`docs/catalogus-titels.md`.

Elke catalogus-pagina (`_index.md` of leaf-`index.md`) heeft minstens:

| Veld | Rol |
| --- | --- |
| `publicatiestatus` | Wat koorleden mogen verwachten (`voorzien` / `concept` / `reviewable` / `productie`) |
| `automatische_inhoud` | Sectie: meestal `true` (kindlijst). Leaf: altijd `false` (score via `bieb`) |

Ids komen uit het **pad** (`zangstuk/variant/uitvoeringsvorm`). Tooling en
shortcode `bieb` gebruiken het pad. Op id-pagina’s zet je geen frontmatter
`title` / `linkTitle`; Hugo en zoeken leiden die namen af.

Op een **uitvoeringsvorm-blad** zet je in de Markdown geen tweede
hoofdtitel (`# …`): de site toont al één titel boven de partituur. De body
is meestal alleen de regel met `bieb`. De PDF achter **Download pagina**
(`index.md.pdf`) volgt dezelfde bladintentie; zie het plan
`docs/plans/catalogus-index-md-pdf.md` en het script
[pdf](../scripts/pdf/).

### Afleiding per laag

| Laag | Korte naam (navigatie) | Paginatitel / zoek |
| --- | --- | --- |
| **Zangstuk** | Uit mapnaam (streepjes → spaties) | Zelfde |
| **Variant** | Uit mapnaam (`default` → Standaard) | Zelfde |
| **Uitvoeringsvorm (leaf)** | Label uit uitvoeringsvorm-id (`Hemelum`, `Groningen`, …) | Uit bron-titel als die er is, anders uit id: `Zangstuk Variant (Label)` |

### Variant-id `default`

Als er nog maar één variant is, heet de map vaak `default`. Op de
**variant-pagina** in de catalogus is de getoonde naam dan **Standaard**.
Zodra er een tweede variant komt, geef je de map een echte id (hernoemen);
`default` mag **niet** naast andere variant-ids onder hetzelfde zangstuk
blijven staan.

**Overzichtsbomen** (Alfabetisch en Per herkomst) slaan
**enkelvoudige tussenlagen** over: heeft een tak precies één kind (één
sub-tak of één blad), dan zie je meteen de inhoud van dat kind — en dat
herhaalt zich tot er meerdere kinderen zijn of je bij een blad bent.
Het **bovenste niveau** van het overzicht blijft wél altijd staan
(herkomst-stam zoals Groningen, of het zangstuk op Alfabetisch). Voorbeeld: onder Rode Gebedenboek met alleen één tropaar
zie je `Rode Gebedenboek` → blad, niet eerst nog een tak «Tropaar».
Onder Groningen verdwijnen zangstuk-takken met maar één blad (zoals
soms Communievers); het blad staat dan direct onder Groningen.
Ook de variant-laag verdwijnt bij **elke** enige variant (niet alleen
bij `default`).

Extra bij (enige) `default`/`standaard`:

1. De bladtitel in de boom is `Zangstuk (uitvoeringsvorm)` — zonder het
   woord «Standaard» (het id `…/default/…` blijft in de code zichtbaar).
2. De sitebuild (`catalogus-referentie`) **faalt** als iemand
   `default`/`standaard` combineert met een andere variant onder
   hetzelfde zangstuk.


### Wat `check` wel en niet doet aan titels

`scripts\check.cmd` (met `--strict`: hard) controleert via
`check_catalogus_leaf_titles` dat
`data/uitvoeringsvorm-link-titles.yaml` gelijk blijft aan de labels in
`scripts/catalogus.py` (Hugo en Python dezelfde namen). Geen eis meer op
handmatige leaf-`title`.

Nog **niet** door `check`: een volledig frontmatter-schema of verplichte
`publicatiestatus`. Mis je `publicatiestatus` op een **leaf**, dan ontbreekt
de `?` naast de titel; de build faalt daar niet op.

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
Voorzien-items en technische overzichten staan onder
[Speciaal](/overzichten/speciaal/). Hemelum-id-naslag en
reserveringen: [Id-register](/overzichten/id-register/)
(niet de bron van waarheid voor wat er bestaat).

## Special pages

Automatisch bijgehouden (bij elke sitebuild):

| Pagina | Inhoud |
| --- | --- |
| [Voorzien](/overzichten/speciaal/voorzien/) | Zangstukken zonder oefenbare inhoud |
| [Ongerefereerd](/overzichten/speciaal/ongerefereerd/) | In de catalogus, nog niet in een koormap |
| [Oefenbaar](/overzichten/speciaal/oefenbaar/) | Platte lijst van linkbare uitvoeringsvormen + id |
| [Handmatig](/overzichten/speciaal/handmatig/) | Uitvoeringsvormen met `manueel: true` |

## Taalvarianten op de uitvoeringsvorm

Nederlands en kerkslavisch zijn **aparte uitvoeringsvormen**. De taal
hoort in het derde padsegment (de leaf-map), niet in een vierde maplaag
en niet als aparte map per bestandsformaat.

**Regel:** geen taalsuffix op de uitvoeringsvorm-id betekent Nederlands.
Andere talen krijgen een suffix achter de leaf-naam (`-ksl`, later
`-en`, `-fr`, …). Gebruik **geen** losse `-nl`-uitgang.

### Wanneer wel, wanneer niet

| Situatie | Wat je doet |
| --- | --- |
| Nederlands (alleen of naast een andere taal) | Geen taalsuffix: leaf `hemelum` |
| Zelfde herkomst in **beide** talen | Twee leaves: `hemelum` en `hemelum-ksl` (in het overzicht *Per herkomst* onder dezelfde herkomst-tak, Nederlands eerst) |
| Alleen kerkslavisch (Cyrillisch) | Suffix `-ksl` op de uitvoeringsvorm-id |
| Mengvorm NL + kerkslavisch in één partituur | Suffix `-nl-ksl` (zeldzaam) |

**Voorkeursconventie** voor nieuw werk: Nederlands zonder suffix; andere
talen via suffix op de **uitvoeringsvorm-id**. Zet de taal **niet** in de
variant-id.

**Legacy / alternatief:** sommige oudere stukken houden taal in de
variant, bijvoorbeeld `trisagion/8a-nederlands/hemelum` naast
`trisagion/8a-slav/hemelum`. Die maps niet hernoemen tot een aparte
migratie; voor **nieuwe** ids volg je de suffix-regel hierboven.

Getranslitereerde producten (Latijns schrift naast Cyrillisch) horen
later; die conventie staat nog niet vast in dit padmodel.

### Pad, catalogus-id en bestandsstam

| Begrip | Vorm | Voorbeeld (schets) |
| --- | --- | --- |
| Cataloguspad | `catalogus\<zangstuk>\<variant>\<uitvoeringsvorm>\` | `catalogus\prijslied\bisschop-gregorios\hemelum\` |
| Catalogus-id (`bieb`) | `zangstuk/variant/uitvoeringsvorm` | `prijslied/bisschop-gregorios/hemelum` |
| Publicatiestam | `{zangstuk}-{variant}-{uitvoeringsvorm}` | `prijslied-bisschop-gregorios-hemelum` |

Voorbeeld-paar (nog niet per se in de catalogus; richting voor nieuw werk):

```text
content-source\catalogus\prijslied\bisschop-gregorios\hemelum\
content-source\catalogus\prijslied\bisschop-gregorios\hemelum-ksl\
```

Catalogus-ids: `prijslied/bisschop-gregorios/hemelum` en
`prijslied/bisschop-gregorios/hemelum-ksl`. Bestandsstam van de
Nederlandse leaf:
`prijslied-bisschop-gregorios-hemelum` (plus extensie van de bron).

Precedent in het [Id-register](/overzichten/id-register/): o.a.
`cherubijnenhymne/15c-kastorski/hemelum-ksl` (stub) en bestaande
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
{{</* bieb id="prijslied/bisschop-gregorios/hemelum" */>}}
{{</* bieb id="prijslied/bisschop-gregorios/hemelum-ksl" */>}}
```

Korte woordenlijst: [Woorden](woorden/) (regel **Taal-suffix**).
Bestaande ids: [Zoeken](/overzichten/zoeken/) of de catalogus.
Hemelum-reserveringen: [Id-register](/overzichten/id-register/).

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
5. Taal: geen suffix = Nederlands; andere talen als suffix op de
   **uitvoeringsvorm** (`-ksl`, …) — zie
   [Taalvarianten](#taalvarianten-op-de-uitvoeringsvorm).

Zie [Zangstuk-soorten](/handleiding/start/zangstuk-soorten/) voor de
inventaristabel en resterende vervolgstappen.

## Klaar als

Je kunt uitleggen waarom een Zwolle-cherubijn eerst in de catalogus hoort;
waarom de Hemelum-liturgiemap géén tweede opslag van PDF’s is; wanneer je
een **sectie** (boom) kiest versus een **compositieblad** (meerdere
shortcodes op één pagina); en hoe je een NL/kerkslavisch-paar als twee
uitvoeringsvormen aanmaakt (`hemelum` + `hemelum-ksl`).

{{< navbuttons "Waar ligt wat|/handleiding/start/waar-ligt-wat/" "Zangstuk-soorten|/handleiding/start/zangstuk-soorten/" >}}
