# Chatklonen — levende chat i reprisen

Chatklonen er en Claude Code-agent som lager simulert chat til reprisen av
et webinar. Den tar chatten fra de siste sendingene av samme webinar og
fletter den inn i dagens opptak, tidsatt etter det verten faktisk sier.

**Problemet den løser:** En automatisk reprise med tom chat føles død. Å
bruke chatten fra én sending gir for lite liv, og å lime sammen flere
sendinger for hånd gir «JA!» på feil sted, spørsmål om priser som ikke
gjelder lenger, og etternavn som ikke skulle vært der. Chatklonen flytter
hver melding dit den hører hjemme i dagens video.

**Hva agenten gjør:**
- Finner ankerpunkter (JA-runden, intro-runden, påmeldingsbølgen) i hver
  sending og flytter meldingene mellom dem, så tidene stemmer
- Leser transkriptet og flytter svar på en oppfordring til minuttet der
  verten ber om akkurat det i dag
- Legger alle kjøp og «jeg er med» i dagens salgsdel
- Vasker personvern: kun fornavn, ingen e-post, telefon, lenker eller
  private meldinger, ingenting fra teamet
- Fjerner meldinger som motsier dagens tilbud
- Foreslår når kjøpsknappen skal vises i reprisen
- Gir én CSV klar for import, og en lesbar tekstversjon

**Hva agenten ALDRI gjør:** finner på deltakermeldinger, tar med noe som
kan identifisere en person, eller lar gamle priser og frister stå igjen
rundt pitchen.

**Du trenger:**
- Claude Code og Python 3 (kun standardbiblioteket)
- Webinarverktøy med chat-eksport (Zoom, eller et hvilket som helst som
  gir tid, navn og melding)
- Et reprise-verktøy med simulert chat og CSV-import (WebinarFuel,
  EverWebinar, WebinarJam, Demio e.l.)
- Whisper eller annen transkribering for dagens opptak

**Kom i gang:**
1. Lag mappa `.claude/skills/chatklone/` i prosjektet ditt og legg
   `SKILL.md` der. Legg `chatklone.py` i prosjektrota.
2. Test skriptet: `python3 chatklone.py --demo`.
3. Lag én mappe per sending med chat-eksporten. Dagens sending får også
   transkriptet og `meta.json` (se «Klokka» i SKILL.md).
4. Si «klon chatten fra de siste to ukene inn i dagens sending».
5. Les `chatklone.txt` rundt pitchen før du importerer.
6. Importer `chatklone.csv` i reprise-verktøyet ditt. Sjekk kolonnenavnene
   verktøyet ditt vil ha, og be agenten tilpasse CSV-en ved behov.

> Tips: den vanligste feilen er klokka. Starter opptaket fem minutter etter
> møtet, havner hele chatten fem minutter feil. Sjekk første «hei» mot
> videoen.
