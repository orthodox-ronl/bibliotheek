---
title: "Publiceren"
linkTitle: "Publiceren"
weight: 40
---

Koorleden zien een **slot-pagina** of **koormap-sectie** in de liturgiemap
(of test in `overig/`). De oefenbestanden staan in de **catalogus**; de
slot-pagina verwijst met `bieb`. Een uitvoeringsvorm mag in
de catalogus staan zonder koormap — zie
[Catalogus en koormappen](../start/catalogus-en-koormappen/) (secties,
compositiebladen, boom versus één blad).

Pijplijn-overzicht (opnemen, productsporen, site-build):
[Werktrajecten](../werktrajecten/). Lifecycle Werkbank → Catalogus:
[Levenscyclus](../start/levenscyclus/).

- Catalogus: `index.md` + basispartituur/PDF/Coria/VSA of print (publicatiestam zonder spaties; eventueel `artefacten_handmatig: true`)
- Slot-pagina: `index.md` + shortcode `bieb` met parameter `id` (drie lagen); optioneel meerdere shortcodes
- Koormap-sectie: `_index.md` met kindlijst of eigen TOC
- Id-lijst: [Id-register](/catalogus/id-register/)
- Special: [werkbank / voorzien / ongerefereerd / oefenbaar](/catalogus/speciaal/)

1. [Opnemen in de catalogus](1-opnemen-in-catalogus/) — HOW `bieb accepteer` (werktraject: [Opnemen](../werktrajecten/opnemen-in-catalogus/))
2. [Catalogus en koormap](1-bladermap/) — koormap-slot met `bieb`
3. [Status en check](2-status-en-check/)
4. [Als het misgaat](3-als-het-misgaat/)
