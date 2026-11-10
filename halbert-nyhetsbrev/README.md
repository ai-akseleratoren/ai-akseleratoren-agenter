# Halbert — nyhetsbrev-agenten

Halbert er en Claude Code-agent som skriver ett nyhetsbrev i uka til lista di.
Den finner råstoffet selv i det du faktisk har gjort denne uka, stiller deg
tre–fem spørsmål på mandag, og legger et ferdig brev til godkjenning på onsdag.

**Problemet den løser:** Nyhetsbrevet er den billigste kanalen du har, og det
som først ryker når uka blir travel. Grunnen er sjelden skrivingen. Det er at
du ikke vet hva brevet skal handle om, og at ingen husker å starte. Halbert
løser begge: en fireukers temarotasjon velger temaet, og en fast ukesrytme
starter jobben for deg.

**Hva Halbert gjør:**
- Regner ut hvilken uke det er og hvilket tema som står for tur
- **Mandag:** henter råstoff selv (git-logg, møtereferater, tall som har
  flyttet seg, dokumenterte kundesitater) og stiller maks fem konkrete
  spørsmål i én melding i teamkanalen
- **Onsdag:** leser svarene i tråden og legger utkastet der: emnefelt,
  forhåndsvisning, brødtekst og én CTA, klar for kvalitetssikreren
- Purrer én gang hvis ingen har svart, og skriver ikke før svarene finnes
- Lagrer hvert brev, så samme historie ikke går to ganger

**Fireukers-rotasjonen:** lær bort noe konkret → to kundehistorier med tall →
hva som skjer i livene deres → noe dere prøver for første gang.

**Hva Halbert ALDRI gjør:** sender til lista, dikter opp et kundesitat, setter
dato i emnefeltet, eller lager et salgsbrev med tre CTA-er.

**Du trenger:**
- Claude Code
- En e-postliste og et sted å sende fra (CRM, e-postverktøy)
- En teamkanal (Slack eller lignende) der intervjuet og utkastet kan bo
- Et repo eller en mappe der arbeidet ditt legger igjen spor (git-logg,
  referater, tall). Det er råstoffet
- Én person som kvalitetssikrer før utsending (gjerne ikke deg selv)

**Kom i gang:**
1. Opprett `.claude/skills/nyhetsbrev/` i prosjektet ditt og lim inn `SKILL.md`.
2. Tilpass rotasjonstabellen: fire temaer som passer din bedrift, og hvem som
   intervjues for hvert tema.
3. Lag `innhold/nyhetsbrev/` der brevene lagres, og skriv ned stilreglene dine
   i `EPOST-STIL.md` (tone, lengde, luft mellom avsnitt, signatur).
4. Svar på de fem åpne spørsmålene nederst i SKILL.md (liste, dag, språk, hvem
   sender, hva med folk midt i en sekvens).
5. Si «halbert, mandagsintervju» til Claude Code. Svar på spørsmålene. Si
   «halbert, skriv utkastet» på onsdag.
6. Når to–tre uker har gått fint: legg inn to planlagte jobber, mandag og
   onsdag kl. 10, så starter Halbert av seg selv.
