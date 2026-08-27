# Luca — fakturaagenten (bokholder)

Luca er en Claude Code-agent som gjør det rutinemessige pengearbeidet:
får fakturaer ut døra, purrer på de som aldri kom tilbake, fører bilag og
holder kundereskontroen ryddig. Oppkalt etter Luca Pacioli, som skrev ned
dobbelt bokholderi i 1494.

**Problemet den løser:** Fakturaer som sendes for sent (eller aldri), purringer
ingen orker å skrive, og en haug gamle «ubetalte» fakturaer ingen vet om er
ekte. Det er der pengene lekker i små bedrifter — ikke i strategien.

**Hva Luca gjør:**
- Lager fakturautkast automatisk når et salg lukkes i CRM-et ditt eller en
  avdragsrad forfaller — og sender KUN etter et ja fra deg
- Ukentlig oversikt over hvem som skylder hva, med aldersbuckets
- Purreliste med ferdigskrevne purreutkast på kundens språk
  (vennlig ved 3 dager, saklig ved 14, ring ved 30, beslutning ved 90)
- Rydder gamle fakturapiler i batcher sammen med regnskapsansvarlig
- Trekker ut dato, leverandør, beløp og mva fra bilag til én tabell

**Hva Luca ALDRI gjør:** finner på beløp, sender uten godkjenning, gir
rabatter på egen hånd, flytter penger eller mailer kunder selv.

**Du trenger:**
- Claude Code
- Et faktureringssystem med API (f.eks. GoHighLevel, Fiken, eller lignende)
- Slack (eller annen kanal) der utkast kan vente på et ja
- En regnskapsansvarlig (deg selv eller en annen) som eier fasiten

**Kom i gang:**
1. Opprett `.claude/skills/faktura/` og lim inn `SKILL.md`.
2. Kopier `.env.example` til `.env` og legg inn API-nøkkelen til
   faktureringssystemet ditt (aldri i git).
3. Tilpass SKILL.md: hvor salgene dine kommer fra (pipeline/skjema), hvem som
   kan godkjenne, og hvilken kanal utkastene postes i.
4. Start med `oversikt` — få det ærlige bildet av hvem som skylder deg penger
   før du automatiserer noe som helst.
5. Når rytmen sitter: sett opp en daglig scheduled task som sveiper salg og
   forfall og legger dagens utkast klare til godkjenning.
