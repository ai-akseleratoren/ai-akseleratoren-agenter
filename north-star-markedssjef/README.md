# North Star — AI-assistenten for markedsteamet

En AI-agent som kjører markedsteamets uke mot ÉN nordstjerne: salg av
hovedtilbudet per uke. Den lager ukeplanen, følger opp fristene, sjekker alt før
det går live, kontrollerer annonsene hver morgen, og skriver én ærlig ukesrapport.

**Problemet den løser:**
- Markedsføring uten prioritering: alt føles like viktig, ingenting måles mot
  ett mål.
- Kampanjer lanseres i siste liten, og den som bygde siden er den eneste som har
  sett på den. Pikselen fyrer på feil hendelse, takkesiden mangler
  kalenderlenke, en annonse har gammel dato.
- Webinarmailen «gikk ut», men ingen sjekket at den faktisk ble levert.
- Ingen følger opp hva teamet lovte på ukemøtet.

**Hva North Star gjør:**
- **Prelansering-sjekkliste** på hver side, mail, SMS, sporing og annonse,
  sjekket mot den ekte siden og ekte data, ikke kildekoden
  (`prelansering-sjekkliste.md`)
- **Annonsekontroll hver morgen:** budsjett, CPL mot fire uker, forbruk uten
  resultat, hendelse mot side, slitasje, datoer i annonser. Stille når alt er fint
- **Utsendingssjekk rundt webinarer:** planlagt dagen før, levert 15 minutter
  etter, salgsoppfølging startet og kjøpere unntatt etterpå
- **Ukeplan og oppfølging:** beslutninger fra ukemøtet blir oppgaver med eier og
  baklengs frister (utkast −7, godkjenning −4, test −2)
- **Pulser og ukesrapport fra skript,** ikke fra modellen, så tallene er like og
  ekte hver gang. To kanaler: annonser for seg, resten for seg

**Hva North Star ALDRI gjør:** lanserer, sender til en liste, bruker
annonsepenger, endrer en annonse eller publiserer tekst som ikke er
kvalitetssikret. Den vurderer heller aldri enkeltpersoner i en åpen kanal. Funn
tas opp som et spørsmål til den som eier arbeidet, og de får 24 timer.

**Du trenger:**
- Claude Code
- Lesetilgang til der tallene bor: betalingsløsning, annonsekonto, CRM
- En oppgaveliste teamet faktisk bruker (Notion, ClickUp e.l.)
- To teamkanaler: én for annonser, én for resten av markedsføringen
- En mappe/repo for kalender, rapporter og beslutningslogg

**Kom i gang:**
1. Kopier `SKILL.md` og `prelansering-sjekkliste.md` til
   `.claude/skills/north-star/` i prosjektet.
2. Bestem nordstjernen: hvilket tall er «salg av hovedtilbudet per uke», og hvor
   leses det? Skriv det inn i skillen.
3. Fyll inn rollene: hvem beslutter, hvem kvalitetssikrer tekst, hvem eier
   sporingen. Fyll inn utsendingstaket ditt.
4. Kopier `.env.example` til `.env` og legg inn lesenøkler.
5. Start med prelansering-sjekken: «North Star, er påmeldingssiden klar til
   lansering?» Det gir mest igjen den første uka.
6. Lag pulsene som små skript som skriver ferdig tekst (tall rett fra API-ene),
   og kjør dem som planlagte jobber. La agenten gjøre det som krever skjønn:
   annonsekontrollen, oppfølgingen og ukesrapportens anbefaling.

## Kjerneprinsippene

- Agenten **anbefaler og sjekker — ledelsen beslutter**.
- Den som bygger, er aldri den eneste som sjekker.
- Tall fra skript og API-er, aldri fra modellens hode.
- Stille når alt er fint. Et varsel skal bety noe.
