---
title: "bieb verwijder"
linkTitle: "bieb verwijder"
weight: 166
---

# NAME

`bieb verwijder` — catalogus-id wissen en dangling verwijzingen tonen

# SYNOPSIS

```cmd
scripts\bieb.cmd verwijder <id> [--dry-run] [--force]
scripts\bieb.cmd delete <id> [--dry-run] [--force]
```

Met `.\scripts` op PATH: `bieb verwijder …`. Engelse alias: `delete`.
Korte hulp: `h bieb verwijder` of `bieb verwijder -h`. Typ `?` bij een
vraag voor uitleg.

# DESCRIPTION

Verwijdert één catalogus-id (zangstuk, variant of uitvoeringsvorm). De
vorm van het id bepaalt het niveau — dezelfde id-vormen en
ambiguïteitsregels als bij [bieb hernoem](../bieb-hernoem/) (slash, dash,
backslash, repo-pad, unieke suffix).

| Vorm | Betekenis |
| --- | --- |
| `ektinia` | hele zangstuk-boom |
| `ektinia/vredes` of `ektinia-vredes` | variant (inclusief alle uitvoeringsvormen eronder) |
| `ektinia/vredes/hemelum` of stam | één uitvoeringsvorm |

Is de invoer ambigu, dan toont het script genummerde voorstellen
(Enter = 1).

Het script:

1. Toont wat er uit `content-source\catalogus\` weggaat (en bladermap-SVG).
2. Zoekt **dangling refs** buiten die map: `bieb id=…`, `alias_van`, paden
   of publicatiestam in `content-source\` en `docs\`.
3. Meldt koormap-**mappen** waarvan de naam gelijk is aan het id/stam —
   die wist het **niet** (elke koormap heeft een eigen beheerder).
4. Zonder `--force`: stopt als er dangling refs zijn (ook bij `--dry-run`
   met exitcode 1, zodat je ziet dat wissen nog niet veilig is).
5. Met `--force`: wist de catalogusmap (en SVG) toch; dangling refs en
   koormap-slots blijven voor handmatig herstel.

Frontmatter-titels worden niet bijgewerkt (die leidt de bouw af).

Daarna: dangling/koormap zelf oplossen, dan
`python scripts\build_zoek_index.py` en `scripts\check.cmd`.

# EXAMPLES

```cmd
scripts\bieb.cmd verwijder ektinia/vredes/hemelum --dry-run
scripts\bieb.cmd delete ektinia\vredes\hemelum --dry-run
scripts\bieb.cmd verwijder ektinia/vredes/hemelum
scripts\bieb.cmd verwijder ektinia/vredes/hemelum --force
```

# WHEN

Als een uitvoeringsvorm (of hogere map) uit de catalogus moet en je wilt
eerst zien wie er nog naar wijst. Niet om alleen een koormap-slot leeg
te maken — pas daar de shortcode of slotpagina aan.

# SEE ALSO

[bieb hernoem](../bieb-hernoem/),
[bieb accepteer](../bieb-accepteer/),
[bieb kopieer](../bieb-kopieer/),
[check](../check/),
[h](../h/)
