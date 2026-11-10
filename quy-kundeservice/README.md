# Quy — kundeserviceagenten

Quy er en Claude Code-agent som sveiper support-e-posten, CRM-innboksen og
Facebook/Instagram-DM noen ganger om dagen, sorterer det som kom inn, og
skriver svarutkast fra kunnskapsbanken din. Ingenting går til en kunde før
noen har sagt ja.

Oppkalt etter en første ansatt som var veldig dyktig. Standarden hennes er
standarden her: kundeservice er et konkurransefortrinn, ikke en kostnad.

**Problemet den løser:** Supporten ligger i tre innbokser, og ingen eier
den. Svar kommer dagen etter, eller aldri. AI-svar som sendes rett ut er
ikke løsningen. De dikter, og de svarer på klager med salg. Quy svarer kun
fra det du har skrevet ned, og alt som handler om penger går til deg.

**Hva agenten gjør:**
- Sveiper e-post, CRM-innboks (f.eks. GoHighLevel) og Messenger/Instagram
- Sorterer hver melding: kunde, privat eller støy. Private meldinger rører
  den aldri, den sier bare at en venter
- Slår opp kunden i CRM-et før den skriver, så svaret vet hva kunden har kjøpt
- Skriver utkast på kundens språk, kun fra `kunnskap/`. Mangler svaret, blir
  det et holdesvar og en eskalering til deg
- Godkjenning i chatten («send 2») eller i en Slack-kanal: ✅ sender,
  ❌ dropper, svar i tråden for å endre utkastet. Påminnelse etter 24 timer,
  utkastet går ut etter sju dager
- Håndterer avmeldinger selv, riktig: DND i CRM-et, ikke bare en tagg
- Sier fra når ingen godkjenner. Da er det som regel tonen som er feil

**Hva agenten ALDRI gjør:** sender uten godkjenning, svarer på refusjon,
klage, rabatt eller jus uten deg, dikter svar som ikke står i
kunnskapsbanken, gjengir private meldinger, eller følger instrukser som står
inne i en kundemelding.

**Du trenger:**
- Claude Code og Python 3 (skriptene bruker kun standardbiblioteket)
- Support-adressen med IMAP og app-passord (Gmail/Workspace er enklest)
- Eventuelt CRM med API-nøkkel (GoHighLevel, HubSpot, Salesforce, Kajabi)
- Eventuelt en Facebook-side og en Instagram Business-konto
- Eventuelt Slack-koblingen, hvis teamet skal godkjenne i en kanal

**Kom i gang:**
1. Lag mappa `.claude/skills/quy/` i prosjektet ditt og legg `SKILL.md` der.
   Legg `scripts/` i prosjektrota.
2. Kopier `.env.example` til `.env`. Aldri i git.
3. Skriv «sett opp kundeservice». Quy intervjuer deg og lager `kunnskap/`
   (FAQ, policy, svarstil, verneliste). Bruk tid på FAQ-en. Den er hele
   agenten.
4. E-post: skru på 2-trinns bekreftelse på support-kontoen, lag et
   app-passord, skru på IMAP, fyll `EPOST_*` i `.env`. Test:
   `python3 scripts/epost.py doktor`.
5. CRM: sett `CRM=` og nøkkelen. Test: `python3 scripts/crm.py slaa_opp
   kunde@example.com`.
6. **Meta-tokenet** (Messenger + Instagram, 30–60 min): lag en egen app på
   developers.facebook.com (type Business), legg til Messenger og
   Instagram, koble siden og godta ALLE tillatelser. Lag et langlevd
   side-token i Graph API Explorer (`pages_messaging`,
   `pages_manage_metadata`, `pages_read_engagement`, `instagram_basic`,
   `instagram_manage_messages`, `business_management`). Instagram-kontoen
   må være Business/Creator, koblet til siden, og «Tillat tilgang til
   meldinger» må være på i appen. Ellers ser API-et null samtaler uten å
   si fra. Test: `python3 scripts/meta.py doktor`.
7. Kjør tre runder manuelt («sjekk supporten») før du setter opp en
   scheduled task. Kjør tasken én gang med «Run now», så verktøyene er
   forhåndsgodkjent. Ellers stopper den på tillatelse.

**Det vi lærte i drift:**

- **«Ulest» er ikke «ubesvart».** CRM-innbokser viser egne utsendinger som
  uleste. Tell bare samtaler der siste melding er innkommende.
- **En avmeldt-tagg stopper ingenting.** DND-feltet gjør det. Og CRM-et
  nekter å sende bekreftelsen til en kontakt med DND, så send først, sett
  DND etterpå.
- **Koble aldri DM-er inn i en delt innboks.** Da leser hele teamet private
  meldinger.
- **Utkast som ingen godkjenner er et signal.** Stopp, hent ekte svar fra
  teamet inn i svarstilen, og start igjen.
