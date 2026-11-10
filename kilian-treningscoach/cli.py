#!/usr/bin/env python3
"""Kilian: dag | uke | status | logg | test. Sannhetskilden er logg/logg.csv.

    python3 cli.py dag [DATO]          dagens økt
    python3 cli.py uke [N]             ukeplanen
    python3 cli.py status              ukestatus, ulogget, dager uten trening, vekttrend
    python3 cli.py logg DATO ja|nei [type] [min] [volum] [vekt] [kommentar]

Planen ligger i program/plan.csv, én rad per uke:
    uke,mandag,man,tir,ons,tor,fre,lor,son,volum_maal
    1,2026-11-16,Styrke A,Sone 2 40 min,Styrke B,Hvile,Hvile,Lang tur 60 min,Rolig gåtur,400
«volum» er det målet ditt måles i: høydemeter, km eller minutter. Kilian skriver planen
sammen med deg i oppsett-intervjuet. Kun standardbiblioteket.
"""
import csv
import datetime as dt
import pathlib
import sys

ROOT = pathlib.Path(__file__).parent
PLAN = ROOT / "program" / "plan.csv"
LOGG = ROOT / "logg" / "logg.csv"
DAGER = ["man", "tir", "ons", "tor", "fre", "lor", "son"]
FELT = ["dato", "ukedag", "planlagt", "gjort", "type", "minutter", "volum", "vekt", "kommentar"]


def plan():
    with open(PLAN, newline="", encoding="utf-8") as f:
        return [{**r, "mandag": dt.date.fromisoformat(r["mandag"])} for r in csv.DictReader(f)]


def uke_for(d, p=None):
    for r in p or plan():
        if r["mandag"] <= d < r["mandag"] + dt.timedelta(days=7):
            return r
    return None


def les():
    if not LOGG.exists():
        return []
    with open(LOGG, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def dag(d=None):
    d = d or dt.date.today()
    p = plan()
    r = uke_for(d, p)
    if not r:
        return f"{d}: utenfor planen ({p[0]['mandag']} – {p[-1]['mandag'] + dt.timedelta(days=6)})."
    return f"{d} ({DAGER[d.weekday()]}), uke {r['uke']}/{len(p)}, volummål {r['volum_maal']}/uke: {r[DAGER[d.weekday()]]}"


def uke(n=None):
    p = plan()
    r = next((x for x in p if x["uke"] == str(n)), None) if n else uke_for(dt.date.today(), p)
    if not r:
        return "Fant ikke uka i planen."
    return f"Uke {r['uke']} (fra {r['mandag']}), volummål {r['volum_maal']}:\n" + \
        "\n".join(f"  {k.capitalize()}: {r[k]}" for k in DAGER)


def logg(dato, gjort, type_="", minutter="", volum="", vekt="", kommentar=""):
    d = dt.date.fromisoformat(dato)
    r = uke_for(d)
    rader = [x for x in les() if x["dato"] != dato]
    rader.append({"dato": dato, "ukedag": DAGER[d.weekday()], "planlagt": r[DAGER[d.weekday()]] if r else "",
                  "gjort": gjort, "type": type_, "minutter": minutter, "volum": volum,
                  "vekt": vekt, "kommentar": kommentar})
    rader.sort(key=lambda x: x["dato"])
    LOGG.parent.mkdir(exist_ok=True)
    with open(LOGG, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, FELT)
        w.writeheader()
        w.writerows(rader)
    return f"Logget {dato}: gjort={gjort} {type_} {minutter}min volum={volum} vekt={vekt}"


def status(d=None):
    d = d or dt.date.today()
    p, rader = plan(), les()
    r = uke_for(d, p)
    slutt = p[-1]["mandag"] + dt.timedelta(days=6)
    ut = [f"Dager igjen av planen: {(slutt - d).days}."]
    if r:
        denne = [x for x in rader if r["mandag"] <= dt.date.fromisoformat(x["dato"]) <= d]
        gjort = [x for x in denne if x["gjort"] == "ja"]
        vol = sum(float(x["volum"] or 0) for x in denne)
        logget = {x["dato"] for x in rader}
        ulogget = [str(r["mandag"] + dt.timedelta(days=i)) for i in range((d - r["mandag"]).days)
                   if str(r["mandag"] + dt.timedelta(days=i)) not in logget]
        ut += [f"Uke {r['uke']}/{len(p)}: {len(gjort)} økter gjort, volum {vol:g}/{r['volum_maal']}.",
               f"Ulogget denne uka: {', '.join(ulogget) or 'ingen'}."]
    rekke = 0
    for x in sorted(rader, key=lambda x: x["dato"], reverse=True):
        if x["gjort"] != "nei":
            break
        rekke += 1
    ut.append(f"Dager på rad uten trening: {rekke}.")
    vekter = [(x["dato"], float(x["vekt"].replace(",", "."))) for x in rader if x["vekt"]]
    if vekter:
        ut.append(f"Vekt: start {vekter[0][1]} ({vekter[0][0]}), sist {vekter[-1][1]} ({vekter[-1][0]}), "
                  f"endring {vekter[-1][1] - vekter[0][1]:+.1f} kg.")
    else:
        ut.append("Vekt: ingen måling ennå.")
    return "\n".join(ut)


def test():
    import tempfile
    global PLAN, LOGG
    with tempfile.TemporaryDirectory() as td:
        PLAN, LOGG = pathlib.Path(td) / "plan.csv", pathlib.Path(td) / "logg.csv"
        PLAN.write_text("uke,mandag,man,tir,ons,tor,fre,lor,son,volum_maal\n"
                        "1,2026-11-16,Styrke A,Sone 2,Styrke B,Hvile,Hvile,Lang tur,Gåtur,400\n"
                        "2,2026-11-23,Styrke A,Sone 2,Styrke B,Intervall,Hvile,Lang tur,Gåtur,500\n")
        assert "Lang tur" in dag(dt.date(2026, 11, 21)) and "uke 1/2" in dag(dt.date(2026, 11, 21))
        assert "Intervall" in dag(dt.date(2026, 11, 26)) and "utenfor" in dag(dt.date(2026, 12, 7))
        logg("2026-11-16", "ja", "Styrke A", "50", "0", "90,5")
        logg("2026-11-17", "ja", "Mølle", "45", "350")
        logg("2026-11-18", "nei")
        s = status(dt.date(2026, 11, 19))
        assert "2 økter gjort, volum 350/400" in s and "Dager på rad uten trening: 1" in s and "2026-11-19" not in s, s
        assert "Ulogget denne uka: ingen" in s, s
        print("ok")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] == "dag":
        print(dag(dt.date.fromisoformat(a[1]) if len(a) > 1 else None))
    elif a[0] == "uke":
        print(uke(int(a[1]) if len(a) > 1 else None))
    elif a[0] == "status":
        print(status())
    elif a[0] == "logg" and len(a) >= 3:
        print(logg(*a[1:]))
    elif a[0] == "test":
        test()
    else:
        print(__doc__)
