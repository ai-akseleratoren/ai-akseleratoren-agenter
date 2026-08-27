# WhatsApp-broen

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
