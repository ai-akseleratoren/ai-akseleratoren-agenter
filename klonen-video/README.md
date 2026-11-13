# Klonen — en video der en klone av deg leser manuset

Klonen er en Claude Code-agent som lager en ferdig video av et manus: en
AI-avatar med din egen klonede stemme til venstre, og et lysark per avsnitt til
høyre. Du filmer en kort åpning selv, sier at resten er en klone, og agenten
lager resten.

**Problemet den løser:** Du vet hva du vil si, men kommer deg aldri foran
kameraet hver uke. Med en klone holder det å godkjenne et manus og høre gjennom
tre minutter lyd.

Den første videoen vi laget slik, tok én dag fra idé til YouTube. Avataren
kostet rundt ti dollar for tre minutter.

**Hva agenten gjør:**
- Kloner stemmen din fra ca. ett minutt der du snakker fritt
- Leser inn manuset avsnitt for avsnitt, og skriver lyden ut igjen som tekst
  så feiluttale oppdages uten at noen må høre gjennom alt
- Lager en snakkende avatar av ett stillbilde, per avsnitt
- Setter avatar og lysark sammen til en video i 1920x1080
- Merker hele videoen «AI-avatar og klonet stemme»

**Hva agenten ALDRI gjør:** kloner andre enn deg, fjerner merkingen, finner på
tall eller hendelser i manuset, eller laster opp. Du ser gjennom og publiserer selv.

**Du trenger:**
- Claude Code og Python 3 (bare standardbiblioteket)
- En fal.ai-konto med saldo. Tale koster lite. Avataren koster ca. 6 cent per sekund.
- ffmpeg og Google Chrome
- Ett minutt lydopptak der du snakker fritt (mp3), og ett stillbilde av deg (stående, 9:16)

**Kom i gang:**
1. Opprett `.claude/skills/klonen/` i prosjektet ditt, og legg inn `SKILL.md`,
   `klone_video.py` og `video.py`.
2. Kopier `.env.example` til `.env` og legg inn `FAL_KEY` (aldri i git).
3. Legg stillbildet ditt i samme mappe som `ansikt.jpg`.
4. Kjør `python3 klone_video.py stemme opptak.mp3` én gang.
5. Si «klonen, lag en video om …» til Claude Code. Den skriver manuset med deg,
   leser det inn, og lar deg høre før den lager avataren.

Går godt sammen med **rubin-innholdsagent** (idé, tittel, thumbnail og tall) og
**thelma-videoklipper** (klipping av åpningen din).
