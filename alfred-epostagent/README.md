# Alfred — e-postagenten

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
