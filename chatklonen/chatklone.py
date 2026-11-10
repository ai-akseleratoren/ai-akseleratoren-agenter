#!/usr/bin/env python3
"""Chatklonen — fletter chatten fra tidligere sendinger av samme webinar inn i
dagens opptak, tidsatt etter det verten faktisk sier, til simulert chat i reprisen.

    python3 chatklone.py klon <målmappe> --kilder <mappe> <mappe> [valg]
    python3 chatklone.py --demo

Hver sending er én mappe med:
    chat.txt        Zoom-skyens chatfil («HH:MM:SS<tab>Navn:<tab>tekst»), ELLER
    chat.csv        kolonnene sekund,navn,melding (andre webinarverktøy)
    transkript.vtt  / .srt / transkript-per-minutt.txt («[MM:00] tekst»). Trengs bare i målet.
    meta.json       valgfri: {"chat_minus_opptak_sek": 315} når chatten regner tid fra
                    møtestart og opptaket fra opptaksstart. Alt i resultatet er VIDEOTID.
    privat.txt      valgfri: Zoom sin lokale chatfil, så meldinger «to Host» tas ut.

Valg:
    --team "Ola,Kari,bot"   navn på vert, team og boter. Deres meldinger tas aldri med.
    --ankerord "a|b|c"      ord publikum svarer med på en fast oppfordring (f.eks. produktnavn).
    --vert "Navn (vert)"    + --gratulasjoner: vertsmelding 15–25 s etter hvert «jeg er med».
    --uten-ai               bare tidsjustering + personvern, ingen Claude-sjekk.
    --eksporter             skriver promptene til <mål>/ai/<hash>.prompt.txt i stedet for å
                            kalle «claude -p». Svar som <hash>.json i samme mappe, kjør igjen.

Resultat i målmappa: chatklone.csv (sekund, tid, navn, melding, kilde) og chatklone.txt.
Kun standardbiblioteket.
"""
import csv
import hashlib
import json
import pathlib
import re
import subprocess
import sys

ARG = sys.argv[1:]


def valg(navn, standard=""):
    return ARG[ARG.index(navn) + 1] if navn in ARG and ARG.index(navn) + 1 < len(ARG) else standard


TEAM_NAVN = [n.strip() for n in valg("--team").split(",") if n.strip()]
TEAM = re.compile("|".join(map(re.escape, TEAM_NAVN)) or r"(?!x)x", re.I)
SKITT = re.compile(r"@|https?://|www\.|\.no\b|\.com\b|\.se\b|\d{8,}|faktura|org\.?\s?nr|betalt|kort|vipps|swish", re.I)


# ---------- lesing ----------
def les_chat(mappe):
    mappe = pathlib.Path(mappe)
    if (mappe / "chat.csv").exists():
        with open(mappe / "chat.csv", encoding="utf-8-sig") as f:
            return [{"sek": int(float(r["sekund"])), "navn": r["navn"].strip(), "tekst": r["melding"].strip()}
                    for r in csv.DictReader(f)]
    ut = []
    for linje in (mappe / "chat.txt").read_text(errors="ignore").splitlines():
        m = re.match(r"^(\d\d):(\d\d):(\d\d)\t(.+?):\t(.*)$", linje)
        if m:
            h, mi, s, navn, tekst = m.groups()
            ut.append({"sek": int(h) * 3600 + int(mi) * 60 + int(s), "navn": navn.strip(), "tekst": tekst.strip()})
        elif ut and linje.strip():
            ut[-1]["tekst"] += " " + linje.strip()
    return ut


def les_transkript(mappe):
    """{minutt: tekst} fra per-minutt-fil, .vtt eller .srt."""
    mappe = pathlib.Path(mappe)
    f = mappe / "transkript-per-minutt.txt"
    if f.exists():
        return {int(m.group(1)): m.group(2) for m in re.finditer(r"^\[(\d+):00\] (.*)$", f.read_text(), re.M)}
    for navn in ("transkript.vtt", "transkript.srt"):
        if (mappe / navn).exists():
            ut, minutt = {}, None
            for linje in (mappe / navn).read_text(errors="ignore").splitlines():
                m = re.match(r"^(\d+):(\d\d):(\d\d)[.,]\d+\s+-->", linje)
                if m:
                    minutt = int(m.group(1)) * 60 + int(m.group(2))
                elif minutt is not None and linje.strip() and not linje.strip().isdigit():
                    ut[minutt] = (ut.get(minutt, "") + " " + linje.strip()).strip()
            return ut
    return {}


def private_tekster(mappe):
    f = pathlib.Path(mappe) / "privat.txt"
    if not f.exists():
        return set()
    priv = set()
    for blokk in f.read_text(errors="ignore").split("\n20"):
        if " to Host and panelists:" in blokk or " to Host:" in blokk:
            priv.add(norm(" ".join(l.strip() for l in blokk.splitlines()[1:] if l.strip())))
    return priv


def norm(t):
    return re.sub(r"\s+", " ", t.lower()).strip()


def fornavn(navn):
    if re.search(r"\d|iphone|ipad|android|samsung|galaxy", navn, re.I):
        return "Gjest"
    deler = re.split(r"[\s._@]+", navn.strip())
    f = deler[0]
    if len(deler) == 1 and len(f) > 9:   # fornavn+etternavn skrevet i ett ord
        return "Gjest"
    return f[:1].upper() + f[1:].lower() if f else "Gjest"


def vask(meldinger, mappe):
    """Personvern: kun fornavn, ingen kontaktinfo/lenker/betaling, ingen private meldinger, ingen team."""
    priv = private_tekster(mappe)
    ut = []
    for m in meldinger:
        if TEAM.search(m["navn"]) or SKITT.search(m["tekst"]) or norm(m["tekst"]) in priv:
            continue
        if m["tekst"].lower().startswith(("replying to", "reacted to")):
            continue
        ut.append({**m, "navn": fornavn(m["navn"])})
    return ut


# ---------- ankere ----------
def klasser():
    k = [
        ("intro", re.compile(r".+"), 6, 120),   # første bølge: «hvorfor er du her»-runden
        ("ja", re.compile(r"^(\S+\s){0,2}(ja+|jup|jepp|jada|yes|absolutt)\W*$", re.I), 4, 120),
        ("tall", re.compile(r"^\d{1,2}(\s?[-–]\s?\d{1,2})?\s?(t|timer|h)?\W*$", re.I), 5, 150),
    ]
    if valg("--ankerord"):
        k.append(("ankerord", re.compile(valg("--ankerord"), re.I), 4, 150))
    k.append(("cta", re.compile(r"jeg er med|\ber med\b|^klar\W*$|blir med|i'?m in\b", re.I), 4, 240))
    return k


def ankere(meldinger):
    """Første tidspunkt der hver klasse har en tydelig bølge, i rekkefølge."""
    funn, etter = {}, 0
    publikum = [m for m in meldinger if not TEAM.search(m["navn"])]
    for navn, rx, minst, vindu in klasser():
        treff = [m["sek"] for m in publikum if m["sek"] >= etter and rx.search(m["tekst"])]
        for i, t in enumerate(treff):
            if sum(1 for u in treff[i:] if u - t <= vindu) >= minst:
                funn[navn] = t
                etter = t + 60
                break
    return funn


def juster(sek, kilde_a, mål_a):
    """Stykkevis lineær flytting mellom felles ankere. Ankere som spriker >15 min kastes."""
    felles = sorted((kilde_a[k], mål_a[k]) for k in kilde_a if k in mål_a)
    if len(felles) >= 3:
        avvik = sorted(m - k for k, m in felles)
        midt = avvik[len(avvik) // 2]
        felles = [(k, m) for k, m in felles if abs((m - k) - midt) <= 900]
    if not felles:
        return sek
    if sek <= felles[0][0]:
        return sek + felles[0][1] - felles[0][0]
    for (k0, m0), (k1, m1) in zip(felles, felles[1:]):
        if k0 <= sek <= k1:
            return round(m0 + (sek - k0) * (m1 - m0) / max(1, k1 - k0))
    return sek + felles[-1][1] - felles[-1][0]


# ---------- Claude ----------
KJØP = re.compile(r"jeg er med|blir med|\ber med\b|^klar\W*$|sammen med deg|meld(er|t) meg (på|inn)"
                  r"|har (kjøpt|bestilt)|da er jeg med|jag är med|count me in|i'?m in\b", re.I)
AI_MAPPE = None


def claude(prompt):
    """claude -p med cache per prompt. --eksporter: skriv prompten, svar legges i ai/<hash>.json."""
    h = hashlib.sha1(prompt.encode()).hexdigest()[:12]
    AI_MAPPE.mkdir(exist_ok=True)
    cache = AI_MAPPE / f"{h}.json"
    if cache.exists():
        return json.loads(cache.read_text())
    if "--eksporter" in ARG:
        (AI_MAPPE / f"{h}.prompt.txt").write_text(prompt)
        return None
    r = subprocess.run(["claude", "-p", prompt], capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        sys.exit(f"claude -p feilet: {(r.stdout + r.stderr).strip()[:200]}\n"
                 "Logg inn med «claude» i en terminal, eller kjør med --eksporter.")
    m = re.search(r"\{.*\}", r.stdout, re.S)
    try:
        svar = json.loads(m.group(0)) if m else None
    except ValueError:
        svar = None
    if svar is not None:
        cache.write_text(json.dumps(svar, ensure_ascii=False))
    return svar


def emneindeks(mål, tr):
    f = pathlib.Path(mål) / "emneindeks.json"
    if f.exists():
        return json.loads(f.read_text())
    tekst = "\n".join(f"[{m:02d}] {tr[m][:500]}" for m in sorted(tr))
    svar = claude(f"""Her er transkriptet av et webinar, minutt for minutt:

{tekst}

Lag en emneindeks: for hvert minutt maks 12 ord om hva verten snakker om. Når verten ber publikum skrive noe i chatten, start linja med «SPØR:» og si hva de skal skrive (f.eks. «SPØR: skriv JA»). Marker når verten presenterer pris/tilbud med «PRIS:».
Svar KUN med JSON der nøkkelen er minuttet: {{"0": "...", "1": "..."}}""") or {}
    if svar:
        f.write_text(json.dumps(svar, ensure_ascii=False, indent=0))
    return svar


def claude_plasser(indeks, vindu_tekst, kandidater, fra_min, til_min, siste):
    liste = "\n".join(f'{c["id"]} | {c["sek"]//60:02d} | {c["tekst"]}' for c in kandidater)
    idx = "\n".join(f"[{int(k):02d}] {v}" for k, v in sorted(indeks.items(), key=lambda kv: int(kv[0])))
    svar = claude(f"""Du lager simulert chat til reprisen av et webinar. Målet er en LEVENDE chat med mange meldinger — verten trenger ikke svare på alt.

Emneindeks for hele webinaret (minutt: tema; SPØR = verten ber chatten skrive noe; PRIS = tilbudet):
{idx}

Det verten sier i minutt {fra_min}–{til_min}:
{vindu_tekst}

Chatmeldinger fra TIDLIGERE sendinger av samme webinar, foreløpig plassert her (id | minutt | tekst):
{liste}

Regler:
- Behold så mye som mulig.
- Generelle spørsmål og kommentarer om temaet passer hvor som helst: behold i samme minutt.
- Svar på en konkret oppfordring (JA, et tall, et navn, hvorfor de er her …) skal stå rett etter at verten ber om akkurat det i dag. Flytt dem dit (bruk SPØR i indeksen). Finnes ikke oppfordringen i dag, forkast.
- Forkast bare det som motsier webinaret (feil tall, navn, priser, datoer, tilbud), viser til noe som ikke skjer i dag, eller er ren gjentakelse.
- Minutt må være mellom 0 og {siste}.
Svar KUN med JSON: {{"plasser": [{{"id": 3, "minutt": 12}}, ...]}} — id-er du ikke tar med, forkastes.""")
    if not svar or "plasser" not in svar:
        return None
    return {int(p["id"]): int(p["minutt"]) for p in svar["plasser"] if "id" in p and "minutt" in p}


# ---------- klon ----------
def spre(meldinger, start, slutt):
    """Fordel meldinger jevnt over [start, slutt], i opprinnelig rekkefølge."""
    meldinger = sorted(meldinger, key=lambda m: m["sek"])
    steg = (slutt - start) / max(1, len(meldinger))
    return [{**m, "sek": int(start + i * steg + (len(m["tekst"]) * 7 % max(1, int(steg))))}
            for i, m in enumerate(meldinger)]


def tid(s):
    return f"{s//3600:02d}:{s%3600//60:02d}:{s%60:02d}"


def videotid(mappe, meldinger):
    meta = pathlib.Path(mappe) / "meta.json"
    forsk = json.loads(meta.read_text()).get("chat_minus_opptak_sek", 0) if meta.exists() else 0
    return [{**m, "sek": max(0, m["sek"] - forsk)} for m in meldinger]


def klon(mål, kilder):
    global AI_MAPPE
    mål = pathlib.Path(mål)
    AI_MAPPE = mål / "ai"
    if not (mål / "meta.json").exists():
        print("  NB: meta.json mangler. Starter opptaket senere enn chatten, blir alt forskjøvet.")
    rå_mål = videotid(mål, les_chat(mål))
    mål_chat = vask(rå_mål, mål)
    mål_a = ankere(rå_mål)
    print(f"mål: {len(mål_chat)} meldinger etter vask, ankere {mål_a}")
    kand = []
    for k in map(pathlib.Path, kilder):
        rå = videotid(k, les_chat(k))
        k_a = ankere(rå)
        vasket = vask(rå, k)
        print(f"  {k.name}: {len(vasket)} meldinger etter vask, ankere {k_a}")
        kand += [{**m, "sek": max(0, juster(m["sek"], k_a, mål_a)), "kilde": k.name} for m in vasket]
    for i, c in enumerate(kand):
        c["id"] = i
    tr = les_transkript(mål)
    siste = max(tr) if tr else max([m["sek"] for m in rå_mål] + [0]) // 60

    # 1. Kjøp og «jeg er med»: alltid i dagens salgsdel, der de andre sier det samme.
    kjøp = [c for c in kand if KJØP.search(c["tekst"])]
    mål_kjøp = [m["sek"] for m in mål_chat if KJØP.search(m["tekst"])]
    lenker = [m["sek"] for m in rå_mål if TEAM.search(m["navn"]) and re.search(r"https?://", m["tekst"])
              and m["sek"] >= mål_a.get("cta", 0)]
    start = (min(lenker) if lenker else None) or mål_a.get("cta") or (min(mål_kjøp) if mål_kjøp else siste * 60 - 1200)
    slutt = min(max([start + 600] + [t for t in mål_kjøp if t >= start]), siste * 60)
    plassert = spre(kjøp, start, slutt)
    print(f"  kjøp/«jeg er med»: {len(kjøp)} flyttet til {tid(start)}–{tid(slutt)}")

    # 2. Resten: Claude plasserer etter hva verten sier.
    øvrige = [c for c in kand if not KJØP.search(c["tekst"])]
    if "--uten-ai" in ARG or not tr:
        if not tr and "--uten-ai" not in ARG:
            print("  (ingen transkript i målmappa — hopper over Claude-sjekken)")
        plassert += [{**c, "sek": min(c["sek"], siste * 60)} for c in øvrige]
    else:
        indeks = emneindeks(mål, tr)
        if not indeks:
            sys.exit(f"  emneindeksen mangler — svar på prompten i {AI_MAPPE} og kjør igjen")
        mangler = 0
        for fra in range(0, siste + 1, 5):
            i_vindu = [c for c in øvrige if fra * 60 <= min(c["sek"], siste * 60) < (fra + 5) * 60]
            if not i_vindu:
                continue
            tekst = "\n".join(f"[{m:02d}:00] {tr[m]}" for m in range(max(0, fra - 1), fra + 5) if m in tr)
            plass = claude_plasser(indeks, tekst or "(stille)", i_vindu, fra, fra + 5, siste)
            if plass is None:
                mangler += 1
                continue
            plassert += [{**c, "sek": max(0, min(siste, plass[c["id"]])) * 60 + c["sek"] % 60}
                         for c in i_vindu if c["id"] in plass]
            print(f"  {fra:02d}–{fra+5:02d} min: {len(plass)}/{len(i_vindu)} beholdt")
        if mangler:
            sys.exit(f"  {mangler} vinduer mangler svar — promptene ligger i {AI_MAPPE}, kjør igjen")

    # 3. Maks 10 kildemeldinger per minutt.
    per_min, valgt = {}, []
    for c in sorted(plassert, key=lambda c: c["sek"]):
        n = per_min.get(c["sek"] // 60, 0)
        if n < 10:
            per_min[c["sek"] // 60] = n + 1
            valgt.append(c)
    alle = sorted([{**m, "kilde": "mål"} for m in mål_chat] + valgt, key=lambda m: m["sek"])
    if tr:
        alle = [{**m, "sek": min(m["sek"], (max(tr) + 1) * 60 - 1)} for m in alle]
    if "--gratulasjoner" in ARG:
        alle = sorted(alle + gratulasjoner(alle, start), key=lambda m: m["sek"])
    # utf-8-sig: Excel og nettlesere viser æøå riktig
    with open(mål / "chatklone.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["sekund", "tid", "navn", "melding", "kilde"])
        for m in alle:
            w.writerow([m["sek"], tid(m["sek"]), m["navn"], m["tekst"], m["kilde"]])
    (mål / "chatklone.txt").write_text("".join(f"{tid(m['sek'])}  {m['navn']}: {m['tekst']}\n" for m in alle),
                                      encoding="utf-8-sig")
    print(f"-> {mål/'chatklone.csv'}: {len(alle)} meldinger ({len(mål_chat)} fra målet, {len(valgt)} fra kildene)")


GRATULER = ["Gratulerer, {n}! 🎉 Velkommen inn", "Velkommen inn, {n}! 🙌", "Så gøy, {n} – gratulerer! 🎉"]


def gratulasjoner(alle, start):
    """Vertsmeldinger 15–25 s etter hver kjøpsmelding i salgsdelen. Én per navn, minst 8 s mellom."""
    ut, sett, siste = [], set(), -999
    for m in alle:
        if m["sek"] < start or not KJØP.search(m["tekst"]) or len(m["tekst"].split()) > 6 or m["navn"] in sett:
            continue
        t = max(m["sek"] + 15 + len(m["navn"]) % 11, siste + 8)
        n = m["navn"]
        tekst = GRATULER[len(ut) % len(GRATULER)].format(n=n) if n != "Gjest" else "Gratulerer, og velkommen inn! 🎉"
        ut.append({"sek": t, "navn": valg("--vert", "Vert"), "tekst": tekst, "kilde": "vert"})
        sett.add(n)
        siste = t
    return ut


def demo():
    a = {"ja": 100, "tall": 400}
    assert juster(250, {"ja": 200, "tall": 300}, a) == 250
    assert juster(50, {"ja": 200}, {"ja": 100}) == -50
    msgs = [{"sek": 10 + i, "navn": "A", "tekst": "hei"} for i in range(6)]
    msgs += [{"sek": 300 + i, "navn": "A", "tekst": t} for i, t in enumerate(["JA", "haha ja", "mhh jup", "Absolutt"])]
    an = ankere(msgs)
    assert an["intro"] == 10 and an["ja"] == 300, an
    assert fornavn("iPhone (3)") == "Gjest" and fornavn("olanordmannsen") == "Gjest" and fornavn("kari") == "Kari"
    assert not vask([{"sek": 2, "navn": "Ola", "tekst": "mail meg på ola@example.com"}], "/finnes-ikke")
    sp = spre([{"sek": 5, "tekst": "a"}, {"sek": 1, "tekst": "b"}], 100, 300)
    assert sp[0]["tekst"] == "b" and 100 <= sp[0]["sek"] < 200 and 200 <= sp[1]["sek"] < 300, sp
    assert KJØP.search("Jeg er med..") and KJØP.search("Klar") and not KJØP.search("klarer ikke dette")
    g = gratulasjoner([{"sek": 100, "navn": "Ola", "tekst": "Jeg er med"}, {"sek": 110, "navn": "Kari", "tekst": "jeg er med"},
                       {"sek": 200, "navn": "Ola", "tekst": "jeg er med"}], 50)
    assert len(g) == 2 and "Ola" in g[0]["tekst"] and g[1]["sek"] - g[0]["sek"] >= 8, g
    print("demo ok")


if __name__ == "__main__":
    if not ARG:
        sys.exit(__doc__)
    if ARG[0] == "--demo":
        demo()
    elif ARG[0] == "klon" and len(ARG) > 1:
        kilder = []
        if "--kilder" in ARG:
            for k in ARG[ARG.index("--kilder") + 1:]:
                if k.startswith("--"):
                    break
                kilder.append(k)
        klon(ARG[1], kilder)
    else:
        sys.exit(__doc__)
