# Thelma — videoannonser fra din egen stemme

Thelma er oppkalt etter Thelma Schoonmaker, som har klippet hver Scorsese-film
siden Raging Bull og sier at hun klipper med ørene, ikke med øynene.

Du snakker inn en historie på mobilen. Hun transkriberer det du sa, lager
videoklipp som passer til hvert ord, legger dem der ordene faller, og skriver
hele prosjektet inn i CapCut — ferdig lagt ut på tidslinja.

**Problemet den løser:** Videoannonser tar en dag. Du skriver manus, filmer,
finner stockvideo som nesten passer, klipper, gir opp, og publiserer den du
hadde fra før.

Og manuset er selve problemet. Første gang vi prøvde dette skrev vi et pent
manus, leste det inn, og bildene gikk sin egen vei — fordi det som ble sagt
var noe annet enn det som sto der. Andre forsøk droppet vi manuset. Da kom
linja «mens jeg så på golf på TV-en, gikk agentene gjennom tallene», og den ble
den beste i hele annonsen.

Derfor: stemmen først, bildene etterpå.

**Hva agenten gjør:**
- Transkriberer opptaket ditt med tidspunkt per setning
- Leser hva du faktisk nevner, og lager et klipp for hver ting
- Legger klippene der ordene faller, ikke jevnt utover
- Kan legge b-roll oppå film av deg selv, så ansiktet ditt står i starten og
  slutten
- Skriver hele prosjektet inn i CapCut, klart til finpuss

**Hva agenten ALDRI gjør:** later som stockvideo er ditt, skriver tekst inn i
bildet (modellen staver norsk feil), eller sakter ned bildene for å fylle tid.

**Du trenger:**
- Claude Code
- En fal.ai-konto med litt saldo — klippene koster seks cent per sekund, en hel
  annonse rundt seks dollar
- CapCut (gratis)
- Repoet [VectCutAPI](https://github.com/sun-guannan/VectCutAPI) klonet til
  `~/capcutapi` — det er biblioteket som skriver CapCut-prosjektet

**Kom i gang:**
1. Opprett `.claude/skills/videoannonse/` og lim inn `SKILL.md`.
2. Legg de tre skriptene i prosjektet ditt. Kjør `python3 video.py --demo` og
   `python3 til_capcut.py --demo` — begge skal si «demo ok».
3. Legg `FAL_KEY` i `.env`.
4. Snakk inn tretti sekunder på mobilen om noe du er lei av i jobben din. Ikke
   skriv manus.
5. Gi lydfila til agenten og si «thelma».

> To feller vi gikk i, så du slipper: CapCut må være helt avsluttet med ⌘Q før
> prosjektet leveres, ellers overskriver den alt — og prosjekter med tekstspor
> nekter å åpne i CapCut International, så legg teksten på med auto-teksting
> etterpå i stedet.
