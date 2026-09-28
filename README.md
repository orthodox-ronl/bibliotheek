# bibliotheek

Hugo-site voor de **bibliotheek** van orthodoxe zangstukken en **koormappen**
(parochie-/kloosterhoekjes). Start: bibliotheek + liturgiemap Hemelum,
overgenomen uit de VSA-demo oefenhoek (`development`).

- Productie (later): https://orthodox-ronl.github.io/bibliotheek/
- Bron: https://github.com/orthodox-ronl/bibliotheek

## Lokaal

Org-conventie: [repo-scripts](https://github.com/orthodox-ronl/bron/blob/main/docs/specs/repo-scripts.md).
Hugo Extended **0.160.1**, `.\scripts` op PATH.

```cmd
cd /d C:\Git\orthodox-ronl\bibliotheek
serve
```

Preview: http://127.0.0.1:18732/

| Commando | Doel |
| -------- | ---- |
| `serve` | lokale Hugo-preview |
| `build` | productie-achtige build in `generated\site` |
| `validate` | `vsa validate` op bibliotheek-content |
| `vsa-products` | Coria-sibling `{stam}.vsa.mxl` bij `.vsa` |
| `check` | preflight (validate + productgate + Coria + Hugo) |

## Structuur

```text
content-source/
  bibliotheek/                 # zangstuk / variant / uitvoeringsvorm
  koormappen/hemelum/liturgie/ # liturgiemap Hemelum
  handleiding/                 # bieb bijhouden
  input/                       # ruwe dumps (geen Hugo-pagina's)
```

Koormappen bevatten geen tweede partituur: ze verwijzen met `bieb`.

## Relatie tot andere repo's

| Repo | Rol |
| ---- | --- |
| **bron** | Org-SoT / VSA-catalogusmetadata — specs linken, niet dupliceren |
| **VSA-tooling** | Parser/CLI — deze repo forkt die tools niet; wrappers roepen `vsa` aan |
| **VSA-demo** | Tooling-demo; oefenhoek was de herkomst van deze content |

Tooling-contract (geen forks; float op `development`, pin op `main`):
[docs/tooling-koppeling.md](docs/tooling-koppeling.md).

## Status

Hugo-site + Coria-fingerprints + `vsa validate` + VSA-productgate
(`{stam}.vsa.mxl` freshness) in `check` / Pages-CI (float/pin via
[docs/tooling-koppeling.md](docs/tooling-koppeling.md)). Sibling-namen en
gates: [docs/productgates.md](docs/productgates.md). Basispartituur-
MSCZ/PDF-gates volgen later — geen gekopieerde tool-Python.
