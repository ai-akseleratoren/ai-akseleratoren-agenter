# Prelansering-sjekkliste

Kjøres på hver side, e-post, SMS-sekvens, sporingsoppsett og annonsekampanje før
den går live, uansett hvem som bygde den. Hver linje er **bestått**, **feilet**
eller **ikke aktuell**, med hva du sjekket.

Sjekk den ekte tingen: åpne den live siden, følg lenkene, les den faktiske
e-postteksten. Aldri døm ut fra kildekode eller en beskrivelse alene.

## Sider (påmelding, takk, kasse)

- [ ] Siden laster på mobil og PC, på kampanjens språk.
- [ ] Dato, klokkeslett og tidssone stemmer med kalenderoppføringen.
- [ ] Pris, garanti og frist stemmer med den frosne beslutningen for kampanjen.
- [ ] Påmeldingssiden nevner aldri opptak.
- [ ] Takkesiden ber folk finne og SVARE på bekreftelsesmailen, og har
      legg-til-i-kalender-lenker.
- [ ] Alle lenker og knapper går til riktig sted. Kassen fullfører i testmodus.

## Sporing

- [ ] Pikselen fyrer på den live siden (sjekket i annonseverktøyets
      hendelsesoversikt, ikke i kildekoden).
- [ ] Konverteringshendelsen i annonsesettet matcher siden annonsen peker på.
- [ ] Server-side-hendelser kommer fram og dedupliseres mot nettleserhendelsene.
- [ ] UTM-parametre når CRM-et på en testpåmelding.

## E-post og SMS

- [ ] Kvalitetssikreren har sjekket teksten.
- [ ] Første mail har legg-til-i-kalender-lenker.
- [ ] Tom linje mellom avsnitt overlever i e-postverktøyet.
- [ ] Hver sending har sin egen møtelenke. Aldri det personlige møterommet.
- [ ] Planen holder seg innenfor utsendingstaket.
- [ ] Kjøpere er tagget, så de ikke får salgsmail.
- [ ] En testsending til den interne testkontakten kom fram og ser riktig ut.

## Annonser (annonseagenten bygger, North Star sjekker)

- [ ] Ingen dato eller ukedag i noen annonse.
- [ ] Landingssiden har bestått sjekkene over før trafikken starter.
- [ ] Budsjett og målgruppe stemmer med godkjent brief.

## Resultat

Post resultatet i oppgaven: alt bestått, eller de feilede linjene som spørsmål
til eieren av arbeidet. Merk aldri noe som klart med en feilet linje, med mindre
eieren eller driftslederen godtar hullet skriftlig.
