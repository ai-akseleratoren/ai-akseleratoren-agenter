---
name: kursopptak
description: Hent opptak, chat og transkript fra Zoom-sendingene dine og gjør dem klare for Skool. Bruk når brukeren sier "kursopptak", "hent opptaket", "ukas sending", "last ned Zoom-opptaket", "legg ut i Skool", eller spør om chatten fra en sending.
---

# Kursopptak — fra Zoom til Skool

Sendingene kjøres ofte fra en annen Zoom-bruker enn din egen, og gjerne på et
fast møterom (PMI). Sett inn ditt eget møte-ID i skriptet. Kjøres de fra en
felles konto, må API-nøkkelen tilhøre den kontoen.

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

Alt havner i `opptak/<dato>-<id>/`: `video.mp4`, `lyd.m4a`,
`chat.txt`, `transkript.vtt` og **`INFO.md`** — som samler dato, varighet,
delelenke, alle spørsmål fra chatten, siste 10 minutter og hele chatten.
Mediefilene og chatten er gitignorert (størrelse + persondata); INFO.md commites.

## 3. Les INFO.md og rapporter

Rapporter: hvor mange spørsmål som kom, hvilke som ikke ble besvart live, og
alt i «Siste 10 minutter» — det er der folk melder interesse for workshops og
events. Navn + hva de skrev, ordrett.

## 4. Til Skool

`hent` lager **`SKOOL.md`** automatisk — leksjonspakken du limer inn i Classroom.
Bygg den på nytt med transkript-id og video-URL når de finnes:

```bash
python3 kursopptak.py pakke opptak/<dato>-<id> --transkript <id> --video-url <url>
```

**Ikke bruk Zooms eget transkript på norsk.** ASR-en står på engelsk og gjør norsk
tale til vrøvl — «Claude Code» blir «CloudKord». Last heller lydfila opp til en
transkriberingstjeneste som kan norsk, eller kjør den gjennom Whisper.

## Merknader

- Zoom-nøklene ligger i `.env` i repo-roten (`ZOOM_*`). Token-et har
  `cloud_recording:read:admin` per bruker, men **ikke** `/meetings/{id}/recordings`
  og **ikke** brukerlisting — derfor er vertskontiene hardkodet i `HOSTS` i skriptet.
  Flyttes sendinga til en ny vert, må `HOSTS` utvides.
- Chat-fila kommer fra cloud recording og kan la vente på seg noen minutter
  etter møteslutt. Kjør på nytt hvis den mangler.
