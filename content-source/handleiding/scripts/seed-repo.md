---
title: "seed-repo"
linkTitle: "seed-repo"
weight: 195
---

# NAME

`seed-repo` — kale kopie van de bibliotheek-repo naar een nieuwe map

# SYNOPSIS

```cmd
scripts\seed-repo.cmd <doelmap> [opties]
```

Met `.\scripts` op PATH: `seed-repo <doelmap> …`. Korte hulp: `h seed-repo`
of `seed-repo -h`. Typ `?` bij een interactieve vraag voor uitleg.

# DESCRIPTION

Maakt een **zo kaal mogelijke** map buiten deze repository, zodat je daar
een nieuwe git-repo kunt starten. Het script kopieert scripts, layouts,
documentatie, homepage, handleiding en catalogus-/koormap-**bronnen**, plus
tekstblad-schermbestanden die historisch handmatig zijn gemaakt.

Het laat **regenereerbare** afgeleiden weg: sibling-MXL/SVG/audio/lyrics van
`.vsa` / `.mvsa` / `.mscz`, koormap- en catalogus-`index.md.pdf`, buildmappen
(`generated/`, Coria-cache), en `.git`. Een lokale Python-venv (`.venv`) gaat
niet mee; die zet je opnieuw met `_ensure`.

Na de kopie kun je in de doelmap opnieuw `serve`, `build`, `products` en
`check` draaien. Catalogus-schermen zonder sibling-SVG blijven arm tot je
`products` draait — dat is bewust.

## Opties

| Optie | Betekenis |
| ----- | --------- |
| `--dry-run` | Alleen tonen; niets schrijven |
| `--force` | Schrijf ook als de doelmap al bestanden heeft |
| `--source <pad>` | Andere bron-repo (default: deze bibliotheek) |
| `--configure` | Site-identiteit invullen; ontbrekende velden vragen |
| `--repo-name` | GitHub-repo-slug |
| `--github-org` | Default `orthodox-ronl` |
| `--site-title` | Hugo-titel |
| `--pages-base-url` | GitHub Pages-basis (anders afgeleid) |
| `--github-web-url` | Browser-URL van de GitHub-repo (anders afgeleid) |
| `--feedback-email` | Default: huidige waarde uit bron-`hugo.toml` |
| `--git-init` | `git init` in de doelmap |
| `--remote-url` | `origin` zetten (alleen met `--git-init`) |
| `--initial-commit` | Eerste commit (geen push) |
| `--ensure` | In de doelmap: `_ensure.py --hugo --vsa-tool` |

Met `--configure` of andere identiteitsflags herschrijft het script in de
**doelmap** `hugo.toml`, `.github/workflows/pages.yml` en
`scripts/fingerprint_coria_mxl.py` (Pages-root). Handleidingsteksten met het
woord «bibliotheek» blijven ongemoeid.

# EXAMPLES

Alleen kale kopie:

```cmd
scripts\seed-repo.cmd C:\Git\orthodox-ronl\parochie-demo
```

Identiteit interactief + deps installeren:

```cmd
scripts\seed-repo.cmd C:\Git\orthodox-ronl\parochie-demo --configure --ensure
```

Volledig meubelen (identiteit, git, eerste commit, ensure):

```cmd
scripts\seed-repo.cmd C:\Git\orthodox-ronl\parochie-demo --configure --git-init --initial-commit --ensure
```

Dry-run met expliciete waarden:

```cmd
scripts\seed-repo.cmd C:\tmp\demo --dry-run --repo-name parochie-demo --site-title "Parochie Demo"
```

# WHEN

Als je een **nieuwe** bibliotheek-achtige repo wilt starten op basis van deze
codebase, zonder de grote berg gegenereerde partituur-producten mee te
slepen. Voor één uitvoeringsvorm binnen dezelfde catalogus: gebruik
[bieb kopieer](../bieb-kopieer/), niet dit script.

# SEE ALSO

[check](../check/),
[products](../products/),
[pdf](../pdf/),
[serve](../serve/),
[h](../h/)
