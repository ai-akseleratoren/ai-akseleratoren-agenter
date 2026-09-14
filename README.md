# AI-Akseleratoren — agentbiblioteket

Dette er de faktiske agentene som driver AweSM hver dag, renset for
nøkler, kundedata og personlige detaljer, og gjort klare for din bedrift.

Du får ikke maler. Du får de ansatte — ferdig opplært, klare til å
omskoleres til din virksomhet.

## Slik bruker du en agent

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

### Fordi det går an
- **wenger-fantasy** — setter fotballaget. Agenter er ikke bare business.

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
