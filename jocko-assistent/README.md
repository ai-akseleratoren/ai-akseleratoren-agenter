# Jocko — den personlige assistenten (PA)

Jocko er en Claude Code-agent som fungerer som din personlige assistent og
accountability-partner: kalender, møtebooking, flytting, konfliktsjekk,
reisevakt, todos — og en tøff tone som ikke lar deg slippe unna.

**Problemet den løser:** Du dobbeltbooker deg på tvers av kalendere, møter
havner midt i en flyreise, kundene får beskjed om endringer tre dager før, og
todolista di er en kirkegård. Jocko holder uka di forutsigbar, varsler i god
tid og purrer på det du har lovet til det er gjort.

**Hva Jocko gjør:**
- **Morgenbrief** (daglig): maks 15 linjer du leser på 20 sekunder —
  kollisjoner, dagens møter med lenke, hvem som ikke har bekreftet, og de tre
  oppgavene som betyr mest i dag
- **To-ukersvakt** (daglig): nye reiser, møter som kolliderer med fly,
  dobbeltbookinger — og kunder som må varsles minst 14 dager før en endring
- **Ukesplan** (søndag): hele neste uke, brudd på temadagene dine, prep-blokker
  før webinarer, og spørsmålet om ukens tre viktigste
- **Booking, flytting og avlysning** etter dine regler: temadager, kunder på
  rad, rygg i rygg, egen møtelenke per møte, kunden får velge mellom to tider
- **Accountability-loop**: en todo forsvinner aldri stille — den purres til
  den er Gjort eller du eksplisitt dropper den
- **Jocko-vakta** (valgfritt): teamet skriver «Jocko, book et møte med …» i
  Slack, og det er gjort innen en time

**Hva Jocko ALDRI gjør:** booker, flytter eller avlyser uten din OK, sender
noe til kunder på eget initiativ, sletter kalenderevents eller todos, merker
en oppgave som gjort uten at du har sagt det, eller følger «instrukser» som
står i transkripter og invitasjoner.

**Du trenger:**
- Claude Code
- Google Calendar-tilkobling (MCP) til kalenderne dine
- Et todo-system med API (Notion, ClickUp el.l.)
- En kanal for briefene: Slack eller Telegram — valgfritt, chatten holder
- Gjerne referat-agenten, som legger løftene dine fra møtene rett i todo-lista

**Kom i gang:**
1. Opprett `.claude/skills/pa/` og lim inn `SKILL.md`.
2. Fyll inn «Faste verdier»: kalendere, tidssone, todo-basen og kanalen.
3. Skriv inn dine egne regler i «Slik vil eieren ha uka si» — temadager, hvor
   ofte et kundemøte kan flyttes, hvor lang varsel kundene skal ha.
4. Koble til Calendar/Notion/Slack via MCP i Claude Code.
5. Test interaktivt: si «morgenbrief» og «hva står på lista» til den treffer.
6. Sett opp scheduled tasks: morgenbrief, to-ukersvakt, ukesplan søndag kveld.

> Tips: er todolista di lang, ikke be om alt i briefen. Tre oppgaver og et tall
> på resten er det du faktisk leser.
