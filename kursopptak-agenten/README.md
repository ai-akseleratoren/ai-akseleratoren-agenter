# Kursopptak-agenten — fra Zoom til ferdig leksjon

Kursopptak-agenten tar hele etterarbeidet etter en sending: henter opptaket,
chatten og transkriptet fra Zoom, sjekker hva du lovet underveis, og pakker
alt som en ferdig leksjon og en post du kan legge rett inn i Skool.

**Problemet den løser:** Sendingen var god. Så ligger opptaket i Zoom-skyen i
tre uker, chatten er borte, og ingen av dem som ikke rakk det får sett den. Og
det du sa underveis — «jeg legger ut prompten i gruppa etterpå» — blir aldri
gjort. Jobben med å laste ned, finne spørsmålene, skrive leksjonsteksten og
huske løftene tar en time, og den timen finnes aldri.

Det som er mest verdt i chatten er dessuten det ingen husker: de siste ti
minuttene, der folk melder interesse for det du selger.

**Hva agenten gjør:**
- Lister sendingene dine og henter den du peker på — også når de kjøres fra
  en kollegas eller en felles Zoom-bruker
- Laster ned video, lyd, chat og transkript
- Lager en `INFO.md` med dato, varighet, delelenke, alle spørsmål fra chatten,
  hele chatten — og de siste ti minuttene som egen seksjon
- **Løftesjekk:** lister alt du lovet på sendinga, og om det er levert
- Samler lenkene du delte i chatten, så de havner i leksjonen
- Lager en `SKOOL.md` og utkast til leksjon og post i feeden

**Hva agenten ALDRI gjør:** publiserer noe uten at du har sagt ja, nevner
opptak i invitasjonen til sendinga, eller bruker Zooms eget norske transkript
(det er ubrukelig — se under).

**Du trenger:**
- Claude Code og Python 3 (skriptet bruker bare standardbiblioteket)
- En Zoom-konto med skyopptak, og en Server-to-Server-app med
  `cloud_recording:read:admin` i Zoom Marketplace
- Whisper (lokalt eller via API) eller et møteverktøy som kan norsk, for
  transkriptet
- Valgfritt: en Skool-tilkobling, hvis agenten skal legge leksjonen inn selv

**Kom i gang:**
1. Opprett `.claude/skills/kursopptak/`, lim inn `SKILL.md`, og legg
   `kursopptak.py` i prosjektmappa.
2. Kopier `.env.example` til `.env` og fyll inn Zoom-nøklene, vertskontoene
   og ordene som står i tittelen på sendingene dine.
3. Kjør `python3 kursopptak.py test`, så `python3 kursopptak.py liste --dager 60`.
4. `hent siste --uten-video` når du bare vil ha chat og transkript. Det går på
   sekunder; full video er 500–600 MB.
5. Si «kursopptak» etter neste sending, og les løftelista før du publiserer.

> Zooms eget transkript står på engelsk og gjør norsk tale til vrøvl — «Claude
> Code» blir «CloudKord». Bruk lydfila mot en tjeneste som kan norsk i stedet.
> Det er forskjellen på et transkript du kan bruke og ett du må lese korrektur på.
