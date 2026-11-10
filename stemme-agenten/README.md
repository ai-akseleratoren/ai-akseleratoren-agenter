# Stemme — fra diktat til ferdig tekst

Stemme er den enkleste agenten i biblioteket, og den de fleste bruker mest. Du
snakker inn en tekst på mobilen, limer inn resultatet, og får tilbake en ryddet
versjon i riktig format — klar til å kopiere.

**Problemet den løser:** Diktering er fem ganger raskere enn å skrive, men
resultatet er fullt av «eh», gjentakelser og setninger som starter på nytt
midtveis. Så bruker du tjue minutter på å rydde, og har spart ingenting.

Ber du en vanlig chatbot om å «rydde dette», får du noe annet tilbake: den
skriver om til sitt eget språk, legger på høflighetsfraser du ikke sa, og
gjør deg til en litt kjedeligere versjon av deg selv.

**Hva agenten gjør:**
- Fjerner fyllord, falske starter og gjentakelser
- Retter tale-til-tekst-feil, også i navn og tall
- Kjenner igjen om det er en e-post, et notat, et innlegg eller en melding, og
  formaterer deretter
- Leverer i en kodeblokk du kan kopiere rått

**Hva agenten ALDRI gjør:** legger til poenger du ikke sa, bytter ut ordene
dine med finere ord, eller gjør en muntlig tekst formell.

**Du trenger:**
- Claude Code
- En måte å diktere på — mobilens eget tastatur holder

**Kom i gang:**
1. Opprett `.claude/skills/stemme/` i prosjektet ditt og lim inn `SKILL.md`.
2. Diktér noe på mobilen. En e-post du uansett skulle skrevet.
3. Lim det inn i Claude Code og si «stemme».
4. Les gjennom. Er tonen blitt stivere enn din egen, si fra — og legg
   rettelsen inn i seksjonen «Tilpass til deg selv», så gjør den ikke samme
   feil igjen.

> Tips: kjører du agentene dine på en server med en Telegram-bot, legg Stemme
> inn der også. Da dikterer du, sender, og får ferdig tekst tilbake uten å
> åpne maskinen.

> Tips: den blir best når du gir den dine egne regler. «Aldri utropstegn»,
> «alltid du-form», «kort i Slack» — tre linjer er nok til at teksten begynner
> å høres ut som deg.
