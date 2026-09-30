# Input voor de bibliotheek (werkbank)

Hier komen **inputs** binnen die **nog geen** canonieke catalogus-bron
zijn: bestanden uit Capella, VOW, MuseScore, een PDF-scan, MusicXML uit
een andere app, enz. Dat is lifecycle-fase **Werkbank**. Pas na
`bieb accepteer` horen oefenbestanden in
`content-source/catalogus/<zangstuk>/<variant>/<uitvoeringsvorm>/`
(fase **Catalogus**). Een **koormap-slot** verwijst daarheen met
shortcode `bieb`.

Uitleg: [Levenscyclus](/handleiding/start/levenscyclus/),
[Werkbank](/handleiding/start/werkbank/).

Deze map staat wél in git (zodat conversie herhaalbaar is), maar **niet**
op de publieke site. Daarom geen `_index.md` hier.

## Mappen

| Map          | Wat erin hoort |
| ------------ | -------------- |
| `capella/`   | Capella / CapToMusic: `.cap`, `.capx`, of een input-`.mxl` (originele naam, spaties mag) |
| `vow/`       | ruwe VOW-`.mscz` |
| `musescore/` | andere ruwe `.mscz` (nog niet de bibliotheek-layout) |
| `musicxml/`  | `.xml` / `.musicxml` / `.mxl` uit andere programma's |
| `pdf/`       | scans of print-PDF die je als bron bewaart |
| `_inbox/`    | lokaal, niet in git: “gisteren in de mail, nog niet gekozen” |
| `_werk/`     | lokaal, niet in git: tussenproducten (opgekuiste MXL, halve layout) |
| `.archief/`  | oude kopieën; git negeert `.archief/` al globaal |

**Inbox:** eerst hierheen (of `_inbox/`), pas committen naar `capella/` /
`vow/` / … als dit dé input is die je wilt bewaren.

**Namen:** inputs mag je laten zoals ze binnenkwamen. Publicatie in de
catalogus: geen spaties, stam = publicatiestam uit de catalogus-id
(`scripts/bibliotheek.py`, `scripts/score_filenames.py`).

**Overzicht:** `werkvoorraad.md` in deze map — één rij per input. Kolommen
**Doel-id** (catalogus-id) en **Koormap** (liturgie-slot). De tabel wordt
bij `check` / `build` / `serve` opnieuw gevuld. Handmatige **notitie** en
**doel-id** in een bestaande rij blijven staan. Op de site: special page
[Werkbank](/catalogus/speciaal/werkbank/) en uitklapbaar onderaan het
catalogus-overzicht.

**Id-lijst:** [bibliotheek/ID-REGISTER.md](../bibliotheek/ID-REGISTER.md).

## Workflow (kort)

1. Input in de juiste herkomst-map (of eerst `_inbox/`).
2. Catalogus-id kiezen (`zangstuk/variant/uitvoeringsvorm`); onbekend:
   in de tabel leeg laten of vragen, niet raden. Meerdere inputs voor
   hetzelfde id: kies **één leidend spoor** (notitie).
3. Converteren in `_werk/` (`opkuisen`, `layout`, MuseScore-review).
4. Klaar: `bieb accepteer` → catalogusmap; daarna `*-products` en
   `check --strict`.
5. `publicatiestatus` op bibliotheek-`index.md` (en koormap) bewust zetten.

Uitgebreider: [Handleiding — Werkbank](/handleiding/start/werkbank/).
