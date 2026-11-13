# Thelma — videoannonser fra din egen stemme

Thelma er oppkalt etter Thelma Schoonmaker, som har klippet hver Scorsese-film
siden Raging Bull og sier at hun klipper med ørene, ikke med øynene.

Du snakker inn en historie, eller filmer deg selv på mobilen. Hun transkriberer
det du sa ord for ord, foreslår bilder som passer til det du sier, lager dem,
legger dem der ordene faller, tekster hele filmen og leverer både en ferdig MP4
og et prosjekt i CapCut du kan finpusse.

**Problemet den løser:** Videoannonser tar en dag. Du skriver manus, filmer,
finner stockvideo som nesten passer, klipper, gir opp, og publiserer den du
hadde fra før.

Og manuset er selve problemet. Første gang vi prøvde dette skrev vi et pent
manus, leste det inn, og bildene gikk sin egen vei, fordi det som ble sagt var
noe annet enn det som sto der. Andre forsøk droppet vi manuset. Da kom linja
«mens jeg så på golf på TV-en, gikk agentene gjennom tallene», og den ble den
beste i hele annonsen.

Derfor: stemmen først, bildene etterpå.

**Hva agenten gjør:**
- Transkriberer opptaket med tidspunkt per ord
- Foreslår 2–3 b-roll og 3–5 tekstlinjer per film, og lager ingenting før du sier ja
- Lager filmatiske klipp med en idé i (humor, overraskelse, visuell metafor),
  og ser gjennom alle før de brukes
- Klipper bort pauser og omstarter, legger b-roll inn på ordet, full teksting,
  sluttkort og lav bakgrunnsmusikk
- Måler pauser og «eh» i lyden (`stram.py`) i stedet for å klippe på øyemål, og
  skriver den ferdige lyden ut som tekst for å oppdage ord som ble klippet bort
- Åpner på bevegelse, med teksten i første bilde: de tre første sekundene avgjør
- Levende tekst: stor tekst som hopper rundt, en huskelapp som hukes av, eller
  TV-grafikk
- Rendrer MP4 direkte med ffmpeg, og bygger samme film som CapCut-prosjekt
- Svensk versjon av samme film med svensk teksting, og engelsk når du filmer på nytt
- To annonsetekster per video, og en melding til den som kjører annonsene

**Hva agenten ALDRI gjør:** genererer før du har sagt ja til forslaget, skriver
tekst eller tall inn i de genererte bildene (modellen staver norsk feil og
finner på sifre), sakter ned bildene for å fylle tid, eller setter dato, pris
eller «live» i en evergreen-annonse.

**Du trenger:**
- Claude Code
- En fal.ai-konto med litt saldo. Klippene koster seks cent per sekund, en hel
  annonse rundt seks dollar.
- CapCut (gratis)
- Repoet [VectCutAPI](https://github.com/sun-guannan/VectCutAPI) klonet til
  `~/capcutapi` med egen `.venv` (følg README-en der). Det er biblioteket som
  skriver CapCut-prosjektet.
- ffmpeg med libass for MP4-rendring (f.eks. npm-pakken `ffmpeg-static`). Ligger den
  ikke i PATH, sett miljøvariabelen `FFMPEG` til full sti.

**Kom i gang:**
1. Opprett `.claude/skills/videoannonse/` og legg inn `SKILL.md` og skriptene.
2. Kopier `.env.example` til `.env` og legg inn `FAL_KEY` (aldri i git).
3. Kjør selvtestene: `python3 video.py --demo`, `python3 transkriber.py --demo`,
   `python3 til_capcut.py --demo` og
   `~/capcutapi/.venv/bin/python render_annonse.py --demo`. Alle skal si «demo ok».
4. Lag en sluttkort-video (3–4 sek mørk bakgrunn, MP4, ikke PNG) og legg den
   på `~/Desktop/sluttkort.mp4`, eller pek på den med `"fil"` i planen.
5. Film deg selv i tretti sekunder om noe du er lei av i jobben din. Ikke
   skriv manus.
6. Gi fila til agenten og si «thelma».

> To feller vi gikk i, så du slipper: CapCut leser prosjektlista bare når den
> starter, så avslutt med ⌘Q og åpne igjen for å se nye prosjekter. Og CapCut
> må være helt avsluttet før et prosjekt leveres på nytt, ellers overskriver
> den rettelsene når den lukkes.
