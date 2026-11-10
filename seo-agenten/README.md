# SEO-agenten — synlig i Google og i AI-svar

SEO-agenten er en Claude Code-agent som sjekker hva Google og AI-robotene
faktisk ser når de besøker nettsiden din, om du dukker opp i søkene som
betyr noe, og hvor mye trafikk som kommer fra Google og AI-assistenter.
Forbedringer skriver den som pull requests. Den publiserer aldri selv.

**Problemet den løser:** Mange nye nettsider er tomme for robotene. Siden
ser fin ut i nettleseren, men ChatGPT, Claude og Perplexity kjører ikke
JavaScript, så de ser en tittel og ingen tekst. Når noen spør en
AI-assistent om det du selger, finnes du ikke. Ingen merker det, fordi
siden ser riktig ut for alle mennesker.

**Hva agenten gjør:**
- Henter hver side slik GPTBot gjør og sjekker tittel, beskrivelse, språk,
  canonical, hreflang, strukturert data, antall ord ekte tekst, robots.txt,
  sitemap og llms.txt
- Søker opp 10–20 søk folk faktisk skriver og noterer om du er med, og
  hvem som er det i stedet. Uke for uke
- Henter klikk, visninger og posisjon fra Search Console, og økter fra
  AI-assistenter i GA4
- Skriver nye sider som pull requests, med kilde for hver påstand
- Sjekker den live siden etter hver merge og varsler søkemotorene

**Hva agenten ALDRI gjør:** publiserer, skriver en påstand uten kilde,
dikter opp anmeldelser, eller gjetter trafikktall før målingen er koblet.

**Du trenger:**
- Claude Code og Python 3 (kun standardbiblioteket, pluss `openssl` for
  trafikkskriptet)
- Nettsiden din, og helst koden i et GitHub-repo så agenten kan lage PR-er
- For trafikk: Google Search Console, GA4 og en Google-tjenestekonto
  (oppskrift i SKILL.md)

**Kom i gang:**
1. Lag mappa `.claude/skills/seo/` i prosjektet ditt og legg `SKILL.md`
   der. Legg `scripts/` i prosjektrota.
2. Kopier `.env.example` til `.env` og sett `SITE_URL`.
3. Kjør `python3 scripts/seo_check.py`. Se på linja med antall ord. Står
   det under 100 på forsiden, er det det første som må fikses.
4. Si «seo». Agenten spør om språk, kunder og konkurrenter, og lager
   `SEO.md` og lista over søk.
5. Si «dukker vi opp i ChatGPT?» for første synlighetstabell.
6. Koble Search Console og GA4 når du har tid. Det tar en halvtime.
7. Sett en scheduled task mandag morgen for ukesrapporten.

**Det vi lærte:**

- **Forhåndsrendering gir mest, uten en eneste ny setning.** Robotene går
  fra å se ingenting til å se alt.
- **Norsk og svensk side med engelsk tittel og canonical til forsiden er
  usynlige** i Norge og Sverige. Google tror de er kopier.
- **Sjekk den live siden etter merge.** En hosting-innstilling kan holde en
  gammel versjon live i ukesvis, uten at noen merker det.
- **Tjenestekontonøkkelen er et passord.** Lagre den lokalt, aldri i en
  chat.
