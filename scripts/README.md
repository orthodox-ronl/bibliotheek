# Scripts (bibliotheek)

Org-conventie: https://github.com/orthodox-ronl/bron/blob/main/docs/specs/repo-scripts.md  
Tooling-contract: [docs/tooling-koppeling.md](../docs/tooling-koppeling.md)

`.\scripts` op PATH; Python 3.14; Hugo Extended 0.160.1.

| Commando | Doel |
| -------- | ---- |
| `validate` | `vsa validate` op `content-source\bibliotheek` (plus `mvsa validate` als er `.mvsa` staat) |
| `vsa-products` | Maakt/vernieuwt sibling `{stam}.vsa.mxl` via `vsa musicxml` + stamp |
| `mscz-products` | Maakt/vernieuwt `{stam}.mscz.pdf` + `{stam}.mscz.mxl` via MuseScore / `mscz mxl` + stamp |
| `tekstblad-products` | Maakt/vernieuwt `{stam}.tekstblad.pdf` via `vsa pdf` + stamp |
| `import-mvsa` | Maakt/vernieuwt bewerkvorm `{stam}.mscz.mvsa` via `mscz import` + stamp (standaard alleen bestaande siblings) |
| `mvsa-products` | Maakt/vernieuwt `{stam}.mvsa.mxl` + `{stam}.mvsa.pdf` via `mvsa musicxml` / `mvsa pdf` + stamp |
| `audio-products` | Maakt/vernieuwt preview-`{stam}.{bron}.mp3` via `vsa audio` + ID3-stamp (Beluisteren) |
| `all-products` | Roept vsa-/mscz-/tekstblad-/mvsa-/import-/audio-products achter elkaar aan |
| `layout` | Past layoutprofiel `partituur` toe op `.mscz` / `.mxl` (via tooling) |
| `ensure-bibliotheek-id` | Zet/controleert colofonregel `Bibliotheek-id:` op basispartituur-`.mscz` |
| `opkuisen` | Herkomstanalyse + inhoudsopkuis (niet in `check`/CI) |
| `bieb accepteer` | Opnemen in `content-source\bibliotheek` onder bibliotheek-id (Werkbank → Catalogus) |
| `update-werkvoorraad` | Tabel `input\werkvoorraad.md` bijwerken (ook in check/build/serve) |
| `werkbank-status` | Open werkbank-cases; `data\werkbank-status.json` (ook via update-werkvoorraad) |
| `lifecycle-grenzen` | Grenzen werkbank ↔ catalogus (spaties / ruwe formats) |
| `oefenhoek-index` | SVG uit bibliotheek-`.vsa` → `static\vsa\bladermap\` (check/build/serve/CI; geen stamp) |
| `serve` | Hugo-preview op http://127.0.0.1:18732/ (niet 1313, niet 18731) |
| `build` | Site in `generated\site` |
| `check` | CI-spiegel / preflight (validate + publicatie-/importcontroles + bibliotheek-id + Coria + Hugo) |

Intern: `_ensure.cmd` (`--hugo`, `--vsa-tool`), `fingerprint_coria_mxl.py`,
`sync_vsa_products.py`, `check_vsa_products.py`, `sync_mscz_products.py`,
`check_mscz_products.py`, `sync_tekstblad_products.py`,
`check_tekstblad_products.py`, `sync_import_mvsa.py`,
`check_import_mvsa.py`, `sync_mvsa_products.py`,
`check_mvsa_products.py`, `sync_audio_products.py`,
`check_audio_products.py`, `apply_mscz_layout.py`,
`ensure_bibliotheek_id.py`, `opkuisen.py`, `cleanup_capella_mxl.py`,
`mscz_content_cleanup.py`, `bieb.py`, `bieb_accepteer.py`,
`update_werkvoorraad.py`, `werkbank_status.py`, `lifecycle_grenzen.py`,
`bibliotheek.py`, `product_meta.py`, `coria_mxl.py`.

**Geen forks van VSA-tooling.** Bibliotheek-specifieke wrappers mogen; die
roepen `vsa` / `mvsa` aan. Zie tooling-koppeling (float op `development`,
pin op `main` via `vsa-tooling.pin`).

```cmd
scripts\_ensure.cmd --hugo --vsa-tool
scripts\vsa-products.cmd
check --strict
```
