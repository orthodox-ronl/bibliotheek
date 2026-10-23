---
title: "Publicatiecontrole en bestandsnamen"
linkTitle: "Publicatiecontrole"
weight: 25
aliases:
  - /handleiding/start/productgates/
---

# Publicatiecontrole en bestandsnamen

Deze pagina is de **specificatie** voor afgeleide bestanden in de
bibliotheek: hoe ze heten, welke bron ze bijhouden, en wat CI controleert.
Doelgroep: beheerder (MuseScore en Windows-cmd; geen programmeur).

Organisatie-termen (`zangstuk-id` → `variant-id` → `uitvoeringsvorm-id` →
`representatie-id`): glossary in
[bron](https://github.com/orthodox-ronl/bron/blob/main/docs/specs/terminologie.md).
Naamgevingsconventie voor conversies (tooling):
[canonieke checklists — bestandsnaamgeving](https://orthodox-ronl.github.io/VSA-tooling/formats/canonical-checklists/#bestandsnaamgeving-conventie).

{{< cue >}}
- **Bron** = één echte extensie: `{stam}.vsa`, `{stam}.mscz`, `{stam}.mvsa`
- **Afgeleide** = `{stam}.{bron-extensie}.{doel-extensie}` —
  bijv. `{stam}.vsa.mxl`, `{stam}.mscz.pdf`, `{stam}.vsa.lyrics.txt`
- **Publicatiecontrole** = versheidscontrole op site-producten (sibling +
  herkomststempel); CI genereert niet, jij wel lokaal
- **Handmatig** = `artefacten_handmatig: true` op `index.md` (vervangt het
  oude `.print.mscz`-spoor)
{{< /cue >}}

## Controles (terminologie)

| Term                    | Betekenis                                                                                                        |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------- |
| **Versheidscontrole**   | Meet en meldt of een sibling bestaat en of de herkomststempel (sha) bij de bron past. Regenereren doet dit niet. |
| **Publicatiecontrole**  | Versheidscontrole op **site-producten** (PDF, Coria-`.mxl`, …).                                                  |
| **Importcontrole**      | Versheidscontrole op een **bewerk-/importvorm** (bijv. sibling `.mscz.mvsa`).                                    |
| **Contractcontrole**    | Meet of een bestaande Coria-`.mxl` de playback-checklist haalt (`mxl validate`).                                 |
| **Geldigheidscontrole** | Bron geldig / formaat-check (`vsa validate`, `mvsa validate`, …).                                                |
| **Strengheid**          | Beleid op die controles (lokaal waarschuwen vs `--strict` / CI falen) — geen apart functietype.                  |

Een **publicatiecontrole** in `check` / GitHub Actions doet dit:

1. Zoek canonieke **bronbestanden** in `content-source\catalogus\`.
2. Eis dat de bijbehorende **afgeleide** (sibling) bestaat.
3. Eis dat de afgeleide een **herkomststempel** heeft die bij de huidige
   bron past (geen verouderd of “leeg” product).

Daarna volgt de **contractcontrole** op bestaande Coria-`.mxl`
(`scripts\check_mxl_playback_contract.py`): M2/M8, Coria-importer-tags en
meta. Faalt die, vernieuw lokaal met
`scripts\products.cmd --kinds mscz,mvsa,vsa --only-invalid`.

Faalt een versheidscontrole, dan vernieuw je lokaal met het product-commando
en commit je bron **en** afgeleide samen. De build op GitHub **schrijft geen**
MuseScore- of MusicXML-producten opnieuw.

## Producten (opnieuw) genereren — `products.cmd`

Eén wrapper voor **alle** product-sporen (inclusief audio en lyrics). Zoekt
**recursief** onder een map naar bronbestanden (`.vsa`, `.mscz`, `.mvsa`, …)
of werkt één opgegeven bronbestand af, en runt de bijbehorende pijplijnen.

Past het brontype niet bij een spoor (bijvoorbeeld een `.mvsa` bij het
mscz-spoor), dan wordt dat spoor **overgeslagen**. Dat is geen fout: je hoeft
`--kinds` niet te zetten om te zeggen dat andere bronnen ontbreken.

**Default-condities** (alle drie tegelijk): het product **ontbreekt**, is
**verouderd** (herkomststempel past niet bij de bron), of is **ongeldig**
(Coria-MXL faalt `mxl validate`). Gebruik `--force` om álles opnieuw te
maken.

```cmd
cd /d C:\Git\orthodox-ronl\bibliotheek

REM Hele bibliotheek: missing + stale + invalid (alle kinds)
scripts\products.cmd

REM Eerst kijken zonder te schrijven
scripts\products.cmd --dry-run

REM Eén .mvsa: mvsa + audio + lyrics e.d.; mscz/import slaan over
scripts\products.cmd content-source\catalogus\alleluia\9a-toon-1\groningen\alleluia-9a-toon-1-groningen.mvsa

REM Alleen één bladermap, alleen partituur + audio (focus)
scripts\products.cmd content-source\catalogus\trisagion --kinds mscz,audio
```

| Optie                             | Betekenis                                                                                        |
| --------------------------------- | ------------------------------------------------------------------------------------------------ |
| `--kinds LIST`                    | Focus: alleen deze kinds (`vsa`, `mscz`, `tekstblad`, `mvsa`, `import`, `audio`, `lyrics`, of `all`). Default `all`. Niet nodig om “ontbrekende” brontypen uit te sluiten — die sporen slaan vanzelf over. |
| `--dry-run`                       | Toon wat zou gebeuren, schrijf niet                                                              |
| `--force`                         | Alles onder de root opnieuw (negeert condities)                                                  |
| `--only-missing`                  | Alleen als het productbestand ontbreekt                                                          |
| `--only-stale`                    | Alleen als de stempel niet meer bij de bron past                                                 |
| `--only-invalid`                  | Alleen als Coria-`.mxl` de checklist faalt (`mxl validate`)                                      |
| `--reasons missing,stale,invalid` | Expliciete subset (niet met `--only-*`)                                                          |

Na een geslaagde run (niet bij `--dry-run`) vernieuwt `products.cmd` ook
de Coria-fingerprints voor de knop **Oefenen**. Losse
`mscz-products.cmd` e.d. doen dat niet; gebruik daarna `check` of
`products.cmd`, of `serve` / `build`.

Alias: `scripts\all-products.cmd` = `products.cmd --kinds all …`.
Losse `mscz-products.cmd` e.d. blijven werken (zelfde flags). Ze delen
dezelfde schil als `products`: geen passende bron = overslaan (geen fout);
audio en lyrics zijn gewone kinds, geen uitzondering.

Contract-ongeldigheid geldt voor **`.mscz.mxl` / `.mvsa.mxl` / `.vsa.mxl`**
(profiel satb of mono). PDF, mp3, lyrics en tekstblad kennen geen aparte
contract-gate in deze stap — daar tellen missing/stale (en `--force`).

## Bestandsnamen (doelvorm)

### Stam

De **publicatiestam** is de bestandsnaam zonder extensies:

`{zangstuk-id}-{variant-id}-{uitvoeringsvorm-id}`

Alleen kleine letters, cijfers, `_` en `-` — **geen spaties**.
Voorbeeld: `trisagion-8a-nederlands-hemelum`.

### Bron versus afgeleide

| Rol           | Patroon                                  | Voorbeelden                                                                |
| ------------- | ---------------------------------------- | -------------------------------------------------------------------------- |
| **Bron**      | `{stam}` + **één** echte extensie        | `….vsa`, `….mscz`, `….mvsa`                                                |
| **Afgeleide** | `{stam}.{bron-extensie}.{doel-extensie}` | `….vsa.mxl`, `….mscz.pdf`, `….mscz.mxl`, `….mvsa.mscz`, `….vsa.lyrics.txt` |

Het **laatste** segment is wat programma’s als bestandstype zien (`.mxl`,
`.pdf`, `.mscz`, …). Het middelste segment zegt **uit welke bron** het
product komt. Zo botsen een Coria-bestand uit VSA en een Coria-bestand uit
een MuseScore-partituur nooit op dezelfde korte naam.

Deze regel sluit aan bij VSA-tooling (`stem.brontype.doeltype`). In de
bibliotheek is die vorm **normatief voor nieuwe en vernieuwde producten**.

### Tekstblad (uitzondering)

Liturgische tekst/dialoog is Markdown, maar een kale `.md` is te breed
(Hugo-pagina’s zijn ook `.md`). Daarom blijft het inhoudstype in de naam:
`{stam}.tekstblad.md`. Blad voor **Download/Print pagina**:
`index.pagina.pdf` via `pagina-pdf` (rechtstreeks uit die bron). Geen
verplichte product-`.tekstblad.pdf` meer; geen Coria uit dit spoor.

### Wat geen bron is

- `{stam}.vsa.mxl`, `{stam}.mscz.pdf`, … — altijd **afgeleide**; niet
  terug importeren om te “layouten”.
- Bestanden onder `content-source\input\` — werkvoorraad, geen publicatiebron.

## Publicatiesporen en publicatiecontroles

Elke bladermap onder `content-source\catalogus\<zangstuk>\<variant>\<uitvoeringsvorm>\`
kan één of meer **sporen** hebben. Het spoor volgt uit het **brontype**
(de echte extensie), niet uit een verzonnen middelste woord zoals vroeger
`partituur` of `print` in de bestandsnaam. Meerdere bronnen in één map
mogen; elk spoor houdt eigen siblings bij.

| Spoor (brontype)          | Canonieke bron                                   | Verwachte afgeleiden (doelvorm)                 | Stamp in afgeleide                    | Lokaal maken                                                | Publicatiecontrole                                                |
| ------------------------- | ------------------------------------------------ | ----------------------------------------------- | ------------------------------------- | ----------------------------------------------------------- | ----------------------------------------------------------------- |
| **vsa**                   | `{stam}.vsa`                                     | `{stam}.vsa.mxl` (Coria), `{stam}.vsa.svg` (scherm; geen verplichte `.vsa.pdf`) | `vsa-source-sha256` van de `.vsa`     | `scripts\vsa-products.cmd`                                  | **Actief:** `check_vsa_products`                                  |
| **lyrics** (zoektekst)    | `{stam}.vsa` / `.mvsa` / `.mscz`                 | `{stam}.vsa.lyrics.txt` / `.mvsa.lyrics.txt` / `.mscz.lyrics.txt` | `vsa-source-sha256` van de bron (`kind` = `vsa` / `mvsa` / `partituur`) | `scripts\lyrics-products.cmd`                               | **Actief:** `check_lyrics_products`                               |
| **mscz** (basispartituur) | `{stam}.mscz`                                    | `{stam}.mscz.mxl`, `{stam}.mscz.svg` (scherm; geen verplichte `.mscz.pdf`) | `vsa-partituur-sha256` van de `.mscz` | `scripts\mscz-products.cmd`                                 | **Actief:** `check_mscz_products`                                 |
| **import** (bewerkvorm)   | `{stam}.mscz`                                    | `{stam}.mscz.mvsa` (optioneel)                  | `vsa-partituur-sha256` in commentaren | `scripts\import-mvsa.cmd`                                   | **Actief:** `check_import_mvsa` (alleen bestaande siblings)       |
| **mvsa**                  | `{stam}.mvsa`                                    | `{stam}.mvsa.mxl`, `{stam}.mvsa.score-ir.json`, `{stam}.mvsa.from-ir.musicxml`; `{stam}.mvsa.svg` optioneel bij geldige from-ir (geen verplichte `.mvsa.pdf`) | `vsa-source-sha256` van de `.mvsa`    | `scripts\mvsa-products.cmd`                                 | **Actief:** `check_mvsa_products`                                 |
| **audio** (preview)       | `{stam}.mvsa` / `.mscz` / `.vsa`                 | `{stam}.mvsa.mp3` / `.mscz.mp3` / `.vsa.mp3`    | hash van die bron in het mp3          | `scripts\audio-products.cmd` (of `products`)                | **Actief:** `check_audio_products` (zelfde bronnen als Coria-MXL) |
| **tekstblad**             | `{stam}.tekstblad.md`                            | geen verplichte product-PDF; blad = `index.pagina.pdf` | —                                     | `scripts\pagina-pdf.cmd`                                    | **Actief:** `check_tekstblad_products` (bron)                     |
| **Coria-contract**        | bestaande `.vsa.mxl` / `.mscz.mxl` / `.mvsa.mxl` | (geen nieuw bestand; checklist op de sibling)   | —                                     | `scripts\products.cmd --kinds mscz,mvsa,vsa --only-invalid` | **Actief:** `check_mxl_playback_contract`                         |

**Catalogus-id** (`zangstuk/variant/uitvoeringsvorm`) hoort op elk
menselijk leesbaar blad (PDF / MuseScore-colofon). Scripts geven dat
expliciet door (`--catalogus-id`); pad-raden is alleen fallback in de
tooling.

### Handmatige artefacten (vervangt `.print.mscz`)

Vroeger markeerde de bestandsnaam **`.print.mscz`** een MuseScore-blad
buiten de automatische keten. Die pseudo-extensie past **niet** in de
regel “bron = één echte extensie”.

**Doelvorm:**

1. Het MuseScore-bestand heet gewoon `{stam}.mscz`.
2. Op de bladermap-`index.md` staat:

```yaml
artefacten_handmatig: true
```

3. PDF (en eventuele Coria-`.mxl`) houd je zelf bij als
   `{stam}.mscz.pdf` / `{stam}.mscz.mxl` (of legacy korte namen tot
   migratie). Publicatiecontroles **slaan** zulke mappen over.

**Nog in de repo:** enkele legacy-bestanden `*.print.mscz`. Die blijven
herkend tot ze hernoemd zijn; nieuwe bladen krijgen geen `.print.` meer
in de naam.

## Herkomststempels (waarom CI “stale” zegt)

De publicatiecontrole kijkt niet naar de klok van het bestand, maar naar
een hash in het product (bij PDF/MXL in metagegevens; bij mp3 in ID3-tags):

| Veld                   | Betekenis                                                                                  |
| ---------------------- | ------------------------------------------------------------------------------------------ |
| `vsa-source-sha256`    | Hash van de tekstbron (`.vsa` / tekstblad-`.md` / `.mvsa`)                                 |
| `vsa-source-kind`      | Welk brontype (`vsa`, `tekstblad`, `mvsa`, `partituur`, …)                                 |
| `vsa-partituur-sha256` | Hash van de basispartituur-`.mscz` (ook in import-`.mscz.mvsa`-commentaren en `.mscz.mp3`) |
| `vsa-generated-at`     | Wanneer het product is gemaakt (informatief)                                               |

Ontbreekt de stamp, of wijkt de hash af van de huidige bron → **unstamped**
of **stale**. Ontbreekt het sibling-bestand → **missing**.

## Wat `check` en CI doen

| Stap                                                       | Lokaal `check`                       | Pages-CI                     |
| ---------------------------------------------------------- | ------------------------------------ | ---------------------------- |
| Geldigheidscontrole (`vsa validate`) op bibliotheek        | ja                                   | ja                           |
| Publicatiecontrole VSA (`.vsa` ↔ MXL/PDF/SVG)               | waarschuwing; met `--strict` fout    | fout (`--fail`)              |
| Publicatiecontrole partituur (`.mscz` ↔ PDF/MXL)           | waarschuwing; met `--strict` fout    | fout (`--fail`)              |
| Publicatiecontrole tekstblad (`.tekstblad.md` ↔ PDF)       | waarschuwing; met `--strict` fout    | fout (`--fail`)              |
| Importcontrole (bestaande `.mscz.mvsa` ↔ `.mscz`)          | waarschuwing; met `--strict` fout    | fout (`--fail`)              |
| Publicatiecontrole mvsa (`.mvsa` ↔ MXL/PDF/SVG)             | waarschuwing; met `--strict` fout    | fout (`--fail`)              |
| Publicatiecontrole audio (`.mvsa`/`.mscz`/`.vsa` ↔ `.mp3`) | waarschuwing; met `--strict` fout    | fout (`--fail`)              |
| Legacy bladermap-SVG uit `.vsa`                            | vernieuwen (`oefenhoek-index --svg`) | vernieuwen (geen stamp-fail) |
| Koormap-blad `index.pagina.pdf`                            | niet (lokaal `pagina-pdf`)           | niet                         |
| Coria-fingerprints + Hugo                                  | ja                                   | ja                           |

CI **genereert geen** MuseScore-/PDF-/audio-producten en geen sibling-SVG
(`.vsa.svg` / `.mvsa.svg`). Vernieuw die lokaal (`all-products`, of apart
`vsa-products`, `mscz-products`, `tekstblad-products`, `mvsa-products`,
`audio-products`, eventueel `import-mvsa`) en commit siblings mee. Het
scherm toont `{stam}.vsa.svg` of `{stam}.mvsa.svg`. Zolang de `.vsa.svg`
ontbreekt, vult `oefenhoek-index --svg` een legacy-plaatje onder
`static\vsa\bladermap\` (geen stempel, geen “stale”-fout).

Het koormap-blad `index.pagina.pdf` is geen catalogus-sibling. `products`
en `check` slaan het over. Na de catalogusproducten:
`scripts\pagina-pdf.cmd`. Bij `pdf-bijelkaar` maakt dat commando een
tijdelijke compacte SVG; `{stam}.mvsa.svg` blijft het gewone webplaatje.
Commit de blad-PDF mee, anders tonen Download pagina en Print pagina niet.

Op bibliotheek-bladermappen: icoon **♪** (linksboven op de partituur)
opent **Oefenen** en **Beluisteren** (Beluisteren bij elke bron met
passende `.mp3`). Alleen in de catalogus: icoon **{}** (rechtsboven)
opent **Bronnen** als er een `.vsa` of `.mvsa` is; dat toont de
feitelijke brontekst in plaats van de gerenderde partituur.
**Downloaden** en **Printen** in dat menu gelden dan voor dat
bronbestand. Bij alleen een `.mscz` (geen VSA-tekst) ontbreekt het
icoon **Bronnen**.

## Legacy-namen (nog toegestaan tot migratie)

Zolang er in één bladermap **hoogstens één** PDF of Coria-`.mxl` van een
bepaald type is, kunnen oude namen nog voorkomen. Nieuwe of vernieuwde
producten gebruiken de doelvorm hierboven.

| Legacy                                          | Betekenis / migratie                                             |
| ----------------------------------------------- | ---------------------------------------------------------------- |
| `{stam}.mxl` / `{stam}.pdf` naast `{stam}.mscz` | Impliciet partituur → doel `{stam}.mscz.mxl` / `{stam}.mscz.pdf` |
| `{stam}.partituur.mxl` / `{stam}.partituur.pdf` | Oude representatie-id in de naam → zelfde doelvorm met `.mscz.`  |
| `{stam}.print.mscz`                             | → `{stam}.mscz` + `artefacten_handmatig: true`                   |
| `{stam}.print.pdf`                              | → `{stam}.mscz.pdf` (handmatig)                                  |
| `{stam}.vsa.mxl`                                | **Al doelvorm** — geen hernoem nodig                             |

Zodra twee producten van hetzelfde type in één map moeten, is de
expliciete `{stam}.{bron-extensie}.{doel-extensie}`-vorm **verplicht**
(geen stille overwrite van een korte naam).

## Voorbeelden

Alleen `.vsa` (actieve publicatiecontrole):

```text
content-source\catalogus\tropaar\zondag-toon-1\groningen\
  tropaar-zondag-toon-1-groningen.vsa
  tropaar-zondag-toon-1-groningen.vsa.mxl
  tropaar-zondag-toon-1-groningen.vsa.pdf
  tropaar-zondag-toon-1-groningen.vsa.svg
  index.md
```

```cmd
scripts\vsa-products.cmd content-source\catalogus\tropaar\zondag-toon-1\groningen
check --strict
```

Of via de wrapper (zelfde map, alle kinds die daar van toepassing zijn):

```cmd
scripts\products.cmd content-source\catalogus\tropaar\zondag-toon-1\groningen
```

Basispartituur (doelvorm; actieve publicatiecontrole):

```text
…
  trisagion-8a-nederlands-hemelum.mscz
  trisagion-8a-nederlands-hemelum.mscz.pdf
  trisagion-8a-nederlands-hemelum.mscz.mxl
```

Handmatig MuseScore-blad (geen automatische publicatiecontrole):

```yaml
# index.md
artefacten_handmatig: true
```

```text
…
  …-hemelum.mscz
  …-hemelum.mscz.pdf
```

## Zie ook

- [Werktrajecten](../werktrajecten/) — pijplijnen per spoor
- [check](../scripts/check/) · [vsa-products](../scripts/vsa-products/) · [validate](../scripts/validate/)
- [Woorden](woorden/)
- Repo-contract (kort): [docs/publicatiecontrole.md](https://github.com/orthodox-ronl/bibliotheek/blob/development/docs/publicatiecontrole.md)
- Tooling-conventie: [bestandsnaamgeving](https://orthodox-ronl.github.io/VSA-tooling/formats/canonical-checklists/#bestandsnaamgeving-conventie)

{{< navbuttons "Woorden|/handleiding/start/woorden/" "Werktrajecten|/handleiding/werktrajecten/" >}}
