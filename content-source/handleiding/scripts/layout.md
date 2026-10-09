---
title: "layout"
linkTitle: "layout"
weight: 90
---

# NAME

`scripts\layout.cmd` — basispartituur-standaard toepassen (normaliseren / layouten)

# SYNOPSIS

```cmd
scripts\layout.cmd <bestand.mscz|.mxl> [-o doel.mscz] [--id ID] [--bron "…"]
```

# DESCRIPTION

Past de bibliotheek-**basispartituur**-standaard toe via het
VSA-tooling-layoutprofiel `partituur`: A4-papier, fonts, leesbaarheid,
copyright/colofon, en (indien bekend) de colofonregel met catalogus-id.
In het dagelijks taalgebruik heet deze stap vaak **layouten**; de
contractterm is **normaliseren**.

- Invoer is een opgekuiste `.mxl` (na [opkuisen](../opkuisen/)): het script
  roept `mxl mscz` aan (MuseScore 4) en past daarna het layoutprofiel toe.
  Zet `-o` naar een `.mscz` zonder spaties in de naam (meestal onder
  `input\_werk\<stam>\`).
- Invoer is al een `.mscz`: zonder `-o` wijzigt het script het bestand
  **in-place**. Opnieuw draaien mag en hoort na elke inhoudelijke editslag
  in MuseScore.
- Bestanden die eindigen op `.print.mscz` worden geweigerd (printvel:
  [Print-.mscz](/handleiding/partituur/7-print-mscz/)).
- **Bronvermelding:** met `--bron` (of automatisch uit
  `bron.uitgangspunt` van een sibling `.vsa`/`.mvsa`) schrijft het
  script MuseScore-meta `source` en de colofonregel “Bron: …”. Korte
  namen: [Uitgave-bronnen](/handleiding/start/uitgave-bronnen/).

Implementatie: `scripts\apply_mscz_layout.py` — dunne wrapper om
`vsa.mscz_layout` (geen fork van layout-logica). Technische norm in
VSA-tooling: layoutprofiel `partituur` / mscz-leesbaarheid.

# OPTIONS

| Optie | Betekenis |
| --- | --- |
| `-o`, `--output` | Pad van de doel-`.mscz` |
| `--id` | Catalogus-id `zangstuk/variant/uitvoeringsvorm` (anders afgeleid uit het pad onder `catalogus/`) |
| `--bron` | Bronvermelding (MuseScore `source` + colofon). Zonder vlag: `bron.uitgangspunt` uit sibling `.vsa`/`.mvsa` indien aanwezig |

# EXAMPLES

Van een opgekuiste `.mxl` naar een basispartituur-`.mscz` (stam is
illustratief):

```cmd
scripts\layout.cmd content-source\input\_werk\STAM\STAM.mxl -o content-source\input\_werk\STAM\STAM.mscz
```

Opnieuw op een bestaande basispartituur na een editslag in MuseScore:

```cmd
scripts\layout.cmd pad\naar\bestand.mscz --bron "Liturgikon, p.58"
```

Met expliciete catalogus-id:

```cmd
scripts\layout.cmd pad\naar\bestand.mscz --id trisagion/8a-nederlands/hemelum
```

# WHEN

Na opkuisen, of meteen als de inhoud van een ruwe `.mscz` al klopt. Opnieuw
na elke inhoudelijke editslag, vóór [mscz-products](../mscz-products/).

# SEE ALSO

- [opkuisen](../opkuisen/)
- [mscz-products](../mscz-products/)
- [ensure-bibliotheek-id](../ensure-bibliotheek-id/)
- Workflow: [Standaard-.mscz](/handleiding/partituur/3-standaard-mscz/)
