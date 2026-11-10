# Warren — finansdirektør-agenten (CFO)

Warren er en Claude Code-agent som fungerer som finansdirektør for bedriften din.
Hver mandag får du et EOS-scorecard med trafikklys du kan lese på 60 sekunder —
uten å åpne et eneste regneark.

**Problemet den løser:** De fleste gründere vet ikke hvordan de ligger an
økonomisk før det er for sent. Tallene bor i Stripe, banken, annonsekontoen og
regnskapsførerens ark — og ingen setter dem sammen ukentlig. Warren gjør det,
og oversetter hvert tall til én setning på klarspråk.

**Hva Warren gjør:**
- Ukentlig scorecard i EOS-format: penger inn, penger ut, cash, gjeld,
  utestående, salg, mot budsjett — med 🟢🟡🔴 og «hva dette betyr»
- Ukes-P&L på kontantbasis hver mandag: hva kom inn per produkt, hva gikk ut,
  og en nummerert liste med det ingen API ser (privatkort, lønn vs refusjon,
  opptjent lønn som ikke er utbetalt). Det er spørsmål til regnskapsføreren,
  ikke tall Warren finner på.
- Gjeldsvakt: total, ukesendring, trend og «i dette tempoet er den borte om N uker»
- Daglig puls (valgfritt): tre linjer om cash og innbetalingstempo
- Månedsavslutning: utkast til faktiske tall som regnskapsansvarlig verifiserer
- Varsler samme dag når noe blir rødt

**Hva Warren ALDRI gjør:** flytter penger, betaler noen, sender fakturaer eller
endrer regnskapet. Warren anbefaler. Mennesker beslutter.

**Lært på den harde måten (står i SKILL.md):** en billett på 1 249 kroner ble
bokført som 1 249 euro, og ukas «penger inn» ble mer enn doblet. Derfor: aldri
pålydende i fremmed valuta, les tilgjengelig og ventende saldo hver for seg, og
en aldersfordelt reskontro viser det som står igjen, aldri fakturabeløpet.

**Du trenger:**
- Claude Code
- Lesetilgang (API-nøkler) til der pengene dine bor, f.eks. Stripe og bankens API
- Eventuelt Meta-annonsekonto (for annonseforbruk) og Slack (for rapportene)
- En regnskapsansvarlig (deg selv eller en annen) som eier de manuelle tallene

**Kom i gang:**
1. Opprett mappa `.claude/skills/cfo/` i prosjektet ditt og lim inn `SKILL.md`.
2. Kopier `.env.example` til `.env` og fyll inn dine egne nøkler (aldri i git!).
3. Tilpass SKILL.md: dine ukemål, din valuta, navnet på din regnskapsansvarlige
   (som rolle) og hvilken Slack-kanal rapporten skal til.
4. Si «run the scorecard» til Claude Code — første gang bygger dere
   scorecardet og gjeldsregisteret sammen, som markdown-filer i repoet.
5. Sett opp en scheduled task søndag kveld, så ligger rapporten klar til
   mandagsmøtet.
6. Når formatet sitter: flytt Warren til en server som alltid er på, så
   rapporten kommer selv om laptopen er lukket. Kjør ham bare ett sted.
