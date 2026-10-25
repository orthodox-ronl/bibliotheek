---
title: "Als het misgaat"
linkTitle: "Als het misgaat"
weight: 30
---

# Als het misgaat

{{< cue >}}
Spaties in de publicatiestam? Hernoemen. Layout kwijt? Niet via MusicXML;
wel `scripts\layout.cmd` op de basispartituur-`.mscz`. Coria rood bij `check`? Gebruik
de `.mxl` in het **bibliotheek** (partituur-product of `{stam}.vsa.mxl`), niet een
`.mxl` onder `input\`. MuseScore niet gevonden? Versie **4**, pad
`C:\Program Files\MuseScore 4\bin\MuseScore4.exe`.
{{< /cue >}}

**Wat je nu doet:** de veelvoorkomende blokkades herkennen. Blijft het
stuk: bewaar de fouttekst en vraag na; probeer niet drie andere scripts
tegelijk.

## Spaties of rare tekens in de naam

**Symptoom:** een script weigert, Coria doet het niet, of `check` klaagt.

Publicatiebestanden in de catalogus: geen spaties, geen `(` of `+`. Stam
alleen `a-z0-9_-`. Ruwe inputs in `input\` mogen hun oude naam houden. Schrijf
uitvoer altijd met `-o` naar een schone naam.

## Doel-id leeg of twijfel

Niet verzinnen. Zet in de werkvoorraad-rij een notitie “welk catalogus-id?”
en vraag het na. Twee inputs naar dezelfde uitvoeringsvorm mag (Capella én VOW);
noteer dat in de notitie. Bestaand id:
[Zoeken](/overzichten/zoeken/); Hemelum-naslag:
[Id-register](/overzichten/id-register/).

## bieb accepteer weigert het bestand

**Symptoom:** `bieb accepteer` eindigt met `FAIL:`.

Lees de regel `Oplossing:` in het opdrachtvenster. Veelvoorkomend: verkeerd
id, bestand bestaat al (dan `--force` alleen als je bewust overschrijft),
`.vsa` die `vsa validate` niet haalt, of een Capella-`.mxl` zonder basispartituur.
Stappen: [Opnemen in de catalogus](../1-opnemen-in-catalogus/).

## Layout of `products --kinds mscz` “herstelt” je speciale partituur

Eindigt de bestandsnaam op `.print.mscz`? Dan hoort die **niet** door
`scripts\layout.cmd` of `products --kinds mscz`. Zie
[Print-.mscz](/handleiding/partituur/7-print-mscz/). Per ongeluk
als gewone `.mscz` gezet? Hernoem terug naar `.print.mscz` vóór de
volgende `check`. Zet `manueel: true` op de catalogus-`index.md`
als PDF/MXL handmatig blijven.

## MuseScore start niet / “niet gevonden”

Layout en `products --kinds mscz` hebben MuseScore **4** nodig. Installeer
MuseScore 4; gebruik niet MuseScore 3. Open het opdrachtvenster opnieuw
na installatie. (Voor alleen `.vsa` → Coria is MuseScore niet nodig:
`products --kinds vsa`.)

## De pagina is lelijk of de stijl is weg

Meestal: geëxporteerd naar MusicXML en weer geopend. Ga terug naar de
basispartituur-`.mscz` (of opnieuw vanaf opgekuiste `.mxl` plus normaliseren). Daarna:

```cmd
scripts\layout.cmd pad\naar\bestand.mscz
```

## Coria: `failed to retrieve file`

Coria haalt het muziekbestand zelf vanaf internet op. **Oefenen** (via
tip-icoon **♪**) moet daarom naar een **volledig** adres op
`raw.githubusercontent.com`
wijzen, bijvoorbeeld
`https://raw.githubusercontent.com/orthodox-ronl/bibliotheek/gh-pages/preview/mxl/c/<hash>.musicxml`
(fingerprint op branch `gh-pages`). De website voor mensen blijft
`https://orthodox-ronl.github.io/bibliotheek/`; Coria's server faalt op
`github.io`-MusicXML regelmatig met `failed to retrieve file`.
Gebruik geen pad zonder host (`/mxl/c/…`), geen `http://127.0.0.1:…`,
geen `github.io`-MusicXML, en geen page-bundle-`.mxl`.

Draai `scripts\check.cmd` of `scripts\build.cmd` opnieuw zodat
`fingerprint_coria_mxl.py` en Hugo meelopen.
`check` controleert ook dat Coria-`.mxl` geen verboden
`source`+`encoding`-combinatie heeft (anders `translation failed`).

Een nieuw zangstuk dat nog niet op branch `gh-pages` staat, opent in Coria
pas na een `git push` (Coria kan de lokale Hugo-server niet bereiken).

## Coria: `translation failed` of check weigert de `.mxl`

Coria’s vertaler (`play_from_url`) kan op meer dan één MusicXML-vorm
falen met dezelfde melding `translation failed`. In de bibliotheek zijn
dit de bekende gevallen:

1. `<identification>` heeft zowel `<source>` als `<encoding>` —
   bronvermelding hoort in `miscellaneous-field name="bron"`.
2. In `<identification>` staat `<miscellaneous>` vóór `<encoding>` —
   Coria eist `encoding` eerst; `products` / stamp zetten die volgorde.
3. De score bevat `<notehead>` (bijvoorbeeld `none` uit MuseScore) —
   die tag hoort niet in Coria-`.mxl`; `products --kinds mscz` / sanitize
   strippen die mee.
4. Binnen `<note>` verkeerde kindvolgorde (M20): `<lyric>` vóór
   `<staff>`, of `<dot>` ná `<accidental>` — `mxl validate` faalt;
   opnieuw producten draaien met actuele tooling / `coria_mxl`.

Als `check` (of `check_mxl_playback_contract`)
`coria_source_encoding` meldt:

```cmd
python scripts\strip_coria_mxl_source.py
check
```

Als de check `coria_notehead` meldt, of na een MuseScore-export opnieuw
`<notehead>` in de Coria-`.mxl` zit:

```cmd
scripts\products.cmd --kinds mscz --only-invalid
```

(`products` vernieuwt daarna zelf de Coria-fingerprints voor **Oefenen**.)

Of producten opnieuw: `scripts\products.cmd --kinds mscz,mvsa,vsa`
(voor de betreffende stukken). De `.mxl` moet uit `products --kinds mscz`,
`products --kinds mvsa` of `products --kinds vsa` komen (of handmatig bij
`manueel` / `manual`), niet een ruwe Capella-`.mxl`.

## Rode banner: partituur- of VSA-afgeleiden niet in orde

| Banner | Oorzaak | Actie |
| --- | --- | --- |
| Basispartituur-afgeleiden | PDF/MXL passen niet bij de basispartituur-`.mscz` | [Afgeleiden](../../partituur/6-afgeleiden/) — layout + `products --kinds mscz` |
| VSA-afgeleiden | `{stam}.vsa.mxl`, `.vsa.pdf` of `.vsa.svg` ontbreekt of past niet bij de `.vsa` | `scripts\products.cmd --kinds vsa`, commit bron en siblings |

Op `main` faalt de build bij dezelfde situaties.

## Gele banner: handmatige artefacten

Geen fout: `manueel: true` staat op die cataloguspagina.
PDF/MXL vernieuwen de scripts niet; doe dat zelf na elke bronwijziging.

## `bieb` faalt bij build

De shortcode verwijst naar een catalogus-pagina die nog niet bestaat, of
het id klopt niet (`zangstuk/variant/uitvoeringsvorm`). Maak eerst de
catalogus-map + `index.md`, of corrigeer het id in het koormap-slot.

## Hugo-waarschuwing: SVG ontbreekt

Shortcode `bieb` toont `{stam}.vsa.svg` of `{stam}.mvsa.svg` naast de
bron. Ontbreekt die sibling, dan noemt de waarschuwing ook het
legacy-pad `static\vsa\bladermap\…`.

```cmd
scripts\products.cmd --kinds vsa content-source\catalogus\<zangstuk>\<variant>\<uitvoeringsvorm>
```

Bij een `.mvsa`: `scripts\products.cmd --kinds mvsa` op die map. `check` vult
de sibling niet aan. Uitleg: [.vsa schrijven](../../vsa/1-vsa-schrijven/).

## `vsa validate` klaagt

De markering zit in de gezongen regel. Vergelijk met een werkend `.vsa`
ernaast. Haal niet “even de rare tekens weg” om groen te worden.

## Template SATB: `TemplateInstanceError`

De sopraan in de VSA volgt de tropaar-toon-4-formule niet (toon of
verplicht slot). Lees de hint in het venster; pas de VSA aan, of (met
iemand die de formule beheert) de template. Werk de `.mscz` niet als
eerste bron van waarheid bij.

## `publicatiestatus` ontbreekt

Elke catalogus-`index.md` en `_index.md` (catalogus en koormap) moet de
regel `publicatiestatus` in de `---` hebben. Handleiding-pagina’s niet.
`check` faalt hier (nog) niet op. Op **leaves** (concrete stukken /
koormap-slots) verschijnt een `?` naast de titel met uitleg en
feedbacklinks; op map-overzichten en hulppagina’s (zoals zoeken) niet.

## Preview op de verkeerde poort

http://127.0.0.1:**18732**/ — niet 1313.

## Check rood, lange muur tekst

Scroll naar het **eerste** `FAILED` of `error`. Vaak is één bestand de
oorzaak. Los dat ene bestand op, draai check opnieuw. Pak niet de hele
foutenmuur tegelijk aan.

## Waar vraag je het

Gebruik dezelfde kanalen als op de catalogus-site-pagina’s (e-mail / GitHub).
Stuur mee: welk catalogus-id, welk commando, de foutregel, en of het om
Capella, VOW of VSA gaat.

{{< navbuttons "Terug naar overzicht|/handleiding/" >}}
