# GitHub: repo-bescherming (bibliotheek)

Korte checklist voor de publieke repository
[orthodox-ronl/bibliotheek](https://github.com/orthodox-ronl/bibliotheek).
Doel: niemand anders dan jij (en de Cursor-agent die **voor jou** werkt)
schrijft zomaar naar `main` of `development`. De site-deploy via GitHub
Actions moet blijven werken.

**Jij moet de regels in GitHub Settings zelf zetten.** Een Cloud Agent heeft
geen admin-rechten op deze repository en kan rulesets niet aanmaken.

---

## Stap A — Cursor mag pushen/mergen als die voor jou werkt

Doe dit **eerst**. Zonder deze bypass kan de Cursor-agent wél een
feature-branch en een pull request maken, maar meestal **niet** mergen naar
`main` of `development` als die branches een verplichte review hebben.

1. Open
   [Settings → Rules → Rulesets](https://github.com/orthodox-ronl/bibliotheek/settings/rules)
   op de repository `bibliotheek`.
2. Kies **New ruleset** → **New branch ruleset** (of bewerk het ruleset dat je
   al voor `main`/`development` hebt).
3. Vul in:
   - **Ruleset name:** bijvoorbeeld `Protect main and development`
   - **Enforcement status:** Active
4. Onder **Target branches** → **Add target** → **Include by pattern**:
   - `main`
   - `development`
5. Onder **Bypass list** → **Add bypass** → kies **GitHub Apps** → zoek en
   selecteer **Cursor**.  
   Zonder deze regel geldt de bescherming ook voor de agent die voor jou
   werkt.
6. Voeg óók toe: **Repository role** → **Admin** (jijzelf), zodat jij in de
   browser niet vastzit aan “één goedkeuring” op je eigen pull request.
7. Onder **Rules** vink aan:
   - **Restrict deletions**
   - **Block force pushes**
   - **Require a pull request before merging**
     - Required approvals: **1**
     - Dismiss stale reviews: aan
8. **Create** / **Save changes**.

Controle (kort): laat de Cursor-agent (in een run die jij start) een kleine
test-PR naar `development` openen en mergen. Lukt de merge, dan staat de
Cursor-bypass goed.

**Let op:** de Cursor-app omzeilt de regels alleen wanneer die met **jouw**
Cursor↔GitHub-koppeling op **deze** repository schrijft. Iemand zonder
schrijfrecht op `orthodox-ronl/bibliotheek` kan daar nog steeds niet naartoe
pushen — ook niet met Cursor op een andere computer.

---

## Stap B — `gh-pages` (site) niet laten vastlopen

De workflow *Deploy site to GitHub Pages* pusht naar de branch `gh-pages`
als `github-actions[bot]`.

1. Maak een **tweede** branch-ruleset, bijvoorbeeld `Protect gh-pages`.
2. Target: alleen `gh-pages`.
3. Rules (minimaal): **Restrict deletions**, **Block force pushes** (force
   push alleen via bypass als jij dat expres nodig hebt).
4. Bypass list:
   - **GitHub Apps** → **GitHub Actions** (of de app die de deploy doet)
   - **Repository role** → **Admin**
   - **GitHub Apps** → **Cursor** (alleen als jij wilt dat de agent ook
     direct op `gh-pages` mag werken, zoals bij opschonen van previews)
5. Geen verplichte pull request op `gh-pages` tenzij je de deploy-workflow
   expres anders inricht.

---

## Stap C — schrijfrechten smal houden

1. **Settings → Collaborators and teams:** alleen jij (en eventueel een
   team dat je bewust wilt) met **Write** of hoger.
2. Geef geen Write aan willekeurige accounts “voor het gemak”.
3. Buitenstaanders kunnen de publieke repo **clonen** en een **fork + PR**
   openen; dat is normaal. Jouw ruleset zorgt dat zo’n PR niet landt zonder
   jouw review (of zonder admin/Cursor-bypass).

---

## Wat dit wél en niet doet

| Wel | Niet |
| --- | --- |
| Blokkeert directe pushes naar `main`/`development` zonder PR (behalve bypass) | Maakt de repo onzichtbaar of niet-clonebaar |
| Vereist jouw review voor andermans werk | Vervangt voorzichtigheid bij grote bestanden in een PR |
| Laat Cursor (voor jou) en jijzelf door via bypass | Geeft elke Cursor-gebruiker op aarde schrijfrecht |

---

## Orphan / history-opschoning later

Bij een latere **force-push** of orphan-rewrite op `main`/`development`: zet
tijdelijk bypass of enforcement op **Disabled**, doe de rewrite, zet de
ruleset daarna weer **Active**. Noteer dat in de chat of issue van die klus.
