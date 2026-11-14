# Tooling-koppeling (bibliotheek ↔ VSA-tooling)

Normatief voor deze repo. Zie ook [AGENTS.md](../AGENTS.md).

**Print-/export-contracten** (checklists, layoutprofielen, Score-IR/OSMD,
Contract-skelet, canoniciteit C1–C4, proces «nieuwe regel → naleving»)
wonen in VSA-tooling — start bij
[contract-index](https://github.com/orthodox-ronl/VSA-tooling/blob/main/docs/formats/contract-index.md)
(§Contract-skelet, §Canoniciteit C*, §Dekkingsmatrix, §Nieuwe regel).
Bibliotheek-specs (o.a. schermpartituur) **linken** daarnaar; geen parallelle
checklist hier. Agentregels: `.cursor/rules/contracten-eerst.mdc`,
`.cursor/rules/canonieke-bestanden.mdc`. Straat-CLIs / products-meta in tooling:
[straat-clis](https://github.com/orthodox-ronl/VSA-tooling/blob/main/docs/plans/straat-clis.md).
Bibliotheek orchestreert met `scripts\products.cmd` en blad-PDF
`scripts\pdf.cmd` → `index.md.pdf`.

## Canoniek in de catalogus

Een catalogusbestand is **canoniek voor publicatie** als:

1. het voldoet aan het **VSA-tooling-formatcontract** van dat type
   (zelfde H2-topics / C1–C4), én
2. het voldoet aan de **bibliotheek-publicatieregels**
   ([publicatiecontrole](publicatiecontrole.md),
   [catalogus-notatiebron](catalogus-notatiebron.md),
   frontmatter [vsa-frontmatter](specs/vsa-frontmatter.md) waar van toepassing).

Zing-deling, melisma, recite/leesbaarheid: **niet** hier herformuleren —
formatpagina’s in tooling, o.a.:

| Type / product              | Formatcontract (VSA-tooling)                                                                                                                                                                                                                                                                  |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `.vsa`                      | [formats/vsa.md](https://github.com/orthodox-ronl/VSA-tooling/blob/main/docs/formats/vsa.md)                                                                                                                                                                                                  |
| `.mvsa`                     | [formats/mvsa.md](https://github.com/orthodox-ronl/VSA-tooling/blob/main/docs/formats/mvsa.md)                                                                                                                                                                                                |
| `.mscz`                     | [formats/mscz.md](https://github.com/orthodox-ronl/VSA-tooling/blob/main/docs/formats/mscz.md)                                                                                                                                                                                                |
| `.mxl`                      | [formats/mxl.md](https://github.com/orthodox-ronl/VSA-tooling/blob/main/docs/formats/mxl.md)                                                                                                                                                                                                  |
| Score-IR / from-ir          | [score-ir](https://github.com/orthodox-ronl/VSA-tooling/blob/main/docs/formats/score-ir.md) · [from-ir](https://github.com/orthodox-ronl/VSA-tooling/blob/main/docs/formats/from-ir.md)                                                                                                       |
| SVG (vsa / mvsa / translit) | [vsa-svg](https://github.com/orthodox-ronl/VSA-tooling/blob/main/docs/formats/vsa-svg.md) · [mvsa-svg](https://github.com/orthodox-ronl/VSA-tooling/blob/main/docs/formats/mvsa-svg.md) · [translit-svg](https://github.com/orthodox-ronl/VSA-tooling/blob/main/docs/formats/translit-svg.md) |
| `*.lyrics.txt`              | [lyrics.txt](https://github.com/orthodox-ronl/VSA-tooling/blob/main/docs/formats/lyrics.txt.md)                                                                                                                                                                                               |
| audio                       | [audio](https://github.com/orthodox-ronl/VSA-tooling/blob/main/docs/formats/audio.md)                                                                                                                                                                                                         |
| products-meta               | [products-meta](https://github.com/orthodox-ronl/VSA-tooling/blob/main/docs/formats/products-meta.md)                                                                                                                                                                                         |
| Syllabificatie (diepte)     | [syllabificatie](https://github.com/orthodox-ronl/VSA-tooling/blob/main/docs/formats/syllabificatie.md)                                                                                                                                                                                       |

Scherm-look (site): [schermpartituur](specs/schermpartituur.md) — linkt
naar tooling voor S8/melisma; voegt geen tweede checklist toe.

## Afspraken

1. **Geen tool-forks.** Er mogen geen Python-tools in `bibliotheek` komen die
   bestaande tools in VSA-tooling uitbreiden of herschrijven. Dat werk hoort
   in [VSA-tooling](https://github.com/orthodox-ronl/VSA-tooling).

2. **Bibliotheek-specifieke tools wél hier.** Scripts voor bibliotheek- en
   koormappenbeheer (paden, `bieb accepteer`, Hugo-check, Coria-fingerprints
   met *deze* Pages-URL’s, …) horen in `bibliotheek/scripts/`. Die tools
   **roepen** VSA-tooling aan (`vsa` CLI of geïnstalleerd package), ze
   dupliceren die logica niet.

3. **Float vs pin**
   - Branch **`development`** (preview-CI): **float** op
     `orthodox-ronl/VSA-tooling@main` — nieuwe tools op tooling-main worden
     hier meteen meegenomen.
   - Branch **`main`** (productie): **pin** via [`vsa-tooling.pin`](../vsa-tooling.pin)
     (commit-SHA of tag). Bump het pin-bestand bewust als productie een
     nieuwere tooling mag gebruiken.

## Installatie

```cmd
scripts\_ensure.cmd --hugo --vsa-tool
```

Volgorde die `_ensure` volgt voor `vsa-tool`:

1. Sibling `..\VSA-tooling` of `vendor\VSA-tooling` (editable) — handig lokaal
2. Anders: `pip install vsa-tool[rendering] @ git+…@<ref>`
   - ref = inhoud van `vsa-tooling.pin` als `BIBLIOTHEEK_TOOLING_MODE=pin`
     of als je op productie-achtige flows zit
   - ref = `main` bij float (default op development / lokale preview)

Override: omgevingvariabele `VSA_TOOLING_REF` (wint van pin/float).

## CI

De Pages-workflow installeert `vsa-tool` (pin/float), runt
`vsa validate content-source/catalogus`, daarna versheidscontroles
(`check_vsa_products`, `check_mscz_products`, `check_tekstblad_products`,
`check_import_mvsa`, `check_mvsa_products`, `check_audio_products`,
`check_lyrics_products` — allemaal met `--fail`), daarna
`check_mxl_playback_contract.py --fail` (bestaande Coria-`.mxl` via
`mxl validate`: M2/M8, importer-tags, meta),
`ensure_bibliotheek_id.py --check-only --fail` (colofon `Bibliotheek-id:`),
daarna Coria-fingerprints en Hugo. CI genereert geen producten — vernieuw
lokaal met `scripts\products.cmd` en commit de siblings. Bibliotheek
exporteert **per slot** (`vsa musicxml`/`vsa svg`, `mscz mxl`/`mscz svg`,
`mvsa mxl`/`svg`/`score-ir`); die CLI’s mergen keys in
`{bron}.products-meta.json` (schema 2; SVG-key `svg` = één tall compacte
sibling). Na MXL kan bibliotheek key `mxl` opnieuw mergen (Coria-bron-id).
`check_*` leest die meta voor snelle versheid, met stamp-fallback zolang
meta nog ontbreekt.

Lokaal: `scripts\validate.cmd` of `check` / `check --strict`.

Naamgeving van bronnen en afgeleiden, en welke publicatiecontroles er (gaan) zijn:
[publicatiecontrole.md](publicatiecontrole.md).

**Scherm (Score-IR / OSMD):** sibling ``.mvsa.from-ir.musicxml`` (plus
``.mvsa.score-ir.json``) via ``products --kinds mvsa`` (tooling
``mvsa score-ir … --musicxml``). Shortcode `muziek` / partial `bieb-score`
tekent die MusicXML met OSMD als die sibling er is (ook via koormap-`bieb`);
anders blijft de MuseScore-SVG- of PDF-fallback. Lookafspraken (cues,
titels, keten): [schermpartituur.md](specs/schermpartituur.md).
`check` eist ``.mvsa.svg`` **niet** wanneer from-ir met geldige
herkomststempel aanwezig is. Na nieuwe from-ir-siblings lokaal:
koormap-pagina’s even herbouwen (serve herstarten of de betreffende
`index.md` aanraken) als je nog PDF ziet.

Workflow Pages bepaalt de ref:

| Trigger-branch                      | Mode  | Ref                         |
| ----------------------------------- | ----- | --------------------------- |
| `development` (en feature-branches) | float | `main`                      |
| `main`                              | pin   | regel uit `vsa-tooling.pin` |

## Pin bumpen

```cmd
cd /d C:\Git\orthodox-ronl\bibliotheek
scripts\bump-vsa-tooling-pin.cmd
```

Optioneel eerst `--dry-run`, of een andere ref: `bump-vsa-tooling-pin 0.2.0`.
Het script schrijft alleen `vsa-tooling.pin`; commit daarna zelf en maak een
PR naar `main` van bibliotheek wanneer tooling op VSA-tooling/`main` (of die
tag) stabiel genoeg is voor productie.

Handleiding: [bump-vsa-tooling-pin](../content-source/handleiding/scripts/bump-vsa-tooling-pin.md).
