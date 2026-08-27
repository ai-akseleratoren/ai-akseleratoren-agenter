# Annonse-analytikeren

En AI-agent som graver seg gjennom 6–12 måneder med annonsedata og finner ut
hva som faktisk gir billige leads — plassering, format, målgruppe, ukedag,
klokkeslett, og hvor lenge en annonse holder før den slutter å virke.

## Hvilket problem løser den?

- Annonsekontoen din har ett år med svar i seg, men Ads Manager viser deg bare
  de siste sju dagene.
- «Kreativen er utslitt» er som regel gjetning. De fleste slår av ting som
  virker, og lar ting som ikke virker stå.
- Ingen sammenligner CPL på tvers av plassering, alder, kjønn og ukedag — det
  er for mye klikking.
- Vinnerannonser dukker opp igjen som «nye» annonser i nye kampanjer, så tallene
  spres og vinneren blir usynlig.

Analytikeren henter alt via Meta Marketing API, cacher det lokalt og skriver ett
langt tallgrunnlag du kan lese på 15 minutter. Den er **lesende** — den rører
aldri kontoen.

## Hva du trenger

- Claude Code og Python 3 (skriptene bruker kun standardbiblioteket)
- Meta Marketing API-token med **lesetilgang** til annonsekontoen din
- Annonsekonto-ID-en din (`act_…`)
- Litt tålmodighet første gang: full henting av 12 måneder tar noen minutter

## Kom i gang

1. Kopier `SKILL.md` inn som `.claude/skills/annonseanalyse/SKILL.md` i
   prosjektet ditt, og legg `hent_meta.py` og `analyse.py` i `scripts/`.
2. Kopier `.env.example` til `.env` og fyll inn token og konto-ID. Aldri i git.
3. Hent dataene: `python3 scripts/hent_meta.py` (cacher i `data/` —
   `--fersk` tvinger ny henting).
4. Kjør analysen: `python3 scripts/analyse.py 2025-08-01` — den skriver
   `rapporter/tallgrunnlag-….md`.
5. Be Claude lese tallgrunnlaget og skrive tolkningen i
   `rapporter/analyse-DATO.md`. Neste gang: les forrige analyse først, så du
   bygger videre i stedet for å gjenta deg selv.

## De fem tolkningsreglene

1. **Lang levetid = vinnersignal.** En annonse som har fått stå i måneder,
   tjener penger. Rapporter langtidskjørere separat fra ferske tester.
2. **Skill kreativ fra adsett.** Kreativer slites ofte ikke i det hele tatt,
   mens adsettet eldes. Da er det adsettet som skal byttes, ikke bildet.
3. **Pikseltall er relative, ikke sannhet.** Si alltid hvilken slice du målte
   (hvilken konto, hvilket vindu, hvilket event). Salg hentes fra CRM-et.
4. **Epler mot epler.** Samme funnel, samme land, samme periode. Aldri to
   ulike produkter i samme tabell.
5. **Én kreativ kan hete fem ting.** Slå sammen på video-ID eller tekst-hash
   før du kårer vinnere — ellers deler du vinneren i fem tapere.
