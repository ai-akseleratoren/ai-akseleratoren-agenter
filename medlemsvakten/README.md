# Medlemsvakten — hvem betaler, og hvem har egentlig tilgang

Medlemsvakten avstemmer to lister som ingen systemer holder i synk av seg selv:
hvem som betaler, og hvem som har tilgang til fellesskapet ditt.

**Problemet den løser:** Betalingen skjer i Stripe. Tilgangen gis manuelt i
Skool. Det finnes ingen kobling mellom dem, så det lekker begge veier samtidig —
folk betaler uten å komme inn, og folk slutter å betale uten å komme ut.

Første gang vi kjørte denne på vårt eget medlemskap, fant vi 26 som betalte uten
å ha tilgang. Noen av dem hadde betalt for et helt år.

**Hva agenten gjør:**
- Henter betalinger fra Stripe og medlemslista fra Skool, og matcher dem
- Deler medlemmene i fire bunker: betaler uten tilgang, lapset med tilgang,
  betaler fra en annen e-post, og tilgang uten betaling
- Matcher også på navn, så folk som betaler fra jobbmailen og logger inn med
  privatmailen ikke havner i feil bunke
- Kjører et vennlig påminnelsesløp ved manglende betaling: dag 1, 7, 14 og 21

**Hva agenten ALDRI gjør:** fjerner noen fra gruppa på egen hånd, eller sender
en betalingspåminnelse uten at du har sagt ja til akkurat den utsendingen. En
feilaktig utkastelse av et betalende medlem er mye dyrere enn en dags
forsinkelse.

**Du trenger:**
- Claude Code
- En Stripe-nøkkel med lesetilgang til charges og customers
- Medlemslista eksportert fra Skool (Members → Export — den må hentes manuelt,
  Skool sender en kode på e-post)

**Kom i gang:**
1. Opprett `.claude/skills/medlemsvakt/` og lim inn `SKILL.md`.
2. Legg `medlemsvakt.py` i prosjektet ditt, og sett `INTERNT_DOMENE` øverst i
   fila til ditt eget domene — de kontoene foreslås aldri fjernet.
3. Legg `STRIPE_API_KEY` i `.env`.
4. Eksporter medlemslista fra Skool og legg CSV-en ved siden av skriptet.
5. Kjør `python3 medlemsvakt.py --demo` for å se at alt virker, så
   `python3 medlemsvakt.py` for rapporten.

> Merk: «aktiv» er utledet, ikke hentet. Stripes restricted keys gir ikke
> tilgang til subscriptions, så skriptet regner en som aktiv hvis det finnes en
> betaling innen 45 dager (måned) eller 400 dager (år). En som nettopp har sagt
> opp, men betalte for tre uker siden, teller fortsatt som aktiv. Si det høyt
> når tallet brukes til noe som betyr noe.
