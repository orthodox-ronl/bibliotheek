# AGENTS.md — bibliotheek

Richtlijnen voor AI-assistenten in deze repository.

Organisatie-context: [orthodox-ronl/AGENTS.md](https://github.com/orthodox-ronl/bron/blob/main/AGENTS.md)
(of org-root). Terminologie: [bron/docs/specs/terminologie.md](https://github.com/orthodox-ronl/bron/blob/main/docs/specs/terminologie.md).

Tooling-contract: [docs/tooling-koppeling.md](docs/tooling-koppeling.md).
**Contracten eerst** (hard): bij elk werk aan bestandsinhoud/export/PDF/SVG/…
eerst VSA-tooling `docs/formats/contract-index.md` + bibliotheek-specs
(`docs/specs/koormap-paginataal.md`, `schermpartituur.md`, …) lezen en
naleven — zie `.cursor/rules/contracten-eerst.mdc`.
Publicatiecontrole / sibling-namen: [docs/publicatiecontrole.md](docs/publicatiecontrole.md)
(leesbaar: handleiding *Publicatiecontrole*).
Lifecycle Werkbank/Catalogus: [docs/levenscyclus.md](docs/levenscyclus.md)
(leesbaar: handleiding *Levenscyclus*).
Catalogus-titels (afleiden bij bouw): [docs/catalogus-titels.md](docs/catalogus-titels.md).
Eén canonieke notatiebron per leaf: [docs/catalogus-notatiebron.md](docs/catalogus-notatiebron.md).

---

## Rol

**bibliotheek** is de publicatie-/oefensite voor:

1. de gedeelde **catalogus** (`zangstuk` → `variant` → `uitvoeringsvorm`);
2. **koormappen** per parochie/klooster/… (views via shortcode `bieb`);
3. de **handleiding** om de bieb bij te houden.

Onderscheid: **bibliotheek** = deze repository / de site als geheel;
**catalogus** = de Hugo-sectie met zangstukken → varianten → uitvoeringsvormen.

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

## Worktrees (lokaal)

| Map | Alleen voor |
| --- | --- |
| `C:\Git\orthodox-ronl\bibliotheek` | Site-/feature-werk (UI, layouts, JS, docs, o.a. branch `translit`) |
| `C:\Git\orthodox-ronl\bibliotheek-onderhoud` | Bronnen importeren/wijzigen + daarna producten genereren |

Transliteratie-UI en andere features **niet** in de onderhoud-worktree.
Detail: `.cursor/rules/worktrees-rollen.mdc`.

---

## Lokaal

```cmd
cd /d C:\Git\orthodox-ronl\bibliotheek
check
serve
```

Preview: **http://127.0.0.1:18732/** — nooit poort **1313**, niet **18731** (VSA-demo).

`check` = validate + publicatiecontrole (VSA inclusief `.vsa.svg`, MSCZ,
tekstblad, mvsa inclusief Score-IR/from-ir MusicXML, audio, lyrics,
import) + bibliotheek-id-colofon (`Bibliotheek-id:`) + Coria-fingerprints
+ legacy bladermap-SVG + Hugo. `check` schrijft geen catalogusproducten.
Vernieuwen: `scripts\products.cmd` (of los `products --kinds vsa` /
`products --kinds mscz` / `products --kinds mvsa` / `products --kinds tekstblad` /
`products --kinds audio` / `products --kinds lyrics`). Koormap-blad `index.md.pdf`:
`scripts\pdf.cmd` (niet in `products` of `check`). Optioneel
tooling klaarzetten:

```cmd
scripts\_ensure.cmd --hugo --vsa-tool
```

(Sibling `..\VSA-tooling` heeft voorrang; anders float/`pin` via git.)

---

## Content-regels (bladermap)

- Partituren alleen onder `content-source/catalogus/…`
- Koormap-slots: markdown + `{{</* bieb id="zangstuk/variant/uitvoeringsvorm" */>}}`
- `publicatiestatus` + `automatische_inhoud` op bladermap-pagina’s
- Ruwe dumps in `content-source/input/` (gitignore `_inbox/` / `_werk/`)
- Taal: geen suffix op uitvoeringsvorm-id = Nederlands; andere talen
 als suffix (`-ksl`, …) — zie handleiding
 [Taalvarianten](content-source/handleiding/start/catalogus-en-koormappen.md)
- Overzichtsbomen: enkelvoudige tussenlagen inklappen (o.a. enige
  variant-tak); bij `default` bladtitel `Zangstuk (uitvoeringsvorm)`.
  Nooit `default` naast andere variant-ids — zie
  [Catalogus en koormappen](content-source/handleiding/start/catalogus-en-koormappen.md)
  en [docs/catalogus-titels.md](docs/catalogus-titels.md)
