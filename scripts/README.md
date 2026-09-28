# Scripts (bibliotheek)

Org-conventie: https://github.com/orthodox-ronl/bron/blob/main/docs/specs/repo-scripts.md

`.\scripts` op PATH; Python 3.14; Hugo Extended 0.160.1.

| Commando | Doel |
| -------- | ---- |
| `serve` | Hugo-preview op http://127.0.0.1:18732/ (niet 1313, niet 18731) |
| `build` | Site in `generated\site` |
| `check` | CI-spiegel / preflight (Hugo + Coria-fingerprints) |

**Fase 1:** geen VSA-tooling in deze repo. Partituren/PDF/SVG die al in
`content-source/` en `static/` staan, worden als-is gepubliceerd.
`fingerprint_coria_mxl.py` maakt Oefenen-URL's onder `static/mxl/c/`.
Productpipelines (`vsa-products`, `mscz-products`, …) komen later via de
gepubliceerde `vsa`-CLI, niet als forked scripts.
