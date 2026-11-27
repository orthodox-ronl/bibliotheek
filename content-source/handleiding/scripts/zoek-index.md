---
title: "zoek-index"
linkTitle: "zoek-index"
weight: 108
---

# NAME

`build_zoek_index.py` — bouwt de zoekindex `static\zoek\index.json` waarmee
[Zoeken](/overzichten/zoeken/) op de site werkt

# SYNOPSIS

```cmd
python scripts\build_zoek_index.py [map]
```

Zonder `map` leest het script `content-source\catalogus`. Korte hulp:
`python scripts\build_zoek_index.py -h`. Er is geen losse `.cmd`: `check`,
`products` en de GitHub Pages-deploy draaien het script zelf.

# DESCRIPTION

Maakt één bestand met een regel per **uitvoeringsvorm** (de bladermap met een
`index.md` onder `zangstuk\variant\uitvoeringsvorm`). Per uitvoeringsvorm
komen er in: titel, id, publicatiestatus, de eerste woorden van de
gezongen tekst (incipit), het pad naar een beluister-mp3 en één
**zoektekst-blok**. Dat blok bevat de titel, de woorden uit het id en de
volledige gezongen tekst, in een vaste schrijfwijze:

- kleine letters, zonder accenten of trema’s (*Mysteriën* wordt *mysterien*);
- zonder `_` (het melisma-streepje, bijvoorbeeld in *verhoor_*);
- een woord met een streepje (*Drie-eenheid*) komt los én aaneen in het
  blok (*drie eenheid drieeenheid*), zodat je het op alle drie de manieren
  vindt;
- overige leestekens worden spaties;
- synoniemen uit `data\zoek-synoniemen.yaml` zijn al toegepast.

De browser past dezelfde schrijfwijze toe op wat je intypt; de uitleg staat
bij [Zoeken](/handleiding/start/zoeken/). Als de schrijfwijze verandert, moeten
`scripts\build_zoek_index.py` en `static/js/catalogus-zoek-kern.js` samen
veranderen; een test (`pytest scripts\test_build_zoek_index.py
scripts\test_zoek_kern_js.py`) bewaakt dat.

**Waar komt de gezongen tekst vandaan?** Uit de `.lyrics.txt` naast de
**canonieke** bron (`.mvsa`, `.vsa` of basis-`.mscz`; zie
[products (lyrics)](../lyrics-products/)). Is er nog geen `.lyrics.txt`, dan
maakt het script de tekst tijdens het bouwen met tooling. Afgeleide
notatie (`{stam}.vsa.mvsa`, `{stam}.mscz.mvsa`) wordt nooit gelezen. Het
veld `zoektekst` in de bronbestanden wordt niet gelezen.

Mappen met `manueel: true` doen wel mee; paden onder `input\` niet. Een
bestandsnaam met een spatie in een bladermap stopt het script met een
duidelijke melding.

Het script schrijft precies één bestand en heeft geen `--dry-run`: de index
is afgeleid en je bouwt hem altijd opnieuw met hetzelfde commando.

# EXAMPLES

```cmd
python scripts\build_zoek_index.py
python scripts\build_zoek_index.py content-source\catalogus\kondak
python scripts\build_zoek_index.py -h
```

# WHEN

- Je hebt een zangstuk toegevoegd, hernoemd of de tekst gewijzigd en wilt
  het meteen kunnen zoeken in `serve`: eerst
  `scripts\products.cmd --kinds lyrics`, dan dit script.
- `check` en `products` doen dit al voor je.
- Op GitHub Pages wordt de index bij elke deploy opnieuw gebouwd; de
  gecommitte `index.json` is alleen een lokale spiegel.

Iets wordt niet gevonden? Zie *Beheer: iets wordt niet gevonden* in
[Zoeken](/handleiding/start/zoeken/).

# SEE ALSO

[Zoeken](/handleiding/start/zoeken/), [products (lyrics)](../lyrics-products/),
[check](../check/), [products](../products/)
