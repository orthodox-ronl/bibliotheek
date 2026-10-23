---
title: "Koormap-blad schrijven"
linkTitle: "Koormap-blad"
weight: 26
---

Op een **slot-pagina** (`index.md` onder `koormappen\…`) zet je zelf de
volgorde, de titels en de uitleg. Muziek haal je uit de catalogus met
`bieb`. Bladindeling voor **Download pagina** / **Print pagina** regel je
met `pdf-…`. Titels op het blad zet je met `kop` — geen HTML.

Lees eerst het model catalogus versus koormap in
[Catalogus en koormappen](catalogus-en-koormappen/). Normatieve details:
`docs\specs\koormap-paginataal.md` in de repository (shortcodes en
paginacontract). Hoe de **partituur op het scherm** eruit moet zien
(OSMD, SVG, titels): `docs\specs\schermpartituur.md`. Pagina-PDF bouwen:
[pagina-pdf](../scripts/pagina-pdf/).

## Spiekbriefje

### De middelen

| Middel | Waarvoor |
| --- | --- |
| `bieb` | Muziek (en desgewenst titel of bron) uit de catalogus |
| `kop` | Bladtitel of rubriek (standaard: midden, groot) |
| `witruimte` | Extra ruimte tussen onderdelen (standaard: middel; ook `klein` / `groot`) |
| `pdf-bijelkaar` | In de download: dit blok bij voorkeur op **één** A4 |
| `pdf-pagina` | In de download: hier begint een **nieuw** A4-blad |

Op het web zie je geen bladscheiding door `pdf-pagina`; alles staat onder
elkaar. Alleen de knoppen **Download pagina** en **Print pagina** gebruiken
die bladindeling, via het bestand `index.pagina.pdf` naast de Markdown.

### Muziek uit de catalogus

Alleen muziek (kort, met afsluitende `/>`):

```markdown
{{</* bieb id="ektinia/vrede/hemelum" */>}}
```

Zelfde uitvoeringsvorm, met titel en muziek (blokvorm — openen met `>`,
sluiten met `/bieb`; de korte vorm hierboven eindigt met `/>`):

```markdown
{{</* bieb id="ektinia/vrede/hemelum" */>}}
{{</* kop */>}}{{</* titel */>}}{{</* /kop */>}}
{{</* muziek */>}}
{{</* /bieb */>}}
```

Het id is altijd `zangstuk/variant/uitvoeringsvorm` (drie lagen, met
schuine strepen). Zonder onderdeelnaam betekent de korte `bieb` hetzelfde
als muziek. Binnen een `bieb`-blok mag je `muziek` en `titel` zonder
telkens het id te herhalen.

### Kopjes op het blad

```markdown
{{</* kop */>}}(1a) Vredeslitanie{{</* /kop */>}}

{{</* kop links middel */>}}Toon 1{{</* /kop */>}}
```

Optioneel bijsturen — alleen deze woorden, hoogstens één uitlijning en één
grootte:

| Soort | Woorden |
| --- | --- |
| Uitlijning | `links` · `midden` · `rechts` |
| Grootte | `groot` · `middel` · `klein` |

Zonder knoppen is de standaard **midden** en **groot** (typische
bladtitel). Een rubriek tussen partituren (zoals «Toon 1») zet je meestal
met `links` en `middel`.

Gebruik geen `<h1 style=…>` en geen class-namen zoals
`koormap-tussenkop`. Gewone Markdown-koppen (`#`, `##`) mag je gebruiken
voor uitlegtekst; voor de bladtitel en rubrieken tussen partituren: `kop`.

### Witruimte tussen onderdelen

Lege regels tussen shortcodes geven **geen** zichtbare ruimte. Zet expliciet:

```markdown
{{</* witruimte */>}}
{{</* witruimte groot */>}}
```

### Nederlands en Kerkslavisch op één slot

Gebruik per uitvoeringsvorm de **titel in de taal van de lyrics** (zoals
`@title` in de `.mvsa`), daarna de korte `bieb` (alleen muziek). Geen
extra tussenkoppen «Nederlands» / «Kerkslavisch». Voorbeeld:

```markdown
{{</* kop */>}}1e Kleine Ektinia{{</* /kop */>}}

{{</* bieb id="ektinia/eerste-kleine/hemelum" */>}}

{{</* witruimte groot */>}}

{{</* kop */>}}Малая ектения{{</* /kop */>}}

{{</* bieb id="ektinia/eerste-kleine/hemelum-ksl" */>}}
```

Korte `bieb` met `/>` volstaat als je geen titel/bron uit de catalogus
op de pagina hoeft te trekken. Bij **grote** stukken (bijv. cherubijnenhymne)
begint elke taal op een **nieuw** blad: `{{</* pdf-pagina */>}}` ertussen,
geen `pdf-bijelkaar`.

### Bladindeling in de download

Nederlands en Kerkslavisch op **één** blad:

```markdown
{{</* pdf-bijelkaar */>}}
{{</* kop */>}}(1a) Vredeslitanie{{</* /kop */>}}
{{</* bieb id="ektinia/vrede/hemelum" */>}}
{{</* bieb id="ektinia/vrede/hemelum-ksl" */>}}
{{</* /pdf-bijelkaar */>}}
```

Elk op een **eigen** blad: laat `pdf-bijelkaar` weg en zet
`{{</* pdf-pagina */>}}` tussen de twee `bieb`-regels.

Compositie met rubrieken (zoals alleluia-tonen):

```markdown
{{</* kop */>}}(9b) Alleluia{{</* /kop */>}}

{{</* pdf-bijelkaar */>}}
{{</* kop links middel */>}}Toon 1{{</* /kop */>}}
{{</* bieb id="alleluia/9a-toon-1/groningen" */>}}
{{</* kop links middel */>}}Toon 2{{</* /kop */>}}
{{</* bieb id="alleluia/9a-toon-2/groningen" */>}}
{{</* /pdf-bijelkaar */>}}
```

Na wijzigingen aan shortcodes of volgorde: draai
[pagina-pdf](../scripts/pagina-pdf/) opnieuw voor die slot-pagina, anders
blijft de oude download staan.

### Niet gebruiken op een koormap-blad

| Oud of elders | Gebruik hier |
| --- | --- |
| `pagebreak`, `pagina`, `keep-together`, `print-only`, `web-only` | Verwijderd; gebruik `pdf-pagina` / `pdf-bijelkaar` |
| VSA-demo-directives zoals `:::include` | `bieb` |
| HTML voor titels (`<h1 style=…>`, class `koormap-tussenkop`) | `kop` |

## Voorbeelden in de site

Proefslots die deze taal al gebruiken:

- [Vredeslitanie (zondag)](/koormappen/hemelum/liturgie-zondag/vredeslitanie/)
- [Eerste kleine litanie (zondag)](/koormappen/hemelum/liturgie-zondag/eerste-kleine-litanie/)
- [Alleluia (zondag)](/koormappen/hemelum/liturgie-zondag/alleluia/)

{{< navbuttons "Catalogus en koormappen|/handleiding/start/catalogus-en-koormappen/" "pagina-pdf|/handleiding/scripts/pagina-pdf/" >}}
