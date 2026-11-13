# AI-Akseleratoren — agentbiblioteket

Dette er de faktiske agentene som driver AweSM hver dag, renset for
nøkler, kundedata og personlige detaljer, og gjort klare for din bedrift.

Du får ikke maler. Du får de ansatte — ferdig opplært, klare til å
omskoleres til din virksomhet.

## Slik bruker du en agent

Hent alt med `git clone https://github.com/ai-akseleratoren/ai-akseleratoren-agenter.git`, eller trykk på den grønne Code-knappen og velg Download ZIP. Har du hentet før, kjører du `git pull` for å få de nyeste versjonene.

1. Åpne mappa til agenten du vil ha, og les `README.md` — den forklarer hva
   agenten gjør og hva du trenger.
2. Kopier `SKILL.md` inn i ditt eget prosjekt, i mappa
   `.claude/skills/<agentnavn>/SKILL.md`.
3. Finnes det en `.env.example`, kopier den til `.env` og fyll inn dine egne
   nøkler. **`.env` skal aldri i git.**
4. Tilpass `SKILL.md`: dine mål, din kadens, dine kanaler. Agenten er skrevet
   for å tilpasses — den er en stillingsbeskrivelse, ikke en låst maskin.
5. Si navnet på agenten til Claude Code, så starter den.

Har du aldri gjort dette før: start med **Referat-agenten** eller
**Jocko**. De trenger ingen integrasjoner og gir resultat første dagen.

## Agentene

Sist oppdatert 13. november 2026. Alle agentene er hentet fra versjonene jeg bruker i dag, med det de har lært siden sist.

Nytt 13. november: **klonen-video** og **pakkeren-podkast** er nye. **rubin-innholdsagent** har fått en tallagent som leser din egen YouTube-kanal. **thelma-videoklipper** har lært å måle pauser i lyden, åpne på bevegelse og kontrollere at ingen ord ble klippet bort.

### YouTube og podkast
- **rubin-innholdsagent** — produsenten: idé, tittel og thumbnail før manus, ukentlig skann av andre kanaler, og tallene fra din egen kanal
- **klonen-video** — en AI-avatar med din klonede stemme leser manuset, med lysark ved siden av. Alltid merket som AI
- **pakkeren-podkast** — titler, beskrivelse, kapitler og søkeord som gjør episoder lette å finne på YouTube
- **thelma-videoklipper** — klipper film av deg: bort med pauser og «eh», b-roll på ordet, full teksting

### Økonomi
- **warren-finansdirektor** — ukentlig scorecard, gjeldsvakt, cash-alarm
- **luca-fakturaagent** — fakturerer, purrer, holder utestående ryddig

### Marked og salg
- **north-star-markedssjef** — eier trakter, mailer, innhold og analyse
- **ogilvy-annonseagent** — bygger, analyserer og optimaliserer annonser
- **annonse-analytikeren** — dypanalyse av annonsekontoen over 6–12 måneder
- **copy-maskinen** — skriver tekst i din stemme, uten å finne på ting
- **halbert-nyhetsbrev** — ett brev i uka, intervjuer deg for råstoff
- **rubin-innholdsagent** — poster og videomanus av det du faktisk bygger
- **zoom-leads-agenten** — høster leads fra webinaret og lager ringeliste
- **webinar-telleren** — teller påmeldinger og varsler deg underveis
- **sully-funnelvakt** — overvåker at traktene dine faktisk virker
- **thelma-videoklipper** — videoannonser fra din egen stemme, ferdig i CapCut
- **rackham-salgsstrateg** — leser transkriptet fra et 1:1-salgsmøte og gir deg referatet, møte 2 og prisen på et 6/12-måneders samarbeid
- **chatklonen** — fletter chatten fra tidligere webinarsendinger inn i reprisen, tidsatt etter det du faktisk sier
- **miller-sosiale-medier** — skriver og legger i kø Facebook- og Instagram-poster, stories og reels som går ut av seg selv
- **seo-agenten** — sjekker hva Google og ChatGPT ser på nettsiden din, om du dukker opp i søkene, og foreslår forbedringer

### Fellesskap og medlemskap
- **skool-redaktoren** — holder liv i community-et ditt etter en fast ukesrytme
- **medlemsvakten** — avstemmer hvem som betaler mot hvem som har tilgang
- **kursopptak-agenten** — Zoom-sending inn, ferdig Classroom-leksjon ut

### Drift og hverdag
- **stemme** — diktert tekst inn, ferdig formatert tekst ut
- **jocko-assistent** — morgenbrief, ukesplan, todo-oppfølging, accountability
- **alfred-epostagent** — flere innbokser, to sveip om dagen, rydder selv
- **referat-agenten** — møte inn, referat og oppgaveliste ut
- **kvalitetsvakten** — kvalitetssikrer alt som skal ut
- **whatsapp-broen** — les og send WhatsApp fra Claude
- **quy-kundeservice** — sveiper support-e-post, CRM-innboks og DM, skriver svarutkast og sender først når du har sagt ja

### Fordi det går an
- **wenger-fantasy** — setter fotballaget. Agenter er ikke bare business.
- **kilian-treningscoach** — sier hva du skal trene i dag, logger økta og holder deg i nakken fram mot målet ditt

## Sikkerhet — les dette

Alle agentene her er renset: ingen nøkler, ingen kundedata, ingen
personopplysninger. Når du bygger videre på dem, hold det slik:

- Nøkler bor i `.env`, aldri i `SKILL.md` og aldri i git
- Legg `.env` i `.gitignore` **før** første commit
- Kundedata, telefonnumre og e-postlister hører ikke hjemme i et repo
- Skal du dele agenten din videre — rens den på nytt, samme måte

## Får du det ikke til?

Spør i fellesskapet. Noen har alltid svart før dagen er omme, og
tirsdagene er til nøyaktig dette: vi bygger sammen, live.
