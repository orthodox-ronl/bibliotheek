# Catalogus title/linkTitle — agent-contract

Goedgekeurde beleidsregel. Leesbare vorm:
[Catalogus en koormappen](../content-source/handleiding/start/catalogus-en-koormappen.md)
(§ Titels).

## Doel

De catalogus blijft **schoon**: bronbestanden + wat daaruit volgt. Geen
handmatige paginatitels als “waarheid” in `index.md` / `_index.md`.
Leesbare, liturgische of koor-specifieke namen horen in **koormappen**
(of andere “mappen”), niet in de catalogus.

Gevolg voor later `bieb hernoem`: titels hoeven niet herschreven — de bouw
leidt ze opnieuw af uit het (nieuwe) pad/id of de bron.

## Keuze (vast)

**Afleiden bij de bouw** (niet als redactionele frontmatter):

- **Hugo** (partials `display-title.html` / `display-link-title.html`) en
  **zoekindex** (`scripts/build_zoek_index.py`) gebruiken hetzelfde
  algoritme uit pad/id, en voor leaf-`title` optioneel uit de bron.
- Frontmatter `title` / `linkTitle` in de catalogus zijn **geen bron van
  waarheid** op id-pagina’s (`zangstuk` / `variant` / leaf). Speciale
  pagina’s (`speciaal/`, `zoeken/`, catalogus-root) blijven FM gebruiken.
- Uitvoeringsvorm-labels: Python
  `catalogus.UITVOERINGSVORM_LINK_TITLES` + spiegel
  `data/uitvoeringsvorm-link-titles.yaml` (check houdt die gelijk).

## Afleidalgoritme

Ids blijven uit het **pad**: `zangstuk/variant/uitvoeringsvorm`.

| Laag | `linkTitle` (kort, navigatie) | `title` (pagina / zoek) |
| --- | --- | --- |
| Zangstuk (`_index`) | `section_title(mapnaam)` | Zelfde |
| Variant (`_index`) | Idem (`default` → Standaard) | Zelfde |
| Uitvoeringsvorm (leaf) | `uitvoeringsvorm_link_title` | **1)** bron (VSA/mvsa `titel:` / `soort:`); **2)** anders `derived_leaf_title_from_id` |

Implementatie: `scripts/catalogus.py` (`section_title`, `derived_leaf_*`,
`title_hint_from_source`).

## Wat wél in catalogus-frontmatter blijft

- `publicatiestatus`, `automatische_inhoud`, `alias_van`,
  build-/productflags, shortcode `bieb` op de leaf.
- Geen redactionele H1-tekst die losstaat van id/bron.

## Implementatiestatus

| Onderdeel | Status |
| --- | --- |
| Dit contract | van kracht |
| Hugo + zoekindex zelfde algoritme | gedaan |
| `bieb accepteer` / `check_catalogus_leaf_titles` | gedaan (accepteer schrijft nog afgeleide FM; `--title` alleen uitzondering) |
| Handleiding § Titels | synchroon |
| `bieb hernoem` verbreden | gedaan (titels niet aanpassen; bouw leidt af) |

## Hard rules (agents)

1. Geen nieuwe handmatige catalogus-`title`/`linkTitle` als redactionele
   inhoud toevoegen of eisen.
2. Bij nieuwe uitvoeringsvorm-labels: Python-dict én
   `data/uitvoeringsvorm-link-titles.yaml` bijwerken.
3. Geen hernoem-uitbreiding die op frontmatter-titels leunt.
