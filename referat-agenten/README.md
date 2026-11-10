# Referat-agenten — ingen møter uten oppfølging

Referat er en Claude Code-agent som tar møtene dine og sørger for at det som
ble avtalt faktisk skjer. Den sorterer hvert møte, og gir det akkurat det det
trenger: et kort notat til teamet, en oversikt til kunden, et tilbudsutkast
etter et salgsmøte, og dine egne løfter rett inn i todo-lista.

**Problemet den løser:** Referatet blir skrevet tre dager for sent, tilbudet
etter salgsmøtet kommer en uke etter at kunden var varm, og det du lovet i
møtet forsvinner. AI-sammendrag er raskere, men de glatter over og finner på —
«de ble sannsynligvis enige om…». Referat gjør det motsatte: alt som er
uklart merkes `[UKLART]`, og ingenting går ut før du har sagt ja.

**Hva agenten gjør:**
- Sorterer møtet: kunde, salg, intern, gruppe (webinar/kurs) eller privat
- **Kunde:** detaljert notat til teamet, og en kort, varm oversikt til kunden
  på møtets språk — uten priser eller noe internt
- **Salg:** tilbudsutkast i e-post-utkastene dine samme dag, og et kort
  strateginotat med tre spørsmål til neste møte
- **Intern:** beslutninger og hvem gjør hva, med dato
- **Dine løfter:** bare det du selv sa i jeg-form blir oppgaver. Er den i tvil,
  lar den det ligge
- Kan gå gjennom alle nye møter selv flere ganger om dagen og legge alt fram
  for én ✅

**Hva agenten ALDRI gjør:** finner på noe som ikke ble sagt, sender noe til
kunden eller teamet uten din ✅, skriver priser i en kundekanal, tar med noe
privat, peker ut hvem som gjorde feil, eller oppretter kontakter i CRM-et.

**Du trenger:**
- Claude Code
- Et transkript — fra et møteopptaks-verktøy (Fireflies, Otter, Teams,
  Zoom) eller bare limt inn tekst
- Valgfritt: Slack (kanal per kunde), e-post-utkast via Gmail, CRM med API og
  en todo-base, hvis den skal gå av seg selv

**Kom i gang:**
1. Opprett `.claude/skills/referat/` i prosjektet ditt og lim inn `SKILL.md`.
2. Start manuelt: lim inn et transkript og si «lag referat».
3. Les `[UKLART]`-markeringene. De er ikke feil — de er stedene møtet faktisk
   var utydelig, og som regel det du må rydde opp i.
4. Når notatene treffer: koble på opptaksverktøyet, kanalene og todo-basen,
   og sett opp sveipen som scheduled task.
5. Godkjenn med ✅ i noen uker før du vurderer å la noe gå ut automatisk.

> Tips: den viktigste regelen er den om løfter. Bare det du selv sa «jeg gjør»
> om blir oppgaver. Ellers blir todo-lista full av ting noen andre mente du
> burde gjøre.
