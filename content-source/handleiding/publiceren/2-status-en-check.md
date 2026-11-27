---
title: "Status, check en live"
linkTitle: "Status en check"
weight: 20
---

# Status, check en live

**Werktraject** voor de hele site-keten:
[Site-build](/handleiding/werktrajecten/site-build/).
Deze pagina is de HOW voor publicatiestatus en lokale controle.

{{< cue >}}
1. Zet `publicatiestatus` op catalogus-`index.md` **en** koormap-`index.md`.
2. `scripts\check.cmd --strict` moet groen zijn.
3. `scripts\serve.cmd` → http://127.0.0.1:18732/ — klik zelf als koorlid (koormap-slot).
4. Live: pas na groen, via git naar `main` (of vragen). `productie` niet raden.
{{< /cue >}}

**Wat je nu doet:** zeggen wat koorleden mogen verwachten, de keten laten
controleren, zelf de pagina nalopen, daarna pas publiceren op internet.

## Publicatiestatus

Op **elke** pagina die koorleden zien (catalogus én koormap),
in de `---` bovenaan:

| Waarde | Wanneer |
| --- | --- |
| `voorzien` | Gepland, nog geen oefenbare uitgave (stub) |
| `concept` | Eerste versie; vooral op sectie-`_index` |
| `reviewable` | Er staat iets in; feedback welkom |
| `productie` | Alleen bewust, nooit gokken |

Catalogus mét basispartituur, VSA of print-PDF: meestal `reviewable`. Lege stub:
`voorzien`. Intern *Stap* in de werkvoorraad (`opkuisen`, `layout`, …) is
iets anders — dat zien koorleden niet.

Optioneel op catalogus-`index.md`: `manueel: true` als PDF
en Coria-`.mxl` in die map niet via de product-pipeline mogen lopen (print /
template). Zie [Print-.mscz](../../partituur/7-print-mscz/).

## Gebreken (ernstige fouten op een blad)

Als materiaal al in de catalogus staat maar ernstige gebreken blijkt te
hebben, markeer je dat met frontmatter — **niet** door alleen
`publicatiestatus` te wijzigen. Je mag dat zetten op drie niveaus:

| Niveau          | Bestand               | Effect                              |
| --------------- | --------------------- | ----------------------------------- |
| Uitvoeringsvorm | leaf-`index.md`       | Alleen die uitvoeringsvorm          |
| Variant         | variant-`_index.md`   | Alle leaves onder die variant       |
| Zangstuk        | zangstuk-`_index.md`  | Alle leaves onder dat zangstuk      |

**Voorbeeld** — één leaf:

```yaml
publicatiestatus: reviewable
gebreken: true
gebreken_toelichting: "Melodie couplet 2 klopt niet; wacht op herziening."
```

**Voorbeeld** — heel zangstuk, één leaf uitzonderen. Op
`catalogus\tropaar\voorbeeld\_index.md`:

```yaml
gebreken: true
gebreken_toelichting: "Hele zangstuk herzien na foutieve opname."
```

Op de leaf die wél goed is, `catalogus\tropaar\voorbeeld\hemelum\groningen\index.md`:

```yaml
gebreken: false
```

| Veld                   | Rol                                                                              |
| ---------------------- | -------------------------------------------------------------------------------- |
| `gebreken: true`       | Markering aan op dit niveau (en lager, tenzij een kind uitzondert)               |
| `gebreken: false`      | Markering uit op dit niveau, ook als een ouder `true` heeft                      |
| `gebreken_toelichting` | Optioneel; de dichtstbijzijnde niet-lege tekst wint (leaf vóór variant vóór zangstuk) |

**Overerving:** de dichtstbijzijnde expliciete `gebreken` wint (eerst de
leaf, dan de variant, dan het zangstuk). Ontbreekt het veld overal, dan
is er geen markering.

Vaste stempeltekst overal: **Gebreken - niet als definitief gebruiken**.
Die verschijnt op het scherm (rode banner op catalogusblad, variant- of
zangstukoverzicht, en op koormap-slots via `bieb`), in `index.md.pdf`
(watermark) en op de sibling-SVG’s na `products`. Het blad blijft
vindbaar en bruikbaar om te oefenen; het is geen verborgen stub.

Advies: zet `publicatiestatus` op getroffen leaves desgewenst op
`reviewable` of `concept`. `check` weigert `productie` op een leaf met
*effectieve* gebreken (dus ook bij markering alleen op variant of
zangstuk). Na zetten of wissen:

```cmd
scripts\products.cmd content-source\catalogus\tropaar\voorbeeld
scripts\pdf.cmd content-source\catalogus\tropaar\voorbeeld
```

`products` zet of haalt de SVG-stempel op alle getroffen leaves onder die
map; `pdf` vernieuwt de pagina-PDF’s (watermark).

## Check

In de map `bibliotheek`:

```cmd
scripts\check.cmd --strict
```

Dat controleert onder meer VSA-notatie, Coria-`.mxl` (basispartituur én
`.vsa.mxl`), of partituur-/VSA-/mvsa-afgeleiden bij hun bron horen, en of
links op de site kloppen. Rood = niet naar live; eerst
[als het misgaat](../3-als-het-misgaat/).

`publicatiestatus` zelf controleert `check` **niet** automatisch; die zet
je zelf volgens
[Catalogus en koormappen](../../start/catalogus-en-koormappen/)
(sectie *Titels en frontmatter*). Wél controleert `check` of een leaf met
effectieve `gebreken` niet op `productie` staat, en of SVG/PDF een
stempel hebben wanneer de markering aan staat.

`check` schrijft geen PDF, Coria-`.mxl` of SVG. Die maak je lokaal met
`products` (of het passende `*-products`-commando) en commit je mee.
Op branch `main` faalt de build als die producten ontbreken of verouderd
zijn.

## Preview

Als `check` groen is:

```cmd
scripts\serve.cmd
```

`serve` start de preview op **http://127.0.0.1:18732/** (nooit poort
1313). Catalogusproducten maakt dat commando niet; die horen al in de
map te staan. Open jouw **koormap-slot** in de liturgiemap. Open tip-icoon
**♪** (**Oefenen** / **Beluisteren**), probeer het **download-icoon** en
de translit-icoonknoppen, blader de partituur — alsof je koorlid bent.
Rode banner over partituur- of VSA-afgeleiden? Terug naar
[Afgeleiden](../../partituur/6-afgeleiden/). Gele banner “Handmatige
artefacten”? Verwacht — jij houdt PDF/MXL zelf bij. Rode banner
“Gebreken - niet als definitief gebruiken”? Frontmatter `gebreken: true`
op de catalogus-leaf (zie hierboven).

## Op internet

De publieke site is
[orthodox-ronl.github.io/bibliotheek](https://orthodox-ronl.github.io/bibliotheek/).
Die site volgt branch `main`. Lokaal groen is de drempel; daarna
committen en pushen (of iemand vragen die git doet). Preview-branches
komen onder `/preview/`.

Je hoeft git niet uit deze handleiding te leren. Wél: nooit pushen met
een rode `check --strict`.

## Klaar als

De publicatiestatus klopt op bibliotheek én koormap, check is groen, jij
hebt de preview als koorlid geklikt, en live is een bewuste volgende stap.

{{< navbuttons "Als het misgaat|/handleiding/publiceren/3-als-het-misgaat/" >}}
