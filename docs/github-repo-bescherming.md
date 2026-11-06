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

## Stap B — `gh-pages` (site): géén Actions in de bypass

De workflow *Deploy site to GitHub Pages* pusht naar `gh-pages` met de
ingebouwde `GITHUB_TOKEN` (`github-actions[bot]`).

**Die actor kun je niet in een ruleset-bypass zetten.** In *Add bypass*
staan rollen, teams en geïnstalleerde GitHub Apps (zoals Cursor) — niet
“GitHub Actions”. Dat is een GitHub-beperking, geen ontbrekende knop.

### Aanbevolen: geen streng ruleset op `gh-pages`

1. Zet **geen** “block force pushes” / “restrict updates” / verplichte PR
   op `gh-pages` zolang de deploy via die token pusht.
2. Bescherm de site indirect: alleen jij (en bewust gekozen accounts) heeft
   **Write** op de repository (stap C). Zonder Write kan niemand — en geen
   willekeurige Actions van een fork — naar `gh-pages` pushen.
3. Optioneel: bypass **Cursor** + **Admin** alleen nodig als je wél een
   ruleset op `gh-pages` zet én de agent daar direct mag werken.

### Alleen als je `gh-pages` tóch streng wilt vastzetten

Dan moet de deploy **niet** meer met `GITHUB_TOKEN` pushen, maar met een
**eigen GitHub App** (Contents: Read & Write), die app op de repo
installeren, die app in de bypass-lijst zetten, en de workflow een token
van die app laten gebruiken. Dat is een aparte, grotere klus — niet nodig
voor de basisbescherming van `main`/`development`.

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
