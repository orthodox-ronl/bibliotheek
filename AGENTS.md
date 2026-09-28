# AGENTS.md — bibliotheek

Richtlijnen voor AI-assistenten in deze repository.

Organisatie-context: [orthodox-ronl/AGENTS.md](https://github.com/orthodox-ronl/bron/blob/main/AGENTS.md)
(of org-root). Terminologie: [bron/docs/specs/terminologie.md](https://github.com/orthodox-ronl/bron/blob/main/docs/specs/terminologie.md).

Tooling-contract: [docs/tooling-koppeling.md](docs/tooling-koppeling.md).

---

## Rol

**bibliotheek** is de publicatie-/oefensite voor:

1. de gedeelde **bibliotheek** (`zangstuk` → `variant` → `uitvoeringsvorm`);
2. **koormappen** per parochie/klooster/… (views via shortcode `bieb`);
3. de **handleiding** om de bieb bij te houden.

---

## Tooling-afspraken (hard)

1. **Geen Python in deze repo die VSA-tooling uitbreidt of herschrijft.**
   Dat werk hoort in [VSA-tooling](https://github.com/orthodox-ronl/VSA-tooling).
2. **Bibliotheek-/koormap-beheertools wél hier** (`scripts\*.cmd` + dunne
   helpers). Die **roepen** `vsa` / VSA-tooling aan; ze kopiëren die logica niet.
3. **Float vs pin:** `development` float op tooling `main`; productie (`main`)
   pin’t via [`vsa-tooling.pin`](vsa-tooling.pin). Detail:
   [docs/tooling-koppeling.md](docs/tooling-koppeling.md).

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
| Tooling-pin | `vsa-tooling.pin` |

---

## Lokaal

```cmd
cd /d C:\Git\orthodox-ronl\bibliotheek
check
serve
```

Preview: **http://127.0.0.1:18732/** — nooit poort **1313**, niet **18731** (VSA-demo).

`check` = Coria-fingerprints + Hugo. Optioneel tooling klaarzetten:

```cmd
scripts\_ensure.cmd --hugo --vsa-tool
```

(Sibling `..\VSA-tooling` heeft voorrang; anders float/`pin` via git.)

---

## Content-regels (bladermap)

- Partituren alleen onder `content-source/bibliotheek/…`
- Koormap-slots: markdown + `{{</* bieb id="zangstuk/variant/uitvoeringsvorm" */>}}`
- `publicatiestatus` + `automatische_inhoud` op bladermap-pagina’s
- Ruwe dumps in `content-source/input/` (gitignore `_inbox/` / `_werk/`)
