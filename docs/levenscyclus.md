# Levenscyclus (bibliotheek) — agent-contract

Leesbare vorm voor beheerders:
[handleiding — Levenscyclus](../content-source/handleiding/start/levenscyclus.md).

## Model

- **Case** = één uitvoeringsvorm (`zangstuk/variant/uitvoeringsvorm`),
  ook als de catalogusmap nog ontbreekt (alleen Doel-id / stub).
- **Lifecycle-fase** ≠ `publicatiestatus` (die is voor koorleden).
- Huidige fases: **Werkbank** (pre-productie) → **Catalogus** (canonieke
  bron in `content-source/catalogus/…`).
- Overgang: meetbare criteria + handmatig `bieb accepteer` (geen
  stille auto-promote).
- Fase-docs: `handleiding/start/werkbank.md`,
  `handleiding/start/catalogus.md`.
- Geen org-spec in **bron** voor dit model (tenzij later bewust).

## Scripts

| Commando | Rol |
| --- | --- |
| `scripts/werkbank-status.cmd` | Open werkbank-cases; schrijft `data/werkbank-status.json` |
| `scripts/lifecycle-grenzen.cmd` | Grenzen werkbank ↔ catalogus (spaties/ruwe formats) |
| `bieb accepteer` | Promote Werkbank → Catalogus |
| `*-products` / `all-products` | Catalogus-producten (pad mag) |

`update_werkvoorraad.py` (in check/build/serve) vernieuwt ook de
werkbank-status-JSON.

## Hard rules

Geen VSA-tooling-forks hier. Wrappers roepen `vsa` / bestaande
bibliotheek-scripts aan. Zie [tooling-koppeling.md](tooling-koppeling.md)
en [publicatiecontrole.md](publicatiecontrole.md).
