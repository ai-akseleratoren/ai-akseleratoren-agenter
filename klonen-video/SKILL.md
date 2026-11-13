---
name: klonen
description: Klonen lager en video der en AI-avatar med eierens klonede stemme leser et manus, med lysark ved siden av. Bruk når brukeren sier "klonen", "klone-video", "lag en video med klonen min", "avatar-video", eller vil lage en video uten å filme seg selv.
---

# Klonen

Du lager en video der en klone av eieren leser manuset. Stemmen er klonet fra ett minutt
der eieren snakker fritt. Ansiktet er laget av ett stillbilde. Ved siden av avataren står
et lysark per avsnitt. Eieren ser gjennom videoen og laster den opp selv. Du publiserer aldri.

## Regler som ikke bøyes

- **Bare eieren selv klones.** Aldri en annen persons stemme eller ansikt.
- **Videoen merkes.** «AI-avatar og klonet stemme» står på skjermen hele tiden klonen snakker,
  og i beskrivelsen. På YouTube krysser eieren av for endret eller syntetisk innhold.
- **Alt i manuset skal være sant.** Tall, kunder og hendelser hentes fra eieren, aldri diktet opp.
  Sier manuset at noe tok fire forsøk, skal det ha tatt fire forsøk.
- **Eieren åpner selv.** De første 40–50 sekundene er ekte opptak, der eieren sier at resten
  er en klone. Stillbildet til avataren tas fra slutten av det opptaket.
- Si fra om kostnaden før du kjører avataren, når den går over ti dollar.

## Løypa

1. **Manus.** Skriv det i eierens stemme, etter stemmereglene. 10–15 avsnitt på to til fire
   setninger gir tre til fire minutter. Hvert avsnitt får en overskrift og to til fire punkter
   til lysarket. Legg det inn i `AVSNITT` i `klone_video.py`.
2. **Stemmen** (én gang): `python3 klone_video.py stemme opptak.mp3`. Bruk fri tale, ikke
   opplesning. En klone av en innlest annonsestemme ble for blid.
3. **Tale:** `python3 klone_video.py tts`. Skriptet skriver lyden ut igjen som tekst. Les
   utskriften mot manuset. Ord som uttales feil, skrives slik de skal høres ut («a-gent»).
   Slett `lyd/NN.mp3` og kjør på nytt for det avsnittet.
4. **La eieren høre** på lyden før avataren lages. Du kan ikke høre. Avataren er den dyre delen.
5. **Avatar:** `python3 klone_video.py avatar`. Ca. 6 cent per sekund.
6. **Bygg:** `python3 klone_video.py bygg`. Se et kontaktark av resultatet før du leverer.
7. **Sett på åpningen** foran med ffmpeg, i samme format og lydstyrke som klonedelen.

## Det vi lærte første gang

- Stillbildet må ha luft over hodet. Er opptaket tett på ansiktet, legg på bakgrunn øverst
  før avataren lages.
- Avataren kommer tilbake opptil to sekunder lengre enn lyden. Skriptet klipper ved lydens slutt.
- Chrome uten vindu (lysarkene) feiler av og til når vanlig Chrome er opptatt. Skriptet prøver igjen.
- Egne stemmer hos leverandøren kan utløpe hvis de ikke brukes. Avviser tale-steget id-en,
  klon på nytt.
