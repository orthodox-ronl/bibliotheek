---
title: "bieb accepteer"
linkTitle: "bieb accepteer"
weight: 160
---

# NAME

`bieb accepteer` — partituur of tekstblad opnemen in de bibliotheek

# SYNOPSIS

```cmd
scripts\bieb.cmd accepteer [id] [bestand...] [opties]
```

Compat-shim: `scripts\bieb-accepteer.cmd` (zelfde argumenten).

# DESCRIPTION

Neemt een klaar bestand op in de **bibliotheek** (de catalogus onder
`content-source\bibliotheek\`), onder een bibliotheek-id van drie lagen:
`zangstuk/variant/uitvoeringsvorm`. Toegestaan: basispartituur-`.mscz`,
`.vsa`, `.mvsa`, handmatig `.mscz` (met `--artefacten-handmatig` of legacy
`.print.mscz`), of `.tekstblad.md` (optioneel sibling-`.pdf` / `.mxl`). Bij
`.tekstblad.md` zet het script indien nodig frontmatter `build: render: never`
zodat de bron geen Hugo-pagina wordt.

Het script maakt ontbrekende `_index.md` / `index.md` met shortcode `bieb`
en hernoemt naar de publicatiestam. Sibling-PDF/MXL krijgen de doelvorm
`{stam}.mscz.pdf` / `{stam}.mscz.mxl` (of `.vsa.mxl` / `.tekstblad.pdf`).
Een kale ongekuiste `.mxl` wordt geweigerd — eerst
[opkuisen](../opkuisen/) / [layout](../layout/). Bij `.vsa` / `.mvsa` draait
validate (tenzij `--skip-vsa-validate`). Default
`publicatiestatus: reviewable` (`voorzien` bij `--stub`). Status
`productie` alleen met `--force`.

Ontbreken id of bestand, dan vraagt het script die interactief. Typ `?`
voor uitleg, daarna opnieuw invullen. Zonder argumenten: beide vragen.

Latere subcommando’s van `bieb` (voorzien): `zoek`, `hernoem`, …

# OPTIONS

| Optie | Betekenis |
| --- | --- |
| `--title` | Titel override |
| `--status` | Publicatiestatus |
| `--stub` | Lege leaf (`voorzien`) |
| `--move` | Bronbestand verplaatsen in plaats van kopiëren |
| `--force` | Overschrijven / `productie` toestaan |
| `--dry-run` | Alleen tonen |
| `--skip-vsa-validate` | Geen `vsa`/`mvsa validate` |
| `--artefacten-handmatig` | Zet `artefacten_handmatig: true` |

# EXAMPLES

```cmd
scripts\bieb.cmd accepteer
scripts\bieb.cmd accepteer 8-trisagion/8a-nederlands/hemelum pad\naar\bestand.mscz --dry-run
```

# WHEN

Als de partituur klaar is om van de **Werkbank** naar de **Catalogus** te
gaan (na opkuisen / normaliseren, of na een werkende `.vsa` / `.mvsa`).
Overgangscriteria: [Werkbank](/handleiding/start/werkbank/#overgangscriteria).
Daarna producten + `check --strict` — [Catalogus](/handleiding/start/catalogus/).

# SEE ALSO

- Lifecycle: [Levenscyclus](/handleiding/start/levenscyclus/)
- Workflow: [Opnemen in de bibliotheek](/handleiding/werktrajecten/opnemen-in-bibliotheek/)
- [werkbank-status](../werkbank-status/)
- [check](../check/)
- [update-werkvoorraad](../update-werkvoorraad/)
- [Publicatiecontrole](/handleiding/start/publicatiecontrole/)
