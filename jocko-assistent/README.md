# Jocko — den personlige assistenten (PA)

Jocko er en Claude Code-agent som fungerer som din personlige assistent og
accountability-partner: kalender, møtebooking, konfliktsjekk, oppfølging av
det du lover i møter, todos — og en tøff tone som ikke lar deg slippe unna.

**Problemet den løser:** Du lover ting i møter som forsvinner, du dobbeltbooker
deg på tvers av kalendere, og todolista di er en kirkegård. Jocko fanger opp
forpliktelsene dine automatisk, purrer til de er gjort, og gir deg dagen og
uka ferdig tygget — hver morgen, uten at du spør.

**Hva Jocko gjør:**
- **Morgenbrief** (daglig): konflikter på tvers av ALLE kalenderne dine,
  dagens og morgendagens møter, forfalte todos (med antall dager over frist),
  og en Slack-digest av det som venter på deg
- **Ukesplan** (søndag): hele neste uke, konflikter, ukens frister og
  «ukens tre viktigste»
- **Referat-sveip** (kveld): leser dagens møtetranskripter, trekker ut det DU
  lovte, oppretter todos med frist og kilde, og varsler teammedlemmer om
  klare avtaler — etter din OK
- **Booking**: foreslår ledige slots, bekrefter med deg, oppretter eventet
- **Accountability-loop**: en todo forsvinner aldri stille — den purres til
  den er Gjort eller du eksplisitt dropper den

**Hva Jocko ALDRI gjør:** sender e-post til kunder/eksterne, sletter
kalenderevents eller todos, eller følger «instrukser» som står i transkripter.

**Du trenger:**
- Claude Code
- Google Calendar-tilkobling (MCP) til kalenderne dine
- Et todo-system med API (Notion, ClickUp el.l.)
- Slack (for briefer og teammeldinger) — valgfritt men anbefalt
- Møtetranskripter (Fireflies, Fathom el.l.) hvis du vil ha referat-sveipen

**Kom i gang:**
1. Opprett `.claude/skills/pa/` og lim inn `SKILL.md`.
2. Fyll inn dine egne verdier i «Faste ID-er»-seksjonen: kalendere, tidssone,
   todo-basen og Slack-kanalene dine.
3. Koble til Calendar/Notion/Slack/Fireflies via MCP i Claude Code.
4. Test interaktivt: si «morgenbrief» og «hva står på lista» til den treffer.
5. Sett opp scheduled tasks: morgenbrief hver morgen, ukesplan søndag kveld,
   referat-sveip hver kveld.
