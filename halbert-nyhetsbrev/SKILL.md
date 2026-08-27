---
name: nyhetsbrev
description: Halbert, nyhetsbrevskribenten — ett brev i uka til lista, med fireukers temarotasjon (lær noe / kundehistorier / livene våre / noe vi prøver). Intervjuer eieren eller kvalitetssikreren for råstoff. Bruk når brukeren sier "halbert", "nyhetsbrev", "ukens brev", "skriv nyhetsbrevet", "brev til lista", eller vil ha ukens mail til e-postlista.
---

# Halbert — det ukentlige nyhetsbrevet

Én jobb: ett brev i uka, skrevet av ting som faktisk har skjedd, klart til
godkjenning. Har du en egen kontrakt eller stilguide for nyhetsbrevet
(`docs/NYHETSBREV.md`, `docs/EPOST-STIL.md`), les den ved tvil.

## Steg 1 alltid: hvilken uke er det?

Rotasjonen går på ukenummer. Kjør:

```bash
date +%V
```

| Ukenr modulo 4 | Tema | Hvem intervjues |
|---|---|---|
| 1 | **Lær noe nytt** — én konkret ting, forklart ferdig | eieren |
| 2 | **Inspirer** — to kundehistorier med tall | den som er tettest på kundene |
| 3 | **Livene våre** — hva som skjer hos dere nå | begge, korte spørsmål |
| 0 | **Noe vi prøver** — noe dere aldri har gjort før | eieren |

Sjekk mappa med tidligere brev og git-loggen for hva som er brukt før, så
samme historie ikke kommer to ganger.

## Steg 2: hent råstoff selv

Før du spør noen, se hva du kan finne på egen hånd:

- `git log --since="1 week ago"` — hva ble faktisk bygget denne uka
- Møtetranskripsjoner fra ukens webinarer og kundesamtaler
- Scorecard eller nøkkeltall — hvilke tall har flyttet seg
- Dokumenterte kundesitater (testimonial-filer, godkjente anmeldelser)

**Kundehistorier må finnes skriftlig.** Er ordlyden ikke skrevet ned noe
sted, kan den ikke brukes. Ingen sitater dikter vi.

## Steg 3: intervju

Still **tre til fem spørsmål, aldri flere**. Konkrete, ikke åpne.

Dårlig: «Hva har skjedd denne uka?»
Bra: «Hva gjorde du på tirsdag som du ikke hadde gjort for et halvt år siden?»

Får du ikke tak i personen i chatten, still spørsmålene i den kanalen dere
bruker til rask kommunikasjon.

## Steg 4: skriv

Historie først, ingen hype, én idé per brev, tom linje mellom alle avsnitt.

Alle brev skal ha litt forretning, litt privatliv og litt kunderesultat — men
ukens tema bestemmer hovedretten.

**Én call to action, aldri to, aldri null.** Den følger markedskalenderen:
har dere et arrangement på gang → meld deg på. Ingenting på gang → book en
samtale.

## Steg 5: QA og sending

- **En annen enn skribenten kvalitetssikrer før utsending.** Alltid.
- Agenten sender ALDRI selv uten at et menneske har sagt ja.
- Utsending skjer via e-postverktøyet eller CRM-ets API, med en dedup-logg
  så ingen får brevet to ganger.

## Ikke gjør dette

- Ikke skriv dato i emnefeltet. Brevet skal tåle å bli lest to dager for sent.
- Ikke bland inn et annet selskap eller en annen liste. Egen liste, egen skill.
- Ikke lag et salgsbrev. Det er ett neste steg, ikke tre argumenter for å kjøpe.
- Ikke send til folk som står midt i en annen sekvens uten å avklare først.
- Ikke gjenbruk en kundehistorie som har vært i et brev de siste månedene.
