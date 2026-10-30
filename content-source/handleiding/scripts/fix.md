---
title: "fix"
linkTitle: "fix"
weight: 22
---

# NAME

`scripts\fix.cmd` — auto-fixbare problemen uit `check` afwerken via
`data\check-fixlist.json`

# SYNOPSIS

```cmd
scripts\fix.cmd [--check] [--dry-run] [-y] [--verbose]
```

# DESCRIPTION

Na een `check` (met of zonder `--strict`) schrijft de repository een
**afwerklijst** in `data\check-fixlist.json`. Elke regel is één probleem
waarvoor check al een eenvoudig herstelcommando kent (`fix_cmd`),
bijvoorbeeld `scripts\pdf.cmd …\index.md` bij een verouderde blad-PDF.

Dit commando:

1. **toont** die lijst (`--dry-run`), of
2. **voert** elke `fix_cmd` uit en **schrapt** geslaagde regels uit het
   bestand.

Zo kun je na `fix` opnieuw `check --strict` draaien en — voor alles wat
auto-fixbaar was — op 0 problemen uitkomen.

**`--check`:** runt eerst `check --strict`, bouwt daarna de fixlist opnieuw
uit de status-JSON’s, en toont of werkt die verse lijst af. Exitcode 1 van
check (er zijn product/pdf-problemen) is **verwacht** en stopt `fix`
niet. Exitcode 2 of hoger (validate/tooling/usage) wél: dan is er geen
betrouwbare lijst.

**`--dry-run`:** schrijft geen producten; met `--check` wél eerst de lijst
vernieuwen, daarna printen.

Zonder `--check` moet `data\check-fixlist.json` al bestaan (na een
eerdere `check` of `fix --check`). Ontbreekt het bestand: duidelijke
foutmelding.

Niet op de lijst: validate- of Hugo-fouten zonder `fix_cmd` — die blijven
handwerk.

Bij veel items (vaak tientallen of honderden blad-PDF’s) toont `fix`
preflight met geschatte duur. Korte runs starten zonder vraag; bij 100+
items de dubbele zekerheidsvraag. `-y` helpt bij zachte batches; bij 100+
niet.

# EXAMPLES

```cmd
REM Verse inventarisatie + alleen tonen
scripts\fix.cmd --check --dry-run

REM Inventariseren en meteen afwerken
scripts\fix.cmd --check

REM Bestaande lijst bekijken / afwerken (na eerdere check)
scripts\fix.cmd --dry-run
scripts\fix.cmd -y
```

# WHEN

Als `check --strict` product- of blad-PDF-problemen meldt en je die snel
wilt wegwerken zonder elk `fix:`-commando handmatig te plakken. Niet als
vervanging van inhoudelijk herstel bij validate-fouten.

# SEE ALSO

- [check](../check/)
- [pdf](../pdf/)
- [products](../products/)
- [Publicatiecontrole](../../start/publicatiecontrole/)
