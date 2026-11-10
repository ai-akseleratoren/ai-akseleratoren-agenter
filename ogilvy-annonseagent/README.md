# Ogilvy — annonseagenten

En AI-agent som eier alt som bruker annonsebudsjett i bedriften din: bygger
kampanjer, skriver annonsetekst i DIN stemme, passer på at annonsene er satt
opp riktig og rapporterer ekte tall fra CRM-et og betalingssystemene. Ikke
fra pikselen.

## Problemet den løser

- Annonsetall fra Meta lyver. Pikselen overrapporterer, og du tar beslutninger
  på feil grunnlag.
- Du vet ikke hvilken annonse som faktisk solgte, fordi salg kommer inn på
  kort, faktura og bankoverføring.
- En kampanje satt opp mot feil land eller med feil konverteringsevent kan
  brenne tusenvis av kroner før noen ser det.
- Kampanjer blir stående og brenne penger etter at eventet er over.
- Annonsetekst skrives i hastverk og publiseres uten kvalitetssjekk.

## Hva agenten gjør

- Bygger kampanjer, alltid pauset, med standard UTM-er og riktig
  konverteringsevent
- Skriver annonser i tre lengder, uten dato, i din stemme
- Oppsettvakt hver time: land, språk, side, UTM, datoer og ukestak per land.
  Si fra med en gang, pause aldri selv
- Salg per annonse hver mandag: alle salg (kort, faktura, bank) koblet til
  annonsen som brakte dem
- Konkurranseanalyse i Ads Library med levetid som vinnersignal

## Hva agenten ALDRI gjør

Aktiverer annonser eller øker budsjett uten ditt ja. Publiserer tekst uten
kvalitetssikring. Endrer priser. Siterer pikseltall som sannhet. Eneste
unntak: nødpause når siden er nede eller eventet har sluttet å fyre, og da
får du beskjed med bevis innen en time.

## Du trenger

- Claude Code
- Meta Marketing API-token for annonsekontoen (lesing holder for analyse og
  oppsettvakt, `ads_management` for å bygge)
- Tilgang til CRM-et ditt (f.eks. GoHighLevel) for å telle ekte leads
- Stripe og eventuelt bank for salgsrapporten
- Slack hvis vakten skal poste funn
- En mappe/repo der agenten kan lagre annonseutkast og endringslogg

## Kom i gang

1. Kopier `SKILL.md` og mappa `scripts/` til `.claude/skills/ogilvy/`.
2. Tilpass SKILL.md: navnet på CRM-et, hvem som er beslutningstaker og hvem
   som kvalitetssikrer tekst.
3. Kopier `.env.example` til `.env` og fyll inn (aldri i git).
4. Test oppsettvakten uten å poste noe:
   `python3 scripts/oppsettvakt.py --selftest`, og så
   `set -a; . ./.env; set +a; python3 scripts/oppsettvakt.py`
5. Test med en ren leseoppgave: «Ogilvy, gi meg analyse på siste 7 dager.»
6. Når du stoler på tallene: ta i bruk bygg- og tekstmodus. Alt opprettes
   PAUSET. Du aktiverer selv.
7. Sett oppsettvakten som scheduled task hver time på dagtid med `--send`.

## Reglene som aldri bøyes

1. Ingen dato i annonser. Datoen bor på landingssiden.
2. Aldri trafikk til en side som ikke er bekreftet klar.
3. CPL og salg rapporteres fra CRM-et og betalingssystemene, aldri fra pikselen.
4. Pause er alltid lov. Aktivering koster penger og krever ditt eksplisitte ja.
