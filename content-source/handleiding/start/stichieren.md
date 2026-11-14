---
title: "Stichieren in de catalogus"
linkTitle: "Stichieren"
weight: 28
---

# Stichieren in de catalogus

**Antwoord eerst:** stichieren horen onder de genre-emmer `stichier`. Elk
werk (bijvoorbeeld *Heer ik roep* in één toon) is een **variant**. Coupletten
die je als aparte partituur in een koormap wilt, krijgen elk een eigen
**uitvoeringsvorm**. De verzamel-`.vsa` met alle bekende coupletten staat in
een aparte uitvoeringsvorm `groningen` (of een andere herkomst).

## Padmodel (voorbeeld toon 6)

```text
catalogus/stichier/
  heer-ik-roep-toon-6/
    groningen-1/     ← couplet 1 (canonieke .vsa + products)
    groningen-2/     ← couplet 2
    groningen/       ← alle bekende coupletten in één .vsa
```

| Catalogus-id | Rol |
| ------------ | --- |
| `stichier/heer-ik-roep-toon-6/groningen-1` | Eerste couplet (*Heer ik roep…*) voor blad/scherm |
| `stichier/heer-ik-roep-toon-6/groningen-2` | Tweede couplet (*Laat mijn gebed…*) |
| `stichier/heer-ik-roep-toon-6/groningen` | Verzamelbron: beide coupletten (later meer) in één `.vsa` |

Publicatiestam: `stichier-heer-ik-roep-toon-6-groningen-1` enzovoort.
Navigatielabels: *Groningen 1*, *Groningen 2*, *Groningen*
(`data/uitvoeringsvorm-link-titles.yaml`).

Per leaf geldt **één** canonieke notatiebron (hier `.vsa`). Geen `.mvsa`
ernaast in dezelfde map — zie [Publicatiecontrole](publicatiecontrole/).

## Wat in welke map zit

| Leaf | Bestand | Inhoud |
| ---- | ------- | ------ |
| `groningen-1` | `…-groningen-1.vsa` | Eén couplet: eigen `[:]` … `[:]` |
| `groningen-2` | `…-groningen-2.vsa` | Idem, tweede couplet |
| `groningen` | `…-groningen.vsa` | Twee (of meer) stukken achter elkaar; elk couplet blijft een eigen `[:]`-blok |

**Frasescheider `//`:** zet die **aan het eind van de een-na-laatste strofe**
(niet op de beginkolom van de laatste). Zo zien zangers al dat de volgende
regel de formulefrase *laatste* is — dezelfde conventie als bij troparen
(`mapping-vsa`: `//` = scheiding vóór laatste).

Op elke leaf: `index.md` met shortcode `bieb` naar dat id.

Producten (lokaal, niet in CI): zelfde straat als andere catalogus-`.vsa`:

```cmd
scripts\products.cmd --kinds vsa,lyrics,audio catalogus\stichier\heer-ik-roep-toon-6
```

Dat levert o.a. `.vsa.svg`, (via T1) `.vsa.mvsa` plus mvsa-producten,
`.vsa.mp3` en `.vsa.lyrics.txt` op.

## Formule (melodie)

Stichiermelodieën staan als formule onder
[Formules](/catalogus/formules/), o.a.
[`stichier-toon-1-groningen`](/catalogus/formules/stichier-toon-1-groningen/)
en
[`stichier-toon-6-groningen`](/catalogus/formules/stichier-toon-6-groningen/)
(machinebron in VSA-tooling). In de `.vsa`-frontmatter:

- `soort: stichier`
- `toon: 6` (of `1`, …)
- `formule: stichier` (kiest de stichier-formule voor die toon)

Speelplan toon 6: `|:` 1, 2, 3 `:|` laatste; bij strofe-aantal n×3:
`|:` 1, 2, 3 `:|` **voorlaatste**, laatste. Toon 1 wijkt licht af (4e
cyclusfrase = 2). Authoring-schets SATB: `vsa mvsa` (werkbank) — dat is
**geen** catalogus-productstraat naast de `.vsa`.

## Koormap: eerste coupletten als partituur

Zelfde patroon als de geloofsbelijdenis (meerdere `bieb` op één blad):

```markdown
{{</* bieb id="stichier/heer-ik-roep-toon-6/groningen-1" */>}}

{{</* witruimte */>}}

{{</* bieb id="stichier/heer-ik-roep-toon-6/groningen-2" */>}}
```

De verzamel-leaf `…/groningen` kun je weglaten op het blad, of eronder
tonen als je de rest ook wilt laten zien.

## Alternatief voor later (nog niet gebouwd)

Eén leaf `groningen` met **één** groot `.mvsa` (of `.vsa`) en
`@sectie couplet-1`, `@sectie couplet-2`, … zou de catalogus dunner maken.
Dan kan de koormap vandaag **niet** “alleen couplet 1 en 2” plukken zonder
nieuwe shortcode-opties (sectiefilter op `bieb`). Dat is een mogelijke
verbetering; tot die tijd blijven aparte uitvoeringsvormen per couplet de
vaste aanpak.

## Zie ook

- [Zangstuk-soorten](../zangstuk-soorten/) — `stichier` als genre-emmer
- [Catalogus en koormappen](../catalogus-en-koormappen/) — compositieblad /
  meerdere `bieb`
- [Formules](/catalogus/formules/) — o.a. `stichier-toon-1-groningen`,
  `stichier-toon-6-groningen`
- [products (vsa)](../../scripts/vsa-products/) — producten bij `.vsa`
