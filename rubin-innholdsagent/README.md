# Rubin — innholdsagenten

Rubin er en Claude Code-agent som lager ukens innhold av det du faktisk har
bygget. Én sak inn, to leveranser ut: én post til medlemsgruppa eller
LinkedIn, og ett videomanus. Skal du bygge en YouTube-kanal for alvor, blir
Rubin produsent: en video går fra idé til filmeplan, ett godkjent steg om
gangen. Du limer inn, spiller inn og laster opp. Rubin publiserer aldri.

**Problemet den løser:** Du gjør interessante ting hver uke, men innholdet
blir aldri laget, fordi «hva skal jeg poste?» er en større terskel enn selve
skrivingen. På YouTube er problemet et annet: folk skriver manus først og
tenker på tittel og thumbnail til slutt, og så ser ingen videoen. Rubin snur
rekkefølgen: bevis på etterspørsel, så pakking, så manus.

**Hva Rubin gjør:**
- Henter råstoff fra git-historikk og arbeidsloggen din
- Foreslår tre saker og lar deg velge én
- Stiller fire faste spørsmål (inkludert «hva gikk galt?», den beste delen)
- Skriver én ferdig post og ett videomanus av samme sak
- Holder en idébank så ingen vinkel gjenbrukes før det har gått tre måneder
- Modus 2: fireukers innholdsplan. Modus 3: gjenbruk av webinar/opptak
- **Modus 4, YouTube:** en idétavle der idéer du nevner flere ganger stiger av
  seg selv; stegene research → pakking → manus → filming → gjenbruk, med et
  lagret dokument per steg; tre tittel/thumbnail-kombinasjoner før det skrives
  et ord manus; kroker i tre versjoner; og en ukentlig skann av 8–10 kanaler
  som finner videoer som gjør det langt bedre enn kanalens median
- **Tallene fra din egen kanal:** en rapport hver uke med visninger, sett tid,
  hvor mange som er igjen etter 30 sekunder og hvor det bratteste fallet er,
  så neste video kan rette på det forrige video mistet folk på

**Hva Rubin ALDRI gjør:** publiserer eller laster opp, dikter opp tall eller
resultater, kopierer andres titler eller manus, eller sender kundedata ut av
prosjektet.

**Du trenger:**
- Claude Code og Python 3 (ingen pakker, bare standardbiblioteket)
- Et repo eller en mappe der arbeidet ditt legger igjen spor (git-logg)
- Et sted å publisere: medlemsgruppe (Skool, Circle, Facebook), LinkedIn,
  YouTube
- For outlier-skannen: en gratis YouTube Data API-nøkkel (se `.env.example`)
- 15 minutter i uka til å svare på fire spørsmål

**Kom i gang:**
1. Opprett `.claude/skills/innhold/` i prosjektet ditt og lim inn `SKILL.md`.
2. Lag `innhold/IDEBANK.md`: hva som skal lages og hva som er brukt, med dato
   og lenke.
3. Skriv stemmereglene dine inn i SKILL.md (§ Ufravikelige regler): hvordan du
   snakker, hva du aldri sier, hvor mye du selger.
4. Si «ukens innhold» til Claude Code. Velg én av de tre sakene og svar på
   spørsmålene.
5. Vil du bruke YouTube-modusen: legg `rubin_mcp.py` i prosjektet, kjør
   `python3 test_rubin_mcp.py` (skal si `ok`), og registrer den som MCP-server:
   `claude mcp add rubin -e YOUTUBE_API_KEY=<din-nøkkel> -- python3 /full/sti/til/rubin_mcp.py`
   (nøkkelen kan droppes i starten). Start Claude på nytt, si «rubin, start
   kanalen» og svar på kontekst-intervjuet.
6. Legg til kanaler med «rubin, overvåk kanalen …», og sett opp en planlagt
   jobb mandag morgen som kjører outlier-skannen.
7. Vil du ha tallene fra din egen kanal: `yt_tall.py` leser YouTube Analytics
   (kun lesing) og lager en rapport med visninger, sett tid, og hvor i videoen
   folk faller av. Du trenger en OAuth-klient av typen «Desktop app» i Google
   Cloud, med «YouTube Data API v3» og «YouTube Analytics API» slått på. Legg
   `GOOGLE_OAUTH_CLIENT_ID` og `GOOGLE_OAUTH_CLIENT_SECRET` i `.env`, kjør
   `python3 yt_tall.py login` én gang, og så `python3 yt_tall.py rapport`.
   `python3 yt_tall.py` uten argumenter er selvtest. Google viser «Google
   hasn't verified this app» ved innlogging, fordi appen er din egen: trykk
   Advanced, og gå videre.
