---
title: "Productgates en bestandsnamen"
linkTitle: "Productgates"
weight: 25
---

# Productgates en bestandsnamen

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
  bijv. `{stam}.vsa.mxl`, `{stam}.mscz.pdf`
- **Productgate** = controle of die afgeleide nog bij de bron past (sha-stamp);
  CI genereert niet, jij wel lokaal
- **Handmatig** = `artefacten_handmatig: true` op `index.md` (vervangt het
  oude `.print.mscz`-spoor)
{{< /cue >}}

## Wat is een productgate?

Een **productgate** is een vaste controle in `check` / GitHub Actions:

1. Zoek canonieke **bronbestanden** in `content-source\bibliotheek\`.
2. Eis dat de bijbehorende **afgeleide** (sibling) bestaat.
3. Eis dat de afgeleide een **provenance-stamp** heeft die bij de huidige
   bron past (geen verouderd of “leeg” product).

Faalt de gate, dan vernieuw je lokaal met het product-commando en commit je
bron **en** afgeleide samen. De build op GitHub **schrijft geen** MuseScore-
of MusicXML-producten opnieuw.

## Bestandsnamen (doelvorm)

### Stam

De **publicatiestam** is de bestandsnaam zonder extensies:

`{zangstuk-id}-{variant-id}-{uitvoeringsvorm-id}`

Alleen kleine letters, cijfers, `_` en `-` — **geen spaties**.
Voorbeeld: `8-trisagion-8a-nederlands-hemelum`.

### Bron versus afgeleide

| Rol | Patroon | Voorbeelden |
| --- | --- | --- |
| **Bron** | `{stam}` + **één** echte extensie | `….vsa`, `….mscz`, `….mvsa` |
| **Afgeleide** | `{stam}.{bron-extensie}.{doel-extensie}` | `….vsa.mxl`, `….mscz.pdf`, `….mscz.mxl`, `….mvsa.mscz` |

De **laatste** segment is wat programma’s als bestandstype zien (`.mxl`,
`.pdf`, `.mscz`, …). Het middelste segment zegt **uit welke bron** het
product komt. Zo botsen een Coria-bestand uit VSA en een Coria-bestand uit
een MuseScore-partituur nooit op dezelfde korte naam.

Deze regel sluit aan bij VSA-tooling (`stem.brontype.doeltype`). In de
bibliotheek is die vorm **normatief voor nieuwe en vernieuwde producten**.

### Tekstblad (uitzondering)

Liturgische tekst/dialoog is Markdown, maar een kale `.md` is te breed
(Hugo-pagina’s zijn ook `.md`). Daarom blijft het inhoudstype in de naam:

| Bron | Afgeleide |
| --- | --- |
| `{stam}.tekstblad.md` | `{stam}.tekstblad.pdf` |

Geen Coria uit dit spoor.

### Wat geen bron is

- `{stam}.vsa.mxl`, `{stam}.mscz.pdf`, … — altijd **afgeleide**; niet
  terug importeren om te “layouten”.
- Bestanden onder `content-source\input\` — werkvoorraad, geen publicatiebron.

## Publicatiesporen en gates

Elke bladermap onder `content-source\bibliotheek\<zangstuk>\<variant>\<uitvoeringsvorm>\`
kan één of meer **sporen** hebben. Het spoor volgt uit het **brontype**
(de echte extensie), niet uit een verzonnen middelste woord zoals vroeger
`partituur` of `print` in de bestandsnaam.

| Spoor (brontype) | Canonieke bron | Verwachte afgeleiden (doelvorm) | Stamp in afgeleide | Lokaal maken | Gate |
| --- | --- | --- | --- | --- | --- |
| **vsa** | `{stam}.vsa` | `{stam}.vsa.mxl` (Coria) | `vsa-source-sha256` van de `.vsa` | `scripts\vsa-products.cmd` | **Actief:** `check_vsa_products` |
| **mscz** (basispartituur) | `{stam}.mscz` | `{stam}.mscz.pdf`, `{stam}.mscz.mxl` | `vsa-partituur-sha256` van de `.mscz` | later `mscz-products` / `mvsa pdf`+`mscz` met `--bibliotheek-id` | **Voorzien** |
| **mvsa** | `{stam}.mvsa` | `{stam}.mvsa.mxl` / `.mscz` / `.pdf` (naarmate het traject) | source-sha van de `.mvsa` | later product-wrapper om `mvsa …` | **Voorzien** (nog geen bieb-`.mvsa`) |
| **tekstblad** | `{stam}.tekstblad.md` | `{stam}.tekstblad.pdf` | `vsa-source-sha256` van de `.md` | later `tekstblad-products` | **Voorzien** |

**Bibliotheek-id** (`zangstuk/variant/uitvoeringsvorm`) hoort op elk
menselijk leesbaar blad (PDF / MuseScore-colofon). Scripts geven dat
expliciet door (`--bibliotheek-id`); pad-raden is alleen fallback in de
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
   migratie). Productgates **slaan** zulke mappen over.

**Nog in de repo:** enkele legacy-bestanden `*.print.mscz`. Die blijven
herkend tot ze hernoemd zijn; nieuwe bladen krijgen geen `.print.` meer
in de naam.

## Provenance-stamps (waarom CI “stale” zegt)

De gate kijkt niet naar de klok van het bestand, maar naar een hash in
het product:

| Veld | Betekenis |
| --- | --- |
| `vsa-source-sha256` | Hash van de tekstbron (`.vsa` / tekstblad-`.md` / later `.mvsa`) |
| `vsa-source-kind` | Welk brontype (`vsa`, `tekstblad`, …) |
| `vsa-partituur-sha256` | Hash van de basispartituur-`.mscz` |
| `vsa-generated-at` | Wanneer het product is gemaakt (informatief) |

Ontbreekt de stamp, of wijkt de hash af van de huidige bron → **unstamped**
of **stale**. Ontbreekt het sibling-bestand → **missing**.

## Wat `check` en CI doen

| Stap | Lokaal `check` | Pages-CI |
| --- | --- | --- |
| `vsa validate` op bibliotheek | ja | ja |
| VSA-productgate (`.vsa` ↔ `.vsa.mxl`) | waarschuwing; met `--strict` fout | fout (`--fail`) |
| Partituur- / tekstblad- / mvsa-gate | nog niet | nog niet |
| Coria-fingerprints + Hugo | ja | ja |

CI **genereert geen** producten. Vernieuw lokaal (nu: `vsa-products`),
commit siblings mee.

## Legacy-namen (nog toegestaan tot migratie)

Zolang er in één bladermap **hoogstens één** PDF of Coria-`.mxl` van een
bepaald type is, kunnen oude namen nog voorkomen. Nieuwe of vernieuwde
producten gebruiken de doelvorm hierboven.

| Legacy | Betekenis / migratie |
| --- | --- |
| `{stam}.mxl` / `{stam}.pdf` naast `{stam}.mscz` | Impliciet partituur → doel `{stam}.mscz.mxl` / `{stam}.mscz.pdf` |
| `{stam}.partituur.mxl` / `{stam}.partituur.pdf` | Oude representatie-id in de naam → zelfde doelvorm met `.mscz.` |
| `{stam}.print.mscz` | → `{stam}.mscz` + `artefacten_handmatig: true` |
| `{stam}.print.pdf` | → `{stam}.mscz.pdf` (handmatig) |
| `{stam}.vsa.mxl` | **Al doelvorm** — geen hernoem nodig |

Zodra twee producten van hetzelfde type in één map moeten, is de
expliciete `{stam}.{bron-extensie}.{doel-extensie}`-vorm **verplicht**
(geen stille overwrite van een korte naam).

## Voorbeelden

Alleen `.vsa` (actieve gate):

```text
content-source\bibliotheek\110-tropaar\zondag-toon-1\groningen\
  110-tropaar-zondag-toon-1-groningen.vsa
  110-tropaar-zondag-toon-1-groningen.vsa.mxl
  index.md
```

```cmd
scripts\vsa-products.cmd content-source\bibliotheek\110-tropaar\zondag-toon-1\groningen
check --strict
```

Basispartituur (doelvorm; gate nog voorzien):

```text
…
  8-trisagion-8a-nederlands-hemelum.mscz
  8-trisagion-8a-nederlands-hemelum.mscz.pdf
  8-trisagion-8a-nederlands-hemelum.mscz.mxl
```

Handmatig MuseScore-blad (geen auto-gate):

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
- Repo-contract (kort): [docs/productgates.md](https://github.com/orthodox-ronl/bibliotheek/blob/development/docs/productgates.md)
- Tooling-conventie: [bestandsnaamgeving](https://orthodox-ronl.github.io/VSA-tooling/formats/canonical-checklists/#bestandsnaamgeving-conventie)

{{< navbuttons "Woorden|/handleiding/start/woorden/" "Werktrajecten|/handleiding/werktrajecten/" >}}
