---
name: zoomleads
description: Hent «ja»-leads fra siste Zoom-webinar eller Q&A, match dem mot CRM-et og lag ringeliste til selgeren. Bruk når brukeren sier "zoomleads", "høst webinaret", "hent leads fra zoom", "hvem sa ja på webinaret" eller nevner ringeliste etter et webinar.
---

# Zoom-leads — ringeliste etter webinar

Én jobb: finn riktig møte, kjør høstingen, lever ringelisten. Hold konteksten
liten — skriptet gjør alt (Zoom-chat og Q&A → «ja»-signaler → CRM-match →
opportunities i målsteget → ringeliste-fil).

1. Finn møte-ID (hopp over hvis brukeren oppga den):
   ```bash
   python3 scripts/zoom_leads.py meetings --days 14
   ```
   Velg webinaret eller Q&A-en brukeren mener — typisk det med flest deltakere
   på den datoen de nevner.

2. Kjør hele flyten (idempotent — trygt å kjøre flere ganger):
   ```bash
   python3 scripts/zoom_leads.py harvest <meetingId>
   ```
   Legg til `--dry-run` hvis du vil se resultatet uten å røre CRM-et.

3. Les ringelisten i `ringelister/<dato>-<id>.md` og gjengi den for brukeren i
   tre bolker: **klare** (navn + telefon + hva de skrev), **tvetydige** (be
   brukeren peke på riktig kontakt), **umatchede**. Er `SLACK_WEBHOOK_URL`
   satt, er varselet allerede sendt — ellers minn om å dele lista med selgeren.

4. Commit ringelisten i repoet.

## Merknader

- Nøkler ligger i `.env` (gitignored). Mangler de, be brukeren følge
  Zoom Server-to-Server OAuth-oppskriften på marketplace.zoom.us og fylle ut
  `.env.example`.
- **Chat-filen kommer fra cloud recording.** Er webinaret nettopp ferdig, kan
  filen la vente på seg noen minutter — kjør harvest på nytt.
- **Tvetydige navn** («Kristian G») løses manuelt: brukeren peker på riktig
  kandidat, og du flytter kontakten til målsteget etter mønsteret i
  `upsert_opportunity` i skriptet.
- Skriptet fanger både rene «ja» og interesse-signaler («interessert»,
  «hvordan booker jeg»). Det siste er der de fleste leadsene ligger — folk
  svarer sjelden «ja» på et spørsmål ingen stilte dem.
- Legger du til nye signalord i `STRONG`, kjør `python3 zoom_leads.py selftest`
  etterpå.

## Etter hver høsting: varsle teamet

Send ÉN kort melding til teamkanalen eller til selgeren: antall deltakere,
antall «ja»-leads med fornavn, og at ringelisten er delt.

Eksempel: «Q&A i dag: 13 deltakere, 5 sa ja (Preben, Gudrun, Geir, Jonas,
Thomas) — ringelista er ute 🎿»

**Aldri telefonnumre eller e-postadresser i en gruppemelding.** Ringelista med
kontaktdetaljer går bare til den som skal ringe.
