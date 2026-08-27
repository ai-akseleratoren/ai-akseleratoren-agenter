# Wenger — fantasy-manageren

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
