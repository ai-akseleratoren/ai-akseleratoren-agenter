---
name: kursopptak
description: Hent opptak, chat og transkript fra Zoom-sendingene dine, sjekk hva du lovet underveis, og gjør alt klart for Skool (leksjon + post). Bruk når brukeren sier "kursopptak", "hent opptaket", "ukas sending", "etter sendinga", "last ned Zoom-opptaket", "legg ut i Skool", "hva lovet jeg på sendinga", eller spør om chatten fra en sending.
---

# Kursopptak — fra Zoom til Skool

Du eier hele etterarbeidet etter hver sending: faste kurssendinger,
velkomstsendinger for nye medlemmer og bonussendinger. Ingen opptak skal ligge
i Zoom-skyen i tre uker, og ingen løfter fra sendinga skal glemmes.

Sendingene kjøres ofte fra en annen Zoom-bruker enn din egen, og gjerne på et
fast møterom. Vertskontoene og ordene i møtetittelen som betyr «kurssending»
står i `.env` (`ZOOM_VERTER`, `SENDING_EMNER`). Finner du ikke en sending:
sjekk at verten står på lista og at tittelen inneholder et av ordene.

## 1. Finn sendinga

```bash
python3 kursopptak.py liste --dager 60
```

Brukes samme møterom hver gang, er `--dato` nødvendig for å hente en eldre sending.

## 2. Hent den

```bash
python3 kursopptak.py hent siste
```

- `hent siste` tar nyeste sending. `hent <møte-id> --dato 2026-08-18` tar en bestemt.
- `--uten-video` når brukeren bare vil ha chat og transkript (går på sekunder;
  full video er 500–600 MB og tar noen minutter).

Alt havner i `opptak/<dato>-<id>/`: `video.mp4`, `lyd.m4a`, `chat.txt`,
`transkript.vtt` og **`INFO.md`** — som samler dato, varighet, delelenke, alle
spørsmål fra chatten, siste 10 minutter og hele chatten. Mediefilene og chatten
holdes utenfor git (størrelse + persondata).

**Lange sendinger** (workshops på flere timer) deles av Zoom i segmenter, hver
med egne filer. Nedlastingslenkene kan gi 404 til **siste** segment er ferdig
behandlet, også for filer som står som ferdige. Det kan ta flere timer. Chat-
fila dukker ofte opp sist. Vent og kjør på nytt; ikke anta at opptaket mangler.

## 3. Transkriber på norsk

**Ikke bruk Zooms egen tekst på norske sendinger.** ASR-en står på engelsk og
gjør norsk tale til vrøvl — «Claude Code» blir «CloudKord». Undertekstene kan
til og med komme ut som svensk. Kjør lydfila gjennom Whisper (lokalt eller via
en API-tjeneste) med språk satt til norsk, og lagre en ren tekstversjon uten
tidskoder ved siden av opptaket. Et møteverktøy som kan norsk (f.eks.
Fireflies) holder også — men bot-en kan falle ut på lange sendinger.

## 4. Les og rapporter

Fra INFO.md og transkriptet:

- **Spørsmål:** hvor mange kom, og hvilke ble ikke besvart live.
- **Siste 10 minutter av chatten:** her melder folk interesse for workshops og
  events. Navn + hva de skrev, ordrett.
- **Løftesjekk:** les hele transkriptet og chatten. List hvert løfte du ga
  («jeg sender», «jeg legger ut», «dere får», «jeg sjekker») med hvem det
  gjelder, når og status: levert eller ikke levert.
- **Lenker du delte:** samle alle lenker du delte i chatten (artifacts,
  dokumenter, maler) med tittel. De skal med i leksjonen.

## 5. Til Skool

`hent` lager **`SKOOL.md`** automatisk — leksjonspakken. Bygg den på nytt når
transkript og video-URL finnes:

```bash
python3 kursopptak.py pakke opptak/<dato>-<id> --transkript-url <url> --video-url <url>
```

1. **Leksjon** i riktig kurs (kurssendinger i opptakskurset, velkomst i
   «Begynn her»-kurset): beskrivelse, transkript, og som ressurser:
   opptakslenken + lenkene du delte. Video kun som lenke.
2. **Post i feeden** i riktig kategori: hva vi gikk gjennom, lenke til
   leksjonen, lenkene. Bruk kategorinavnet nøyaktig slik det står i gruppa.
3. **Vis eieren utkast til leksjon og post, og løftelista, før noe
   publiseres.** Publiser på ja. Uleverte løfter blir oppgaver hos
   assistent-agenten.

### Skool-teknikk som har kostet tid

- Skool har ingen offisiell API. Enten nettleseren, eller en egen
  tilkobling som logger inn som en egen admin-bruker for agenten (ikke din).
- Send alltid med gruppens slug. Uten den havner kallet i feil gruppe, og
  det ser ut som om kategoriene mangler.
- Classroom-kall trenger kursets navnefelt (slug), ikke kurs-ID-en.
- Video som innebygd YouTube-ID kan gi serverfeil — legg den som ressurslenke.
- Titler med parentes kan feile. Dropp parentesene.

## Faste regler

- Aldri publiser noe uten eierens ja.
- Aldri nevn opptak i invitasjoner til sendinga. Da møter færre opp live.
- Chat og transkript inneholder navn og spørsmål fra medlemmer. De deles i
  leksjonen, aldri utenfor gruppa.
- Chat-fila kan la vente på seg noen minutter etter møteslutt. Kjør på nytt
  hvis den mangler.
