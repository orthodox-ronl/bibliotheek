# Tooling-koppeling (bibliotheek ↔ VSA-tooling)

Normatief voor deze repo. Zie ook [AGENTS.md](../AGENTS.md).

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
`check_import_mvsa`, `check_mvsa_products`, `check_audio_products` — allemaal
met `--fail`), daarna `check_mxl_playback_contract.py --fail` (bestaande
Coria-`.mxl` via `mxl validate`: M2/M8, importer-tags, meta),
`ensure_bibliotheek_id.py --check-only --fail` (colofon `Bibliotheek-id:`),
daarna Coria-fingerprints en Hugo. CI genereert geen producten — vernieuw
lokaal met `scripts\products.cmd` (of de losse `*-products.cmd`) en commit
de siblings.

Lokaal: `scripts\validate.cmd` of `check` / `check --strict`.

Naamgeving van bronnen en afgeleiden, en welke publicatiecontroles er (gaan) zijn:
[publicatiecontrole.md](publicatiecontrole.md).

Workflow Pages bepaalt de ref:

| Trigger-branch | Mode | Ref |
| -------------- | ---- | --- |
| `development` (en feature-branches) | float | `main` |
| `main` | pin | regel uit `vsa-tooling.pin` |

## Pin bumpen

```cmd
gh api repos/orthodox-ronl/VSA-tooling/commits/main --jq .sha > vsa-tooling.pin
```

Commit het pin-bestand op een PR naar `main` van bibliotheek nadat tooling
op VSA-tooling/`main` stabiel genoeg is voor productie.
