# Plan: de GitHub Pages-publicatie onder 1 GB

Status: **voorstel, nog niet uitgevoerd** (metingen van 28 november 2026).

## Antwoord eerst

De grootste winst is het weghalen van 460 oude blad-PDF's uit de echte site.
Die PDF's zijn samen ongeveer 735 MB. De echte site gaat daarmee van
ongeveer 983 MB naar ongeveer 248 MB.

## Waarom het nodig is

GitHub Pages is de dienst die de site op internet zet. GitHub staat een site
van ten hoogste 1 GB toe en breekt een publicatie af na 10 minuten
([grenzen van GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits)).

De tak `gh-pages` bevat alles wat online staat:

| Onderdeel | Wat het is | Grootte |
| --- | --- | --- |
| Echte site | de publicatie van `main` | 983 MB |
| `preview/` | de publicatie van `development` | 366 MB |
| Elke proefsite van een andere tak | zelfde inhoud als `preview/` | 366 MB |

## Waar de ruimte in zit

| Soort bestand | Echte site | `preview/` |
| --- | --- | --- |
| blad-PDF (`index.md*.pdf`) | 735 MB | 0 MB |
| geluid (`.mp3`) | 94 MB | 108 MB |
| plaatjes (`.svg`) | 73 MB | 164 MB |
| partituurdata (`.musicxml`) | 42 MB | 53 MB |
| overig | ongeveer 39 MB | ongeveer 41 MB |

De blad-PDF's horen sinds [pdf-r2.md](pdf-r2.md) op Cloudflare R2 (een
aparte opslagdienst). De publicatie van `main` voegt alleen bestanden toe en
verwijdert nooit iets (`keep_files: true` in `pages.yml`). De oude blad-PDF's
zijn daarom blijven staan.

## Eerst herstellen: de downloadknop op de echte site

In de gepubliceerde pagina's van de echte site begint de PDF-link met
`//production/...`. Zo'n link werkt niet. De oorzaak is dat op `main` in
`layouts/partials/pdf-asset-url.html` twee waarden bij `strings.TrimSuffix`
verwisseld zijn. Op `development` is de fout al hersteld. De echte site is
dus hersteld zodra de herstelling op `main` staat.

## Stappen

1. **Downloadknop herstellen** op `main`.
2. **Controleren dat R2 de blad-PDF's heeft** in de map `production/`.
   Zonder die controle mogen de oude PDF's niet weg.
3. **De 460 oude blad-PDF's verwijderen** van `gh-pages`. Winst: 735 MB.
4. **Herhaling voorkomen:** de publicatie van `main` ruimt bestanden op die
   niet meer in de site horen. De mappen `preview/` en de proefsites van
   andere takken blijven daarbij staan.

Na stap 3 is het totaal ongeveer 614 MB (echte site plus `preview/`). Eén
proefsite van een andere tak brengt het totaal op ongeveer 980 MB.

## Later, als het weer krap wordt

| Maatregel | Winst per proefsite | Nadeel |
| --- | --- | --- |
| Geen proefsite meer per tak, alleen `preview/` | 366 MB | Een wijziging is pas te bekijken na samenvoegen. |
| Geen geluid in proefsites van takken | ongeveer 108 MB | Geluid is daar niet te beluisteren. |
| Geluid naar R2, ook voor de echte site | ongeveer 100 MB per site | Extra stap bij uploaden. |

Aanbeveling: voer eerst stap 1 tot en met 4 uit. Kies daarna pas uit de
tabel hierboven.
