# Scripts (bibliotheek)

Org-conventie: https://github.com/orthodox-ronl/bron/blob/main/docs/specs/repo-scripts.md  
Tooling-contract: [docs/tooling-koppeling.md](../docs/tooling-koppeling.md)

`.\scripts` op PATH; Python 3.14; Hugo Extended 0.160.1.

| Commando | Doel |
| -------- | ---- |
| `validate` | `vsa validate` op `content-source\bibliotheek` (plus `mvsa validate` als er `.mvsa` staat) |
| `serve` | Hugo-preview op http://127.0.0.1:18732/ (niet 1313, niet 18731) |
| `build` | Site in `generated\site` |
| `check` | CI-spiegel / preflight (validate + Coria-fingerprints + Hugo) |

Intern: `_ensure.cmd` (`--hugo`, `--vsa-tool`), `fingerprint_coria_mxl.py`.

**Geen forks van VSA-tooling.** Bibliotheek-specifieke wrappers mogen; die
roepen `vsa` / `mvsa` aan. Zie tooling-koppeling (float op `development`,
pin op `main` via `vsa-tooling.pin`).

```cmd
scripts\_ensure.cmd --hugo --vsa-tool
```
