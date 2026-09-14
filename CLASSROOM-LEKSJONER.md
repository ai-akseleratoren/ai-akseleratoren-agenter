# Classroom-leksjoner — klar til copy-paste

Ett kurs: **Agentbiblioteket**. Leksjon 1 er kom-i-gang. Deretter én leksjon per agent, i denne rekkefølgen.

---

## SEKSJON: Start her

### Leksjon 1: Slik tar du i bruk en agent (SE DENNE FØRST)

_Legg videoen «Kom i gang» øverst i denne leksjonen, og ZIP-fila som vedlegg._

Velkommen til agentbiblioteket. Her ligger de faktiske agentene som driver
bedriften min hver dag, renset for mine nøkler og mine kundedata, klare til å
omskoleres til din bedrift.

**Fem steg — det er hele oppskriften:**

1. Last ned ZIP-fila i denne leksjonen og pakk den ut et sted du finner igjen.

2. Velg ÉN agent — ikke sytten. Les README-fila i den mappa først. Den forteller
   hva agenten gjør og hva du trenger for å kjøre den.

3. I ditt eget prosjekt lager du mappa `.claude/skills/` og legger agentens
   `SKILL.md` der, i en undermappe med agentens navn.
   Eksempel: `.claude/skills/referat/SKILL.md`

4. Ligger det en `.env.example` i agentmappa: kopier den til `.env` og fyll inn
   dine egne nøkler. **Legg `.env` i `.gitignore` FØR du committer noe.**

5. Åpne Claude Code i prosjektet og si navnet på agenten. Så starter den.

**Har du aldri gjort dette før?** Start med Referat-agenten eller Jocko. De
trenger ingen integrasjoner og ingen nøkler — du er i gang på et kvarter og ser
resultatet samme dag.

**Ikke start med Warren eller Ogilvy.** De er de kraftigste, men krever at du
kobler på systemene dine først. Ta dem i uke to.

**Sikkerhetsregelen du ikke kan hoppe over:** nøkler bor i `.env`, aldri i
`SKILL.md`, aldri i git. Legger du `.env` i `.gitignore` etter første commit,
ligger nøkkelen fortsatt i historikken selv om du sletter fila.

Står du fast: post i gruppa, eller ta med agenten på Labs på tirsdag.

---


### Leksjon 2: Referat-agenten — møtereferat som faktisk blir brukt

Referat er en Claude Code-agent som tar et møtetranskript og leverer tre ting:
et kort referat, en hvem-gjør-hva-liste med frister, og et ferdig utkast til
oppfølgingsmail. Alltid på norsk, uansett hvilket språk møtet gikk på.

**Problemet den løser:** Referatet blir skrevet av den som husker møtet best,
tre dager for sent, og oppgavene forsvinner. AI-sammendrag er raskere, men de
glatter over og finner på — «de ble sannsynligvis enige om…». Referat-agenten
gjør det motsatte: alt som er uklart i transkriptet merkes `[UKLART]` i stedet
for å gjettes.

**Hva agenten gjør:**
- Tar transkript limt inn, som filsti, eller hentet fra møteopptaks-verktøyet
- Referat på maks 10 linjer: hva ble diskutert, hva ble besluttet
- Hvem gjør hva, per person, med frist — og en egen «uavklart eier»-seksjon
- Utkast til oppfølgingsmail, klar til å sendes eller limes inn
- Regner om «på tirsdag» til faktisk dato ut fra møtedatoen

**Hva agenten ALDRI gjør:** finner på noe som ikke ble sagt, lager referat av
et AI-sammendrag uten å si fra, eller sender mailen uten at du har sagt «send».

**Du trenger:**
- Claude Code
- Et transkript — fra et møteopptaks-verktøy (Fireflies, Otter, Teams,
  Zoom-transkripsjon) eller bare limt inn tekst
- Eventuelt en e-postkanal eller CRM med API, hvis agenten skal kunne sende

**Kom i gang:**
1. Opprett `.claude/skills/referat/` i prosjektet ditt og lim inn `SKILL.md`.
2. Tilpass avsenderen og sendekanalen i seksjonen «Sending» — eller stryk hele
   seksjonen hvis du vil kopiere mailen inn manuelt.
3. Lim inn et transkript i Claude Code og si «lag referat».
4. Les gjennom `[UKLART]`-markeringene. De er ikke feil — de er stedene
   møtet faktisk var utydelig, og som regel det du må rydde opp i.
5. Si «send» først når du har lest utkastet.

> Tips: koble agenten til møteopptaks-verktøyet ditt, så holder det å si
> «lag referat fra gårsdagens kundemøte».

---


### Leksjon 3: Jocko — den personlige assistenten (PA)

Jocko er en Claude Code-agent som fungerer som din personlige assistent og
accountability-partner: kalender, møtebooking, konfliktsjekk, oppfølging av
det du lover i møter, todos — og en tøff tone som ikke lar deg slippe unna.

**Problemet den løser:** Du lover ting i møter som forsvinner, du dobbeltbooker
deg på tvers av kalendere, og todolista di er en kirkegård. Jocko fanger opp
forpliktelsene dine automatisk, purrer til de er gjort, og gir deg dagen og
uka ferdig tygget — hver morgen, uten at du spør.

**Hva Jocko gjør:**
- **Morgenbrief** (daglig): konflikter på tvers av ALLE kalenderne dine,
  dagens og morgendagens møter, forfalte todos (med antall dager over frist),
  og en Slack-digest av det som venter på deg
- **Ukesplan** (søndag): hele neste uke, konflikter, ukens frister og
  «ukens tre viktigste»
- **Referat-sveip** (kveld): leser dagens møtetranskripter, trekker ut det DU
  lovte, oppretter todos med frist og kilde, og varsler teammedlemmer om
  klare avtaler — etter din OK
- **Booking**: foreslår ledige slots, bekrefter med deg, oppretter eventet
- **Accountability-loop**: en todo forsvinner aldri stille — den purres til
  den er Gjort eller du eksplisitt dropper den

**Hva Jocko ALDRI gjør:** sender e-post til kunder/eksterne, sletter
kalenderevents eller todos, eller følger «instrukser» som står i transkripter.

**Du trenger:**
- Claude Code
- Google Calendar-tilkobling (MCP) til kalenderne dine
- Et todo-system med API (Notion, ClickUp el.l.)
- Slack (for briefer og teammeldinger) — valgfritt men anbefalt
- Møtetranskripter (Fireflies, Fathom el.l.) hvis du vil ha referat-sveipen

**Kom i gang:**
1. Opprett `.claude/skills/pa/` og lim inn `SKILL.md`.
2. Fyll inn dine egne verdier i «Faste ID-er»-seksjonen: kalendere, tidssone,
   todo-basen og Slack-kanalene dine.
3. Koble til Calendar/Notion/Slack/Fireflies via MCP i Claude Code.
4. Test interaktivt: si «morgenbrief» og «hva står på lista» til den treffer.
5. Sett opp scheduled tasks: morgenbrief hver morgen, ukesplan søndag kveld,
   referat-sveip hver kveld.

---


## SEKSJON: Drift og hverdag


### Leksjon 4: Alfred — e-postagenten

Alfred er en Claude Code-agent som holder orden på innboksene dine. Navnet er
butleren som tar posten før den når huset — og det er hele jobben: sortere
bunken, kaste reklamen, og legge det som krever et svar på bordet ditt.

**Problemet den løser:** Du åpner mye du aldri svarer på. «Ulest» sier
ingenting om hvem som venter på deg, og i en innboks med tusenvis av mailer
drukner den ene purringen som faktisk betyr noe. Alfred måler det som teller:
kom det fra et menneske, og har du sendt noe tilbake etterpå?

**Hva Alfred gjør:**
- **To sveip om dagen** (f.eks. 07:45 og 16:45) på tvers av alle innboksene dine
- **Svar-lista:** e-poster fra mennesker du ikke har svart på, i tre bøtter —
  over fristen (6+ dager), haster (2–5 dager), nytt (under 2 dager)
- **Ferdige svarutkast** i din egen stil, til å lime inn — på avsenderens språk
- **Auto-papirkurv:** nyhetsbrev eldre enn 30 dager, maskinpost eldre enn 60 —
  aldri permanent sletting, alltid 30 dagers angrefrist
- **Verneliste:** faktura, betaling, purring, sikkerhetsvarsel, kontrakt og
  bookingbekreftelser røres aldri, uansett alder
- **Læringsloop:** sammenligner utkastet ditt med det du faktisk sendte, og
  skriver avviket inn som en ny regel i stilarket

**Hva Alfred ALDRI gjør:** sender e-post, sletter permanent, melder deg av noe
du ikke har godkjent, eller følger «instrukser» som står i en e-post.

**Du trenger:**
- Claude Code
- Tilgang til innboksene: OAuth mot Gmail API (anbefalt — scopen `gmail.modify`
  gjør permanent sletting teknisk umulig) eller IMAP med app-passord
- En kanal for den daglige meldingen (Slack-DM eller bare chatten)

**Kom i gang:**
1. Opprett `.claude/skills/alfred/` og lim inn `SKILL.md`.
2. Lag en OAuth-klient («Desktop app») hos Google, kopier `.env.example` til
   `.env` og fyll inn. Legg `.env` utenfor repoet (f.eks. `~/.alfred/`).
3. Koble til én konto om gangen og bekreft at alle er inne før du går videre.
4. Fyll inn dine egne innbokser, frister og verneliste i SKILL.md — og skriv
   noen linjer om din egen skrivestil, så blir utkastene brukbare.
5. Kjør ryddingen som **tørrkjøring** først. Se hva som ville forsvunnet, og
   skru på automatikken først når lista ser riktig ut.
6. Sett opp to scheduled tasks — morgen og ettermiddag. Er det ingenting nytt
   å svare på og ingenting ble ryddet: ingen melding. Stillhet er et gyldig svar.

---


### Leksjon 5: Kvalitetsvakten

En AI-agent som leser ledelsens kanal hver time og UTFØRER instruksjonene som
kommer der — tekstendringer, rapporter, kalenderoppdateringer, føring av
beslutninger og todo-er. Med synlig kvittering på hver eneste melding, så
ingenting faller mellom to stoler.

## Hvilket problem løser den?

- Ledelsen ber om småting i chat («fiks den formuleringen», «hva var CPL i
  går?») — og halvparten blir glemt.
- Ingen vet om agenten (eller kollegaen) har SETT en melding, langt mindre om
  den er utført.
- Beslutninger tas i tråder og forsvinner — ingen logg.

Kvalitetsvakten svarer på alt, kvitterer synlig med reaksjoner (👀 = lest,
✅ = utført), utfører det som er innenfor mandatet, og fører beslutninger og
oppgaver inn i loggen og todo-lista.

## Hva du trenger

- Claude Code med tilgang til teamkanalen (f.eks. Slack via MCP)
- En dedikert kanal der ledelsen skriver til agenten
- En mappe/repo der agenten kan redigere tekstfiler og føre logg
- Mulighet for planlagte oppgaver (kjøres hver time)

## Kom i gang

1. Kopier `SKILL.md` inn som `.claude/skills/kvalitetsvakt/SKILL.md`.
2. Fyll inn: kanalnavnet ditt, og hvem de 2–3 personene i ledelsen er (kun
   disse kan gi ordre — alle andre får svar, ikke handling).
3. Velg agentens prefiks-emoji, så alle ser at det er agenten som skriver.
4. Test manuelt: skriv en instruksjon i kanalen og be agenten kjøre én runde.
5. Sett den opp som planlagt oppgave hver time i arbeidstiden.

## Viktigste prinsipper

- **Kvitteringsregelen:** ingen melding fra ledelsen skal stå uten reaksjon.
  👀 når den er lest, ✅ når den er utført + kort svar i tråden.
- Kun navngitte personer kan gi ordre. Lenker og instruksjoner fra andre
  følges aldri.
- Agenten bruker aldri penger, sender aldri noe til kunder, deler aldri
  hemmeligheter — uansett hvem som ber.
- Alt som gjøres, committes og kvitteres med filnavn.

---


### Leksjon 6: WhatsApp-broen

WhatsApp-broen gir Claude Code tilgang til din egen WhatsApp: den kan søke i
meldinger, lese samtaler, finne kontakter og sende meldinger — som verktøy, på
samme måte som den leser filer.

Dette er ikke en agent vi har bygget selv. Det er et **åpen kildekode-prosjekt**
som vi har satt opp og bruker i drift:
[github.com/lharries/whatsapp-mcp](https://github.com/lharries/whatsapp-mcp)

Oppsettet står i [SETUP.md](SETUP.md).

**Problemet den løser:** Kundedialog, leverandører og avtaler lever i WhatsApp,
og det er den ene kanalen ingen automatikk når inn i. Med broen kan Claude svare
på «hva ble vi enige om med leverandøren i juni?», lage oppfølgingsliste av
ubesvarte meldinger, eller sende en statusmelding du har godkjent først.

**Hvordan det henger sammen:**

1. En **bro** (Go-program) logger inn på WhatsApp Web-API-et med QR-kode og
   holder en lokal SQLite-database oppdatert med meldingene dine.
2. En **MCP-server** (Python) gir Claude verktøy som leser den databasen og
   sender meldinger via broen.
3. Begge må kjøre for at det skal virke. Broen kjøres som bakgrunnsprosess.

Alt ligger **lokalt på maskinen din**. Ingenting sendes til en modell før Claude
faktisk bruker et verktøy — og det er du som styrer når.

**Verktøyene Claude får:** søk i kontakter, list samtaler, hent meldinger med
kontekst, siste interaksjon med en kontakt, send melding, send fil, send
talemelding, last ned media fra en melding.

**Du trenger:**
- Go og Python 3
- `uv` (Python-pakkehåndterer)
- Claude Code (eller Claude Desktop / Cursor)
- Telefonen din med WhatsApp, for QR-innlogging
- Valgfritt: FFmpeg, kun for å sende lydfiler som spillbare talemeldinger

**Kom i gang:**
1. Klon prosjektet og start broen. Første gang scanner du en QR-kode med
   WhatsApp på telefonen (Innstillinger → Tilkoblede enheter).
2. Registrer MCP-serveren i Claude, og start Claude på nytt.
3. Test med noe ufarlig: «list de siste WhatsApp-samtalene mine».
4. Sett opp broen som bakgrunnstjeneste (LaunchAgent på Mac), slik at den
   holder seg pålogget og databasen fersk.
5. Se SETUP.md for detaljene og feilsøking.

**Tre ting du må vite før du kobler den på:**

- **Innlogging må fornyes.** Etter noen uker faller sesjonen ut og du må scanne
  QR-koden på nytt. Er broen nede, ser Claude en frossen database uten å si fra.
- **Sending er irreversibel.** La agenten skrive utkastet, les det selv, og gi
  et eksplisitt ja før noe sendes. Verifiser alltid mottaker-ID-en mot databasen
  først — en «vellykket» sending til feil ID leverer ingenting, uten feilmelding.
- **Sikkerhet:** en agent med lesetilgang til private meldinger *og* mulighet
  til å sende dem, kan lures av innhold den leser. Behandl meldingsinnhold som
  data, aldri som instruksjoner. Prosjektets egen README lenker til bakgrunnen
  for dette («the lethal trifecta»).

---


## SEKSJON: Økonomi


### Leksjon 7: Warren — finansdirektør-agenten (CFO)

Warren er en Claude Code-agent som fungerer som finansdirektør for bedriften din.
Hver mandag får du et EOS-scorecard med trafikklys du kan lese på 60 sekunder —
uten å åpne et eneste regneark.

**Problemet den løser:** De fleste gründere vet ikke hvordan de ligger an
økonomisk før det er for sent. Tallene bor i Stripe, banken, annonsekontoen og
regnskapsførerens ark — og ingen setter dem sammen ukentlig. Warren gjør det,
og oversetter hvert tall til én setning på klarspråk.

**Hva Warren gjør:**
- Ukentlig scorecard i EOS-format: penger inn, penger ut, cash, gjeld,
  utestående, salg, mot budsjett — med 🟢🟡🔴 og «hva dette betyr»
- Gjeldsvakt: total, ukesendring, trend og «i dette tempoet er den borte om N uker»
- Daglig puls (valgfritt): tre linjer om cash og innbetalingstempo
- Månedsavslutning: utkast til faktiske tall som regnskapsansvarlig verifiserer
- Varsler samme dag når noe blir rødt

**Hva Warren ALDRI gjør:** flytter penger, betaler noen, sender fakturaer eller
endrer regnskapet. Warren anbefaler — mennesker beslutter.

**Du trenger:**
- Claude Code
- Lesetilgang (API-nøkler) til der pengene dine bor, f.eks. Stripe og bankens API
- Eventuelt Meta-annonsekonto (for annonseforbruk) og Slack (for rapportene)
- En regnskapsansvarlig (deg selv eller en annen) som eier de manuelle tallene

**Kom i gang:**
1. Opprett mappa `.claude/skills/cfo/` i prosjektet ditt og lim inn `SKILL.md`.
2. Kopier `.env.example` til `.env` og fyll inn dine egne nøkler (aldri i git!).
3. Tilpass SKILL.md: dine ukemål, din valuta, navnet på din regnskapsansvarlige
   (som rolle) og hvilken Slack-kanal rapporten skal til.
4. Si «run the scorecard» til Claude Code — første gang bygger dere
   scorecardet og gjeldsregisteret sammen, som markdown-filer i repoet.
5. Sett opp en scheduled task søndag kveld, så ligger rapporten klar til
  mandagsmøtet.

---


### Leksjon 8: Luca — fakturaagenten (bokholder)

Luca er en Claude Code-agent som gjør det rutinemessige pengearbeidet:
får fakturaer ut døra, purrer på de som aldri kom tilbake, fører bilag og
holder kundereskontroen ryddig. Oppkalt etter Luca Pacioli, som skrev ned
dobbelt bokholderi i 1494.

**Problemet den løser:** Fakturaer som sendes for sent (eller aldri), purringer
ingen orker å skrive, og en haug gamle «ubetalte» fakturaer ingen vet om er
ekte. Det er der pengene lekker i små bedrifter — ikke i strategien.

**Hva Luca gjør:**
- Lager fakturautkast automatisk når et salg lukkes i CRM-et ditt eller en
  avdragsrad forfaller — og sender KUN etter et ja fra deg
- Ukentlig oversikt over hvem som skylder hva, med aldersbuckets
- Purreliste med ferdigskrevne purreutkast på kundens språk
  (vennlig ved 3 dager, saklig ved 14, ring ved 30, beslutning ved 90)
- Rydder gamle fakturapiler i batcher sammen med regnskapsansvarlig
- Trekker ut dato, leverandør, beløp og mva fra bilag til én tabell

**Hva Luca ALDRI gjør:** finner på beløp, sender uten godkjenning, gir
rabatter på egen hånd, flytter penger eller mailer kunder selv.

**Du trenger:**
- Claude Code
- Et faktureringssystem med API (f.eks. GoHighLevel, Fiken, eller lignende)
- Slack (eller annen kanal) der utkast kan vente på et ja
- En regnskapsansvarlig (deg selv eller en annen) som eier fasiten

**Kom i gang:**
1. Opprett `.claude/skills/faktura/` og lim inn `SKILL.md`.
2. Kopier `.env.example` til `.env` og legg inn API-nøkkelen til
   faktureringssystemet ditt (aldri i git).
3. Tilpass SKILL.md: hvor salgene dine kommer fra (pipeline/skjema), hvem som
   kan godkjenne, og hvilken kanal utkastene postes i.
4. Start med `oversikt` — få det ærlige bildet av hvem som skylder deg penger
   før du automatiserer noe som helst.
5. Når rytmen sitter: sett opp en daglig scheduled task som sveiper salg og
   forfall og legger dagens utkast klare til godkjenning.

---


## SEKSJON: Marked og salg


### Leksjon 9: North Star — markedssjef-agenten

En AI-agent som leder markedsarbeidet ditt mot ÉN nordstjerne-KPI: å fylle
pipelinen til hovedtilbudet ditt. Alt annet — annonser, webinarer, e-post,
lavterskeltilbud — er trapper som skal lede dit.

## Hvilket problem løser den?

- Markedsføring uten prioritering: alt føles like viktig, ingenting måles mot
  ett mål.
- Kampanjer lanseres i siste liten uten plan, godkjenning eller tekst-QA.
- Tall bor i hodene på folk. Avvik oppdages for sent.
- Ingen følger opp hva teamet lovte på ukemøtet.

North Star overvåker tallene daglig, fører markedskalender minst 4 uker frem,
purrer på frister — og anbefaler alltid, men beslutter aldri.

## Hva du trenger

- Claude Code installert
- Et sted tallene bor: CRM (pipeline/leads), annonsekonto, ev. betalingsdata
- En teamkanal (f.eks. Slack) der agenten kan varsle
- En mappe/repo for pulsrapporter, kalender og beslutningslogg

## Kom i gang

1. Kopier `SKILL.md` inn som `.claude/skills/north-star/SKILL.md` i prosjektet.
2. Definer nordstjernen din: hvilket tall er «nye kvalifiserte leads/uke» for
   hovedtilbudet ditt? Skriv det inn i skillen.
3. Fyll inn rollene: hvem beslutter (eier/driftsleder), hvem kvalitetssikrer
   tekst, hvem eier teknisk sporing.
4. Kjør første puls manuelt: «North Star, kjør daglig puls.» Juster kildene til
   dine egne script/API-er.
5. Når pulsen sitter: sett den opp som daglig planlagt oppgave, og legg til
   ukemøte-modusen på fast ukedag.

## Kjerneprinsippene

- Agenten **anbefaler — ledelsen beslutter**. Aldri pengebruk, utsendelser
  eller funnel-endringer på egen hånd.
- All kundevendt tekst kvalitetssikres av et menneske før publisering.
- Alt som lanseres skal ha stått i kalenderen først: utkast 7 dager før,
  godkjenning 4 dager før, teknisk test 2 dager før.
- Rapportering i EOS-scorecard-form: ett tall per linje, én eier, ukesmål,
  på/av sporet.

---


### Leksjon 10: Ogilvy — annonseagenten

En AI-agent som eier alt som bruker annonsebudsjett i bedriften din: bygger
kampanjer, skriver annonsetekst i DIN stemme, overvåker forbruk og rapporterer
ekte tall fra CRM-et — ikke fra pikselen.

## Hvilket problem løser den?

- Annonsetall fra Meta lyver: pikselen overrapporterer, og du tar beslutninger
  på feil grunnlag.
- Kampanjer blir stående og brenne penger etter at eventet er over.
- Annonsetekst skrives i hastverk, uten system, og publiseres uten kvalitetssjekk.
- Ingen sjekker hva konkurrentene faktisk kjører — og hvor lenge.

Ogilvy gjør dette til faste rutiner med klare regler, og rører ALDRI penger
uten at du sier ja.

## Hva du trenger

- Claude Code installert
- Meta Marketing API-token med tilgang til annonsekontoen din (kun lesing holder
  for analyse-modus)
- Tilgang til CRM-et ditt (f.eks. GoHighLevel) for å telle ekte leads
- En mappe/repo der agenten kan lagre annonseutkast og endringslogg

## Kom i gang

1. Kopier `SKILL.md` inn i prosjektet ditt som `.claude/skills/ogilvy/SKILL.md`.
2. Les gjennom og tilpass: sett inn navnet på CRM-et ditt, hvem som er
   beslutningstaker og hvem som kvalitetssikrer tekst.
3. Legg API-nøklene dine i en `.env`-fil i prosjektet (aldri i selve skillen).
4. Test med en ren leseoppgave først: «Ogilvy, gi meg analyse-modus på siste
   7 dager.»
5. Når du stoler på tallene: ta i bruk bygg- og tekst-modus. Husk at alt
   opprettes PAUSET — du aktiverer selv.

## De fire reglene som aldri bendes

1. Ingen dato i annonser — datoen bor på landingssiden.
2. Aldri trafikk til en side som ikke er bekreftet klar.
3. CPL og salg rapporteres fra CRM-et, aldri fra pikselen.
4. Pause er alltid lov. Aktivering koster penger og krever ditt eksplisitte ja.

---


### Leksjon 11: Annonse-analytikeren

En AI-agent som graver seg gjennom 6–12 måneder med annonsedata og finner ut
hva som faktisk gir billige leads — plassering, format, målgruppe, ukedag,
klokkeslett, og hvor lenge en annonse holder før den slutter å virke.

## Hvilket problem løser den?

- Annonsekontoen din har ett år med svar i seg, men Ads Manager viser deg bare
  de siste sju dagene.
- «Kreativen er utslitt» er som regel gjetning. De fleste slår av ting som
  virker, og lar ting som ikke virker stå.
- Ingen sammenligner CPL på tvers av plassering, alder, kjønn og ukedag — det
  er for mye klikking.
- Vinnerannonser dukker opp igjen som «nye» annonser i nye kampanjer, så tallene
  spres og vinneren blir usynlig.

Analytikeren henter alt via Meta Marketing API, cacher det lokalt og skriver ett
langt tallgrunnlag du kan lese på 15 minutter. Den er **lesende** — den rører
aldri kontoen.

## Hva du trenger

- Claude Code og Python 3 (skriptene bruker kun standardbiblioteket)
- Meta Marketing API-token med **lesetilgang** til annonsekontoen din
- Annonsekonto-ID-en din (`act_…`)
- Litt tålmodighet første gang: full henting av 12 måneder tar noen minutter

## Kom i gang

1. Kopier `SKILL.md` inn som `.claude/skills/annonseanalyse/SKILL.md` i
   prosjektet ditt, og legg `hent_meta.py` og `analyse.py` i `scripts/`.
2. Kopier `.env.example` til `.env` og fyll inn token og konto-ID. Aldri i git.
3. Hent dataene: `python3 scripts/hent_meta.py` (cacher i `data/` —
   `--fersk` tvinger ny henting).
4. Kjør analysen: `python3 scripts/analyse.py 2025-08-01` — den skriver
   `rapporter/tallgrunnlag-….md`.
5. Be Claude lese tallgrunnlaget og skrive tolkningen i
   `rapporter/analyse-DATO.md`. Neste gang: les forrige analyse først, så du
   bygger videre i stedet for å gjenta deg selv.

## De fem tolkningsreglene

1. **Lang levetid = vinnersignal.** En annonse som har fått stå i måneder,
   tjener penger. Rapporter langtidskjørere separat fra ferske tester.
2. **Skill kreativ fra adsett.** Kreativer slites ofte ikke i det hele tatt,
   mens adsettet eldes. Da er det adsettet som skal byttes, ikke bildet.
3. **Pikseltall er relative, ikke sannhet.** Si alltid hvilken slice du målte
   (hvilken konto, hvilket vindu, hvilket event). Salg hentes fra CRM-et.
4. **Epler mot epler.** Samme funnel, samme land, samme periode. Aldri to
   ulike produkter i samme tabell.
5. **Én kreativ kan hete fem ting.** Slå sammen på video-ID eller tekst-hash
   før du kårer vinnere — ellers deler du vinneren i fem tapere.

---


### Leksjon 12: Copy-maskinen — kundetekst uten oppspinn

Copy-maskinen er en Claude Code-agent som skriver annonser, e-poster og
landingsside-tekst i kundens egen stemme — og som ikke får lov til å dikte.
Den henter hver historie, hvert sitat og hvert tall fra en historiebank du
har fylt med ting som faktisk har skjedd.

**Problemet den løser:** AI skriver kjapt og skriver generisk. Den fyller
tomrommet der en ekte historie skulle stått med varm, tom empati («mange
kjenner seg igjen i dette»), og den finner på kundehistorier når den mangler
input. Resultatet er tekst som kunne stått i hvilken som helst trakt — og som
kunden må rette hver gang. Copy-maskinen snur det: mangler den råstoff,
stopper den og ber om det i stedet for å fylle på.

**Hva agenten gjør:**
- Skriver annonser, e-postsekvenser og sidetekst i kundens tone
- Krever minst én ekte scene fra historiebanken i hver tekst
- Kjører en generisk-test på hele settet før du får se det (bytt-ut-test,
  skjelett-test, frase-test)
- Sjekker at vinkelen faktisk er innenfor det kunden leverer, før den skriver
- Logger tilbakemelding tilbake i kontekstfila, så hver runde blir skarpere

**Hva agenten ALDRI gjør:** finner på en historie, «forbedrer» en detalj,
gjenbruker samme frase i hele settet, eller publiserer selv. Kunden godkjenner.

**Du trenger:**
- Claude Code
- Råstoff fra kunden: stemmenotater, transkripsjoner fra webinar/Q&A, DM-er,
  kundemail — kundens egne ord, ikke det som allerede er publisert
- 30–60 minutter til å fylle historiebanken første gang
- Én person hos kunden som eier faglige grenser og sier ja/nei

**Kom i gang:**
1. Opprett `.claude/skills/copy-maskin/` i prosjektet ditt og lim inn `SKILL.md`.
2. Del `HISTORIEBANK-MAL.md` i to filer i prosjektmappa — `HISTORIEBANK.md`
   og `KONTEKST.md` — og fyll ut det du allerede vet: hva kunden IKKE vil si,
   hvilke påstander som er lov, hvordan kunden faktisk snakker.
3. Be kunden om ett 30-minutters stemmenotat: «fortell om de tre siste
   kundene du snakket med, og hva som overrasket deg». Transkriber det og
   høst historiene inn i banken, med kilde og dato.
4. Si «skriv fem annonser om [vinkel]» til Claude Code. Får du «jeg mangler
   ekte materiale til denne vinkelen» — det er agenten som gjør jobben sin.
5. Kunden retter. Logg hver rettelse i `KONTEKST.md` under «ikke bruk» eller
   «stemmemarkører». Det er der maskinen blir god.

> Historiebanken er hele poenget. En tom bank gir generisk copy uansett hvor
> god prompten er.

---


### Leksjon 13: Halbert — nyhetsbrev-agenten

Halbert er en Claude Code-agent som skriver ett nyhetsbrev i uka til lista di.
Den finner råstoffet selv i det du faktisk har gjort denne uka, stiller deg
tre–fem spørsmål, og leverer et ferdig brev til godkjenning.

**Problemet den løser:** Nyhetsbrevet er den billigste kanalen du har, og det
som først ryker når uka blir travel. Grunnen er sjelden skrivingen — det er at
du ikke vet hva brevet skal handle om. Halbert løser det med en fireukers
temarotasjon: du slipper å finne på et tema, du svarer bare på spørsmål.

**Hva Halbert gjør:**
- Regner ut hvilken uke det er og hvilket tema som står for tur
- Henter råstoff selv: git-logg, møtereferater, tall som har flyttet seg,
  dokumenterte kundesitater
- Intervjuer deg med maks fem konkrete spørsmål (aldri «hva har skjedd?»)
- Skriver brevet med historie først, én idé, og én call to action
- Sjekker mot tidligere brev at samme historie ikke går to ganger

**Fireukers-rotasjonen:** lær bort noe konkret → to kundehistorier med tall →
hva som skjer i livene deres → noe dere prøver for første gang.

**Hva Halbert ALDRI gjør:** sender uten at et menneske har sagt ja, dikter opp
et kundesitat, eller lager et salgsbrev med tre CTA-er.

**Du trenger:**
- Claude Code
- En e-postliste og et sted å sende fra (CRM, e-postverktøy)
- Et repo eller en mappe der arbeidet ditt legger igjen spor (git-logg,
  referater, tall) — det er råstoffet
- Én person som kvalitetssikrer før utsending (gjerne ikke deg selv)

**Kom i gang:**
1. Opprett `.claude/skills/nyhetsbrev/` i prosjektet ditt og lim inn `SKILL.md`.
2. Tilpass rotasjonstabellen: fire temaer som passer din bedrift, og hvem som
   intervjues for hvert tema.
3. Lag `innhold/`-mappa der brevene lagres, og skriv ned stilreglene dine i
   `EPOST-STIL.md` (tone, lengde, luft mellom avsnitt, signatur).
4. Si «skriv ukens brev» til Claude Code. Svar på spørsmålene den stiller.
5. La kvalitetssikreren lese, og send selv. Etter tre–fire uker kan du legge
   inn en scheduled task som starter jobben på fast dag.

---


### Leksjon 14: Rubin — innholdsagenten

Rubin er en Claude Code-agent som lager ukens innhold av det du faktisk har
bygget. Én sak inn, to leveranser ut: én post til medlemsgruppa eller
LinkedIn, og ett videomanus. Du limer inn og spiller inn — Rubin poster aldri.

**Problemet den løser:** Du gjør interessante ting hver uke, men innholdet
blir aldri laget, fordi «hva skal jeg poste?» er en større terskel enn selve
skrivingen. Rubin snur på det: den leser git-loggen og arbeidet ditt, foreslår
tre saker, og intervjuer deg om det som mangler. Ingenting oppdiktet — alt
peker tilbake på noe du faktisk gjorde.

**Hva Rubin gjør:**
- Henter råstoff fra git-historikk og arbeidsloggen din
- Foreslår tre saker og lar deg velge én
- Stiller fire faste spørsmål (inkludert «hva gikk galt?» — den beste delen)
- Skriver én ferdig post og ett videomanus av samme sak
- Holder en idébank så ingen vinkel gjenbrukes før det har gått tre måneder
- Modus 2: fireukers innholdsplan. Modus 3: gjenbruk av webinar/opptak til
  én video, tre poster og 5–8 nye idéer

**Hva Rubin ALDRI gjør:** poster selv, dikter opp tall eller resultater, eller
sender kundedata ut av prosjektet.

**Du trenger:**
- Claude Code
- Et repo eller en mappe der arbeidet ditt legger igjen spor (git-logg)
- Et sted å publisere: medlemsgruppe (Skool, Circle, Facebook), LinkedIn,
  YouTube — Rubin er kanaluavhengig
- 15 minutter i uka til å svare på fire spørsmål

**Kom i gang:**
1. Opprett `.claude/skills/innhold/` i prosjektet ditt og lim inn `SKILL.md`.
2. Lag `innhold/IDEBANK.md` — en liste over hva som skal lages og hva som er
   brukt, med dato og lenke.
3. Skriv ned stemmereglene dine i SKILL.md (§ Ufravikelige regler): hvordan du
   snakker, hva du aldri sier, hvor mye du selger.
4. Si «ukens innhold» til Claude Code. Velg én av de tre foreslåtte sakene og
   svar på spørsmålene.
5. Lim inn posten selv, spill inn videoen, og kryss av i idébanken. Svar på
   hver kommentar innen et døgn — det er der livet i gruppa kommer fra.

---


### Leksjon 15: Zoom-leads-agenten — ringeliste rett etter webinaret

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

---


### Leksjon 16: Webinar-telleren

En AI-agent som hver dag teller påmeldte til neste webinar, sammenligner mot
annonseforbruket, og varsler deg med en kort, skannbar rapport. Med på kjøpet:
en tagg-vakt (Python) som fanger opp påmeldinger som havner i feil
e-postsekvens i CRM-et.

## Hvilket problem løser den?

- «Hvor mange er påmeldt egentlig?» — Meta sier ett tall, CRM-et et annet, og
  ingen vet fasiten.
- Gjenbrukte påmeldingsskjemaer tagger folk inn i FORRIGE webinars sekvens —
  de får bekreftelse med død møtelenke uten at noen merker det.
- Du oppdager for sent at annonsene gir dyre påmeldinger.

Telleren rapporterer daglig: totalt påmeldte, nye siste døgn, CPL per
annonsesett — og tagg-vakta retter feiltaggede påmeldinger før sekvensen
rekker å gjøre skade.

## Hva du trenger

- Claude Code og Python 3 (kun standardbibliotek + curl)
- CRM med API-tilgang (oppskriften bruker GoHighLevel — tilpass endepunktene
  om du bruker noe annet)
- Meta Marketing API-token (lesing) hvis du kjører annonser
- Ev. webinar-plattformens API (Zoom e.l.) som fasit-kilde

## Kom i gang

1. Kopier mappen inn i prosjektet ditt, `SKILL.md` til
   `.claude/skills/webinar-teller/SKILL.md`.
2. Kopier `.env.example` til `.env` og fyll inn nøkler, skjema-ID og taggene
   dine.
3. Test telleren manuelt: «Kjør webinar-telleren.» Sjekk at tallene stemmer
   med det du ser i CRM-et.
4. Trenger du tagg-vakta: kjør `python3 webinar_vakt.py` (tørrkjøring — rører
   ingenting) og deretter med `--fiks` når du ser at den finner de riktige.
5. Sett begge opp som planlagte oppgaver (telleren daglig, vakta oftere i
   dagene før webinaret).

## Viktigste prinsipper

- Påmeldingssiden er eneste fasit for dato — aldri stol på at datoen i en
  oppgavefil er fersk.
- CRM-tallet er fasit for påmeldinger; Meta-pikselen brukes bare som relativ
  pekepinn.
- Filtrer alltid bort test- og interne påmeldinger før du rapporterer.
- Telleren leser og rapporterer — den endrer aldri annonser eller kontakter.

---


### Leksjon 17: Sully — funnelvakten

Sully er en Claude Code-agent som hver morgen går gjennom webinarfunnelene dine
slik en lead faktisk møter dem: den åpner sidene i en ekte nettleser, leser det
som står der, og sammenligner mot en kontrakt du har skrevet på forhånd.

Oppkalt etter pilot Chesley Sullenberger: sjekklista kjøres likt hver gang,
uansett hvor kjedelig den er.

**Problemet den løser:** Funneler dør stille. Datoen på påmeldingssiden gikk ut
i går mens annonsene fortsatt sender trafikk. Pikselen ble slettet i en
redigering ingen husker. Opptakssiden viser forrige måneds webinar. Ingen
feilmelding, ingen alarm — bare påmeldinger som forsvinner. Målet er å finne
feilen før kunden gjør det.

**Hva Sully sjekker hver dag:**
- Laster sidene i det hele tatt, og er det bygget i verktøyet du tror?
- **Fyrer** Meta-pikselen faktisk — ikke bare at koden finnes — og er det riktig piksel-ID?
- Står det en gyldig, fremtidig dato på påmeldingssiden? Er den passert uten erstatning?
- Bryter sidene innholdsreglene (f.eks. opptak nevnt på en påmeldingsside)?
- Har takkesiden kalenderlenke, og ber den folk finne bekreftelsesmailen, sjekke spam og SVARE?
- Har teksten endret seg siden den ble godkjent?
- Står det forbudte påstander på siden («garantert», «risikofritt»)?
- Finnes alle sidene traktformen din krever?
- Lever podcast-/lydlenkene som sendes på SMS fortsatt?
- Endret opptakssiden seg etter siste webinar, eller ligger forrige opptak der?
- Ble annonsene skrudd av ved webinarstart, og kom ny dato inn raskt nok?

**Hva Sully ALDRI gjør:** retter noe selv. Den sier fra. Mennesker fikser.

**Du trenger:**
- Claude Code, Python 3 og Playwright med Chromium (`playwright install chromium`)
- URL-ene til sidene i funnelen(e) dine
- Piksel-ID og eventuelt annonsekonto-ID for hver funnel
- Valgfritt: et sted rapporten skal lande (Slack) og en scheduled task/cron

**Kom i gang:**
1. Lag mappa `.claude/skills/funnelvakt/` i prosjektet ditt og lim inn `SKILL.md`.
2. Lag `funneler/<navn>/funnel.yaml` fra malen i SKILL.md — én per funnel. Dette
   er fasiten. Uten en definisjon av «riktig» kan ingenting sjekkes.
3. Felt du ikke har svar på ennå: la stå tomme. Vakten hopper over dem og sier
   at de mangler, i stedet for å gjette.
4. Si «kjør funnelvakten» til Claude Code. Første kjøring bygger skriptet og
   skriver `rapporter/vakt-DATO.md`.
5. Sett opp en scheduled task hver morgen. La kjøringen gi exit-kode 1 når det
   finnes røde funn — det er signalet cron varsler på, ikke en feil.

**To leseregler du må kunne før første rapport:**

- **Grått er ikke grønt.** En funnel uten URL-er i kontrakten er *uovervåket*,
  ikke frisk. Fravær av funn betyr bare at ingenting ble sjekket.
- **Tell årsaker, ikke linjer.** Én utløpt dato gir flere røde linjer om samme
  hendelse. Grupper på årsak før du teller.

---


## SEKSJON: Fordi det går an


### Leksjon 18: Wenger — fantasy-manageren

Wenger er en Claude Code-agent som styrer Fantasy Premier League-laget ditt:
bygger tropp, velger kaptein, regner ut om et bytte lønner seg, sveiper
skadenyheter før hver deadline og analyserer minilligaen du er med i.

Oppkalt etter en manager som var økonom før han var trener, bygde lag over år og
ikke kjøpte panikkløsninger i januar.

**Hvorfor denne er med:** den løser ingen forretningsoppgave. Den er her for å
vise at en agent kan brukes til hva som helst — og fordi fantasy er en uvanlig
god måte å lære agentbygging på. Du får ferske data hver uke, et fasitsvar hver
runde, og en helt tydelig måling på om modellen din er bedre enn magefølelsen.
Alt du lærer her — hente API-data, bygge en modell, skrive en beslutningsregel,
rapportere kort — er nøyaktig det samme du gjør i en agent som teller kroner.

**Hva Wenger gjør:**
- Bygger egne angreps- og forsvarsratinger per lag i stedet for å bruke spillets
  håndsatte vanskelighetstall (som ikke skiller «tungt å score mot» fra «tungt å
  holde nullen mot» — to helt forskjellige spørsmål)
- Regner forventede poeng per spiller, med poengsystemet **lest ut av API-et**,
  ikke fra hukommelsen
- Optimerer troppen på det beste lovlige ellevern troppen kan stille over seks
  runder, ikke på summen av 15 spillere — det er den eneste målfunksjonen som gir
  riktig svar på hva en benkespiller er verdt
- Sveiper skader og nyheter, med en streng kilderangering
- Regner **effektivt eierskap i din liga**, ikke globalt, og setter modus etter
  hvor langt bak du ligger
- Skriver et dashboard og kan varsle i Slack før deadline

**Du trenger:**
- Claude Code og Python 3.9 (ingen andre avhengigheter — alt er standardbibliotek,
  så agenten kan kjøre fra cron på en naken maskin)
- Ditt eget lag-ID og ID-en til minilligaen din (begge står i URL-ene når du er
  innlogget)
- En innloggingscookie fra nettleseren — kun nødvendig for å lese ditt eget lag
  og gjennomføre bytter. Uten cookie fungerer alt annet.

**Kom i gang:**
1. Lag mappa `.claude/skills/wenger/` i prosjektet ditt og lim inn `SKILL.md`.
2. Kopier `.env.example` til `.env` og fyll inn lag-ID og liga-ID.
   Aldri i git — cookien er en innlogging.
3. Skriv din egen `WENGER.md`: hva du faktisk konkurrerer om. Premiestrukturen i
   din liga avgjør oppførselen, og den er ikke lik noen andres.
4. Si «kjør runden» til Claude Code. Den henter data, setter laget, foreslår
   kaptein og bytter, og skriver dashboardet.
5. Sett en scheduled task torsdag, så ligger briefen klar før deadline.

**Reglene som betyr mest:**

- **Vinn ligaen, ikke maksimer poeng.** To forskjellige oppgaver. Ligger du foran,
  er varians fienden. Ligger du bak, er varians eneste vei tilbake.
- **Gjør ingenting som standard.** Et bytte skal betale seg over seks runder.
  Et poengtrekk på fire krever minst seks poengs gevinst.
- **Ingen bytter før fredagens pressekonferanser.** Tall fra tirsdag kan være
  verdiløse fredag ettermiddag.
- **Modellen er et estimat.** Den vet ikke at en spiller mistet plassen fordi
  treneren var sur på ham. Det er derfor nyhetssveipen finnes.

---

---

## SEKSJON: Nye agenter (september)

### Leksjon: Thelma — videoannonser fra din egen stemme

Du snakker inn tretti sekunder på mobilen. Thelma transkriberer det du sa, lager
videoklipp som passer hvert ord, legger dem der ordene faller, og skriver hele
prosjektet inn i CapCut — ferdig lagt ut på tidslinja.

Hun er oppkalt etter Thelma Schoonmaker, som har klippet hver Scorsese-film
siden Raging Bull og sier at hun klipper med ørene, ikke med øynene. Det er
hele metoden: stemmen først, bildene etterpå.

**Du trenger:** Claude Code, en fal.ai-konto med litt saldo, CapCut, og repoet
VectCutAPI klonet til `~/capcutapi`.

**Hva det koster:** seks cent per sekund video. En hel annonse med atten kutt
lander på rundt seks dollar.

**To feller jeg gikk i, så du slipper:** CapCut må være helt avsluttet med ⌘Q
før prosjektet leveres, ellers overskriver den alt. Og prosjekter med tekstspor
nekter å åpne i CapCut International — legg teksten på med auto-teksting
etterpå i stedet.

Mappa heter `thelma-videoklipper`.

---

### Leksjon: Medlemsvakten — hvem betaler, og hvem har egentlig tilgang

Betalingen skjer i Stripe. Tilgangen gis manuelt i Skool. Det finnes ingen
kobling mellom dem, så det lekker begge veier samtidig.

Første gang jeg kjørte denne på mitt eget medlemskap fant den 26 som betalte
uten å ha tilgang. Noen hadde betalt for et helt år.

Agenten deler medlemmene i fire bunker og kjører et vennlig påminnelsesløp ved
manglende betaling — dag 1, 7, 14 og 21. Den fjerner aldri noen selv.

**Du trenger:** en Stripe-nøkkel med lesetilgang, og medlemslista eksportert fra
Skool. Husk at «aktiv» er utledet, ikke hentet — les avsnittet om det i README.

Mappa heter `medlemsvakten`.

---

### Leksjon: Skool-redaktøren — fellesskapet som ikke dør

Fem innlegg i uka etter en rytme der hvert innlegg mater det neste: mandag viser
du noe du har bygget, fredag får de et oppdrag, onsdag deler de hva de fikk til.

Et community dør av at eieren poster og ingen svarer. Grunnen er nesten alltid
at innleggene er til å beundre, ikke til å svare på. Agenten snur det.

Den henter råstoff fra git-loggen din — altså det du faktisk gjorde forrige uke
— og legger utkastet ferdig i editoren. Du trykker POST.

Mappa heter `skool-redaktoren`.

---

### Leksjon: Kursopptak-agenten — Zoom inn, ferdig leksjon ut

Henter opptak, chat og transkript fra sendingen din og pakker det som en
leksjon du kan lime rett inn her i Classroom.

Den tar også vare på det de fleste mister: de siste ti minuttene av chatten,
der folk melder interesse for det du selger.

**Én advarsel:** ikke bruk Zooms eget transkript på norsk. ASR-en står på
engelsk og gjør norsk tale til vrøvl — «Claude Code» blir «CloudKord». Kjør
lydfila gjennom noe som kan norsk i stedet.

Mappa heter `kursopptak-agenten`.

---

### Leksjon: Stemme — diktert tekst inn, ferdig tekst ut

Den enkleste agenten i biblioteket, og den jeg bruker mest selv.

Du dikterer på mobilen, limer inn, og får tilbake en ryddet versjon i riktig
format — e-post, notat, innlegg eller melding. Den kjenner igjen sjangeren selv.

Det den ikke gjør, er å skrive om tonen din. En vanlig chatbot gir deg teksten
tilbake i sitt eget språk, med høflighetsfraser du ikke sa. Denne fjerner «eh»
og gjentakelser, og lar resten stå.

**Start her hvis du aldri har satt opp en agent før.** Ingen nøkler, ingen
integrasjoner, resultat på fem minutter.

Mappa heter `stemme-agenten`.
