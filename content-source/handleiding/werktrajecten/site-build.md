---
title: "Site-build"
linkTitle: "Site-build"
weight: 50
---

# Site-build

Dit werktraject zet `content-source` om naar een browsbare site:
lokaal onder `generated\site`, of op GitHub Pages na een push.

{{< cue >}}
```cmd
check
serve
```
Open http://127.0.0.1:18732/ — **niet** poort 1313, niet 18731.
{{< /cue >}}

## Waartoe

Koorleden en jij zien markdown, SVG’s, PDF’s en knoppen pas nadat de
site is gebouwd. Productpipelines (`vsa-products`, `mscz-products`, …)
draai je lokaal vóór `check`; CI controleert versheid maar schrijft die
producten niet. Lifecycle van een uitvoeringsvorm:
[Levenscyclus](../start/levenscyclus/).

## Eindresultaat

| Output | Rol |
| --- | --- |
| `static\mxl\c\` | Coria-MusicXML (fingerprint; gegenereerd, niet committen) |
| `generated\site` | Hugo-site |
| GitHub Pages | Productie / preview / branch-URL |

**Klaar** als: `check` groen is; lokaal opent de preview; na push is de
juiste Pages-URL bijgewerkt.

| Branch | URL |
| --- | --- |
| `main` | https://orthodox-ronl.github.io/bibliotheek/ |
| `development` | https://orthodox-ronl.github.io/bibliotheek/preview/ |
| andere | https://orthodox-ronl.github.io/bibliotheek/{slug}/ |

## Volgorde

```text
content-source (bronnen + product-siblings)
    |
    +-- fingerprint_coria_mxl  ->  static/mxl/c + data/coria-fp.json
    +-- oefenhoek-index --svg  ->  static/vsa/bladermap (plaatjes; geen stamp)
    +-- Hugo  ->  generated/site
```

Productpipelines (`vsa-products`, `mscz-products`, `mvsa-products`, …)
draai je lokaal; CI controleert versheid maar schrijft die producten niet.

## See also

- [check](/handleiding/scripts/check/)
- [serve](/handleiding/scripts/serve/)
- [Wat heb je nodig](/handleiding/start/wat-heb-je-nodig/)
