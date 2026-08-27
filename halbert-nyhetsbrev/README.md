# Halbert — nyhetsbrev-agenten

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
