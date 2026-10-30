---
title: "bieb accepteer"
linkTitle: "bieb accepteer"
weight: 160
---

# NAME

`bieb accepteer` — partituur of tekstblad opnemen in de catalogus

# SYNOPSIS

```cmd
scripts\bieb.cmd accepteer [id] [bestand...] [opties]
scripts\bieb.cmd accepteer [bestand|map] [opties]
scripts\bieb.cmd accept [id] [bestand...] [opties]
```

Engelse alias: `accept`. Compat-shim: `scripts\bieb-accepteer.cmd`
(zelfde argumenten).

# DESCRIPTION

Neemt een klaar bestand op in de **bibliotheek** (de catalogus onder
`content-source\catalogus\`), onder een catalogus-id van drie lagen:
`zangstuk/variant/uitvoeringsvorm`. Toegestaan: basispartituur-`.mscz`,
`.vsa`, `.mvsa`, handmatig `.mscz` (met `--manueel` of legacy
`.print.mscz`), of `.tekstblad.md` (optioneel sibling-`.pdf` / `.mxl`). Bij
`.tekstblad.md` zet het script indien nodig frontmatter `build: render: never`
zodat de bron geen Hugo-pagina wordt.

Invoer volgt [bestand of map](../invoer-bestand-of-map/): één bronbestand,
of een **map** (recursief `.mscz` / `.vsa` / `.mvsa` / `.tekstblad.md`). Bij
een map wordt elk primair bestand apart opgenomen; het catalogus-id komt
uit de publicatiestam (geen interactieve id-vragen, geen `--title` of los
id). Preflight toont aantal + geschatte duur; bevestiging of `-y`. Eerst
`--dry-run` aanbevolen. `--move` blijft expliciet (verplaatst bronnen).

## Bestand eerst, id uit de bestandsnaam

Zonder argumenten vraagt het script **eerst** het bronbestand (of `stub`).
Dat bestand wordt meteen gecontroleerd (formaat; bij `.vsa` / `.mvsa` ook
validate). Pas daarna komt het catalogus-id — zo verspil je geen tijd aan
een id als de bron nog niet klopt.

Geef het bronbestand bij voorkeur al de **publicatiestam**-naam:

`zangstuk-variant-uitvoeringsvorm.ext`

voorbeeld: `kondak-johannes-de-theoloog-toon-2-liturgikon.vsa`.

Daaruit leidt accepteer het id af en vraagt ter bevestiging. Als je zowel
id als bestand doorgeeft, moet de bestandsstam bij het id passen; anders
stopt het script (typo-vangnet; `--force` om toch door te gaan).

Je mag het bestand ook als **eerste** CLI-argument geven (zonder id); het
script herkent een pad en leidt het id af.

## Bladpagina: geen title / linkTitle

Het script maakt ontbrekende `_index.md` / `index.md` met shortcode `bieb`
en hernoemt naar de publicatiestam. Getoonde namen leidt Hugo/zoek af uit
het id (en de bron); zie
[Catalogus en koormappen](../../start/catalogus-en-koormappen/) (§ Titels).
Op catalogus-id-pagina’s schrijft het script **geen** `title` / `linkTitle`.

`--title` alleen bij een **tekstblad**-bron (titel in die bron).
`check --strict` controleert dat de UV-labels in
`data/uitvoeringsvorm-link-titles.yaml` gelijk blijven aan Python
(`check_catalogus_leaf_titles`).

Sibling-PDF/MXL krijgen de doelvorm `{stam}.mscz.pdf` / `{stam}.mscz.mxl`
(of `.vsa.mxl` / `.tekstblad.pdf`). Een kale ongekuiste `.mxl` wordt
geweigerd — eerst [opkuisen](../opkuisen/) / [layout](../layout/). Default
`publicatiestatus: reviewable` (`voorzien` bij `--stub`). Status `productie`
alleen met `--force`.

Ontbreekt bestand of id, dan vraagt het script die interactief. Typ `?`
voor uitleg.

Andere subcommando’s van `bieb`: [hernoem](../bieb-hernoem/) (catalogus-id
wijzigen), [verwijder](../bieb-verwijder/) (wissen + dangling refs),
[kopieer](../bieb-kopieer/) (uitvoeringsvorm dupliceren).

# OPTIONS

| Optie | Betekenis |
| --- | --- |
| `--title` | Alleen tekstblad: titel in de tekstblad-bron |
| `--status` | Publicatiestatus |
| `--stub` | Lege leaf (`voorzien`); schrijft meteen `index.md.pdf` (tekst «Voorzien», geen partituur) |
| `--move` | Bronbestanden verplaatsen (default: kopieer) |
| `--force` | Overschrijven / `productie` / stam-mismatch toestaan |
| `--dry-run` | Alleen tonen |
| `-y`, `--yes` | Batch zonder bevestigingsvraag |
| `--skip-vsa-validate` | Geen `vsa`/`mvsa validate` |
| `--manueel` | Zet `manueel: true` |

# EXAMPLES

```cmd
rem Interactief: eerst bestand, dan bevestig afgeleid id
scripts\bieb.cmd accepteer

rem Bestand met publicatiestam-naam (id wordt afgeleid)
scripts\bieb.cmd accepteer pad\naar\trisagion-8a-nederlands-hemelum.vsa --dry-run

rem Klassiek: id + bestand (stammen moeten kloppen)
scripts\bieb.cmd accepteer trisagion/8a-nederlands/hemelum pad\naar\bestand.mscz --dry-run
```

# WHEN

Als de partituur klaar is om van de **Werkbank** naar de **Catalogus** te
gaan (na opkuisen / normaliseren, of na een werkende `.vsa` / `.mvsa`).
Overgangscriteria: [Werkbank](/handleiding/start/werkbank/#overgangscriteria).
Daarna producten + `check --strict` — [Catalogus](/handleiding/start/catalogus/).

# SEE ALSO

- Lifecycle: [Levenscyclus](/handleiding/start/levenscyclus/)
- Workflow: [Opnemen in de catalogus](/handleiding/werktrajecten/opnemen-in-catalogus/)
- Titels: [Catalogus en koormappen](/handleiding/start/catalogus-en-koormappen/#titels-en-frontmatter-in-de-catalogus)
- [werkbank-status](../werkbank-status/)
- [check](../check/)
- [update-werkvoorraad](../update-werkvoorraad/)
- [Publicatiecontrole](/handleiding/start/publicatiecontrole/)
