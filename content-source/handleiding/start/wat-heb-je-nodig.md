---
title: "Wat heb je nodig"
linkTitle: "Wat heb je nodig"
weight: 10
---

# Wat heb je nodig

{{< cue >}}
1. Installeer de programma’s uit de tabel hieronder (minstens: Git, Python 3.14, Hugo Extended, MuseScore 4, ffmpeg).
2. Zet de mappen uit [PATH](#path) op je gebruikers-PATH; controleer met `where`.
3. Zorg dat de map `bibliotheek` staat onder `C:\Git\orthodox-ronl\`.
4. Open Verkenner, ga naar `C:\Git\orthodox-ronl\bibliotheek`, typ `cmd` in de adresbalk, druk Enter.
5. Controletest: `check` (moet zonder “not found on PATH” eindigen). Lokale preview: `serve` → http://127.0.0.1:18732/
{{< /cue >}}

**Wat je nu doet:** je pc zo inrichten dat de rest van deze handleiding
neerkomt op copy-paste in het Windows-opdrachtvenster, zonder zoeken naar
paden.

Je schrijft geen Python-programma’s. Je plakt kant-en-klare regels. MuseScore
bedien je met de muis. Org-conventie voor scripts en PATH (technischer):
[repo-scripts in bron](https://github.com/orthodox-ronl/bron/blob/main/docs/specs/repo-scripts.md).

## Programma’s

| Programma                                                          | Waarvoor                                                                                | Verplicht?                         |
| ------------------------------------------------------------------ | --------------------------------------------------------------------------------------- | ---------------------------------- |
| [Git for Windows](https://git-scm.com/download/win)                | Repository ophalen en bijwerken (`git pull` / push); Cursor en scripts verwachten `git` | Ja                                 |
| [Python 3.14](https://www.python.org/downloads/)                   | Draait de scripts achter `check`, `products`, `validate`, …                             | Ja                                 |
| [Hugo Extended 0.160.1](https://github.com/gohugoio/hugo/releases) | Lokale site (`serve` / `build` / deel van `check`)                                      | Ja                                 |
| [MuseScore 4](https://musescore.org/)                              | Partituren openen en opslaan; PDF/MXL/audio via `products` / `layout`                   | Ja (voor partituur- en audio-werk) |
| [ffmpeg](https://www.gyan.dev/ffmpeg/builds/)                      | Preview-`.mp3` inkorten na MuseScore (geen seconden stilte aan het eind)                | Ja (voor `products --kinds audio`) |
| De map `bibliotheek` op schijf                                     | Bestanden en commando’s uit deze handleiding                                            | Ja                                 |
| Een browser                                                        | Lokale preview of https://orthodox-ronl.github.io/bibliotheek/preview/                  | Ja                                 |
| Cursor, VS Code of Kladblok                                        | Bestanden `.md`, `.vsa`, `.mvsa` bewerken                                               | Aanbevolen                         |
| Sibling-map `VSA-tooling`                                          | Levert het commando `vsa` (tooling); `_ensure` zet dat klaar                            | Sterk aanbevolen                   |

**Niet** MuseScore 3 gebruiken. Alleen MuseScore **4**.

Alleen de site bekijken zonder partituur of audio te maken kan met Git,
Python, Hugo en de map `bibliotheek`. Zodra je `products --kinds mscz`,
`layout` of Beluisteren-audio draait, heb je MuseScore 4 nodig; voor audio
ook ffmpeg.

## Installeren (Windows)

Doe dit **eenmaal** per pc. Na elke installatie: opdrachtvenster **nieuw**
openen (oude vensters kennen nieuwe PATH-regels niet).

### Git

1. Download **Git for Windows** en installeer met de standaardopties.
2. Laat de installer “Git from the command line” / PATH aanpassen aanstaan.
3. Controle in een nieuw `cmd`-venster:

```cmd
where git
git --version
```

Verwacht: een pad onder bijvoorbeeld `C:\Program Files\Git\cmd\` en een
versienummer. Geen `where`-regel → Git staat niet op PATH; herinstalleer of
voeg `C:\Program Files\Git\cmd` toe (zie [PATH](#path)).

### Python 3.14

1. Download Python **3.14** van python.org (niet de Microsoft Store-app).
2. Installeer bij voorkeur naar `C:\Python314\`.
3. Vink tijdens de setup **Add python.exe to PATH** aan, of zet zelf
   `C:\Python314\` én `C:\Python314\Scripts\` op PATH.
4. Controle:

```cmd
where python
python --version
```

Verwacht: `where` wijst naar `C:\Python314\python.exe` (of vergelijkbaar),
**niet** naar `...\WindowsApps\python.exe`. Versie: `Python 3.14.x`.
Staat `WindowsApps` vooraan? Zet `C:\Python314\` hoger in PATH of verwijder
de Store-aliassen.

### Hugo Extended 0.160.1

1. Download de **extended**-build voor Windows van de
   [Hugo-releases](https://github.com/gohugoio/hugo/releases) (bestand met
   `extended` en `windows` in de naam), versie **0.160.1**.
2. Pak uit naar bijvoorbeeld `C:\Git\tools\hugo\` zodat `hugo.exe` daar staat.
3. Zet die map op PATH.
4. Controle:

```cmd
where hugo
hugo version
```

Verwacht: het woord `extended` in de versieregel, en `v0.160.1`.

### MuseScore 4

1. Installeer vanaf [musescore.org](https://musescore.org/) (versie 4).
2. Standaardpad: `C:\Program Files\MuseScore 4\bin\MuseScore4.exe`.
3. De tooling vindt MuseScore daar vaak automatisch. Handig op PATH (optioneel):
   `C:\Program Files\MuseScore 4\bin`.
4. Controle (optioneel):

```cmd
where MuseScore4
```

Geen `where`-treffer is geen probleem zolang het bestand onder
`Program Files\MuseScore 4\` staat. Foutmelding “MuseScore niet gevonden” →
[Als het misgaat](../../publiceren/3-als-het-misgaat/).

### ffmpeg

Nodig voor preview-audio (`products --kinds audio` / Beluisteren). MuseScore
maakt het geluid; ffmpeg knipt de nutteloze stilte aan het **eind** van het
`.mp3` weg (anders hoor je vaak nog een stuk stilte na de laatste noot).

1. Download een Windows-build (bijvoorbeeld “ffmpeg full” van
   [gyan.dev](https://www.gyan.dev/ffmpeg/builds/)), of via
   `winget install ffmpeg` als je winget gebruikt.
2. Zorg dat `ffmpeg.exe` op PATH staat (vaak de map `bin` in de uitpaklocatie).
3. Controle:

```cmd
where ffmpeg
ffmpeg -version
```

Verwacht: een pad naar `ffmpeg.exe` en een versiekop. Zonder ffmpeg faalt
audio-export met een duidelijke fout over ontbrekende ffmpeg.

### Editor (Cursor / VS Code / Kladblok)

- **Cursor** of **VS Code**: handig voor `.md` / `.vsa` / `.mvsa` en git.
- **Kladblok**: volstaat voor kleine tekstwijzigingen.
- MuseScore blijft het programma voor `.mscz`.

## De repository-map op schijf

```text
C:\Git\orthodox-ronl\
  bibliotheek\          <-- hier werk je (deze handleiding)
  VSA-tooling\          <-- sibling: levert het commando vsa
  bron\                 <-- sibling: org-specs (optioneel lokaal)
```

Clone of pull via Git zodat `bibliotheek` op die plek staat. Sibling
`VSA-tooling` is sterk aanbevolen: `check` / `products` gebruiken dan de
lokale tooling (`vsa`). Zonder sibling haalt `_ensure` tooling via git/pin
binnen (langzamer; volg de fouttekst als iets ontbreekt).

## PATH {#path}

**PATH** is de lijst mappen waarin Windows zoekt als je in `cmd` een
programmanaam typt (`git`, `python`, `hugo`, `ffmpeg`, `vsa`, `check`, …)
zonder het volledige pad ernaartoe. Zo kun je die namen typen zonder
`C:\…\programma.exe` ervoor.

### Wat er op je gebruikers-PATH moet staan

| Map op PATH                                      | Zodat je dit kunt typen                                                    |
| ------------------------------------------------ | -------------------------------------------------------------------------- |
| `.\scripts`                                      | `check`, `serve`, `products`, `validate`, … (org-conventie; letterlijk zo) |
| `C:\Python314\` en `C:\Python314\Scripts\`       | `python`, `pip`                                                            |
| `C:\Git\tools\hugo` (of jouw Hugo-map)           | `hugo`                                                                     |
| `C:\Git\orthodox-ronl\VSA-tooling\.venv\Scripts` | `vsa` (na eerste `_ensure` / install in die venv)                          |
| Map met `ffmpeg.exe`                             | `ffmpeg`                                                                   |
| `C:\Program Files\Git\cmd`                       | `git` (vaak al gezet door de installer)                                    |
| Optioneel: `C:\Program Files\MuseScore 4\bin`    | `MuseScore4`                                                               |

De regel **`.\scripts`** is bewust relatief. Die werkt alleen goed als het
huidige mapje in `cmd` de **repo-root** is:
`C:\Git\orthodox-ronl\bibliotheek`. Daarom open je `cmd` altijd vanuit die
map (Verkenner → adresbalk → `cmd`). Scripts controleren of `.\scripts` in
PATH staat; anders krijg je een duidelijke fout.

Zonder `.\scripts` op PATH mag je nog steeds vanaf de repo-root
`scripts\check.cmd` typen — langer, maar geldig.

### PATH wijzigen op Windows

1. Druk op Start, typ `omgevingsvariabelen`, open **Omgevingsvariabelen voor
   dit account bewerken**.
2. Onder “Gebruikersvariabelen” selecteer **Path** → **Bewerken**.
3. **Nieuw**: plak één map per regel (zie de tabel hierboven).
4. OK op alle dialogen. Open daarna een **nieuw** opdrachtvenster.

### Controleren

Open `cmd` in `C:\Git\orthodox-ronl\bibliotheek` en plak:

```cmd
where git
where python
where hugo
where ffmpeg
where vsa
where check
python --version
hugo version
ffmpeg -version
```

| Commando                                   | Verwacht                                                        |
| ------------------------------------------ | --------------------------------------------------------------- |
| `where git` / `python` / `hugo` / `ffmpeg` | Minstens één pad; eerste treffer is degene die Windows gebruikt |
| `where vsa`                                | Pad onder `VSA-tooling\.venv\Scripts` (na setup)                |
| `where check`                              | Iets met `bibliotheek\scripts\check.cmd`                        |
| `python --version`                         | `Python 3.14.x`                                                 |
| `hugo version`                             | `v0.160.1` én `extended`                                        |
| `ffmpeg -version`                          | Begint met `ffmpeg version …`                                   |

Eerste `where`-regel wijst naar de verkeerde map? Zet de juiste map **hoger**
in de gebruikers-PATH, of verwijder een oude dubbele installatie.

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

Dat bouwt de site (Hugo) en doet de publicatiecontroles. Ontbreekt Python,
Hugo, `vsa` of `.\scripts` op PATH, dan stopt `_ensure` met een korte
Nederlandse/Engelse aanwijzing — los dat eerst op (tabel hierboven).

Daarna:

```cmd
serve
```

Open in de browser **http://127.0.0.1:18732/**. Gebruik niet poort 1313
(lokaal gereserveerd) en niet 18731 (VSA-demo).

Laat het venster van `serve` open zolang je kijkt. Klaar: Ctrl+C.

Publieke preview: https://orthodox-ronl.github.io/bibliotheek/preview/

### Extra: eerste audio-product

Als je Beluisteren-`.mp3` maakt:

```cmd
scripts\products.cmd --kinds audio content-source\catalogus\alleluia\9a-toon-8\groningen
```

MuseScore **en** ffmpeg moeten dan gevonden worden. Zie
[products (audio)](../../scripts/audio-products/).

{{< navbuttons "Waar ligt wat|/handleiding/start/waar-ligt-wat/" "Woorden|/handleiding/start/woorden/" >}}
