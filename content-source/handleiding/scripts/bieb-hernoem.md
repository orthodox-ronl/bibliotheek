---
title: "bieb hernoem"
linkTitle: "bieb hernoem"
weight: 165
---

# NAME

`bieb hernoem` — zangstuk-id hernoemen (map, publicatiestam, verwijzingen)

# SYNOPSIS

```cmd
scripts\bieb.cmd hernoem <oud-zangstuk> <nieuw-zangstuk> [--dry-run]
```

# DESCRIPTION

Hernoemt één **zangstuk-id** (de bovenste map onder
`content-source\catalogus\`). Voorbeeld uit de afgeronde hernoem-golf:
`110-tropaar` → `tropaar` (die hernoeming is al uitgevoerd; de
commando’s hieronder zijn ter illustratie).

Het script:

1. Verplaatst de zangstuk-map naar de nieuwe naam.
2. Hernoemt alle productbestanden waarvan de naam met `{oud}-` begint
   (publicatiestam: `.vsa`, `.vsa.mxl`, `.lyrics.txt`, `.mp3`, …).
3. Verplaatst bladermap-SVG’s onder `static\vsa\bladermap\catalogus\`.
4. Werkt tekstverwijzingen bij (`bieb id=…`, `alias_van`, colofons, docs).

Daarna opnieuw: `python scripts\build_zoek_index.py` en
`scripts\check.cmd` (SVG/fingerprints/Hugo).

# EXAMPLES

```cmd
scripts\bieb.cmd hernoem 110-tropaar tropaar --dry-run
scripts\bieb.cmd hernoem 110-tropaar tropaar
scripts\bieb.cmd hernoem 120-kondak kondak
```

(Die voorbeelden zijn historisch; die mappen heten al `tropaar` /
`kondak`.)
# SEE ALSO

[bieb accepteer](../bieb-accepteer/),
[Zangstuk-soorten](/handleiding/start/zangstuk-soorten/)
