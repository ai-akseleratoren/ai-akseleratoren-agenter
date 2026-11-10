# Rackham — strategipartneren for 1:1-salg

Rackham er en Claude Code-agent som hjelper deg å selge et lengre
samarbeid (6 eller 12 måneder) til én kunde. Den leser transkriptet fra
salgsmøtet og forteller deg hva kunden egentlig sa, skriver referatet som
får kunden til å ville videre, legger opp møte 2, og foreslår forløp og pris.

Oppkalt etter Neil Rackham, mannen bak SPIN Selling. Store salg vinnes ved
å forstå kunden bedre enn kunden selv. Ikke ved press.

**Problemet den løser:** Etter et godt førstemøte skjer det samme hver
gang. Referatet blir generisk, møte 2 blir en pitch, og prisen settes etter
magefølelse og blir for lav. Rackham holder deg til kundens egne ord og
setter prisen etter det kunden sa de skal ha ut av det.

**Hva agenten gjør:**
- Trekker ut businessen, målet, smerten, konsekvensen, manuelt arbeid,
  hvordan kunden beslutter, kjøpssignaler og bremser. Ordrett der det går
- Skriver et referat på maks ~300 ord i kundens språk: «slik forstår jeg
  situasjonen din», hva som kan bygges, og forslag om møte 2
- Legger opp møte 2 som behovsanalyse (SPIN), med spørsmål bygget på det
  kunden faktisk sa. Pris kommer i møte 3, sammen med planen
- Foreslår 6- og 12-måneders forløp og en begrunnet pris, ankret i kundens
  eget mål, kun til deg
- Holder en mappe per prospekt med status

**Hva agenten ALDRI gjør:** finner på noe kunden ikke sa, setter pris
eller dato i tekst til kunden, skriver «ingen pitch» noe sted, eller
sender noe. Du limer inn selv.

**Du trenger:**
- Claude Code
- Et transkript fra salgsmøtet: møteopptaks-verktøy, limt inn, eller en
  lydfil. Norsk tale bør transkriberes med Whisper eller tilsvarende,
  ikke møteverktøyets engelske talegjenkjenning

**Kom i gang:**
1. Lag mappa `.claude/skills/rackham/` i prosjektet ditt og legg `SKILL.md`
   der.
2. Si «rackham» første gang. Den spør om hva du selger, din egen historie,
   prisgulvet ditt og valuta, og lager `RACKHAM-OPPSETT.md`.
3. Lim inn transkriptet fra et salgsmøte og si «rackham, analyser».
4. Les del 1 først. Det er der du ser hva du gikk glipp av i møtet.
5. Rett referatet, lim det inn i din egen e-post og send.
6. Før møte 2: «rackham, forbered møte 2».

**Reglene som betyr mest:**

- **Møte 2 er intervjuet, ikke closing.** Første utkast blir nesten alltid
  for salgsaktig. Sjekk at du hørte riktig, vær nysgjerrig, spør om
  konsekvens sent og mykt.
- **Prisen ankres i kundens mål.** Rundt 10 % av det kunden sa de skal ha
  ut av det, fast honorar først. Din standardpris er gulvet, ikke ankeret.
- **Å si at du ikke selger, er å selge.** Vis det gjennom spørsmålene.

> Tips: `saker/` inneholder kundedata. Hold den utenfor offentlige repoer.
