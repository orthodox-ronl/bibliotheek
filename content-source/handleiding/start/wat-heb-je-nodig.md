---
title: "Wat heb je nodig"
linkTitle: "Wat heb je nodig"
weight: 10
---

# Wat heb je nodig

{{< cue >}}
1. Installeer MuseScore **4** (niet MuseScore 3) als je partituren bewerkt.
2. Zorg dat de map `bibliotheek` staat onder `C:\Git\orthodox-ronl\`.
3. Open Verkenner, ga naar `C:\Git\orthodox-ronl\bibliotheek`, typ `cmd` in de adresbalk, druk Enter.
4. Zet `.\scripts` op je PATH (org-conventie), of roep `scripts\….cmd` aan vanuit de repo-root.
5. Lokale preview: `serve` en open http://127.0.0.1:18732/ in de browser.
{{< /cue >}}

**Wat je nu doet:** je pc zo inrichten dat de rest van deze handleiding
neerkomt op copy-paste, zonder zoeken naar paden.

## Programma’s

| Programma | Waarvoor |
| --- | --- |
| [MuseScore 4](https://musescore.org/) | Partituren openen, nakijken, opslaan als `.mscz` |
| De repository-map `bibliotheek` op je schijf | Bestanden zetten en de commando’s uit deze handleiding draaien |
| Een browser | De site lokaal of op de preview bekijken |
| Optioneel: Cursor of Kladblok | Bestanden `.md` en `.vsa` bewerken |

Je schrijft geen Python-programma’s. Je plakt kant-en-klare regels in het
Windows-opdrachtvenster. MuseScore bedien je met de muis.

## De repository-map op schijf

```text
C:\Git\orthodox-ronl\
  bibliotheek\          <-- hier werk je
```

Sibling-mappen `bron` en `VSA-tooling` zijn handig lokaal (`_ensure`
gebruikt sibling `VSA-tooling` als die er is). Voor alleen site bekijken
voldoet `check` / `serve` (die zetten `vsa-tool` via sibling of git).

## Het Windows-opdrachtvenster (eenmaal openen)

1. Open Verkenner.
2. Ga naar `C:\Git\orthodox-ronl\bibliotheek`.
3. Klik in de adresbalk, typ `cmd`, druk Enter.
4. Plak commando’s in **dat** venster.

Plakken: rechtsklik, of Ctrl+V. Druk Enter. Wacht tot de prompt terugkomt.
Rode tekst of `FAILED` → [Als het misgaat](../../publiceren/3-als-het-misgaat/).

## Eerste keer

```cmd
check
```

Dat bouwt de site (Hugo) en maakt Coria-fingerprints. Daarna:

```cmd
serve
```

Open in de browser **http://127.0.0.1:18732/**. Gebruik niet poort 1313
(lokaal gereserveerd) en niet 18731 (VSA-demo).

Laat het venster van `serve` open zolang je kijkt. Klaar: Ctrl+C.

Publieke preview: https://orthodox-ronl.github.io/bibliotheek/preview/

{{< navbuttons "Waar ligt wat|/handleiding/start/waar-ligt-wat/" "Woorden|/handleiding/start/woorden/" >}}
