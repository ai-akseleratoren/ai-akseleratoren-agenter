#!/usr/bin/env python3
"""Medlemsvakt — avstemmer betalinger i Stripe mot tilgang i Skool.

Bruk:
    python3 medlemsvakt.py                      # rapport til skjerm
    python3 medlemsvakt.py --json               # maskinlesbart
    python3 medlemsvakt.py --csv fil.csv        # skriv til CSV

Skool-eksporten må hentes manuelt (Members -> Export, krever e-postkode) og
ligge som ~/Downloads/community_members.csv, eller pekes på med --skool.

Rapporterer aldri annet enn tall og navn. Fjerner ingen, sender ingenting.
"""
import os, sys, json, csv, time, re, argparse, urllib.request
from collections import defaultdict
from datetime import datetime, timezone

# Ditt eget domene — medlemmer herfra regnes som interne og foreslås aldri fjernet.
INTERNT_DOMENE = "@dittfirma.no"

# Medlemskapsbeløp i EUR-cent -> (syklus, pris). Legg til nye priser her.
MEDLEMSKAP = {
    9900:  ("mnd", 99),
    99000: ("aar", 990),
    7900:  ("mnd", 79),    # tidligere månedspris
    79000: ("aar", 790),   # tidligere årspris
}
# Hvor lenge etter siste betaling vi fortsatt regner medlemmet som aktivt.
# Månedlig får 15 dagers slark (kortfornyelse, feilede forsøk som lykkes senere).
FRIST = {"mnd": 45, "aar": 400}
DAGER_TILBAKE = 400


def les_env(*filer):
    env = {}
    for f in filer:
        if os.path.exists(f):
            for line in open(f):
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def stripe_hent(key, path):
    """Henter alle sider fra et Stripe-endepunkt."""
    ut, url = [], f"https://api.stripe.com/v1/{path}"
    while url:
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}"})
        d = json.load(urllib.request.urlopen(req))
        ut.extend(d["data"])
        if d.get("has_more") and d["data"]:
            sep = "&" if "?" in path else "?"
            url = f"https://api.stripe.com/v1/{path}{sep}starting_after={d['data'][-1]['id']}"
        else:
            url = None
    return ut


def normaliser(navn):
    n = re.sub(r"\s+", " ", (navn or "").lower().strip())
    return n.replace("ø", "o").replace("æ", "a").replace("å", "a")


def analyser(key, skool_csv):
    since = int(time.time()) - DAGER_TILBAKE * 86400
    charges = stripe_hent(key, f"charges?limit=100&created[gte]={since}")
    ok = [c for c in charges if c["status"] == "succeeded" and not c["refunded"]]

    betalere = defaultdict(list)
    for c in ok:
        if c["amount"] in MEDLEMSKAP and c["currency"] == "eur":
            bd = c.get("billing_details") or {}
            epost = (bd.get("email") or c.get("receipt_email") or "").lower().strip()
            if epost:
                betalere[epost].append((c["created"], c["amount"], (bd.get("name") or "").strip()))

    naa = datetime.now(timezone.utc)
    rader = []
    for epost, kjop in betalere.items():
        kjop.sort()
        sist, belop, navn = kjop[-1]
        dager = (naa - datetime.fromtimestamp(sist, timezone.utc)).days
        syklus, pris = MEDLEMSKAP[belop]
        rader.append({
            "epost": epost, "navn": navn, "syklus": syklus, "pris": pris,
            "dager": dager, "aktiv": dager <= FRIST[syklus],
            "sist": datetime.fromtimestamp(sist, timezone.utc).strftime("%Y-%m-%d"),
        })

    skool = {}
    with open(skool_csv) as f:
        for row in csv.DictReader(f):
            e = (row.get("Email") or "").lower().strip()
            if e:
                skool[e] = f"{row.get('FirstName','')} {row.get('LastName','')}".strip()
    skool_navn = {normaliser(v) for v in skool.values() if v.strip()}

    aktive = [r for r in rader if r["aktiv"]]
    lapset = [r for r in rader if not r["aktiv"]]

    # Et medlem kan betale fra én adresse og være i Skool med en annen.
    # Navnematch fanger det, så vi ikke inviterer folk som allerede er inne.
    mangler_tilgang, annen_epost = [], []
    for r in aktive:
        if r["epost"] in skool:
            continue
        (annen_epost if r["navn"] and normaliser(r["navn"]) in skool_navn
         else mangler_tilgang).append(r)

    betalt_noen_gang = {r["epost"] for r in rader}
    mnd = [r for r in aktive if r["syklus"] == "mnd"]
    aar = [r for r in aktive if r["syklus"] == "aar"]
    mrr = sum(r["pris"] for r in mnd) + sum(r["pris"] / 12 for r in aar)

    return {
        "dato": naa.strftime("%Y-%m-%d"),
        "skool_totalt": len(skool),
        "betalende_aktive": len(aktive),
        "mnd": len(mnd), "aar": len(aar),
        "mrr": round(mrr), "arr": round(mrr * 12),
        "mangler_tilgang": sorted(mangler_tilgang, key=lambda r: r["epost"]),
        "annen_epost": sorted(annen_epost, key=lambda r: r["epost"]),
        "lapset_med_tilgang": sorted(
            [dict(r, skool_navn=skool[r["epost"]]) for r in lapset if r["epost"] in skool],
            key=lambda r: -r["dager"]),
        "uten_betaling": sorted(
            [{"epost": e, "navn": n, "intern": e.endswith(INTERNT_DOMENE)}
             for e, n in skool.items() if e not in betalt_noen_gang],
            key=lambda r: r["epost"]),
    }


def skriv_rapport(a):
    p = print
    p(f"MEDLEMSVAKT — {a['dato']}")
    p("")
    p(f"  Betalende aktive:  {a['betalende_aktive']}  ({a['mnd']} mnd + {a['aar']} år)")
    p(f"  Tilgang i Skool:   {a['skool_totalt']}")
    p(f"  MRR:               EUR {a['mrr']}      ARR: EUR {a['arr']}")
    p("")
    if a["mangler_tilgang"]:
        p(f"🔴 BETALER UTEN TILGANG — {len(a['mangler_tilgang'])} (inviter i dag)")
        for r in a["mangler_tilgang"]:
            p(f"     {r['epost']:38} {r['navn'][:24]:24} sist {r['sist']} ({r['syklus']})")
        p("")
    if a["lapset_med_tilgang"]:
        eksterne = [r for r in a["lapset_med_tilgang"] if not r["epost"].endswith(INTERNT_DOMENE)]
        p(f"🟡 LAPSET MED TILGANG — {len(eksterne)} eksterne")
        for r in a["lapset_med_tilgang"]:
            merk = "  (intern)" if r["epost"].endswith(INTERNT_DOMENE) else ""
            p(f"     {r['epost']:38} {r['skool_navn'][:24]:24} {r['dager']} dager{merk}")
        p("")
    if a["annen_epost"]:
        p(f"🔵 BETALER FRA ANNEN E-POST — {len(a['annen_epost'])} (bare rydd i registeret)")
        for r in a["annen_epost"]:
            p(f"     {r['epost']:38} {r['navn']}")
        p("")
    eksterne = [r for r in a["uten_betaling"] if not r["intern"]]
    p(f"⚪ TILGANG UTEN BETALING — {len(eksterne)} eksterne, "
      f"{len(a['uten_betaling']) - len(eksterne)} interne (krever skjønn)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skool", default=os.path.expanduser("~/Downloads/community_members.csv"))
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--csv")
    args = ap.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))
    env = les_env(os.path.join(here, "../../.env"), os.path.join(here, "../.env"))
    key = env.get("STRIPE_API_KEY") or os.environ.get("STRIPE_API_KEY")
    if not key:
        sys.exit("Mangler STRIPE_API_KEY")
    if not os.path.exists(args.skool):
        sys.exit(f"Fant ikke Skool-eksporten: {args.skool}\n"
                 "Hent den i Skool: Members → Export (krever e-postkode).")

    a = analyser(key, args.skool)

    if args.json:
        print(json.dumps(a, ensure_ascii=False, indent=1))
        return
    if args.csv:
        with open(args.csv, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["Epost", "Navn", "Status", "Syklus", "Sist betalt", "Dager", "Handling"])
            for r in a["mangler_tilgang"]:
                w.writerow([r["epost"], r["navn"], "BETALER UTEN TILGANG", r["syklus"],
                            r["sist"], r["dager"], "Inviter til Skool i dag"])
            for r in a["annen_epost"]:
                w.writerow([r["epost"], r["navn"], "BETALER FRA ANNEN EPOST", r["syklus"],
                            r["sist"], r["dager"], "Rydd i registeret"])
            for r in a["lapset_med_tilgang"]:
                w.writerow([r["epost"], r["skool_navn"], "LAPSET MED TILGANG", r["syklus"],
                            r["sist"], r["dager"], "Påminnelse, fjern etter 21 dager"])
            for r in a["uten_betaling"]:
                w.writerow([r["epost"], r["navn"], "TILGANG UTEN BETALING", "", "", "",
                            "Intern - behold" if r["intern"] else "Vurder"])
        print(f"Skrev {args.csv}")
        return
    skriv_rapport(a)


def demo():
    """Selvsjekk av logikken uten å røre Stripe."""
    assert normaliser("  Pål-Ørjan  JOHANSEN ") == "pal-orjan johansen"
    assert normaliser("Åse Æøå") == "ase aoa"
    assert MEDLEMSKAP[9900] == ("mnd", 99)
    assert FRIST["mnd"] < FRIST["aar"]
    # årlig medlem betalt for 300 dager siden er fortsatt aktiv, månedlig er ikke
    assert 300 <= FRIST["aar"] and 300 > FRIST["mnd"]
    print("demo ok")


if __name__ == "__main__":
    if "--demo" in sys.argv:
        demo()
    else:
        main()