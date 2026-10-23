---
title: "Catalogus-id hernoemen"
linkTitle: "Hernoemen"
weight: 15
---

# Catalogus-id hernoemen

Dit werktraject wijzigt een **catalogus-id** op zangstuk-, variant- of
uitvoeringsvorm-niveau en houdt producten, tekstverwijzingen en
passende koormap-slots in de pas. HOW-detail:
[bieb hernoem](../scripts/bieb-hernoem/).

{{< cue >}}
1. Bepaal oud en nieuw id (slash, dash, pad, of korte nieuw-vorm — zie [bieb hernoem](../scripts/bieb-hernoem/)).
2. Dry-run: `scripts\bieb.cmd hernoem <oud> <nieuw> --dry-run` (alias: `rename`)
3. Uitvoeren zonder `--dry-run`.
4. Zoekindex: `python scripts\build_zoek_index.py`
5. Controle: `scripts\check.cmd --strict`
{{< /cue >}}

## Waartoe

Na taxonomie-besluiten moet de mapnaam op schijf gelijk zijn aan het
canonieke id. Zonder dit traject blijven oude paden in docs,
`bieb id=…`, of koormap-inhoudsopgaven staan — of ontstaat een 404
omdat de TOC al `{nieuw}/` zegt terwijl de map nog `{oud}/` heet.

## Eindresultaat en criteria

| Op schijf | Rol |
| --- | --- |
| `catalogus\…\<nieuw>\…` | Verhuisde boom + hernoemde publicatiestam |
| `static\vsa\bladermap\catalogus\…` | Bladermap-SVG’s mee verhuisd |
| `koormappen\…` | 1:1-slotmappen waarvan de mapnaam = oude id/stam |
| Tekst in repo | `bieb id`, `alias_van`, docs, TOC-links bijgewerkt |

**Klaar** als: dry-run klopte; `check --strict` groen is (inclusief
koormap-slotlinks); lokale preview de TOC en bladermap toont onder de
nieuwe naam.

## Wanneer wel / wanneer niet

| Wel | Niet |
| --- | --- |
| Zangstuk-, variant- of uitvoeringsvorm-id wijzigen | Alleen `title`/`linkTitle` — dat is frontmatter |
| Ids met 1:1-koormap-slots | Litanie-plekken die bewust een andere mapnaam houden (`ektinia`) |
| Na een taxonomie-PR / inventaris in Zangstuk-soorten | Cosmetische navigatietekst zonder mapwijziging |

## Volgorde

1. Lees [Zangstuk-soorten](../start/zangstuk-soorten/). Controleer via
   [Zoeken](/overzichten/zoeken/) of de catalogus of het nieuwe id al
   bestaat; Hemelum-reserveringen in het
   [Id-register](/overzichten/id-register/) — nieuw id mag niet botsen.
2. Open het Windows-opdrachtvenster in de repository-map `bibliotheek`.
3. Dry-run (schrijft niets):

```cmd
scripts\bieb.cmd hernoem oud-id nieuw-id --dry-run
```

Voorbeelden (vol id, korte nieuw-vorm, Windows-pad):

```cmd
scripts\bieb.cmd hernoem ektinia/vredes ektinia/litanie --dry-run
scripts\bieb.cmd hernoem ektinia/vredes/hemelum groningen --dry-run
scripts\bieb.cmd hernoem ektinia\vredes\hemelum vredes\groningen --dry-run
scripts\bieb.cmd rename content-source\catalogus\ektinia\vredes ektinia\litanie --dry-run
```

4. Als de lijst klopt:

```cmd
scripts\bieb.cmd hernoem oud-id nieuw-id
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
- [bieb verwijder](../scripts/bieb-verwijder/)
- [bieb kopieer](../scripts/bieb-kopieer/)
- [check](../scripts/check/)
- [Opnemen in de catalogus](opnemen-in-catalogus/)
- [Catalogus en koormappen](../start/catalogus-en-koormappen/)

{{< navbuttons "Opnemen|/handleiding/werktrajecten/opnemen-in-catalogus/" "Site-build|/handleiding/werktrajecten/site-build/" >}}
