# Sully — funnelvakten

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
- **Virker påmeldingen faktisk?** Sully melder seg på som en testlead: sender
  skjemaet, sjekker takkesiden, CRM-taggen og at bekreftelsesmailen kommer fram
  med riktig dato. På webinardagen sjekker den at påminnelsene kommer. Pikselen
  blokkeres, så testen aldri teller som lead
- **Brenner annonsene penger uten påmeldinger?** Forbruk siste to timer og null
  leads gir rødt varsel med en gang
- Dekker siden det kunden faktisk godkjente, ikke bare det som sto der i går?

**Hva Sully ALDRI gjør:** retter noe selv, endrer annonser eller kundens
systemer, eller kontakter kunden. Den sier fra i en intern kanal, én gang per
endring. Mennesker fikser.

**Byggemodus:** har du mange kunder, er det tyngste å få fasiten inn. En egen
morgenjobb samler svar fra teamet, fyller kontraktene, purrer den som blokkerer
(maks hver tredje dag) og holder en tavle: X av N kunder overvåket.

**Du trenger:**
- Claude Code, Python 3 og Playwright med Chromium (`playwright install chromium`)
- URL-ene til sidene i funnelen(e) dine, helst i ett register (Notion, regneark)
  som er eneste kilde til sannhet
- Piksel-ID og eventuelt annonsekonto-ID for hver funnel
- Valgfritt: et sted rapporten skal lande (Slack) og en scheduled task/cron
- For registreringstesten: en innboks vakten kan lese (plussadresser), og
  lesetilgang til CRM-et

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
6. Slå på registreringstesten for én funnel: fyll `registreringstest` i
   kontrakten, kjør en tørrkjøring som bare finner feltene, og slå den på når
   selektorene treffer.

**To leseregler du må kunne før første rapport:**

- **Grått er ikke grønt.** En funnel uten URL-er i kontrakten er *uovervåket*,
  ikke frisk. Fravær av funn betyr bare at ingenting ble sjekket.
- **Tell årsaker, ikke linjer.** Én utløpt dato gir flere røde linjer om samme
  hendelse. Grupper på årsak før du teller.
