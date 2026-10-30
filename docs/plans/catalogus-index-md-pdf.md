# Plan: catalogusblad + `index.md.pdf`

Status: **index.md.pdf-traject + voorzien-placeholders** — 181 muziek-PDF’s;
stub/voorzien zonder notatie → A4 «Voorzien» (`compose_voorzien_pdf`);
`bieb accepteer --stub` schrijft die mee. Dialoog/tekstblad (§4) nog open.

Normatieve scherm-/print-eisen blijven in:

- [schermpartituur.md](../specs/schermpartituur.md)
- [koormap-paginataal.md](../specs/koormap-paginataal.md) §8a / §9
- [catalogus-titels.md](../catalogus-titels.md)

Doel van dit plan: **één bladintentie** op scherm en in `index.md.pdf`
voor elke catalogus-uitvoeringsvorm-pagina, zonder catalogus-product-PDF’s
(`.vsa.pdf` / `.mscz.pdf` / `.mvsa.pdf` / `.tekstblad.pdf`) te plakken.

---

## 1. Contract catalogus-leaf (vast voorstel)

### 1.1 Markdown-body

| Mag | Mag niet |
| --- | --- |
| Self-closing `{{</* bieb id="zangstuk/variant/uv" */>}}` | Markdown-`#` / `<h1>` met dezelfde (of andere) hoofdtitel als de template-H1 |
| Korte toelichting in gewone alinea’s (zeldzaam; bijv. dialoog) | Shortcode `kop` als tweede hoofdtitel naast de template-H1 |
| Frontmatter: `publicatiestatus`, `automatische_inhoud: false`, optioneel `pdf_bestandsnaam`, product-/buildflags | Redactionele `title` / `linkTitle` (bouw leidt af; zie `docs/catalogus-titels.md`) |
| Shortcode `kop` als **ondertitel** (liturgische regel) | `kop` als enige/vervangende hoofdtitel i.p.v. weergavetitel |
| | `pdf-bijelkaar` op een leaf met **één** stuk — geen winst; compact is koormap-keuze |

Canonieke minimale leaf:

```markdown
---
publicatiestatus: reviewable
automatische_inhoud: false
---

{{< bieb id="tropaar/zondag-toon-1/groningen" />}}
```

(Geen `title` / `linkTitle` op id-pagina’s; zie `docs/catalogus-titels.md`.)

### 1.2 Scherm

- Precies **één** hoofdtitel: template-H1 via afgeleide catalogustitel
  (`display-title`; geen frontmatter-`title`).
- Muziek via `bieb`: keten uit schermpartituur (OSMD → SVG → PDF-fallback).
- Nav **Download pagina** / **Print pagina** zodra `index.md.pdf`
  bestaat (page resource).
- Score-Download/Print naar product-PDF: buiten scope van *dit* plan;
  afbouwbesluit en volgorde staan in
  [product-pdf-afbouw.md](product-pdf-afbouw.md).

### 1.3 `index.md.pdf`

- Zelfde inhoudelijke intentie: **afgeleide bladtitel + muziek** (geen
  metadata-dubbeling uit product-PDF-plak).
- Bouw: kale blad-SVG’s uit `.mvsa` / `.vsa` / `.mscz` + titel in de
  compositor (`scripts\index_md_pdf.py`) — zie §2.
- Leesbaar A4; lange stukken als bladreeks (bestaand gedrag), niet door
  stille `--compact` buiten `pdf-bijelkaar`.

### 1.4 Wanneer géén pagina-PDF eisen

| Situatie | Gedrag |
| --- | --- |
| `publicatiestatus: voorzien` en nog geen `.vsa`/`.mvsa`/`.mscz`/tekstblad-bron | Geen `index.md.pdf`; knoppen blijven weg |
| Leaf zonder `bieb` (alleen “nog geen bron”-tekst) | `pdf.cmd` skip (huidig: geen flows) |
| Tekstblad-only | Apart pad (§4); niet via product-`.tekstblad.pdf`-plak |

---

## 2. Titel in de PDF zonder Markdown-`#`

**Probleem:** vandaag leest `pagina_pdf` titels uit `kop` of legacy `#`.
Als de catalogus-`#` weggaat (scherm: geen dubbele H1), zou de PDF zonder
aanpassing **alleen muziek** krijgen.

**Keuze (pagina-PDF-titel op catalogus-leaf):**

1. **Weergavetitel** = afgeleide leaf-titel (bron / id) — zelfde als
   site-H1 (`catalogus_weergave_title`). Frontmatter ``title`` telt niet.
2. Body-``kop`` / ``#`` wordt **ondertitel** (niet de hoofdtitel).

Koormap-slots blijven: titel uit `kop` / `#` in de Markdown (geen
template-H1, geen FM-injectie hier). Tekstblad-dialoog: eigen titelpad.

---

## 3. Groepconventies (licht)

Geen aparte shortcodes per soort. Wel vaste verwachtingen:

| Groep (voorbeelden) | Body | `pdf-bijelkaar` | Opmerkingen |
| --- | --- | --- | --- |
| **tropaar**, **kondak**, **alleluia**, korte **prokimen** met bron | Alleen `bieb` | Nee | Kort; één A4 meestal zonder compact |
| **ektinia** (één uitvoeringsvorm per leaf) | Alleen `bieb` | Nee | NL en KSL = aparte leaves, niet één catalogusblad |
| **antifonen**, **cherubijnenhymne**, andere lange **mvsa** | Alleen `bieb` | Nee | Bladreeks over meerdere A4; niet forceren op één blad |
| **dialoog** e.d. (tekstblad) | `bieb` + eventueel korte alinea | n.v.t. tot §4 | Geen notatie-SVG |
| Placeholders **voorzien** zonder bron | Geen eis pagina-PDF | — | Eerst bron, dan blad |

Metadata (soort, toon, liturgische titel) hoort in de **bron** (VSA/mvsa
frontmatter) of het **pad**, niet als handmatige H1 in de leaf.

---

## 4. Tekstblad-pad (open, apart in mijlpaal 3+)

Enige huidige tekstblad-only leaf:
`catalogus/dialoog-met-diaken/default/hemelum/`
(`.tekstblad.md` + `.tekstblad.pdf`, geen `.vsa`/`.mvsa`/`.mscz`).

`find_notation_source` faalt daar nu bewust (“plakt geen catalogus-PDF”).

**Richting (nog niet gebouwd):**

- Pagina-PDF uit **tekstinhoud** (Markdown/HTML van het tekstblad of de
  leaf-body), gezet op A4 naast de afgeleide titel — niet door
  `.tekstblad.pdf` te plakken als die product-chrome heeft.
- Exacte renderer (bestaande tekstblad-helper vs. dunne pymupdf-tekst)
  kiezen bij implementatie; steekproef verplicht vóór bulk.

---

## 5. Docs die synchroon moeten blijven

| Plaats | Afspraak |
| --- | --- |
| `content-source/handleiding/scripts/pdf.md` | NAME/DESCRIPTION = blad-SVG’s, geen product-PDF-plak |
| `scripts/pdf.cmd -h` | Idem |
| Dit plan | Groep- en titelkeuze tot de handleiding § Titels een korte zin over “geen `#` op catalogus-leaf” heeft |

Product-PDF-knoppen op het catalogusblad afschaffen: **niet** in dit
traject.

---

## 6. Steekproefkader (mijlpaal 3–4, na OK)

| Rol | Pad |
| --- | --- |
| Kort tropaar | `content-source/catalogus/tropaar/zondag-toon-1/groningen/` |
| Kort kondak | `content-source/catalogus/kondak/zondag-toon-1/groningen/` |
| Lang mvsa | `content-source/catalogus/cherubijnenhymne/15e-bortnjanski/hemelum/` |
| Tekstblad | `content-source/catalogus/dialoog-met-diaken/default/hemelum/` (pas na §4) |

Per steekproef: body zonder `#` → `scripts\pdf.cmd … --force` →
controleren op http://127.0.0.1:18732/ (één H1, muziekketen, nav-knoppen)
én de PDF (titel + muziek, geen product-plak).

Dry-run/bulk pas in mijlpaal 4, na groene steekproef.

---

## 7. Mijlpalen (rest)

| # | Inhoud |
| --- | --- |
| **2** | Ontwerp + docs-leugen weg — gedaan |
| **3** | Gedaan: `ensure_catalogus_derived_titles`; steekproef tropaar/kondak (1 A4) + cherubijnen (3 A4, breedte-schaal); tekstblad nog open |
| **4** | Gedaan: 192× `#` weg; 181× pagina-pdf (~14 min); skip zonder notatiebron |
| **5** | Gedaan: zie §8 hieronder |

Geen Coria/audio. Product-PDF-afbouw: niet stil in dit traject —
  zie [product-pdf-afbouw.md](product-pdf-afbouw.md).

---

## 8. Checklijst mijlpaal 5 (steekproef)

Norm: [schermpartituur.md](../specs/schermpartituur.md) §8 +
[catalogus-titels.md](../catalogus-titels.md).

| URL / blad | H1 | Keten | Nav Download/Print pagina | PDF titel+muziek |
| --- | --- | --- | --- | --- |
| `/catalogus/tropaar/zondag-toon-1/groningen/` | 1× afgeleid | SVG (`.vsa`) | ja | 1 A4, titel OK |
| `/catalogus/kondak/zondag-toon-1/groningen/` | 1× | SVG | ja | 1 A4 OK |
| `/catalogus/cherubijnenhymne/15e-bortnjanski/hemelum/` | 1× | OSMD (from-ir) | ja | 3 A4 OK |
| `/catalogus/ektinia/vrede/hemelum/` | 1× | OSMD (from-ir) | ja | 1 A4 OK |
| `/catalogus/dialoog-met-diaken/default/hemelum/` | 1× | tekstblad-PDF | nee (geen `index.md.pdf`) | n.v.t. tot §4 |

Dekking: 195 leaves, **0** Markdown-`#`, **181** `index.md.pdf`.
Score-product-PDF: zie afbouwbesluit
[product-pdf-afbouw.md](product-pdf-afbouw.md) (eerst inventaris).

Open: tekstblad → pagina.pdf (§4); 14 leaves zonder notatiebron.
