# Referat-agenten — møtereferat som faktisk blir brukt

Referat er en Claude Code-agent som tar et møtetranskript og leverer tre ting:
et kort referat, en hvem-gjør-hva-liste med frister, og et ferdig utkast til
oppfølgingsmail. Alltid på norsk, uansett hvilket språk møtet gikk på.

**Problemet den løser:** Referatet blir skrevet av den som husker møtet best,
tre dager for sent, og oppgavene forsvinner. AI-sammendrag er raskere, men de
glatter over og finner på — «de ble sannsynligvis enige om…». Referat-agenten
gjør det motsatte: alt som er uklart i transkriptet merkes `[UKLART]` i stedet
for å gjettes.

**Hva agenten gjør:**
- Tar transkript limt inn, som filsti, eller hentet fra møteopptaks-verktøyet
- Referat på maks 10 linjer: hva ble diskutert, hva ble besluttet
- Hvem gjør hva, per person, med frist — og en egen «uavklart eier»-seksjon
- Utkast til oppfølgingsmail, klar til å sendes eller limes inn
- Regner om «på tirsdag» til faktisk dato ut fra møtedatoen

**Hva agenten ALDRI gjør:** finner på noe som ikke ble sagt, lager referat av
et AI-sammendrag uten å si fra, eller sender mailen uten at du har sagt «send».

**Du trenger:**
- Claude Code
- Et transkript — fra et møteopptaks-verktøy (Fireflies, Otter, Teams,
  Zoom-transkripsjon) eller bare limt inn tekst
- Eventuelt en e-postkanal eller CRM med API, hvis agenten skal kunne sende

**Kom i gang:**
1. Opprett `.claude/skills/referat/` i prosjektet ditt og lim inn `SKILL.md`.
2. Tilpass avsenderen og sendekanalen i seksjonen «Sending» — eller stryk hele
   seksjonen hvis du vil kopiere mailen inn manuelt.
3. Lim inn et transkript i Claude Code og si «lag referat».
4. Les gjennom `[UKLART]`-markeringene. De er ikke feil — de er stedene
   møtet faktisk var utydelig, og som regel det du må rydde opp i.
5. Si «send» først når du har lest utkastet.

> Tips: koble agenten til møteopptaks-verktøyet ditt, så holder det å si
> «lag referat fra gårsdagens kundemøte».
