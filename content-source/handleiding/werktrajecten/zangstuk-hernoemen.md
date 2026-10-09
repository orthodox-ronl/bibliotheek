---
title: "Zangstuk hernoemen"
linkTitle: "Hernoemen"
weight: 15
---

# Zangstuk hernoemen

Dit werktraject wijzigt één **zangstuk-id** (de bovenste map onder
`content-source\catalogus\`) en houdt producten, tekstverwijzingen en
passende koormap-slots in de pas. HOW-detail: [bieb hernoem](../scripts/bieb-hernoem/).

{{< cue >}}
1. Bepaal oud en nieuw id (`[a-z0-9_-]+`, geen slash).
2. Dry-run: `scripts\bieb.cmd hernoem <oud> <nieuw> --dry-run`
3. Uitvoeren zonder `--dry-run`.
4. Zoekindex: `python scripts\build_zoek_index.py`
5. Controle: `scripts\check.cmd --strict`
{{< /cue >}}

## Waartoe

Na taxonomie-besluiten (bijvoorbeeld genummerde ids weg) moet de mapnaam
op schijf gelijk zijn aan het canonieke id. Zonder dit traject blijven
oude paden in docs, `bieb id=…`, of koormap-inhoudsopgaven staan — of
ontstaat een 404 omdat de TOC al `{nieuw}/` zegt terwijl de map nog
`{oud}/` heet.

## Eindresultaat en criteria

| Op schijf | Rol |
| --- | --- |
| `catalogus\<nieuw>\…` | Verhuisde zangstuk-boom + hernoemde publicatiestam |
| `static\vsa\bladermap\catalogus\<nieuw>\` | Bladermap-SVG’s mee verhuisd |
| `koormappen\…\<nieuw>\` | Alleen slots die exact `{oud}` heetten |
| Tekst in repo | `bieb id`, `alias_van`, docs, TOC-links bijgewerkt |

**Klaar** als: dry-run klopte; `check --strict` groen is (inclusief
koormap-slotlinks); lokale preview de TOC en bladermap toont onder de
nieuwe naam.

## Wanneer wel / wanneer niet

| Wel | Niet |
| --- | --- |
| Top-level zangstuk-id wijzigen | Alleen variant- of uitvoeringsvorm-map |
| Ids die 1:1 koormap-slots hebben (`trisagion`, …) | Litanie-plekken die bewust `vredeslitanie` heten terwijl het id `ektinia` is |
| Na een taxonomie-PR / inventaris in Zangstuk-soorten | Cosmetische `title`/`linkTitle` — dat is frontmatter, geen hernoem |

## Volgorde

1. Lees [Zangstuk-soorten](../start/zangstuk-soorten/) en het
   [Id-register](/catalogus/id-register/) — nieuw id mag niet botsen.
2. Open het Windows-opdrachtvenster in de repository-map `bibliotheek`.
3. Dry-run (schrijft niets):

```cmd
scripts\bieb.cmd hernoem oud-zangstuk nieuw-zangstuk --dry-run
```

4. Als de lijst klopt (catalogusmap, stam-bestanden, eventuele
   koormap-slots, tekstbestanden):

```cmd
scripts\bieb.cmd hernoem oud-zangstuk nieuw-zangstuk
python scripts\build_zoek_index.py
scripts\check.cmd --strict
```

5. Optioneel: `scripts\serve.cmd` en klik de koormap-inhoudsopgave.

## CI

GitHub Actions draait dezelfde slotlink-check als lokaal `check`
(`scripts\check_koormap_slot_links.py`). Producten worden in CI niet
opnieuw gegenereerd; die horen vóór de push al kloppend te zijn.

## Zie ook

- [bieb hernoem](../scripts/bieb-hernoem/)
- [check](../scripts/check/)
- [Opnemen in de catalogus](opnemen-in-catalogus/)
- [Catalogus en koormappen](../start/catalogus-en-koormappen/)

{{< navbuttons "Opnemen|/handleiding/werktrajecten/opnemen-in-catalogus/" "Site-build|/handleiding/werktrajecten/site-build/" >}}
