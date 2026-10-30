# Catalogus: één canonieke notatiebron — agent-contract

Goedgekeurde beleidsregel. Leesbare vorm:
[Publicatiecontrole](../content-source/handleiding/start/publicatiecontrole.md)
(§ Publicatiesporen) en archief:
[`content-source/input/archief-bronnen/`](../content-source/input/archief-bronnen/).

## Doel

Op één uitvoeringsvorm-blad (`zangstuk/variant/uitvoeringsvorm`) toont
de site **één** partituur. Twee canonieke notatiebronnen in dezelfde
bladermap leveren dubbele SVG’s, dubbele products/check en verwarring
over wat leidend is.

## Keuze (vast)

Per catalogus-leaf geldt voor **notatie** precies **één** canonieke bron:

| Toegestaan (kies er één) | Bestandsvorm |
| --- | --- |
| VSA | `{stam}.vsa` |
| MVSA | `{stam}.mvsa` |
| Basispartituur MuseScore | `{stam}.mscz` |

**Niet** tegelijk twee of meer van die drie in dezelfde leaf-map.

### Wat wél naast de gekozen bron mag

| Soort | Voorbeeld | Rol |
| --- | --- | --- |
| Afgeleiden van die bron | `{stam}.mvsa.svg`, `{stam}.mvsa.mscz`, `{stam}.mscz.mxl`, … | Producten (één laag; geen product-van-product) |
| Import-bewerkvorm bij **alleen** `.mscz` | `{stam}.mscz.mvsa` | Bewerk-/importvorm, **geen** tweede canonieke bron |
| Tekstblad | `{stam}.tekstblad.md` | Eigen spoor (dialoog e.d.); geen notatie-SVG |

`{stam}.mvsa.mscz` / `{stam}.vsa.mscz` is een **product** van mvsa/vsa,
geen tweede bron. Zie [publicatiecontrole.md](publicatiecontrole.md).

### Voorkeur bij nieuwe of blijvende bron

Nieuwe of omgezette notatie bij voorkeur **`.mvsa`** (één keten met
SVG/OSMD). Een aangeleverde `.mscz` mag de enige bron blijven tot
omzetting nuttig is — zie [product-pdf-afbouw.md](plans/product-pdf-afbouw.md).

## Oude MuseScore-bron bewaren

Als een leaf van `.mscz` naar `.mvsa` (of andersom) overgaat en de
vervangen canonieke bron nog nodig kan zijn:

1. Verplaats **alleen** dat bronbestand naar
   `content-source/input/archief-bronnen/` (zelfde bestandsnaam /
   publicatiestam).
2. Verwijder uit de leaf de keten van die bron (SVG, MXL, mp3, lyrics,
   meta, import-`.mscz.mvsa` als die bij de gearchiveerde `.mscz` hoorde).
3. Laat de producten van de **blijvende** bron staan.

De map `archief-bronnen` staat in git (wél committen). Lokale rommel
onder `.archief/` blijft genegeerd door git — daar hoort dit **niet**.

## Check (bedoeling)

`check` / `--strict` hoort te melden (later: hard falen) wanneer een
leaf meer dan één canonieke notatiebron heeft. Status: **contract vast;
automatische check nog niet gebouwd**.

## Hard rules (agents)

1. Geen tweede canonieke `.vsa` / `.mvsa` / `.mscz` in een leaf zetten.
2. Bij vervanging: bronbestand archiveren onder `input/archief-bronnen/`,
   niet stil wissen.
3. Scherm en `index.md.pdf` volgen één bron (voorkeur `.mvsa` → `.vsa`
   → `.mscz`); zie `find_notation_source` / schermpartituur.
4. `Meerdere bronnen in één map mogen` in oudere tekst = **achterhaald**
   voor canonieke notatie; alleen nog: één notatiebron + diens spoor
   (+ optioneel tekstblad / import-bewerkvorm).
