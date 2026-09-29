---
title: "Waar ligt wat"
linkTitle: "Waar ligt wat"
weight: 20
---

# Waar ligt wat

{{< cue >}}
- Input: `content-source\input\<herkomst>\` (originele bestandsnaam mag spaties hebben)
- Tussenwerk: `content-source\input\_werk\<stam>\` (publicatiestam; alleen op jouw pc, niet in git)
- Bibliotheek (catalogus-fase): `content-source\bibliotheek\<zangstuk>\<variant>\<uitvoeringsvorm>\` — **geen spaties** in bestandsnamen
- Koormap: `content-source\koormappen\hemelum\liturgie-zondag\` of
  `liturgie-weekdagen\` — sectie-`_index.md` of slot-`index.md` + `bieb`
  (geen basispartituur-bestanden)
- Register: `content-source\input\werkvoorraad.md` en [Id-register](/bibliotheek/id-register/)
- Lifecycle: [Levenscyclus](levenscyclus/) — Werkbank vs Catalogus
{{< /cue >}}

**Wat je nu doet:** vier soorten plekken uit elkaar houden. Anders verdwijnt
het origineel, of komt een half af bestand op de publieke site. In de
[Werkbank](werkbank/) horen input en `_werk`; in de
[Catalogus](catalogus/) de canonieke bron onder `bibliotheek\`.

Een **bibliotheek-uitvoeringsvorm** is één map in de bibliotheek met
`index.md` en de bestanden die koorleden oefenen (basispartituur, PDF, Coria, VSA of
print). In de Hemelum-**koormap** verwijst een **slot-pagina**
(`index.md`) met `bieb` naar die uitvoeringsvorm. Een
**koormap-sectie** (`_index.md`) groepeert kindpagina’s op één liturgische
plek. Zie
[Bibliotheek en koormappen](/handleiding/start/bibliotheek-en-koormappen/).

## Vier plekken

| Plek | Map (vanaf `content-source\`) | Op de publieke site? |
| --- | --- | --- |
| Ruw, ongewijzigd | `input\capella\` (of `vow\`, `musescore\`, `musicxml\`, `pdf\`) | Nee |
| Halverwege (tussenwerk) | `input\_werk\` | Nee (en niet in git) |
| Bibliotheek | `bibliotheek\<zangstuk>\<variant>\<uitvoeringsvorm>\` | Ja |
| Koormap (sectie of slot-pagina) | `koormappen\hemelum\liturgie-zondag\` of `liturgie-weekdagen\` | Ja |

De map `input\_inbox\` is een lokale brievenbus (gitignore). Pas als een
bestand dé bron is die je wilt houden, verplaats je het naar een
herkomst-map.

## Herkomst-mappen

| Map onder `input\` | Wat erin hoort |
| --- | --- |
| `capella\` | Capella / CapToMusic: `.cap`, `.capx`, of een `.mxl` zoals het binnenkwam |
| `vow\` | Ruwe VOW-`.mscz` |
| `musescore\` | Andere ruwe `.mscz` (nog niet de bibliotheek-layout) |
| `musicxml\` | `.xml` / `.musicxml` / `.mxl` uit een ander programma |
| `pdf\` | Scans of print-PDF die je als bron bewaart |

Laat de **originele bestandsnaam** van de input staan, ook met spaties.
Hernoemen gebeurt pas bij publicatie in de bibliotheek.

## Publicatienamen

In de bibliotheek (en in `_werk`): geen spaties; alleen kleine letters,
cijfers, `-` en `_`. Voorbeeld: id `trisagion/8a-nederlands/hemelum` →
`trisagion-8a-nederlands-hemelum.mscz`.

## Koormap vs bibliotheek-id

| Veld | Betekenis |
| --- | --- |
| **Bibliotheek-id** | Drie lagen: `zangstuk/variant/uitvoeringsvorm` — in werkvoorraad en in `bieb` |
| **Koormap** | Liturgie-pad (bijv. `trisagion/8a-trisagion`) |

Weet je de bibliotheek-id niet? Laat **Doel-id** leeg en vraag na. Raad
niet. Lijst: [Id-register](/bibliotheek/id-register/).

## Klaar als

Voor een willekeurig bestand kun je zeggen: input, tussenwerk, bibliotheek,
of koormap — en of je in de [Werkbank](werkbank/) of
[Catalogus](catalogus/) zit.

{{< navbuttons "Wat heb je nodig|/handleiding/start/wat-heb-je-nodig/" "Levenscyclus|/handleiding/start/levenscyclus/" >}}
