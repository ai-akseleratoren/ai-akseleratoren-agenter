# Ogilvy — annonseagenten

En AI-agent som eier alt som bruker annonsebudsjett i bedriften din: bygger
kampanjer, skriver annonsetekst i DIN stemme, overvåker forbruk og rapporterer
ekte tall fra CRM-et — ikke fra pikselen.

## Hvilket problem løser den?

- Annonsetall fra Meta lyver: pikselen overrapporterer, og du tar beslutninger
  på feil grunnlag.
- Kampanjer blir stående og brenne penger etter at eventet er over.
- Annonsetekst skrives i hastverk, uten system, og publiseres uten kvalitetssjekk.
- Ingen sjekker hva konkurrentene faktisk kjører — og hvor lenge.

Ogilvy gjør dette til faste rutiner med klare regler, og rører ALDRI penger
uten at du sier ja.

## Hva du trenger

- Claude Code installert
- Meta Marketing API-token med tilgang til annonsekontoen din (kun lesing holder
  for analyse-modus)
- Tilgang til CRM-et ditt (f.eks. GoHighLevel) for å telle ekte leads
- En mappe/repo der agenten kan lagre annonseutkast og endringslogg

## Kom i gang

1. Kopier `SKILL.md` inn i prosjektet ditt som `.claude/skills/ogilvy/SKILL.md`.
2. Les gjennom og tilpass: sett inn navnet på CRM-et ditt, hvem som er
   beslutningstaker og hvem som kvalitetssikrer tekst.
3. Legg API-nøklene dine i en `.env`-fil i prosjektet (aldri i selve skillen).
4. Test med en ren leseoppgave først: «Ogilvy, gi meg analyse-modus på siste
   7 dager.»
5. Når du stoler på tallene: ta i bruk bygg- og tekst-modus. Husk at alt
   opprettes PAUSET — du aktiverer selv.

## De fire reglene som aldri bendes

1. Ingen dato i annonser — datoen bor på landingssiden.
2. Aldri trafikk til en side som ikke er bekreftet klar.
3. CPL og salg rapporteres fra CRM-et, aldri fra pikselen.
4. Pause er alltid lov. Aktivering koster penger og krever ditt eksplisitte ja.
