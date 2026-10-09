---
title: "bieb hernoem"
linkTitle: "bieb hernoem"
weight: 165
---

# NAME

`bieb hernoem` — zangstuk-id hernoemen (catalogusmap, publicatiestam,
tekstverwijzingen, koormap-slots)

# SYNOPSIS

```cmd
scripts\bieb.cmd hernoem <oud-zangstuk> <nieuw-zangstuk> [--dry-run]
```

Met `.\scripts` op PATH: `bieb hernoem …`. Korte hulp: `h bieb hernoem`
of `bieb hernoem -h`.

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
4. Hernoemt **koormap-slotmappen** die exact `{oud}` heten naar `{nieuw}`
   (bijvoorbeeld `…\liturgie-weekdagen\8-trisagion\` → `…\trisagion\`).
   Zo blijven inhoudsopgave-links en mapnamen gelijk; anders ontstaat een
   404 doordat Hugo de mapnaam volgt.
5. Werkt tekstverwijzingen bij (`bieb id=…`, `alias_van`, colofons, docs,
   inclusief koormap-inhoudsopgaven).

Hugo-`aliases` voor oude URL’s worden **niet** gezet.

Daarna opnieuw: `python scripts\build_zoek_index.py` en
`scripts\check.cmd` (SVG/fingerprints/Hugo). `check` controleert ook of
relatieve links in koormappen naar bestaande mappen wijzen
(`check_koormap_slot_links.py`).

**Let op:** koormap-slots die *niet* dezelfde mapnaam hebben als het
zangstuk-id (bijvoorbeeld litanie-slots na consolidatie naar `ektinia`)
worden niet hernoemd — die mappen blijven de liturgische pleknaam.

# EXAMPLES

Eerst altijd dry-run:

```cmd
scripts\bieb.cmd hernoem oud-zangstuk nieuw-zangstuk --dry-run
scripts\bieb.cmd hernoem oud-zangstuk nieuw-zangstuk
scripts\check.cmd --strict
```

Historische voorbeelden (die mappen heten al zo):

```cmd
scripts\bieb.cmd hernoem 110-tropaar tropaar --dry-run
scripts\bieb.cmd hernoem 120-kondak kondak
```

# WHEN

Als je een **zangstuk-id** (topmap onder `catalogus\`) wilt wijzigen
en alle verwijzingen, producten en 1:1-koormap-slots mee moeten. Niet
voor alleen een variant- of uitvoeringsvorm-map hernoemen — dat is
handmatig of een aparte migratie.

Werktraject: [Zangstuk hernoemen](/handleiding/werktrajecten/zangstuk-hernoemen/).

# SEE ALSO

[bieb accepteer](../bieb-accepteer/),
[check](../check/),
[Zangstuk hernoemen](/handleiding/werktrajecten/zangstuk-hernoemen/),
[Zangstuk-soorten](/handleiding/start/zangstuk-soorten/),
[Catalogus en koormappen](/handleiding/start/catalogus-en-koormappen/),
[h](../h/)
