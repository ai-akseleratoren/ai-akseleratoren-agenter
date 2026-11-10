# Luca — fakturaagenten (bokholder)

Luca er en Claude Code-agent som gjør det rutinemessige pengearbeidet:
får fakturaer ut døra, purrer på de som aldri kom tilbake, følger opp
kortbetalinger som feilet, fører bilag og holder kundereskontroen ryddig.
Oppkalt etter Luca Pacioli, som skrev ned dobbelt bokholderi i 1494.

**Problemet den løser:** Fakturaer som sendes for sent (eller aldri), purringer
ingen orker å skrive, kort som feiler uten at noen merker det, og en haug gamle
«ubetalte» fakturaer ingen vet om er ekte. Det er der pengene lekker i små
bedrifter. Ikke i strategien.

**Hva Luca gjør:**
- Lager fakturautkast når et salg lukkes i CRM-et, en avdragsrad forfaller
  eller en kunde ber om faktura i kassa di. Sender KUN etter et ja.
- Fakturaer forfaller dagen etter at de er sendt. Kort frist og fast
  purretrapp får pengene inn.
- Purretrapp med fire sjekker før hvert steg (betalt? svart? bestrider?
  allerede sendt på nytt?): vennlig dag 1, ny påminnelse dag 7,
  inkassovarsel dag 14 etter ditt ja, inkassobyrå fra dag 28.
- Stripe-purring hver uke: hvem har kort som feiler, hvem har Stripe
  allerede kansellert, og hvem fullførte aldri kjøpet. Med ferdige utkast.
- Ukentlig oversikt over hvem som skylder hva, med aldersbuckets.
- Rydder gamle fakturapiler i batcher på 20 sammen med regnskapsføreren.
- Trekker ut dato, leverandør, beløp og mva fra bilag til én tabell.

**Hva Luca ALDRI gjør:** finner på beløp, sender faktura uten godkjenning,
gir rabatter på egen hånd, flytter penger, rører Stripe, legger på gebyrer
ingen har avtalt, eller purrer på noen som har betalt eller bestrider kravet.

**Du trenger:**
- Claude Code
- Et faktureringssystem med API. Skriptene er laget for GoHighLevel. Bruker
  du Fiken eller Tripletex, ber du Claude skrive om `faktura.py` mot det
  API-et. Reglene i SKILL.md gjelder uansett.
- Stripe hvis du tar kortbetaling (en begrenset lesenøkkel holder)
- Slack eller en annen kanal der utkast kan vente på et ja
- En regnskapsfører (deg selv eller en annen) som eier fasiten

**Kom i gang:**
1. Opprett `.claude/skills/faktura/` og legg inn `SKILL.md` og mappa `scripts/`.
2. Kopier `.env.example` til `.env` og fyll inn nøklene (aldri i git).
3. Kjør `python3 scripts/faktura.py sjekk`. Den tester lese- og skrivetilgang
   uten å lage noe.
4. Kjør `python3 scripts/faktura.py mal`. Den kopierer logo, adresse og
   bankdetaljer fra den nyeste betalte fakturaen din. Sjekk at org.nr står i
   teksten.
5. Start med `oversikt`. Få det ærlige bildet av hvem som skylder deg penger
   før du automatiserer noe som helst.
6. Tilpass SKILL.md: hvor salgene kommer fra, hvem som kan godkjenne, hvilken
   kanal utkastene postes i.
7. Når rytmen sitter: én daglig scheduled task som sveiper salg og forfall,
   og én ukentlig for `stripe_purring.py`.
