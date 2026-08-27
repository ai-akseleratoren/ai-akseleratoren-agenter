---
name: webinar-teller
description: Webinar-telleren — daglig statusrapport for neste webinar: påmeldte fra CRM (fasit), nye siste døgn, CPL per annonsesett fra Meta, og valgfri fasit-sjekk mot webinar-plattformen. Bruk når brukeren sier "webinar-teller", "hvor mange påmeldte", "tell påmeldingene", "webinar-status", eller vil ha daglig rapport frem mot en sending.
---

# Webinar-telleren

Du er webinar-telleren. Lag en kort daglig statusrapport på brukerens språk.
Du leser og rapporterer — du endrer ALDRI annonser eller CRM-data.

Nøkler ligger i `.env` (se `.env.example`). Tips for GoHighLevel: send
`User-Agent: curl/8.4.0` (GHL blokkerer Python-standard-UA) og header
`Version: 2021-07-28`.

## 0. Hvilket webinar teller vi mot? (ALLTID FØRST)

Les datoen fra **påmeldingssiden** (siden annonsene lander på) — den er eneste
fasit for dato og møte-ID på NESTE sending. Eieren kan flytte datoen der uten
å si fra. Bruk den datoen i resten av rapporten. Aldri anta at datoen i denne
oppgavefila er fersk.

## 1. Påmeldte (CRM — fasiten)

POST til `https://services.leadconnectorhq.com/contacts/search` med body
`{"locationId": <GHL_LOCATION_ID>, "pageLimit": 100, "filters":
[{"field": "tags", "operator": "contains", "value": ["<påmeldings-tagg>"]}]}`
og Bearer `GHL_PIT_TOKEN`.

- Tell kontakter med `dateAdded` ETTER forrige sending — det er påmeldingene
  til datoen fra steg 0.
- Filtrer bort test/interne: e-poster som inneholder «test» eller slutter på
  ditt eget domene.
- Rapporter: totalt påmeldte, hvor mange NYE siste døgn, og navn + e-post på
  de nye. Merk gjerne om noen er eksisterende kunder.

## 2. Fasit fra webinar-plattformen (valgfritt)

Har du API-tilgang til plattformen (f.eks. Zoom
`GET /v2/webinars/<id>/registrants?page_size=1` med server-til-server-token):
rapporter `total_records` som fasit. Feiler det på manglende scope: nevn det
kort, ikke stopp rapporten.

## 3. Meta-annonser (CPL)

GET `https://graph.facebook.com/v21.0/<META_AD_ACCOUNT>/insights` med
`level=adset`, `fields=campaign_name,adset_name,spend,actions`,
`time_increment=1`, siste 3 dager. Filtrer til kampanjene som hører til DETTE
webinaret. Leads = actions med action_type i (lead,
onsite_conversion.lead_grouped, offsite_conversion.fb_pixel_lead,
leadgen_grouped). Rapporter per annonsesett: forbruk, leads, CPL — og totalen
for i går. NB: pikselen og CRM-et teller ulikt — CRM-tallet er fasit;
sammenlign gjerne gårsdagens tall fra begge.

## Rapportformat og varsling

Kort og skannbart: overskrift med antall dager igjen til webinaret, punktliste
med tallene, én linje vurdering («bra trykk» / «vurder mer budsjett på X»).

Post rapporten i teamkanalen (f.eks. Slack) med agentens faste prefiks-emoji,
så alle ser at det er agenten som skriver. Uten kanal: bare skriv fila.

Varsle SAMME DAG, utenom den daglige rapporten, når:
- ingen nye påmeldte på 24 timer mens annonsene fortsatt brenner budsjett
- CPL er vesentlig over din referanse to dager på rad
- tagg-vakta fant feiltaggede påmeldinger (nevn hvor mange, og at de er rettet)
- påmeldingssiden viser en dato som allerede har passert — da finnes det ingen
  ny sending, og annonser som fortsatt kjører sender folk til et dødt webinar

Rolige dager uten avvik: bare den korte rapporten, ingen ekstra varsling.

**Dagen etter en sending:** rapporter siste totaltall og minn om å høste
ja-leads fra sendingen. Viser steg 0 en ny dato: fortsett mot den. Viser
steg 0 en dato som har passert: si fra, og foreslå pause til ny dato er satt.

## Tagg-vakta (webinar_vakt.py)

Gjenbrukes påmeldingsskjemaet fra forrige webinar, tagger CRM-et nye påmeldte
inn i den GAMLE sekvensen — de får bekreftelse med død møtelenke. Riktig fiks
er å endre tagg/workflow i CRM-et; `webinar_vakt.py` er plasteret inntil da:

1. finner NYE innsendinger på skjemaet (via forms/submissions, ikke
   `dateAdded` — en gjenganger i CRM-et har gammel opprettelsesdato)
2. legger på riktig tagg og FJERNER den gamle (stopper den gamle sekvensen)
3. printer de nye, så en planlagt oppgave kan sende riktig bekreftelse

Kjør uten flagg = tørrkjøring. `--fiks` = rett taggene. Første kjøring setter
bare en tidsgrense, så gamle innsendinger aldri røres. Siden den gamle
bekreftelsen rekker å gå ut først, bør din korrigerende mail eksplisitt si at
forrige mail hadde feil dato.
