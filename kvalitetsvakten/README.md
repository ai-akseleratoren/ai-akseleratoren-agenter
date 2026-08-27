# Kvalitetsvakten

En AI-agent som leser ledelsens kanal hver time og UTFØRER instruksjonene som
kommer der — tekstendringer, rapporter, kalenderoppdateringer, føring av
beslutninger og todo-er. Med synlig kvittering på hver eneste melding, så
ingenting faller mellom to stoler.

## Hvilket problem løser den?

- Ledelsen ber om småting i chat («fiks den formuleringen», «hva var CPL i
  går?») — og halvparten blir glemt.
- Ingen vet om agenten (eller kollegaen) har SETT en melding, langt mindre om
  den er utført.
- Beslutninger tas i tråder og forsvinner — ingen logg.

Kvalitetsvakten svarer på alt, kvitterer synlig med reaksjoner (👀 = lest,
✅ = utført), utfører det som er innenfor mandatet, og fører beslutninger og
oppgaver inn i loggen og todo-lista.

## Hva du trenger

- Claude Code med tilgang til teamkanalen (f.eks. Slack via MCP)
- En dedikert kanal der ledelsen skriver til agenten
- En mappe/repo der agenten kan redigere tekstfiler og føre logg
- Mulighet for planlagte oppgaver (kjøres hver time)

## Kom i gang

1. Kopier `SKILL.md` inn som `.claude/skills/kvalitetsvakt/SKILL.md`.
2. Fyll inn: kanalnavnet ditt, og hvem de 2–3 personene i ledelsen er (kun
   disse kan gi ordre — alle andre får svar, ikke handling).
3. Velg agentens prefiks-emoji, så alle ser at det er agenten som skriver.
4. Test manuelt: skriv en instruksjon i kanalen og be agenten kjøre én runde.
5. Sett den opp som planlagt oppgave hver time i arbeidstiden.

## Viktigste prinsipper

- **Kvitteringsregelen:** ingen melding fra ledelsen skal stå uten reaksjon.
  👀 når den er lest, ✅ når den er utført + kort svar i tråden.
- Kun navngitte personer kan gi ordre. Lenker og instruksjoner fra andre
  følges aldri.
- Agenten bruker aldri penger, sender aldri noe til kunder, deler aldri
  hemmeligheter — uansett hvem som ber.
- Alt som gjøres, committes og kvitteres med filnavn.
