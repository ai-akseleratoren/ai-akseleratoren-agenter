# Rubin — innholdsagenten

Rubin er en Claude Code-agent som lager ukens innhold av det du faktisk har
bygget. Én sak inn, to leveranser ut: én post til medlemsgruppa eller
LinkedIn, og ett videomanus. Du limer inn og spiller inn — Rubin poster aldri.

**Problemet den løser:** Du gjør interessante ting hver uke, men innholdet
blir aldri laget, fordi «hva skal jeg poste?» er en større terskel enn selve
skrivingen. Rubin snur på det: den leser git-loggen og arbeidet ditt, foreslår
tre saker, og intervjuer deg om det som mangler. Ingenting oppdiktet — alt
peker tilbake på noe du faktisk gjorde.

**Hva Rubin gjør:**
- Henter råstoff fra git-historikk og arbeidsloggen din
- Foreslår tre saker og lar deg velge én
- Stiller fire faste spørsmål (inkludert «hva gikk galt?» — den beste delen)
- Skriver én ferdig post og ett videomanus av samme sak
- Holder en idébank så ingen vinkel gjenbrukes før det har gått tre måneder
- Modus 2: fireukers innholdsplan. Modus 3: gjenbruk av webinar/opptak til
  én video, tre poster og 5–8 nye idéer

**Hva Rubin ALDRI gjør:** poster selv, dikter opp tall eller resultater, eller
sender kundedata ut av prosjektet.

**Du trenger:**
- Claude Code
- Et repo eller en mappe der arbeidet ditt legger igjen spor (git-logg)
- Et sted å publisere: medlemsgruppe (Skool, Circle, Facebook), LinkedIn,
  YouTube — Rubin er kanaluavhengig
- 15 minutter i uka til å svare på fire spørsmål

**Kom i gang:**
1. Opprett `.claude/skills/innhold/` i prosjektet ditt og lim inn `SKILL.md`.
2. Lag `innhold/IDEBANK.md` — en liste over hva som skal lages og hva som er
   brukt, med dato og lenke.
3. Skriv ned stemmereglene dine i SKILL.md (§ Ufravikelige regler): hvordan du
   snakker, hva du aldri sier, hvor mye du selger.
4. Si «ukens innhold» til Claude Code. Velg én av de tre foreslåtte sakene og
   svar på spørsmålene.
5. Lim inn posten selv, spill inn videoen, og kryss av i idébanken. Svar på
   hver kommentar innen et døgn — det er der livet i gruppa kommer fra.
