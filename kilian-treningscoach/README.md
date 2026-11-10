# Kilian — treningscoachen

Kilian er en Claude Code-agent som holder deg i nakken fram mot et
treningsmål med dato. Den sier hva du skal trene i dag, logger det du
gjorde, purrer når du ikke har logget, og justerer planen etter det som
faktisk skjer.

Oppkalt etter en løper som vant på å gå opp, ikke bare på å kjøre ned.

**Hvorfor denne er med:** den løser ingen forretningsoppgave. Den er her
fordi den er en av de agentene som brukes hver eneste dag, og fordi den
viser mønsteret bedre enn noen: en plan i en fil, en logg som er
sannheten, en melding morgen og kveld, og en lærdomsfil der hver endring
får en dato og en grunn. Det er nøyaktig det samme du bygger i en agent
som følger opp kunder.

**Problemet den løser:** Treningsprogrammer dør i uke to. Ikke fordi
programmet er dårlig, men fordi ingen spør. Og når livet skjer (syk,
reise, regn), faller planen sammen i stedet for å bli justert.

**Hva agenten gjør:**
- Lager plan uke for uke fram mot målet ditt, med faser, lettuker og
  kontrollmålinger
- Sender dagens økt hver morgen, og spør hver kveld om du trente
- Henter økter fra treningsappen (f.eks. Strava) og sier fra når en rolig
  økt var for hard
- Gir minsteversjonen når du ikke orker, og hotellvarianten når du reiser
- Følger vekta som trend, ikke som dagsform
- Skriver styrkeprogrammet så en PT kan ta det i bruk, og en
  kostholdsplan til den som lager maten, uten dine personlige tall

**Hva agenten ALDRI gjør:** gjetter at en ulogget dag var hvile, endrer
planen uten å skrive hvorfor, moraliserer om mat, eller gir medisinske
råd. Smerte over to dager, brystsmerter eller svimmelhet: lege.

**Du trenger:**
- Claude Code og Python 3 (kun standardbiblioteket)
- Et mål med en dato: `<DITT MÅL OG DATO>`
- Valgfritt: pulsbelte eller -klokke, og en treningsapp-kobling (Strava har
  connector i Claude)
- Valgfritt: Slack, Telegram eller lignende for meldingene morgen og kveld

**Kom i gang:**
1. Lag mappa `.claude/skills/kilian/` i prosjektet ditt og legg `SKILL.md`
   der. Legg `cli.py` i prosjektrota.
2. Test: `python3 cli.py test`.
3. Si «kilian». Den intervjuer deg om mål, utgangspunkt, sted og utstyr,
   og lager planen, programmene og lærdomsfila.
4. Les planen og si fra hvis den er urealistisk. Første uke viser hva du
   faktisk tåler, og planen justeres etter det.
5. Sett opp to scheduled tasks, morgen og kveld (se «Daglig rutine» i
   SKILL.md). Kjør hver én gang med «Run now» så verktøyene er godkjent.
6. Svar på morgenmeldingen. Resten tar Kilian.

**Reglene som betyr mest:**

- **Ulogget er ulogget.** Ikke hvile.
- **Pulssoner fra aldersformel er ubrukelige.** Snakketest og et fast
  pulstak til makspulsen er målt. De fleste går altfor hardt på rolige økter.
- **Måldatoen flytter seg ikke.** Mister du en uke, kuttes en lettuke.
- **Alle endringer får dato og grunn i lærdomsfila.** Det er den som gjør
  at planen blir bedre, ikke bare lengre.
