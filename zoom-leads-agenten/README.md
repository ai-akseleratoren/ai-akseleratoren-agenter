# Zoom-leads-agenten — ringeliste rett etter webinaret

En Claude Code-agent som høster «ja»-leads fra chatten og Q&A-en i Zoom-
webinaret ditt, matcher dem mot CRM-et, flytter dem i pipelinen og leverer en
ferdig ringeliste med navn, telefonnummer og hva personen faktisk skrev.

**Problemet den løser:** De varmeste leadsene dine sitter i webinar-chatten og
skriver «ja, veldig interessert!» — og så blir chatten aldri lest. Neste dag er
temperaturen borte. Å lese gjennom chatten manuelt og slå opp hver person i
CRM-et tar en time du ikke har rett etter et webinar.

**Hva agenten gjør:**
- Lister møtene dine i Zoom så du finner riktig webinar
- Henter deltakere, chat og Q&A, og finner både rene «ja» og interesse-signaler
  («interessert», «hvordan booker jeg?») — det er der de fleste leadsene ligger
- Matcher mot CRM-et på e-post først, så navn, med tiebreak på e-postinitialer
  og hvor ferske kontaktene er
- Oppretter eller flytter opportunity til «Engaged»-steget (eller ditt eget)
- Skriver `ringelister/<dato>-<møte-id>.md` med tre bolker: klare, tvetydige,
  ikke funnet — og varsler på Slack hvis du har satt opp en webhook

**Hva agenten ALDRI gjør:** ringer, sender meldinger til leadsene, eller legger
telefonnumre i en gruppechat. Kjør med `--dry-run` når du vil se resultatet
uten å røre CRM-et.

**Du trenger:**
- Claude Code og Python 3 (ingen pakker å installere — kun standardbiblioteket)
- En Zoom Server-to-Server OAuth-app (marketplace.zoom.us) med scopes for
  rapporter og opptak — chat-filen kommer fra cloud recording, så webinaret må
  tas opp i skyen
- Et CRM med API. Skriptet er skrevet mot GoHighLevel; bruker du noe annet, er
  det bare CRM-funksjonene i skriptet som må skrives om

**Kom i gang:**
1. Legg `zoom_leads.py` i `scripts/` i prosjektet ditt, og lim inn `SKILL.md` i
   `.claude/skills/zoomleads/`.
2. Kopier `.env.example` til `.env`, fyll inn nøklene dine, og legg `.env` i
   `.gitignore`.
3. Kjør `python3 scripts/zoom_leads.py selftest` — den sjekker at
   chat-parsingen og signaldeteksjonen virker.
4. Kjør `python3 scripts/zoom_leads.py meetings --days 14` for å finne møte-ID.
5. Si «zoomleads» til Claude Code etter neste webinar. Er chat-filen ikke klar
   ennå (opptaket bruker noen minutter), kjør på nytt om en kvart time.

> Tilpass signalordene i `STRONG` i skriptet til din egen målgruppe og ditt
> eget språk — det er den enkleste måten å få flere treff på.

**Kjører du Q&A som Zoom-webinar?** Da havner spørsmålene i Q&A-panelet, ikke i
chatten, og API-et gir dem ikke ut uten ekstra scopes. Hent Q&A-rapporten fra
Zoom-adminen (Reports › Usage reports › Meeting and webinar history) etter hver
sending og legg den ved ringelista. Det er der de som spurte om pris står.
