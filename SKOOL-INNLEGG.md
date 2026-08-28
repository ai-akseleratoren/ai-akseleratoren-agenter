# Skool-innlegg — Kunngjøringer

**Tittel:** Agentbiblioteket er ute - alle mine 17 agenter, klare til bruk

---

Da er den her: hele agentbiblioteket mitt ligger nå klart til dere.

Dette er ikke maler eller eksempler. Dette er de faktiske agentene som driver bedriften min hver eneste dag — Warren som lager finansrapporten min hver søndag, Alfred som rydder fire innbokser, Ogilvy som passer på annonsene. Jeg har renset dem for mine nøkler og mine kundedata, og gjort dem klare til å omskoleres til DIN bedrift.

ZIP-fila ligger vedlagt nederst. Last den ned, så har du alt.

SLIK KOMMER DU I GANG — helt fra bunn

1. Last ned ZIP-fila nederst i innlegget og pakk den ut et sted du finner igjen.

2. Åpne mappa og velg ÉN agent — ikke sytten. Les README-fila som ligger i den mappa. Den forteller hva agenten gjør og hva du trenger.

3. I ditt eget prosjekt lager du mappa .claude/skills/ og legger agentens SKILL.md der, i en undermappe med agentens navn. Eksempel: .claude/skills/referat/SKILL.md

4. Ligger det en .env.example i agentmappa: kopier den til .env og fyll inn dine egne nøkler. Legg .env i .gitignore FØR du committer noe som helst.

5. Åpne Claude Code i prosjektet ditt og si navnet på agenten. Så starter den.

HAR DU ALDRI GJORT DETTE FØR? START HER

Ta Referat-agenten eller Jocko. De trenger ingen integrasjoner og ingen nøkler — du er i gang på et kvarter og ser resultatet samme dag. Referat-agenten tar et møtetranskript og gir deg kort referat, hvem-gjør-hva-liste med frister, og utkast til oppfølgingsmail. Jocko er den personlige assistenten min.

Ikke start med Warren eller Ogilvy. De er de kraftigste, men de krever at du kobler på systemene dine først. Ta dem i uke to.

DETTE FÅR DU

Økonomi: Warren (finansdirektør med ukentlig scorecard), Luca (fakturerer og purrer)

Marked og salg: North Star (markedssjef), Ogilvy (annonser), Annonse-analytikeren (dypanalyse av kontoen din), Copy-maskinen (skriver i din stemme uten å finne på ting), Halbert (nyhetsbrev), Rubin (innhold), Zoom-leads-agenten, Webinar-telleren, Sully (funnelvakt)

Drift og hverdag: Jocko (assistent), Alfred (e-post), Referat-agenten, Kvalitetsvakten, WhatsApp-broen

Og Wenger, som setter fotballaget mitt. Fordi agenter ikke bare er business.

DEN VIKTIGSTE REGELEN: HOLD NØKLENE DINE TRYGGE

Jeg renset alt for mine egne nøkler før jeg delte dette. Gjør det samme når du bygger videre:

Nøkler bor i .env-fila. Aldri i SKILL.md, aldri i git. Legg .env i .gitignore FØR første commit — gjør du det etterpå, ligger nøkkelen fortsatt i historikken selv om du sletter fila. Kundedata, telefonnumre og e-postlister hører ikke hjemme i et repo. Og skal du dele agenten din videre til noen: rens den på nytt, på samme måte.

STÅR DU FAST?

Post spørsmålet her i gruppa. Noen har alltid svart før dagen er omme. Og på Labs hver tirsdag bygger vi sammen, live — ta med agenten du sitter fast på, så tar vi den der.

Én siste ting: du trenger ikke sytten agenter. Du trenger ÉN som funker. Start der, så kommer resten av seg selv.

Kjør på 🚀
