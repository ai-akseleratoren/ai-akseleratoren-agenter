# Helgeoppdrag — fredag 4. september 2026

**Kategori:** Generell diskusjon
**E-postvarsel:** AV (aldri på helgeoppdrag)

**Tittel:** Helgeoppdraget: en agent som gjør diktering til ferdig tekst

---

Du skal bygge én ting i helgen: en agent som tar rå tale-til-tekst og gir deg ferdig e-post, notat eller innlegg — i din tone, uten at den finner på noe.

Hvorfor den er verdt en lørdag: du dikterer allerede på telefonen mens du går eller kjører. Problemet er at det som kommer ut må skrives om for hånd før noen kan lese det. Med denne limer du inn rotet og får tilbake noe du kan sende. Jeg sparer 10–15 minutter hver gang, og jeg gjør det flere ganger om dagen.

Den er også den enkleste veien inn i mekanikken fra agentbiblioteket: én mappe, én SKILL.md, så sier du navnet. Ingen nøkler, ingen integrasjoner. 20–40 minutter.

Slik gjør du:

1. Åpne Claude Code i en mappe du bruker til jobb.

2. Lim inn prompten under.

3. Diktér noe på telefonen — helst en e-post du faktisk skulle sendt — lim det inn i Claude Code og skriv «stemme».

Startprompten, ferdig til å lime inn:

```
Du skal lage en Claude Code-skill for meg som heter "stemme".

Den tar diktert tale-til-tekst som jeg limer inn, og leverer én ryddet versjon klar til å kopiere.

Slik skal den jobbe:
- Fjern "eh", gjentakelser, falske starter og avbrutte setninger. Rett tegnsetting og åpenbare tale-til-tekst-feil i navn og tall.
- Kjenn igjen sjangeren selv: e-post (emnelinje, hilsen, avsnitt med tom linje mellom), notat (overskrift og korte punkter), innlegg (korte avsnitt, ingen emnelinje), melding (kort, ingen hilsen-seremoni).
- Behold mine ord og min tone. Ikke bytt ut ordene mine med finere synonymer, og ikke gjør setningene lengre.
- Aldri legg til innhold jeg ikke har sagt. Ingen nye poenger, ingen høflighetsfraser jeg ikke dikterte.
- Lever alltid i en kodeblokk, uten kommentarer inni blokken.
- Én linje under blokken: hvilken sjanger du antok.

Før du skriver fila: still meg tre spørsmål om hvordan jeg skriver, så tonen blir min og ikke en generisk.

Lagre den som .claude/skills/stemme/SKILL.md i denne mappa, med YAML-frontmatter som har name og description. Description skal si når skillen brukes: "diktert", "rydd teksten", "jeg snakket inn dette".

Når fila er lagret: si hva jeg skal skrive for å bruke den.
```

Post i denne tråden når du har den kjørende — gjerne hva den bommet på i første forsøk. Det er der du finner justeringen som gjør den til din.

Står du fast, ta det med til Labs på tirsdag.
