---
title: "h"
linkTitle: "h"
weight: 10
---

# NAME

`scripts\h.cmd` — overzicht van commando’s, of doorverwijzen naar `-h`

# SYNOPSIS

```cmd
scripts\h.cmd
scripts\h.cmd <naam>
scripts\h.cmd bieb hernoem
scripts\h.cmd -h
```

Met `.\scripts` op PATH kun je ook `h` of `h check` typen.

# DESCRIPTION

Zonder argument toont `h` een korte lijst van de
gebruikerscommando’s (`.cmd`) in deze repository, met één zin wat elk
doet.

Met een naam (bijvoorbeeld `check`, `serve` of `bieb`) roept `h`
**hetzelfde** aan als `<naam> -h`. Voor subcommando’s:

```cmd
h bieb hernoem
```

is gelijk aan `bieb hernoem -h`.

De console-tekst is bewust kort. De **uitgebreide** uitleg staat in
deze handleiding-sectie [Scripts](../).

# EXAMPLES

```cmd
scripts\h.cmd
scripts\h.cmd check
scripts\h.cmd bieb
scripts\h.cmd bieb hernoem
```

# WHEN

Als je de naam van een script niet meer weet, of even de opties wilt
zien zonder de browser te openen.

# SEE ALSO

- [Script-referentie](../)
- Bestand `scripts\README.md` in de repository-map `bibliotheek`
