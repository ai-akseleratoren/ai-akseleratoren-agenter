# North Star — markedssjef-agenten

En AI-agent som leder markedsarbeidet ditt mot ÉN nordstjerne-KPI: å fylle
pipelinen til hovedtilbudet ditt. Alt annet — annonser, webinarer, e-post,
lavterskeltilbud — er trapper som skal lede dit.

## Hvilket problem løser den?

- Markedsføring uten prioritering: alt føles like viktig, ingenting måles mot
  ett mål.
- Kampanjer lanseres i siste liten uten plan, godkjenning eller tekst-QA.
- Tall bor i hodene på folk. Avvik oppdages for sent.
- Ingen følger opp hva teamet lovte på ukemøtet.

North Star overvåker tallene daglig, fører markedskalender minst 4 uker frem,
purrer på frister — og anbefaler alltid, men beslutter aldri.

## Hva du trenger

- Claude Code installert
- Et sted tallene bor: CRM (pipeline/leads), annonsekonto, ev. betalingsdata
- En teamkanal (f.eks. Slack) der agenten kan varsle
- En mappe/repo for pulsrapporter, kalender og beslutningslogg

## Kom i gang

1. Kopier `SKILL.md` inn som `.claude/skills/north-star/SKILL.md` i prosjektet.
2. Definer nordstjernen din: hvilket tall er «nye kvalifiserte leads/uke» for
   hovedtilbudet ditt? Skriv det inn i skillen.
3. Fyll inn rollene: hvem beslutter (eier/driftsleder), hvem kvalitetssikrer
   tekst, hvem eier teknisk sporing.
4. Kjør første puls manuelt: «North Star, kjør daglig puls.» Juster kildene til
   dine egne script/API-er.
5. Når pulsen sitter: sett den opp som daglig planlagt oppgave, og legg til
   ukemøte-modusen på fast ukedag.

## Kjerneprinsippene

- Agenten **anbefaler — ledelsen beslutter**. Aldri pengebruk, utsendelser
  eller funnel-endringer på egen hånd.
- All kundevendt tekst kvalitetssikres av et menneske før publisering.
- Alt som lanseres skal ha stått i kalenderen først: utkast 7 dager før,
  godkjenning 4 dager før, teknisk test 2 dager før.
- Rapportering i EOS-scorecard-form: ett tall per linje, én eier, ukesmål,
  på/av sporet.
