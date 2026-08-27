# Annonse-analytikeren

En AI-agent + et Python-script som gjør dypanalyse av Meta-annonsekontoen din
over 6–12 måneder: hva gir egentlig billige leads? Plasseringer, kreativtyper,
levetid og slitasje, adsett-aldring, av/på-mønster, målgrupper, ukedag og time.

## Hvilket problem løser den?

Ads Manager viser deg siste uke. Den viser deg ikke:

- om kreativene dine faktisk slites — eller om det er adsettene som eldes
- hvilke plasseringer som konsekvent gir billigst leads over et helt år
- hva stadig av/på-skruing og budsjettrykk koster i læringsfase
- hvilke kreativer som er gjenbrukt i mange kampanjer og fortsatt leverer

Analytikeren henter rådata på annonsenivå per dag og regner ut alt dette som
markdown-tabeller du kan lese — og som Claude kan tolke for deg.

## Hva du trenger

- Claude Code og Python 3 (scriptet bruker kun standardbiblioteket)
- Meta Marketing API-token med LESE-tilgang til annonsekontoen
- En mappe med `data/` (rådata som JSON) og `rapporter/` (output)

## Kom i gang

1. Kopier mappen inn i et eget prosjekt, og `SKILL.md` til
   `.claude/skills/annonse-analytiker/SKILL.md`.
2. Kopier `.env.example` til `.env` og fyll inn token og konto-ID.
3. Be Claude hente rådata fra Marketing API til `data/` (filene scriptet
   forventer står listet i `SKILL.md`) — insights på annonsenivå per dag er
   kjernen.
4. Kjør `python3 analyse.py 2025-01-01` — tallgrunnlaget havner i `rapporter/`.
5. Be agenten tolke: «Les tallgrunnlaget og skriv analyse med anbefalinger.»
   Tolkningen skrives alltid som egen fil, oppå forrige analyse.

## Viktigste prinsipper

- Pikseltall er relative, ikke sannhet. Si alltid hvilken slice du måler.
- Agenten er **lesende** — den endrer aldri noe i kontoen via API.
- Epler mot epler: sammenlign samme funnel/land/periode.
- Lang levetid = vinnersignal. Rapporter langtidskjørere separat fra ferske
  tester.
