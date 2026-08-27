# Webinar-telleren

En AI-agent som hver dag teller påmeldte til neste webinar, sammenligner mot
annonseforbruket, og varsler deg med en kort, skannbar rapport. Med på kjøpet:
en tagg-vakt (Python) som fanger opp påmeldinger som havner i feil
e-postsekvens i CRM-et.

## Hvilket problem løser den?

- «Hvor mange er påmeldt egentlig?» — Meta sier ett tall, CRM-et et annet, og
  ingen vet fasiten.
- Gjenbrukte påmeldingsskjemaer tagger folk inn i FORRIGE webinars sekvens —
  de får bekreftelse med død møtelenke uten at noen merker det.
- Du oppdager for sent at annonsene gir dyre påmeldinger.

Telleren rapporterer daglig: totalt påmeldte, nye siste døgn, CPL per
annonsesett — og tagg-vakta retter feiltaggede påmeldinger før sekvensen
rekker å gjøre skade.

## Hva du trenger

- Claude Code og Python 3 (kun standardbibliotek + curl)
- CRM med API-tilgang (oppskriften bruker GoHighLevel — tilpass endepunktene
  om du bruker noe annet)
- Meta Marketing API-token (lesing) hvis du kjører annonser
- Ev. webinar-plattformens API (Zoom e.l.) som fasit-kilde

## Kom i gang

1. Kopier mappen inn i prosjektet ditt, `SKILL.md` til
   `.claude/skills/webinar-teller/SKILL.md`.
2. Kopier `.env.example` til `.env` og fyll inn nøkler, skjema-ID og taggene
   dine.
3. Test telleren manuelt: «Kjør webinar-telleren.» Sjekk at tallene stemmer
   med det du ser i CRM-et.
4. Trenger du tagg-vakta: kjør `python3 webinar_vakt.py` (tørrkjøring — rører
   ingenting) og deretter med `--fiks` når du ser at den finner de riktige.
5. Sett begge opp som planlagte oppgaver (telleren daglig, vakta oftere i
   dagene før webinaret).

## Viktigste prinsipper

- Påmeldingssiden er eneste fasit for dato — aldri stol på at datoen i en
  oppgavefil er fersk.
- CRM-tallet er fasit for påmeldinger; Meta-pikselen brukes bare som relativ
  pekepinn.
- Filtrer alltid bort test- og interne påmeldinger før du rapporterer.
- Telleren leser og rapporterer — den endrer aldri annonser eller kontakter.
