---
title: "Opnemen in de catalogus"
linkTitle: "Opnemen"
weight: 10
aliases:
  - "/handleiding/werktrajecten/opnemen-in-bibliotheek/"
---

# Opnemen in de catalogus

Dit werktraject is de **poort** naar de catalogus: van ruw aangeleverd
materiaal naar een map onder `catalogus\` met een
**catalogus-id** (`zangstuk/variant/uitvoeringsvorm`). Publicatiesporen
([Basispartituur](../basispartituur/), [VSA](../vsa/),
[Print-vel](../print-vel/)) sluiten hierop aan — nádat het bestand klaar
genoeg is om op te nemen.

{{< cue >}}
1. Bewaar het ruwe bestand onder `content-source\input\`.
2. Werk de tabel
   `content-source\input\werkvoorraad.md` bij
   (`update-werkvoorraad` of `check`).
3. Vul het **doel-id** in — niet raden; zie het
   [Id-register](/catalogus/id-register/).
4. Als het bestand klaar is (basispartituur-`.mscz`, `.vsa`, `.mvsa`,
   handmatig `.mscz`, of `.tekstblad.md`): `bieb accepteer`.
5. Controleer met `scripts\check.cmd --strict`.
{{< /cue >}}

## Waartoe

Koorleden zien alleen wat in de **bibliotheek** staat (of via een
**koormap**-slot ernaar verwijst). Ruwe Capella-, PDF- of VOW-bestanden
horen niet rechtstreeks in die catalogus. Dit traject is de
**overgang** van lifecycle-fase [Werkbank](../../start/werkbank/) naar
[Catalogus](../../start/catalogus/): input bijhouden, klaar bestand
opnemen met `bieb accepteer`. Model: [Levenscyclus](../../start/levenscyclus/).

## Eindresultaat en criteria

| Op schijf | Rol |
| --- | --- |
| `content-source\input\<herkomst>\…` | Origineel ruw bestand (originele naam) |
| `input\werkvoorraad.md` | Rij per input, met doel-id / koormap / notitie |
| `catalogus\<zangstuk>\<variant>\<uitvoeringsvorm>\` | Map met `index.md` + bestand onder **publicatiestam** |

**Klaar** als: het doel-id klopt (of bewust leeg met een vraag in de
notitie); na `bieb accepteer` bestaat de bladermap met shortcode `bieb`;
`scripts\check.cmd --strict` is groen voor de bibliotheekstructuur.

`bieb accepteer` maakt **geen** PDF of Coria-`.mxl`. PDF en Coria-`.mxl`
horen bij [Basispartituur](../basispartituur/) of [VSA](../vsa/).

## Wanneer wel / wanneer niet

| Wel | Niet |
| --- | --- |
| Nieuw Capella-, VOW-, MuseScore-, MusicXML-, PDF- of `.vsa`-bestand | Bestand al in de catalogus onder het juiste id |
| Klaar oefenbestand in de catalogus zetten | Ruwe Capella-`.capx` of ongekuiste `.mxl` rechtstreeks “publiceren” |

## Volgorde (bestanden)

### Placeholder: ruw materiaal binnenhalen

> **Let op:** opkuisen is fase-afhankelijk — in de
> [Werkbank](../../start/werkbank/) zwaar (Capella → `_werk`), in de
> [Catalogus](../../start/catalogus/) alleen gericht herstel. HOW’s:
> [Partituur](../../partituur/) en [VSA](../../vsa/).

1. Kopieer het bestand naar
   `content-source\input\<herkomst>\`
   (of eerst `_inbox\` — die map gaat niet naar git). Laat de
   **originele bestandsnaam** staan. Herkomst-mappen:
   [Waar ligt wat](../../start/waar-ligt-wat/).
2. Open het Windows-opdrachtvenster in de repository-map `bibliotheek`.
3. Ververs de werkvoorraad:

```cmd
scripts\update-werkvoorraad.cmd
```

   Of draai `scripts\check.cmd` — die doet dezelfde update plus de rest
   van de site-keten.
4. Open `content-source\input\werkvoorraad.md`. Zoek
   de nieuwe rij. Vul kolom **Doel-id** in als je het catalogus-id kent
   (bijvoorbeeld `trisagion/8a-nederlands/hemelum`). Ken je het id
   niet? Laat de cel leeg en vraag na — **niet verzinnen**.
5. Pas **Koormap** of **Notitie** aan als dat nodig is. Kolommen *Stap*
   en *Volgende* vult het script; die niet met de hand “rechtzetten”.

### Klaar bestand opnemen

6. Zorg dat het bestand een bruikbare **basispartituur-`.mscz`**,
   **`.vsa`**, **`.print.mscz`** of **`.tekstblad.md`** is (niet een ruwe
   Capella-file).
7. Neem op in de catalogus:

```cmd
bieb accepteer
```

   Het script vraagt catalogus-id en bestand na (of je geeft die op de
   regel). Het maakt de mappen, zet `index.md` met shortcode `bieb`, en
   kopieert het bestand naar de **publicatiestam**-naam.
8. Daarna: het juiste publicatiespoor (PDF/Coria of print-PDF), daarna
   eventueel een [koormap](../../publiceren/1-bladermap/)-slot, daarna
   [Site-build](../site-build/).

Stapsgewijze HOW voor stap 7:
[Opnemen in de catalogus (Publiceren)](../../publiceren/1-opnemen-in-catalogus/).

## Automatisch (CI)

GitHub Actions **exporteert geen** MuseScore- of VSA-producten bij
opnemen. Wel controleren `check` / CI of de bibliotheekstructuur klopt
(`bibliotheek.py`, publicatiestatus, enz.). Nieuwe of gewijzigde
productbestanden moet jij lokaal maken en **meecommitten**.

## Handmatig

| Situatie | Commando | Man-page |
| --- | --- | --- |
| Open werkbank tonen | `scripts\werkbank-status.cmd` | [werkbank-status](../../scripts/werkbank-status/) |
| Werkvoorraad bijwerken | `scripts\update-werkvoorraad.cmd` | [update-werkvoorraad](../../scripts/update-werkvoorraad/) |
| Bestand in de catalogus zetten | `bieb accepteer` | [bieb accepteer](../../scripts/bieb-accepteer/) |
| Grenzen werkbank/catalogus | `scripts\lifecycle-grenzen.cmd` | [lifecycle-grenzen](../../scripts/lifecycle-grenzen/) |
| Alles controleren vóór commit | `scripts\check.cmd --strict` | [check](../../scripts/check/) |

## Zie ook

- HOW: [Ruw materiaal binnenhalen (Partituur)](../../partituur/1-binnenhalen/)
  (doorverwijzing; canonieke plek is deze werktrajectpagina)
- HOW: [Opnemen (Publiceren)](../../publiceren/1-opnemen-in-catalogus/)
- [Id-register](/catalogus/id-register/)
- Namen/publicatiecontrole: [Publicatiecontrole](/handleiding/start/publicatiecontrole/)

{{< navbuttons "Werktrajecten|/handleiding/werktrajecten/" "Basispartituur|/handleiding/werktrajecten/basispartituur/" >}}
