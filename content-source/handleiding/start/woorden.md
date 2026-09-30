---
title: "Woorden en bestanden"
linkTitle: "Woorden"
weight: 30
---

# Woorden en bestanden

{{< cue >}}
- **basispartituur** / basispartituur-`.mscz` = canonieke MuseScore-partituur (hier bewerk je; daarna normaliseren). Bronextensie `.mscz`; afgeleiden `{stam}.mscz.pdf` / `{stam}.mscz.mxl`
- **handmatig MuseScore-blad** = gewone `{stam}.mscz` in een map met `artefacten_handmatig: true` (vervangt het oude `.print.mscz`)
- **versheidscontrole** = sibling bestaat + herkomststempel past bij bron; meet/meldt alleen
- **publicatiecontrole** = versheidscontrole op site-producten; zie [Publicatiecontrole](publicatiecontrole/)
- **importcontrole** = versheidscontrole op bewerk-/importvorm (bijv. `.mscz.mvsa`); zie [import-mvsa](/handleiding/scripts/import-mvsa/)
- **geldigheidscontrole** = `vsa validate` / `mvsa validate` / …
- **artefacten_handmatig** = frontmatter op bibliotheek-`index.md`: PDF/MXL niet auto-bijwerken
- `.mxl` / `.vsa.mxl` / `.mscz.mxl` = MusicXML voor Coria (**afgeleide**; niet terug importeren om te layouten)
- `.pdf` / `.mscz.pdf` = A4-afgeleide om te lezen of te printen
- `.mp3` / `.mvsa.mp3` / `.mscz.mp3` / `.vsa.mp3` = preview-audio voor **Beluisteren** (zelfde bronnen als Coria-`.mxl`; zie [audio](/handleiding/werktrajecten/audio/))
- `.vsa` / `.mvsa` = tekstbronnen (VSA / meerstemmig); overzicht: [Werktrajecten](/handleiding/werktrajecten/)
- **werktraject** = vaste pijplijn (waartoe, eindresultaat, CI, handmatige `.cmd`); catalogus: [Werktrajecten](/handleiding/werktrajecten/)
- **tekstblad** = bron `{stam}.tekstblad.md` → product `{stam}.tekstblad.pdf`; zie [Tekstblad](/handleiding/werktrajecten/tekstblad/)
- **audio** = preview-`.mp3` naast `.mvsa` / `.mscz` / `.vsa`; zie [audio](/handleiding/werktrajecten/audio/)
- **opkuisen** = inhoud opschonen (stemmen/balken, lettergreep↔noot); script of handmatig in MuseScore
- **normaliseren** / **layouten** = basispartituur-standaard met `scripts\layout.cmd` (zelfde scriptstap; “layouten” is de gewone naam)
- **catalogus-id** = `zangstuk/variant/uitvoeringsvorm` (drie lagen); zichtbaar op bibliotheek-leaves en in het colofon van basispartituur-`.mscz`/PDF
- **`bieb`** (shortcode) = knoppen + partituur van een catalogus-id; **`bieb`** (CLI, later) = beheercommando’s (`accepteer`, `zoek`, …)
- **`bieb accepteer`** = overgang Werkbank → Catalogus (bestand opnemen); zie [Opnemen](/handleiding/werktrajecten/opnemen-in-catalogus/)
- **Werkbank** = lifecycle pre-productie (`input\`, `_werk\`); zie [Werkbank](/handleiding/start/werkbank/)
- **Catalogus** (lifecycle) = canonieke bron in `catalogus\…`; zie [Catalogus](/handleiding/start/catalogus/)
- **publicatiestatus** = wat koorleden op de pagina zien (sticky header); intern *Stap* in de werkvoorraad én lifecycle-fase zijn iets anders
{{< /cue >}}

**Wat je nu doet:** dezelfde namen gebruiken als de rest van de keten, zodat
commando’s en mappen kloppen.

## Bestanden

| Extensie | In het kort | Wat jij ermee doet |
| --- | --- | --- |
| basispartituur-`.mscz` | MuseScore 4-bestand; bron voor PDF en Coria | Openen, nakijken, opslaan; daarna `scripts\layout.cmd`; afgeleiden `{stam}.mscz.pdf` / `{stam}.mscz.mxl` |
| handmatig `.mscz` | Zelfde soort MuseScore-bestand, map met `artefacten_handmatig: true` | Alleen in MuseScore bewerken; PDF handmatig; geen automatische publicatiecontrole — zie [Publicatiecontrole](publicatiecontrole/) |
| `.mxl` / `.vsa.mxl` / `.mscz.mxl` | Samengeperste MusicXML (**afgeleide**) | Naar Coria; of (na opkuisen) als start voor een nieuwe basispartituur. Nooit roundtrip: `.mscz` → `.mxl` → weer `.mscz` gooit de layout weg. |
| `.pdf` / `.mscz.pdf` | A4-blad (afgeleide of handmatige export) | Downloaden of printen |
| `.mp3` / `.mvsa.mp3` e.d. | Preview-audio (afgeleide) | Beluisteren op de site; maken met `audio-products` |
| `.vsa` | VSA-notatie | Schrijven in een editor; sitebuild maakt SVG; `check`/`vsa-products` maakt Coria-`.vsa.mxl` — zie [.vsa schrijven](/handleiding/vsa/1-vsa-schrijven/) |
| `.mvsa` | Meerstemmige tekstbron | Schrijven/valideren met `mvsa`; producten via `mvsa-products` (Coria-`.mvsa.mxl` + A4-`.mvsa.pdf`) — zie [mvsa](/handleiding/werktrajecten/mvsa/) |

**Namen en publicatiecontrole:** [Publicatiecontrole](publicatiecontrole/) (bron vs afgeleide,
sha-stamps, wat CI controleert). Repo-kort: `docs/publicatiecontrole.md`.

**Opkuisen** = inhoudelijke opschoning: stemmen en notenbalken goed zetten,
lettergrepen synchroon met noten. MusicXML: `scripts\opkuisen.cmd`. Bij een
`.mscz`: vaak handmatig in MuseScore. Zie
[Opkuisen](/handleiding/partituur/2-opkuisen/).

**Normaliseren** (gangbaar: **layouten**) = de basispartituur-standaard toepassen met
`scripts\layout.cmd` (A4, fonts, reciteertoon). Zie
[Standaard-.mscz](/handleiding/partituur/3-standaard-mscz/) en
[Reviewen](/handleiding/partituur/4-reviewen/).

## Plaatsen en status

| Woord | Betekenis |
| --- | --- |
| **Bibliotheek** | Deze repository / de site als geheel (`github.com/orthodox-ronl/bibliotheek`) |
| **Catalogus** (sectie) | Hugo-sectie onder `catalogus\`: alle oefenbestanden per uitvoeringsvorm; mag stukken bevatten zonder koormap |
| **Catalogus-id** | Drie segmenten `[a-z0-9_-]+`, bijv. `trisagion/8a-nederlands/hemelum` (colofon in `.mscz`: regel `Bibliotheek-id:`) |
| **Variant-id `default`** | Middelste laag als er maar één variant is (bijv. `5-eniggeboren-zoon/default/hemelum`) |
| **Taal-suffix** | Op uitvoeringsvorm-id: geen = NL; `-ksl` = Kerkslavisch Cyrillisch; `-ksl-trlat` = getranslitereerd; `-nl-ksl` = mengvorm |
| **Koormap** | Geordende view (navigatieboom) voor een gelegenheid; geen basispartituur-bestanden in de slotmappen |
| **Koormap-sectie** | Map met `_index.md` in de koormap: liturgische plek / hoofdstuk (kindlijst of eigen TOC) |
| **Slot-pagina** | Map met `index.md` in de koormap: markdown plus `bieb` (geen catalogus-include in de oefenhoek) |
| **Compositieblad** | Slot-pagina met proza en **meerdere** `bieb`-shortcodes (bijv. prokimens van de week) |
| **Alias-variant** | Variant zonder eigen uitvoeringsvorm-bestanden; op de variant-`_index.md` staat `alias_van: zangstuk/canonieke-variant` |
| **Diversen** | (verouderd als zangstuk-id) Losse gezangen hebben nu een eigen zangstuk-id, bv. `tropaar/uw-heilig-kruis/hemelum` |
| **Tropaar** / **kondak** | Nederlandse termen voor die gezangen (niet “troparion” / “kondakion”) |
| **Special page** | Automatisch overzicht onder `catalogus\speciaal\` (werkbank, voorzien, ongerefereerd, oefenbaar) |
| **Werkvoorraad** | Tabel in `input\werkvoorraad.md`: per *input* hoe ver de conversie is |
| **Stap** (werkvoorraad) | Intern: `ontvangen`, `opkuisen`, `layout`, `gepubliceerd`, … — niet zichtbaar voor koorleden |
| **Werkbank** | Lifecycle-fase pre-productie: reserveren, binnenhalen, opkuisen, proefdraaien — [Werkbank](/handleiding/start/werkbank/) |
| **Catalogus** (lifecycle) | Lifecycle-fase: canonieke bron + producten in `catalogus\…` — [Catalogus](/handleiding/start/catalogus/) |
| **Levenscyclus** | Case per uitvoeringsvorm door fases; los van `publicatiestatus` — [Levenscyclus](/handleiding/start/levenscyclus/) |
| **Publicatiestatus** | Op `index.md` in catalogus én koormap: `voorzien`, `reviewable`, `concept`, `productie` (sticky header; niet raden) |
| **artefacten_handmatig** | Frontmatter: afgeleiden in die catalogusmap niet auto; gele banner voor beheerders |
| **SATB** | Sopraan, alt, tenor, bas — de vier stemmen op één partituur |
| **Coria** | Online oefenen; knop **Oefenen** bij shortcode `bieb`; heeft een schone `.mxl` nodig |
| **Uitvoeringsvorm** | Een concrete manier om een zangstuk uit te voeren (schrijf het woord uit; gebruik niet de afkorting “uv”) |
| **Werktraject** | Pijplijn van bron naar eindproduct (site of PDF); zie [Werktrajecten](/handleiding/werktrajecten/) |
| **Tekstblad** | Catalogus-spoor: `{stam}.tekstblad.md` → `{stam}.tekstblad.pdf` (geen Hugo-pagina); [Tekstblad](/handleiding/werktrajecten/tekstblad/) |

Org-brede termen: [glossary in bron](https://github.com/orthodox-ronl/bron/blob/main/docs/specs/terminologie.md).

Id-lijst Hemelum: [Id-register](/catalogus/id-register/).
Model: [Catalogus en koormappen](/handleiding/start/catalogus-en-koormappen/).
Pijplijnen: [Werktrajecten](/handleiding/werktrajecten/).

## Klaar als

Je kunt een mail “hier is de Capella” vertalen naar: input in
`input\capella\`, later een basispartituur-`.mscz` in de catalogus, plus
`{stam}.mscz.pdf` en `{stam}.mscz.mxl` — slot-pagina met `bieb`. Voor een
handmatig MuseScore-blad: `{stam}.mscz` + handmatige PDF (+
`artefacten_handmatig: true`) in de catalogus, slot-pagina in de koormap.
Voor een eenstemmige VSA: `.vsa` + `.vsa.mxl` via `check` / `vsa-products`.
Namen en publicatiecontrole: [Publicatiecontrole](/handleiding/start/publicatiecontrole/). Model van
secties en compositiebladen:
[Catalogus en koormappen](/handleiding/start/catalogus-en-koormappen/).

{{< navbuttons "Publicatiecontrole|/handleiding/start/publicatiecontrole/" "Werktrajecten|/handleiding/werktrajecten/" >}}
