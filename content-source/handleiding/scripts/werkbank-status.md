---
title: "werkbank-status"
linkTitle: "werkbank-status"
weight: 132
---

# NAME

`scripts\werkbank-status.cmd` — overzicht open werkbank-cases

# SYNOPSIS

```cmd
scripts\werkbank-status.cmd [--quiet]
```

# DESCRIPTION

Toont welke uitvoeringsvormen of inputs nog in de lifecycle-fase
**Werkbank** (pre-productie) hangen:

- rijen in `content-source\input\werkvoorraad.md` waarvan de stap niet
  `gepubliceerd` is;
- bibliotheek-leaves zonder canonieke bron (`.mscz` / `.vsa` / `.mvsa` /
  `.tekstblad.md`), typisch stubs met `publicatiestatus: voorzien`;
- lokale mappen onder `content-source\input\_werk\` (alleen op jouw pc).

Schrijft `data\werkbank-status.json` voor de special page
[Werkbank](/catalogus/speciaal/werkbank/). Met `--quiet` alleen die
JSON (zoals vanuit `update-werkvoorraad` / `check` / `build` / `serve`).

# EXAMPLES

```cmd
scripts\werkbank-status.cmd
```

# WHEN

Als je wilt weten wat er nog in pre-productie openstaat, of vóór je een
batch `bieb accepteer` plant. Fase-uitleg:
[Werkbank](/handleiding/start/werkbank/).

# SEE ALSO

- [lifecycle-grenzen](../lifecycle-grenzen/)
- [update-werkvoorraad](../update-werkvoorraad/)
- [bieb accepteer](../bieb-accepteer/)
- [Levenscyclus](/handleiding/start/levenscyclus/)
