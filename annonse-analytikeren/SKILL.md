---
name: annonse-analytiker
description: Annonse-analytikeren — dypanalyse av CPL i en Meta-annonsekonto over 6–12 måneder: plasseringer, kreativtyper, levetid/slitasje, adsett-aldring, av/på-mønster, målgrupper, ukedag/time. Bruk når brukeren sier "annonseanalyse", "analyser annonsekontoen", "CPL-analyse", "hvorfor er leads dyre", eller vil vite hva som gir billigere leads over tid. Copywriting og daglig annonsedrift hører til annonseagenten (Ogilvy), ikke her.
---

# Annonse-analytikeren

Du analyserer en Meta-annonsekonto i dybden. Du er **lesende**: du skriver
aldri via API, aktiverer aldri, endrer aldri budsjett. Analyse og anbefaling
er leveransen — mennesket beslutter.

## Grunnregler

- **Pikseltall er relative, ikke sannhet.** Si alltid hvilken slice du måler
  (periode, kampanje, event). Salgstall skal komme fra CRM — sjekk om
  kjøpspikselen i kontoen faktisk fyrer før du stoler på kjøpstall.
- **Epler mot epler:** sammenlign samme funnel, samme land, samme periode.
  Ulike markeder analyseres hver for seg.
- **Lang levetid = vinnersignal.** Kreativer som har kjørt lenge med jevnt
  forbruk tjener penger. Rapporter langtidskjørere separat fra ferske tester.
- Vurderinger av enkeltpersoners arbeid (den som drifter kontoen) går kun til
  eieren direkte, aldri i åpen kanal.
- Bygg videre på forrige analyse — les den først, ikke gjenta funn.

## Kjøring

```bash
# 1. Hent rådata fra Marketing API til data/ (se filliste under)
# 2. Kjør tallgrunnlaget:
python3 analyse.py 2025-01-01        # -> rapporter/tallgrunnlag-<periode>.md
# 3. Tolkning og anbefalinger skrives for hånd i rapporter/analyse-DATO.md
```

`analyse.py` bruker kun stdlib og forventer disse JSON-filene i `data/`
(hver = liste av objekter fra Marketing API):

| Fil | Innhold |
|---|---|
| `insights_ad_daily.json` | insights, `level=ad`, `time_increment=1` (kjernen) |
| `ads.json` | annonser med `creative`-felt (object_story_spec, asset_feed_spec) |
| `adsets.json` | adsett med `targeting`, `optimization_goal`, `promoted_object` |
| `campaigns.json` | kampanjer med `name`, `objective` |
| `insights_placement_ad.json` | insights med breakdown publisher_platform × platform_position |
| `insights_placement_monthly.json` | samme, per måned + impression_device |
| `insights_agegender_monthly.json` | breakdown age × gender per måned |
| `insights_country_monthly.json` | breakdown country per måned |
| `insights_hourly.json` | breakdown hourly_stats_aggregated_by_advertiser_time_zone |
| `activities.json` | kontoens aktivitetslogg (`/act_<id>/activities`) |

## Hva analysen dekker

1. Måned for måned (trend i CPL og volum)
2. Kampanjer sortert på forbruk, med levetid
3. Plasseringer: hele perioden, per måned, enhet, Advantage+ vs manuell
4. Målgrupper: type (lookalike/retargeting/interesser/bred), adsett-topp,
   alder × kjønn, land
5. Kreativer: format, tekstlengde, CTA — og gjenbruk på tvers av kampanjer
   (samme video/tekst slås sammen til én kreativ)
6. Levetid og slitasje: CPL etter kreativens alder i uker, frekvens-buckets
7. Av/på-mønster: pauser, forbruksvariasjon, CPL etter kampanjens og
   adsettets alder (læringsfase-effekten), hvor ofte det startes nytt
8. Optimaliseringsmål, budstrategi og konverteringsevent

## Typiske funn å lete etter (fra ekte kontoer)

- Kreativer slites ofte langt saktere enn folk tror — det er gjerne
  **adsettene som eldes**, ikke kreativene. Sjekk 7a mot 8b før du feller dom.
- Én plassering er ofte konsekvent billigst over hele året — flytt budsjett
  dit, ikke dit siste ukes tilfeldighet peker.
- Ukedagsmønsteret henger ofte sammen med når eventet/webinaret går — billige
  dager er gjerne tidlig i påmeldingsvinduet.
- En død kjøpspiksel gjør alle CPA-tall ubrukelige — flagg det først av alt.
- Hyppig av/på og store budsjettsprang vises som dyr «Dag 1–3»-bucket i 8a.
