# Copy-maskinen — kundetekst uten oppspinn

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
2. Kopier `HISTORIEBANK-MAL.md` inn i prosjektmappa som `HISTORIEBANK.md` og
   `KONTEKST.md`, og fyll ut det du allerede vet: hva kunden IKKE vil si,
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
