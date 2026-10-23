# Scripts (bibliotheek)

Org-conventie: https://github.com/orthodox-ronl/bron/blob/main/docs/specs/repo-scripts.md  
Tooling-contract: [docs/tooling-koppeling.md](../docs/tooling-koppeling.md)

`.\scripts` op PATH; Python 3.14; Hugo Extended 0.160.1.

Korte hulp in het opdrachtvenster: `h` (lijst) of `h <naam>` (zelfde als
`<naam> -h`).

| Commando | Doel |
| -------- | ---- |
| `h` | Overzicht van commando’s; `h <naam>` = `<naam> -h` |
| `validate` | `vsa validate` op `content-source\catalogus` (plus `mvsa validate` als er `.mvsa` staat) |
| `vsa-products` | Maakt/vernieuwt `{stam}.vsa.mxl` + `{stam}.vsa.pdf` + `{stam}.vsa.svg` via `vsa musicxml` / `vsa pdf` / `vsa svg` + stamp |
| `mscz-products` | Maakt/vernieuwt `{stam}.mscz.pdf` + `{stam}.mscz.mxl` via MuseScore / `mscz mxl` + stamp |
| `tekstblad-products` | Maakt/vernieuwt `{stam}.tekstblad.pdf` via `vsa pdf` + stamp |
| `import-mvsa` | Maakt/vernieuwt bewerkvorm `{stam}.mscz.mvsa` via `mscz import` + stamp (standaard alleen bestaande siblings) |
| `mvsa-products` | Maakt/vernieuwt `{stam}.mvsa.mxl` + `{stam}.mvsa.pdf` + `{stam}.mvsa.svg` + `{stam}.mvsa.score-ir.json` + `{stam}.mvsa.from-ir.musicxml` via `mvsa musicxml` / `pdf` / `svg` / `score-ir --musicxml` + stamp |
| `audio-products` | Maakt/vernieuwt preview-`{stam}.{bron}.mp3` via `vsa audio` + ID3-stamp (Beluisteren) |
| `lyrics-products` | Maakt/vernieuwt `{stam}.….lyrics.txt` (zoektekst) |
| `products` / `all-products` | Product-kinds achter elkaar (`all-products` = `--kinds all`); daarna Coria-fingerprints (niet bij `--dry-run`). Geen `pagina-pdf`. |
| `pagina-pdf` | `index.pagina.pdf` naast een koormap- of catalogus-`index.md` (lokaal; niet in `products` / `check` / CI) |
| `layout` | Past layoutprofiel `partituur` toe op `.mscz` / `.mxl` (via tooling) |
| `ensure-bibliotheek-id` | Zet/controleert colofonregel `Bibliotheek-id:` op basispartituur-`.mscz` |
| `bump-vsa-tooling-pin` | Zet `vsa-tooling.pin` op tip van VSA-tooling (`main` of andere ref) |
| `opkuisen` | Herkomstanalyse + inhoudsopkuis (niet in `check`/CI) |
| `bieb accepteer` (`accept`) | Opnemen in `content-source\catalogus` onder catalogus-id (Werkbank → Catalogus) |
| `bieb hernoem` (`rename`) | Catalogus-id hernoemen (zangstuk/variant/uitvoeringsvorm; map, stam, refs, koormap-slots; flexibele id-vormen) |
| `bieb verwijder` (`delete`) | Catalogus-id wissen; dangling refs / koormap-slots rapporteren |
| `bieb kopieer` (`copy`) | Uitvoeringsvorm kopiëren naar nieuw id |
| `update-werkvoorraad` | Tabel `input\werkvoorraad.md` bijwerken (ook in check/build/serve) |
| `werkbank-status` | Open werkbank-cases; `data\werkbank-status.json` (ook via update-werkvoorraad) |
| `lifecycle-grenzen` | Grenzen werkbank ↔ catalogus (spaties / ruwe formats) |
| `oefenhoek-index` | Legacy SVG uit catalogus-`.vsa` → `static\vsa\bladermap\` (check/build/serve/CI; geen stamp). Scherm gebruikt sibling `{stam}.vsa.svg` zodra die er is. |
| `serve` | Hugo-preview op http://127.0.0.1:18732/ (niet 1313, niet 18731) |
| `build` | Site in `generated\site` |
| `check` | CI-spiegel / preflight (validate + publicatie-/importcontroles + bibliotheek-id + koormap-slotlinks + Coria + Hugo) |

Intern: `_ensure.cmd` (`--hugo`, `--vsa-tool`), `fingerprint_coria_mxl.py`,
`check_koormap_slot_links.py`, `sync_vsa_products.py`,
`check_vsa_products.py`, `sync_mscz_products.py`,
`check_mscz_products.py`, `sync_tekstblad_products.py`,
`check_tekstblad_products.py`, `sync_import_mvsa.py`,
`check_import_mvsa.py`, `sync_mvsa_products.py`,
`check_mvsa_products.py`, `sync_audio_products.py`,
`check_audio_products.py`, `apply_mscz_layout.py`,
`ensure_bibliotheek_id.py`, `opkuisen.py`, `cleanup_capella_mxl.py`,
`mscz_content_cleanup.py`, `bieb.py`, `bieb_accepteer.py`,
`bieb_hernoem.py`, `bieb_verwijder.py`, `bieb_kopieer.py`,
`update_werkvoorraad.py`, `werkbank_status.py`,
`lifecycle_grenzen.py`, `catalogus.py`, `product_meta.py`,
`coria_mxl.py`.

**Geen forks van VSA-tooling.** Bibliotheek-specifieke wrappers mogen; die
roepen `vsa` / `mvsa` aan. Zie tooling-koppeling (float op `development`,
pin op `main` via `vsa-tooling.pin`).

```cmd
scripts\_ensure.cmd --hugo --vsa-tool
scripts\vsa-products.cmd
check --strict
```
