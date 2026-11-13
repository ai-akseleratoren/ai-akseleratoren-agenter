# Pakkeren — gjør podkasten og videoene dine lette å finne

Pakkeren er en Claude Code-agent som tar en episode som allerede ligger ute, og
leverer alt som gjør at folk finner den i søk: tre titler å teste, en beskrivelse
med søkeordet og lenken øverst, kapitler med tider, tagger, festet kommentar og
tekst til miniatyrbildet.

**Problemet den løser:** Du legger ut en god episode med en tittel ingen søker
etter, uten kapitler, og med lenken gjemt bak «vis mer». YouTube er verdens nest
største søkemotor, og de fleste podkaster bruker den som et lager.

Den ble bygget for en podkast som nettopp var lansert, etter én bestilling:
trafikk først.

**Hva agenten gjør:**
- Henter tittel, beskrivelse, tagger, kapitler og tall for hver episode
- Henter YouTubes autoteksting og rydder den til et transkript med tider
- Slår opp hva folk faktisk skriver i YouTube-søket
- Skriver en ferdig pakke per episode, klar til å lime inn i YouTube Studio
- Lister alt den er usikker på, så du kan sjekke det faglige

**Hva agenten ALDRI gjør:** publiserer eller endrer noe på kanalen, lover noe
episoden ikke holder, eller bruker søkeord for problemer du ikke jobber med.

**Du trenger:**
- Claude Code og Python 3 (bare standardbiblioteket)
- `yt-dlp` installert (`brew install yt-dlp` på Mac, `pip install yt-dlp` ellers)
- Episoder som ligger på YouTube. Ingen nøkler: den leser bare offentlige data.

**Kom i gang:**
1. Opprett `.claude/skills/pakkeren/` i prosjektet ditt, og legg inn `SKILL.md`
   og `hent.py`.
2. Fyll inn «Fakta om kanalen» i `SKILL.md`.
3. Kjør `python3 hent.py <video-id>` på én episode. Du får `episoder/<id>/naa.md`
   og `transkript.txt`.
4. Si «pakkeren, pakk denne episoden» til Claude Code.
5. Lim inn det du vil bruke i YouTube Studio. Fortell agenten hva du valgte og
   hva du rettet, så husker den det neste gang.

Pakkeren er den første av flere roller i et podkast-team. Den går godt sammen
med **rubin-innholdsagent** (idé, manus og tall) og **thelma-videoklipper**
(korte klipp fra episodene).
