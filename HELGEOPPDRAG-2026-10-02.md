# Helgeoppdrag — fredag 2. oktober 2026

**Kategori:** Generell diskusjon
**E-postvarsel:** AV (aldri på helgeoppdrag)

**Tittel:** Helgeoppdraget: et møtereferat med hvem-gjør-hva på to minutter

---

Du skal bygge én ting i helgen: en agent som gjør rotete møtenotater om til et kort referat, en liste over hvem som gjør hva innen når, og et utkast til oppfølgingsmail.

Tom skrev tidligere i uka at han tok sitt første møtereferat med Wispr Flow i stedet for tastaturet. Dette er neste steg: du dikterer det du husker rett etter møtet, limer det inn, og får tilbake noe du kan sende. Jeg brukte før 15–20 minutter per referat. Nå bruker jeg to.

Ingen koblinger, ingen nøkler. Bare en mappe og én fil. 20–40 minutter.

Slik gjør du:

1. Åpne Claude Code i mappa du bruker til jobb.

2. Lim inn prompten under og svar på de tre spørsmålene den stiller.

3. Ta et ekte møte fra denne uka. Diktér eller lim inn notatene dine, og skriv /referat foran.

Startprompten, ferdig til å lime inn:

```
Du skal lage en Claude Code-skill for meg som heter "referat".

Den tar møtenotater jeg limer inn — diktert tale, stikkord eller et transkript — og leverer tre ting:

1. Referat på maks 8 linjer: hva vi snakket om og hva vi bestemte.
2. Hvem gjør hva: én linje per oppgave med navn og frist. Oppgaver uten tydelig eier samles under "Uavklart eier".
3. Utkast til oppfølgingsmail til de andre i møtet: kort, du-form, maks 10 linjer, tom linje mellom avsnittene.

Regler:
- Aldri finn på noe som ikke står i notatene. Er noe uklart, skriv [UKLART] i stedet for å gjette.
- Regn om "på tirsdag" og "neste uke" til faktisk dato ut fra møtedatoen. Spør om møtedatoen hvis den mangler.
- Skriv på norsk, uansett hvilket språk notatene er på.
- Behold mine ord og min tone i mailen.
- Send aldri noe. Du lager bare utkastet.

Før du skriver fila: still meg tre spørsmål om hvordan jeg vil ha referatene mine, så de blir mine og ikke generiske.

Lagre den som .claude/skills/referat/SKILL.md i denne mappa, med YAML-frontmatter som har name og description. Description skal si når skillen brukes: "referat", "møtenotater", "oppsummer møtet", "hvem gjør hva".

Når fila er lagret: si hva jeg skal skrive for å bruke den.
```

Post i denne tråden når du har den kjørende. Skriv hvor mange [UKLART] den fant i første referat. Det er som regel der møtet faktisk var uklart.

Står du fast, ta det med til Labs på tirsdag.
