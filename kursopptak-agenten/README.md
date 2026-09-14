# Kursopptak-agenten — fra Zoom til ferdig leksjon

Kursopptak-agenten henter opptaket, chatten og transkriptet fra Zoom-sendingen
din, og pakker det som en ferdig leksjon du kan legge rett inn i Classroom.

**Problemet den løser:** Sendingen var god. Så ligger opptaket i Zoom-skyen i
tre uker, chatten er borte, og ingen av dem som ikke rakk det får sett den.
Jobben med å laste ned, finne spørsmålene og skrive leksjonsteksten tar en time,
og den timen finnes aldri.

Det som er mest verdt i chatten er dessuten det ingen husker: de siste ti
minuttene, der folk melder interesse for det du selger.

**Hva agenten gjør:**
- Lister sendingene dine og henter den du peker på
- Laster ned video, lyd, chat og transkript
- Lager en `INFO.md` med dato, varighet, delelenke, alle spørsmål fra chatten,
  hele chatten — og de siste ti minuttene som egen seksjon
- Lager en `SKOOL.md`: leksjonsteksten, ferdig til å limes inn

**Hva agenten ALDRI gjør:** publiserer opptaket et sted uten at du har sagt fra,
eller bruker Zooms eget norske transkript (det er ubrukelig — se under).

**Du trenger:**
- Claude Code
- En Zoom-konto med skyopptak, og en app med `recording:read` i Zoom
  Marketplace. Kjøres sendingene fra en annen bruker enn deg selv, må nøkkelen
  tilhøre den kontoen
- `ZOOM_ACCOUNT_ID`, `ZOOM_CLIENT_ID` og `ZOOM_CLIENT_SECRET` i `.env`

**Kom i gang:**
1. Opprett `.claude/skills/kursopptak/` og lim inn `SKILL.md`.
2. Sett inn ditt eget møte-ID der PMI-en står omtalt.
3. Kjør `liste --dager 60` for å se hvilke sendinger som finnes.
4. `hent siste --uten-video` når du bare vil ha chat og transkript. Det går på
   sekunder; full video er 500–600 MB.

> Zooms eget transkript står på engelsk og gjør norsk tale til vrøvl — «Claude
> Code» blir «CloudKord». Bruk lydfila mot en tjeneste som kan norsk i stedet.
> Det er forskjellen på et transkript du kan bruke og ett du må lese korrektur på.
