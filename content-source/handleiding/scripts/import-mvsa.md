---
title: "import-mvsa"
linkTitle: "import-mvsa"
weight: 105
---

# NAME

`scripts\import-mvsa.cmd` — bewerkvorm `{stam}.mscz.mvsa` maken naast een
basispartituur-`.mscz`

# SYNOPSIS

```cmd
scripts\import-mvsa.cmd [pad] [--force] [--dry-run] [--create] [--pitch a-g]
```

# DESCRIPTION

Maakt of vernieuwt de sibling **`{stam}.mscz.mvsa`**: een meerstemmige
tekstbron die je uit de basispartituur-`.mscz` haalt om verder te bewerken
in VSA/mvsa. Dit is een **import-/bewerkvorm**, geen PDF of Coria voor de
site. Koormappen en publicatiecontroles eisen die sibling **niet**.

Onder de motorkap roept het script de tooling-CLI `mscz import` aan
(MuseScore 4 zet de partituur eerst om naar MusicXML; daarna volgt
`.mvsa`). Daarna schrijft het script herkomstcommentaren bovenaan het
bestand (`vsa-partituur-sha256`, `vsa-generated-at`), zodat
`check` / CI kunnen zien of de import nog bij de huidige `.mscz` past.

**Standaard (map of hele bibliotheek):** alleen **bestaande**
`.mscz.mvsa`-siblings vernieuwen die verouderd of zonder stamp zijn.
Er wordt geen nieuwe `.mscz.mvsa` aangemaakt voor elke partituur.

**Nieuwe import:** geef één `.mscz`-bestand op de regel, of gebruik
`--create` op een map om ontbrekende siblings te maken.

Bestanden in `input\`, namen die eindigen op `.print.mscz`, en mappen met
`artefacten_handmatig: true` worden overgeslagen. CI genereert deze
bestanden niet; jij wel lokaal (MuseScore 4 nodig), daarna committen als
je de bewerkvorm wilt bijhouden.

# OPTIONS

| Optie | Betekenis |
| --- | --- |
| `--force` | Ook importeren als `.mscz.mvsa` al bij de bron past |
| `--dry-run` | Alleen tonen wat er zou gebeuren |
| `--create` | Bij een map: ook ontbrekende `.mscz.mvsa` maken |
| `--pitch` | Spelling voor `mscz import`: `a-g` (default), `doremi`, `abc`, `vsa` |

# EXAMPLES

```cmd
rem Vernieuw bestaande import-siblings onder de hele bibliotheek:
scripts\import-mvsa.cmd

rem Eerste import voor één partituur:
scripts\import-mvsa.cmd content-source\bibliotheek\trisagion\8a-nederlands\hemelum\trisagion-8a-nederlands-hemelum.mscz

rem Alle ontbrekende siblings in één tak (zeldzaam):
scripts\import-mvsa.cmd content-source\bibliotheek\trisagion --create
```

# WHEN

Als je een basispartituur als `.mvsa` wilt bewerken, of als `check --strict`
meldt dat een bestaande `.mscz.mvsa` verouderd of zonder stamp is.

# SEE ALSO

- [check](../check/)
- [mscz-products](../mscz-products/) (site-PDF/Coria; ander spoor)
- [Publicatiecontrole](/handleiding/start/publicatiecontrole/) (importcontrole)
- Tooling: [`mscz import`](https://orthodox-ronl.github.io/VSA-tooling/reference/cli/mscz/)
