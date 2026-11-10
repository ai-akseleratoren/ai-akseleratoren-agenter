---
name: chatklone
description: Chatklonen — fletter chatten fra de siste sendingene av samme webinar inn i dagens opptak, tidsatt etter det verten faktisk sier, til simulert chat i reprisen (WebinarFuel, EverWebinar, WebinarJam, Demio eller andre verktøy med simulert chat). Foreslår også når kjøpsknappen skal vises. Bruk når brukeren sier "chatklone", "klon chatten", "simulert chat", "flett chatten", "chat til reprisen", "automatisk webinar", eller vil ha chatten fra flere sendinger slått sammen.
---

# Chatklonen

Lager én chat-tidslinje til reprisen av et webinar: dagens ekte chat, pluss
de meldingene fra tidligere sendinger som passer der verten sier det samme.
Ikke alle meldinger skal med. Bare de som stemmer med det som blir sagt i
minuttet de havner i.

Målet er en levende chat. Verten trenger ikke svare på alt.

## Forberedelser per sending

Én mappe per sending, f.eks. `sendinger/2026-11-03/`:

| Fil | Hva | Hvor fra |
|---|---|---|
| `chat.txt` eller `chat.csv` | Chatten. Zoom-format, eller `sekund,navn,melding` | Webinarverktøyets chat-eksport |
| `transkript.vtt` / `.srt` / `transkript-per-minutt.txt` | Hva verten sier. **Trengs bare for målet** | Whisper på lydfila (se under) |
| `meta.json` | `{"chat_minus_opptak_sek": N}` | Regnes ut, se «Klokka» |
| `privat.txt` | Lokal chatfil med meldinger «to Host» | Zoom: Documents/Zoom/<møte>/ |

**Kilder:** standard er sendingene de siste to ukene før målet. Eldre
sendinger har oftere andre priser, datoer og tilbud.

**Transkriptet:** automatisk transkripsjon fra møteverktøyet er ofte
ubrukelig på norsk. Kjør lydfila gjennom Whisper (lokalt eller via en
API-tjeneste) og lagre som `.vtt`. Ta lyd, ikke video: mindre fil, raskere.

## Klokka: videotid, ikke chattid

Chatfila regner ofte tid fra **møtestart**, opptaket fra **opptaksstart**.
Startet opptaket fem minutter etter møtet, havner hele chatten fem minutter
feil. Hent begge tidspunktene fra opptaksverktøyet (i Zoom-API-et:
`start_time` på møtet og `recording_start` på filene), og skriv forskjellen i
sekunder til `meta.json`. Skriptet trekker den fra, så alt i resultatet er
videotid. Sjekk ved å sammenligne første «hei» i chatten med når verten
hilser i videoen.

## Kjør

```bash
python3 chatklone.py klon sendinger/2026-11-03 --kilder sendinger/2026-10-20 sendinger/2026-10-27 \
    --team "<DITT NAVN>,<TEAMMEDLEM>,Notetaker" --ankerord "<ORD PUBLIKUM SVARER MED>"
```

- `--team`: verten, teamet og boter. Deres meldinger tas aldri med.
- `--ankerord`: hvis verten ber publikum skrive et bestemt ord (et
  produktnavn, et navn på noe dere bygger), blir det et ekstra anker.
- `--gratulasjoner --vert "<NAVN> (vert)"`: vertsmelding 15–25 sekunder
  etter hvert «jeg er med» i salgsdelen, én per navn.
- `--uten-ai`: bare tidsjustering og personvern, til en rask første titt.

Resultat i målmappa: `chatklone.csv` (sekund, tid, navn, melding, kilde) for
import, og `chatklone.txt` til lesing.

**Når `claude -p` ikke er logget inn:** kjør med `--eksporter`. Promptene
havner i `<mål>/ai/<hash>.prompt.txt`. Svar på dem (selv eller med
hjelpeagenter) som `<hash>.json` i samme mappe, og kjør igjen. Første
runde lager bare emneindeksen, andre runde vinduene. Svar caches, så en ny
kjøring koster ingenting.

## Slik virker den

1. **Ankere.** Øyeblikkene der mange svarer på samme oppfordring:
   intro-runden, JA-runden, timetallet, ankerordet, påmeldingsrunden. De
   finnes i alle sendingene fordi presentasjonen er den samme.
   Kildemeldinger flyttes stykkevis lineært mellom ankrene. Ankere som
   spriker mer enn 15 minutter fra resten kastes.
2. **Personvern.** Kun fornavn («Gjest» når navnet er et telefonnummer eller
   en enhet), ingen e-post, telefon, lenker, betalingsdetaljer, ingen
   private meldinger til verten, ingen fra teamet eller boter.
3. **Kjøp og «jeg er med»** flyttes alltid til dagens salgsdel (fra første
   kjøpslenke til siste «jeg er med»), spredt jevnt, så de står der de
   andre sier det samme.
4. **Claude plasserer resten.** Først en emneindeks for hele opptaket
   (minutt → tema, SPØR der verten ber chatten skrive noe, PRIS der
   tilbudet kommer). Så per 5-minutters vindu: svar på en oppfordring
   flyttes til minuttet der verten ber om det i dag. Generelle spørsmål
   står der de står. Bare det som motsier dagens webinar (tall, priser,
   datoer, tilbud) eller er ren gjentakelse fjernes.
5. **Maks 10 kildemeldinger per minutt.**

## Før du leverer

- Les `chatklone.txt` rundt pitchen (siste 30 minutter): ingen meldinger om
  priser, frister eller bonuser som ikke stemmer med dagens tilbud.
- Chatten inneholder ekte deltakeres meldinger. Les gjennom og si fra hvis
  noe kan identifisere en person. Har noen bedt om å bli fjernet: fjern
  navnet og alle meldinger som nevner dem, også i fremtidige kloner.
- Lever fila til den som setter opp reprisen. Slack-koblingen kan ikke
  legge ved filer, så last den opp et sted og del lenken.

## Forslag til kjøpsknapp (CTA)

Simulerte webinarer kan vise en klikkbar knapp til kassesiden. Finn
tidspunktene slik:

1. Vertens egne lenkeposter i chatten (husk å trekke fra
   `chat_minus_opptak_sek`).
2. Bekreft hver mot transkriptet («lenken», «linken», «jeg poster»,
   «registrer deg»).
3. Lag en tabell: vis / skjul / sitat, og hva chatten gjør rundt hver.

Anbefaling: vis knappen hver gang verten sier at lenken deles, i ca. 40
sekunder, og la den stå fast fra slutten av spørsmålsrunden til videoen er
ferdig.

## Aldri

- Finne på meldinger. Alt i klonen er sagt av ekte deltakere i en sending
  av samme webinar, bortsett fra vertsgratulasjonene du ber om selv.
- Ta med meldinger som motsier dagens tilbud.
- Ta med etternavn, kontaktinfo eller private meldinger.
