# Catalogus: één canonieke notatiebron — agent-contract

Goedgekeurde beleidsregel. Leesbare vorm:
[Publicatiecontrole](../content-source/handleiding/start/publicatiecontrole.md)
(§ Publicatiesporen) en archief:
[`content-source/input/archief-bronnen/`](../content-source/input/archief-bronnen/).

**Canoniek** voor de *inhoud* van `.vsa` / `.mvsa` / `.mscz` = VSA-tooling
formatcontract
([contract-index](https://github.com/orthodox-ronl/VSA-tooling/blob/main/docs/formats/contract-index.md);
pagina’s [vsa](https://github.com/orthodox-ronl/VSA-tooling/blob/main/docs/formats/vsa.md) /
[mvsa](https://github.com/orthodox-ronl/VSA-tooling/blob/main/docs/formats/mvsa.md) /
[mscz](https://github.com/orthodox-ronl/VSA-tooling/blob/main/docs/formats/mscz.md)).
Dit document regelt alleen: **één** van die drie per leaf. Zie ook
[tooling-koppeling — Canoniek in de catalogus](tooling-koppeling.md#canoniek-in-de-catalogus).

## Doel

Op één uitvoeringsvorm-blad (`zangstuk/variant/uitvoeringsvorm`) toont
de site **één** partituur. Twee canonieke notatiebronnen in dezelfde
bladermap leveren dubbele SVG’s, dubbele products/check en verwarring
over wat leidend is.

## Keuze (vast)

Per catalogus-leaf geldt voor **notatie** precies **één** canonieke bron:

| Toegestaan (kies er één) | Bestandsvorm  |
| ------------------------ | ------------- |
| VSA                      | `{stam}.vsa`  |
| MVSA                     | `{stam}.mvsa` |
| Basispartituur MuseScore | `{stam}.mscz` |

**Niet** tegelijk twee of meer van die drie in dezelfde leaf-map.

### Wat wél naast de gekozen bron mag

| Soort                                    | Voorbeeld                                                   | Rol                                                                                                  |
| ---------------------------------------- | ----------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| Afgeleiden van die bron                  | `{stam}.mvsa.svg`, `{stam}.mvsa.mscz`, `{stam}.mscz.mxl`, … | Producten (één laag; geen product-van-product)                                                       |
| Schets-MVSA bij **alleen** `.vsa`        | `{stam}.vsa.mvsa`                                           | Product van `vsa mvsa` (T1); daarna mvsa-bron voor mxl/svg/IR/audio — **geen** tweede canonieke bron |
| Import-bewerkvorm bij **alleen** `.mscz` | `{stam}.mscz.mvsa`                                          | Bewerk-/importvorm, **geen** tweede canonieke bron                                                   |
| Tekstblad                                | `{stam}.tekstblad.md`                                       | Eigen spoor (dialoog e.d.); geen notatie-SVG                                                         |

`{stam}.mvsa.mscz` / `{stam}.vsa.mscz` is een **product** van mvsa/vsa,
geen tweede bron. Zie [publicatiecontrole.md](publicatiecontrole.md).

**Tekstbron voor zoeken en lyrics:** alleen de canonieke bron. De schets-MVSA
(`{stam}.vsa.mvsa`) en de import-bewerkvorm (`{stam}.mscz.mvsa`) leveren
nooit de gezongen tekst voor de zoekindex; zie
[zoek-index](../content-source/handleiding/scripts/zoek-index.md).

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

## Uitzondering: formule dekt het blad niet

Soms past een goedgekeurde zetting **niet** in `vsa mvsa` (T1–T7), bv.
een ere-coda buiten de standaardfrasen. Dan:

1. Canonieke bron = **`{stam}.mvsa`** (handmatig onderhouden).
2. Eventuele oude `{stam}.vsa` → `content-source/input/archief-bronnen/`
   (melodie-archief; **niet** leidend voor products/check).
3. Geen `{stam}.vsa.mvsa` in de leaf (dat zou weer naar VSA wijzen).
4. Op de blad-`index.md` kort vermelden: notatiebron = `.mvsa`; niet
   overschrijven met `vsa mvsa` / `products --kinds vsa`.

Voorbeeld: `tropaar/zondag-toon-1/groningen` (ere zij Uw Koningschap /
Voorzienigheid). Later eventueel `mvsa → vsa` (S-extractie); géén
mapper-special-case in T1.

## Hard rules (agents)

1. Geen tweede canonieke `.vsa` / `.mvsa` / `.mscz` in een leaf zetten.
2. Bij vervanging: bronbestand archiveren onder `input/archief-bronnen/`,
   niet stil wissen.
3. Scherm en `index.md.pdf` volgen één bron (voorkeur `.mvsa` → `.vsa`
   → `.mscz`); zie `find_notation_source` / schermpartituur.
4. `Meerdere bronnen in één map mogen` in oudere tekst = **achterhaald**
   voor canonieke notatie; alleen nog: één notatiebron + diens spoor
   (+ optioneel tekstblad / import-bewerkvorm).
5. Bij formule-uitzondering (zie hierboven): `.mvsa` wint; geen stille
   VSA→MVSA-regeneratie op dat leaf.
