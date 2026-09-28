---
title: "ensure-bibliotheek-id"
linkTitle: "ensure-bibliotheek-id"
weight: 120
---

# NAME

`scripts\ensure-bibliotheek-id.cmd` — bibliotheek-id in het colofon zetten of controleren

# SYNOPSIS

```cmd
scripts\ensure-bibliotheek-id.cmd [root] [--check-only] [--fail]
```

# DESCRIPTION

Elke basispartituur-`.mscz` onder `content-source\bibliotheek\` moet in het
colofon de regel `Bibliotheek-id:` hebben. Die waarde moet gelijk zijn aan
het pad `zangstuk/variant/uitvoeringsvorm` van de map.

Lokaal herstelt dit commando ontbrekende of verkeerde id’s door hetzelfde
layoutprofiel te draaien als [layout](../layout/) (geen MuseScore-venster
nodig). Met `--check-only` (of in CI) alleen rapporteren, niet schrijven.
Op `main`, met `--fail`, of met `BIBLIOTHEEK_ID_STRICT=1` faalt de check
als er nog problemen zijn.

Zonder `root` zoekt het script onder `content-source\bibliotheek`.
Mappen met `artefacten_handmatig: true` en bestanden `*.print.mscz` worden
overgeslagen. Na een herstel: opnieuw [mscz-products](../mscz-products/)
voor verse PDF’s met het juiste colofon.

# OPTIONS

| Optie | Betekenis |
| --- | --- |
| `root` | Map waaronder gezocht wordt (default: bibliotheek) |
| `--check-only` | Alleen controleren, niet schrijven |
| `--fail` | Exitcode 1 bij problemen (ook buiten de strenge pipeline) |

# WHEN

Na [layout](../layout/) of na verplaatsing in de bibliotheek, of als `check`
een id-mismatch meldt.

# SEE ALSO

- [layout](../layout/)
- [mscz-products](../mscz-products/)
- [Publicatiecontrole](/handleiding/start/publicatiecontrole/)
