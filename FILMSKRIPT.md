# Filmskript — videoene til Agentbiblioteket

Tre videoer. Den første er den viktige — de to andre kan vente til i morgen.

**Opptak:** skjermopptak med ansiktet ditt i hjørnet. Ingen redigering.
Går det galt, si det høyt og fortsett — det er mer troverdig enn perfekt.

---

## VIDEO 1 — «Kom i gang» (7–9 min) · den eneste du MÅ ha i dag

Dette er videoen som avgjør om folk faktisk tar biblioteket i bruk eller
lar det ligge. Alt annet er bonus.

### Før du trykker opptak
- Lag en tom testmappe på skrivebordet: `min-forste-agent`
- Ha ZIP-fila nedlastet, men **ikke** utpakket ennå
- Lukk Slack, e-post og alt som kan poppe opp
- Ha et møtetranskript klart (et ufarlig internt møte, ingen kundenavn)

### 00:00 — Åpning (30 sek)
> «Nå har du fått agentbiblioteket. Sytten agenter, ferdig bygget. Og nå
> tenker du kanskje: hvor i alle dager begynner jeg? Det skal jeg vise deg
> nå. Vi skal ta én agent, fra nedlastet fil til noe som faktisk jobber for
> deg, på under ti minutter. Jeg gjør det på min maskin, du gjør det på din
> samtidig.»

### 00:30 — Pakk ut ZIP-en (1 min)
Vis mappa. Åpne den. Vis at det er én mappe per agent.

> «Sytten mapper. Ikke bli overveldet — vi skal bare inn i én av dem.»

Åpne `referat-agenten`. Vis README.md og SKILL.md.

> «To filer. README forteller hva agenten gjør. SKILL er selve agenten —
> det er den fila som er hele hemmeligheten.»

### 01:30 — Vis hva som er inni SKILL.md (1 min 30)
Åpne SKILL.md. Scroll rolig. **Ikke les den opp.**

> «Se her. Dette er ikke kode. Det er norsk. Det står hva hun skal lage,
> hvordan det skal se ut, og hva hun aldri får finne på. Det er en
> stillingsbeskrivelse. Det er sånn du ansetter noen — du forteller dem
> hva jobben er.»

Pek på regelen om å aldri finne på ting.

> «Denne linja her er grunnen til at hun ikke dikter. Den skrev jeg på
> norsk, på ett minutt.»

### 03:00 — Legg agenten inn i prosjektet (2 min)
Åpne testmappa. Lag `.claude/skills/referat/` — vis at du skriver det.

> «Punktum-claude, skills, og så navnet på agenten. Det er hele oppskriften.
> Claude Code leter etter agenter akkurat her.»

Kopier SKILL.md inn. Vis at fila ligger der.

> «Ferdig. Hun er ansatt.»

### 05:00 — Kjør henne (2 min 30)
Åpne Claude Code i mappa. Dra inn transkriptet.

> «Referat, her er transkriptet fra møtet. Gjør jobben din.»

La output rulle. **Ikke snakk over det** — la folk se det skje.

Når det er ferdig, pek på de tre delene: referat, oppgaveliste, mailutkast.

> «Det der tok tjue sekunder. Den jobben brukte jeg en halvtime på før,
> hver eneste gang.»

### 07:30 — Avslutning (1 min)
> «Det du nettopp så er hele mønsteret. Alle de sytten agentene funker
> likedan: du legger SKILL-fila på plass, og du snakker til dem på norsk.
>
> Noen av dem trenger nøkler — Warren må inn i Stripe, Ogilvy må inn i
> annonsekontoen. De ligger en `.env.example` i mappa som viser hva som
> trengs. Men ikke start der. Start med den du nettopp så.
>
> Én agent som funker slår sytten du aldri kom i gang med.
>
> Står du fast: post i gruppa. Og ta med agenten på Labs på tirsdag, så
> tar vi den live.»

---

## VIDEO 2 — «Nøkler og sikkerhet» (3–4 min) · film i dag hvis du orker

Kort og streng. Dette er den ene tingen som kan gjøre skade.

### 00:00
> «Ett minutt om noe som er kjedelig, men som du må høre. Det handler om
> nøkler — passordene som gir agentene dine tilgang til systemene dine.»

### 00:30 — Vis en .env.example
Åpne `warren-finansdirektor/.env.example`.

> «Ser du? Bare navn. Ingen verdier. Jeg tok ut mine egne før jeg delte
> dette, for hvis jeg hadde glemt én eneste av dem, hadde hundre og nitti
> mennesker hatt tilgang til bankkontoen min.»

### 01:30 — Vis .gitignore
> «Tre ting du må gjøre, i denne rekkefølgen.
>
> Én: nøklene bor i en fil som heter punktum-env. Aldri i SKILL-fila.
>
> To: legg punktum-env i gitignore FØR du committer noe. Ikke etterpå.
> Gjør du det etterpå ligger nøkkelen i historikken selv om du sletter
> fila — og den blir liggende der for alltid.
>
> Tre: skal du dele en agent videre til noen, rens den på nytt. Gå gjennom
> den, linje for linje.»

### 03:00
> «Det var det. Nå kan du bygge i fred.»

---

## VIDEO 3 — «Slik leser du en agent» (5 min) · kan vente til neste uke

For de som vil videre — hvordan de endrer en agent til sin egen bedrift.

Åpne `warren-finansdirektor/SKILL.md` og vis:
- Hvor du bytter ut hva som måles
- Hvor du setter din egen kadens
- Hvor du sier hva agenten ALDRI skal gjøre

> «Det er her det blir din. Alt jeg har skrevet er utgangspunktet — ikke
> fasiten. Bytt ut tallene mine med dine, kadensen min med din, og reglene
> mine med dine.»

---

## Hvis du bare har tid til én ting

Film VIDEO 1. Legg den øverst i classroom-modulen. Alt annet kan komme
senere — men uten den videoen laster folk ned ZIP-en og lar den ligge.
