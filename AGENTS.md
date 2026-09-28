# AGENTS.md — bibliotheek

Richtlijnen voor AI-assistenten in deze repository.

Organisatie-context: [orthodox-ronl/AGENTS.md](https://github.com/orthodox-ronl/bron/blob/main/AGENTS.md)
(of org-root). Terminologie: [bron/docs/specs/terminologie.md](https://github.com/orthodox-ronl/bron/blob/main/docs/specs/terminologie.md).

---

## Rol

**bibliotheek** is de publicatie-/oefensite voor:

1. de gedeelde **bibliotheek** (`zangstuk` → `variant` → `uitvoeringsvorm`);
2. **koormappen** per parochie/klooster/… (views via shortcode `bieb`);
3. de **handleiding** om de bieb bij te houden.

Geen fork van VSA-tooling-scripts. Repo-specifieke `.cmd` mag; tooling-logica
hoort in VSA-tooling of als aanroep van de gepubliceerde `vsa`-CLI.

---

## Terminologie

`zangstuk-id` → `variant-id` → `uitvoeringsvorm-id` → `representatie-id`

Vermijd: `uv-id`, afkorting `uv` als id, **uitvoeringsalternatief**,
impliciet weggelaten variant-id.

---

## Structuur

| Onderdeel | Pad |
| --------- | --- |
| Bewerkbare bron | `content-source/` |
| Hugo-templates | `layouts/` |
| Statische assets | `static/` (SVG’s o.a. in `static/vsa/bladermap/`) |
| Scripts | `scripts/` |
| Gegenereerd | `generated/` (niet committen) |

---

## Lokaal

```cmd
cd /d C:\Git\orthodox-ronl\bibliotheek
check
serve
```

Preview: **http://127.0.0.1:18732/** — nooit poort **1313**, niet **18731** (VSA-demo).

Fase 1: `check` = Hugo-build only (geen `import vsa`).

---

## Content-regels (bladermap)

- Partituren alleen onder `content-source/bibliotheek/…`
- Koormap-slots: markdown + `{{</* bieb id="zangstuk/variant/uitvoeringsvorm" */>}}`
- `publicatiestatus` + `automatische_inhoud` op bladermap-pagina’s
- Ruwe dumps in `content-source/input/` (gitignore `_inbox/` / `_werk/`)
