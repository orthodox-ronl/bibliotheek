---
title: "pagina-pdf"
linkTitle: "pagina-pdf"
weight: 52
---

# NAME

`scripts\pagina-pdf.cmd` — PDF van een koormap- of cataloguspagina
samenstellen uit catalogus-product-PDF’s

# SYNOPSIS

```cmd
scripts\pagina-pdf.cmd <pad\naar\index.md> [--force]
scripts\pagina-pdf.cmd --all-koormappen [--force]
```

# DESCRIPTION

Leest de Markdown van een bladermap-pagina (`bieb` / `muziek`). Voor elke
partituur op die pagina zoekt het script de product-PDF in de catalogus
(`.mvsa.pdf`, anders `.mscz.pdf` / `.vsa.pdf`) en plakt die achter elkaar.
Het resultaat komt naast de Markdown als `index.pagina.pdf`. Die file is
een Hugo page resource: de knop **Download** bovenaan de pagina wijst
ernaar.

Dit is de download van de **getoonde pagina**, niet van één los catalogusstuk.
Op het scherm kun je met **Print** de browserafdruk gebruiken (print-CSS,
inclusief `pdf-pagina`).

`pdf-bijelkaar` beïnvloedt in deze versie vooral de browserafdruk; de
samengevoegde PDF zet stukken gewoon na elkaar zonder te verkleinen.

# OPTIONS

| Optie | Betekenis |
| --- | --- |
| `--all-koormappen` | Alle `index.md` onder `content-source\koormappen` |
| `--force` | Opnieuw schrijven, ook als de PDF nieuwer lijkt dan de bronnen |

# EXAMPLES

Vredeslitanie (NL + KSL, met `pdf-pagina` in de Markdown):

```cmd
scripts\pagina-pdf.cmd content-source\koormappen\hemelum\liturgie-zondag\vredeslitanie\index.md
```

# WHEN

Je hebt de shortcodes op een slot-pagina gezet of gewijzigd en wilt de
Download-knop een actuele pagina-PDF geven.

# SEE ALSO

- [Catalogus en koormappen](/handleiding/start/catalogus-en-koormappen/)
- Spec: `docs\specs\koormap-paginataal.md` in de repository
