# Miller — sosiale medier som går ut av seg selv

Miller er en Claude Code-agent som driver de organiske Facebook- og
Instagram-kontoene dine. Den skriver postene, velger bildene, lager
nedtellingsgrafikk og reels, og holder køen full. Et GitHub-repo publiserer
automatisk tre ganger i uka i feeden og tre ganger i uka i stories.

Oppkalt etter Warren Miller, filmskaperen som fikk folk til å lengte etter
vinteren. Det er jobben: få folk til å glede seg til det du selger.

**Problemet den løser:** Sosiale medier dør i travle uker. Ingen har tid,
så det går tre uker uten post, og så kommer fem på én dag. Miller fyller
køen i forkant, og publiseringen går uansett hvor travelt du har det.

**Hva agenten gjør:**
- Skriver feed-poster, stories og reels i din stemme, med en myk oppfordring
  og 6–9 emneknagger
- Finner ubrukte bilder og viser deg et kontaktark før den velger
- Lager nedtellingsbilder der tallet stemmer med dagen posten går ut
- Lager 9:16-reels fra bilder og videoklipp, med tekst og sluttkort
- Sjekker at køen ikke er tom, og at Instagram faktisk får postene
- Holder seg til det som har skjedd. Ingen oppdiktede nyheter

**Hva agenten ALDRI gjør:** pusher til køen uten ditt OK, bruker
AI-bilder, setter priser eller «bare 3 plasser igjen» uten at du har
bekreftet det, eller ber om tokenet i chatten.

**Du trenger:**
- Claude Code og Python 3 med Pillow (`pip install pillow`)
- ffmpeg for reels
- Et offentlig GitHub-repo til publiseringen (bildene serveres derfra)
- En Facebook-side og en Instagram Professional-konto koblet til siden
- En Meta-app med et side-token (oppskrift i SKILL.md)

**Kom i gang:**
1. Lag mappa `.claude/skills/miller/` i prosjektet ditt og legg `SKILL.md`
   der.
2. Lag publiseringsrepoet: `queue/`, `stories/`, `posted/`, `assets/`,
   `scripts/` med de tre skriptene herfra, og de to workflow-filene fra
   «Oppsett» i SKILL.md.
3. Sett opp Meta-appen og legg `META_TOKEN`, `IG_USER_ID` og `FB_PAGE_ID`
   som GitHub Secrets. Sett appen til **Live**.
4. Kjør workflowen med dry run. Grønn = koblet.
5. Si «miller, fyll køen». Den spør hva folk skal glede seg til, og når,
   og lager `MILLER.md`.
6. Se gjennom kontaktarket og tekstene, si OK, og la den pushe.

**Det vi lærte i drift:**

- **Utviklingsmodus lyver.** API-et sier «publisert», men ingen andre ser
  postene. Appen må stå på Live.
- **En plassholder i IG_USER_ID betyr null poster på Instagram.** Uten
  feilmelding. Les loggen fra publiseringen.
- **Upushet kø er tom kø.** Push med en gang etter OK.
- **Nedtellingstallet hører til publiseringsdagen,** ikke dagen du lager
  bildet.
- **Planlagte GitHub-kjøringer kommer ofte timer for sent.** Ikke lov en
  bestemt time.
