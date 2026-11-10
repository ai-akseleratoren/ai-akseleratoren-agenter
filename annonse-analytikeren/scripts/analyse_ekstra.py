#!/usr/bin/env python3
"""Tilleggsanalyser: slitasje per langtidskreativ (paret), læringsfase/ukeleads per
adsett, samtidige adsett, ukefrekvens, kopier, budsjettendringer.

Bruk: python3 scripts/analyse_ekstra.py SIDEN [DATAKATALOG] >> rapporter/tallgrunnlag-....md

Skriver til stdout. Leser bare data/*.json fra hent_meta.py; rører aldri kontoen.
Beløp i kontoens valuta. Juster MIN_MND_FORBRUK etter kontoens størrelse."""
import json, os, sys, collections, hashlib
from datetime import date
sys.path.insert(0, os.path.dirname(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATADIR = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "data")
MIN_MND_FORBRUK = 3000   # celler under dette i 7d vises bare som forbruk
KOPI_MERKER = ("copy", "kopi", "(reuse)", "bản sao")   # navn Ads Manager gir dupliserte annonser
D = lambda n: json.load(open(os.path.join(DATADIR, f"{n}.json")))
SINCE = sys.argv[1] if len(sys.argv) > 1 else sys.exit(__doc__)
daily = [r for r in D("insights_ad_daily") if r["date_start"] >= SINCE]
ads = {a["id"]: a for a in D("ads")}; adsets = {a["id"]: a for a in D("adsets")}; camps = {c["id"]: c for c in D("campaigns")}
def act(r, t): return sum(int(a["value"]) for a in r.get("actions", []) if a["action_type"] == t)
def f(x): return float(x or 0)
def fmt(x, d=0): return "–" if x is None else f"{x:,.{d}f}".replace(",", " ").replace(".", ",")
def cpl(s, l): return fmt(s / l) if l else "–"
def video_of(ad):
    c = ad.get("creative", {}); oss = c.get("object_story_spec", {}); afs = c.get("asset_feed_spec", {})
    return c.get("video_id") or oss.get("video_data", {}).get("video_id") or (afs.get("videos") or [{}])[0].get("video_id")
def body_of(ad):
    c = ad.get("creative", {}); oss = c.get("object_story_spec", {}); afs = c.get("asset_feed_spec", {})
    return c.get("body") or oss.get("video_data", {}).get("message") or oss.get("link_data", {}).get("message") or (afs.get("bodies") or [{}])[0].get("text", "")
def ck(ad):
    v = video_of(ad); return ("video:" + v) if v else "body:" + hashlib.md5(body_of(ad).encode()).hexdigest()[:10]
SL = collections.defaultdict(lambda: [0.0, 0])
def add(d, k, r): d[k][0] += f(r["spend"]); d[k][1] += act(r, "lead")

# 1. Månedlig CPL for de største kreativene (slitasje-sjekk)
per = collections.defaultdict(lambda: collections.defaultdict(lambda: [0.0, 0])); tot = collections.defaultdict(lambda: [0.0, 0]); names = {}
for r in daily:
    k = ck(ads.get(r["ad_id"], {})); names.setdefault(k, ads.get(r["ad_id"], {}).get("name", r["ad_id"]))
    per[k][r["date_start"][:7]][0] += f(r["spend"]); per[k][r["date_start"][:7]][1] += act(r, "lead"); tot[k][0] += f(r["spend"]); tot[k][1] += act(r, "lead")
top = sorted(tot, key=lambda k: -tot[k][1])[:10]
months = sorted({m for k in top for m in per[k]})
print("### 7d. Månedlig CPL for de 10 største kreativene (slitasje-sjekk)\n")
print("| Kreativ | " + " | ".join(m[2:] for m in months) + " |\n|---|" + "---:|" * len(months))
for k in top:
    print(f"| {names[k][:38]} | " + " | ".join((f"{cpl(*per[k][m])} ({fmt(per[k][m][0]/1000)}k)" if per[k][m][0] >= MIN_MND_FORBRUK else ("·" if per[k][m][0] == 0 else f"({fmt(per[k][m][0]/1000)}k)")) for m in months) + " |")
print(f"\n(CPL, forbruk i tusen i parentes; celler under {fmt(MIN_MND_FORBRUK)} i forbruk viser bare forbruket)\n")

# 2. Paret sammenligning: kreativer med >= 45 dager: CPL dag 1–14 vs dag 31+
first = {k: min(r["date_start"] for r in daily if ck(ads.get(r["ad_id"], {})) == k) for k in tot}
early = collections.defaultdict(lambda: [0.0, 0]); late = collections.defaultdict(lambda: [0.0, 0])
for r in daily:
    k = ck(ads.get(r["ad_id"], {}))
    if first[k] < (date.fromisoformat(SINCE) + __import__("datetime").timedelta(days=8)).isoformat(): continue
    dd = (date.fromisoformat(r["date_start"]) - date.fromisoformat(first[k])).days
    if dd < 14: add(early, k, r)
    elif dd >= 30: add(late, k, r)
pairs = [(k, early[k], late[k]) for k in late if early[k][1] >= 10 and late[k][1] >= 10]
print(f"### 7e. Samme kreativ: dag 1–14 mot dag 31+ ({len(pairs)} kreativer startet i perioden, min. 10 leads i begge vinduer)\n")
print("| Kreativ | CPL dag 1–14 | CPL dag 31+ | Endring |\n|---|---:|---:|---:|")
worse = 0; se = sl = le = ll = 0
for k, e, l in sorted(pairs, key=lambda x: -x[2][0]):
    ce, cl_ = e[0] / e[1], l[0] / l[1]; worse += cl_ > ce; se += e[0]; sl += l[0]; le += e[1]; ll += l[1]
    print(f"| {names[k][:40]} | {fmt(ce)} | {fmt(cl_)} | {(cl_/ce-1)*100:+.0f} % |")
print(f"\nSamlet: dag 1–14 CPL {cpl(se, le)} (forbruk {fmt(se)}) vs dag 31+ CPL {cpl(sl, ll)} (forbruk {fmt(sl)}). {worse} av {len(pairs)} ble dyrere med alderen.\n")

# 3. Læringsfase: adsett-uke med < 50 leads vs >= 50
wk = collections.defaultdict(lambda: [0.0, 0])
for r in daily:
    d = date.fromisoformat(r["date_start"]); w = d.isocalendar()[:2]
    wk[(r["adset_id"], w)][0] += f(r["spend"]); wk[(r["adset_id"], w)][1] += act(r, "lead")
b = collections.defaultdict(lambda: [0.0, 0, 0])
for (s, w), (sp, ld) in wk.items():
    key = "< 10 leads/uke" if ld < 10 else "10–24" if ld < 25 else "25–49" if ld < 50 else "50–99" if ld < 100 else "100+ leads/uke"
    b[key][0] += sp; b[key][1] += ld; b[key][2] += 1
print("### 8h. Adsett-uker etter antall leads i uka (læringsfasen trenger ~50 konverteringer/uke)\n")
print("| Leads per adsett-uke | Adsett-uker | Forbruk | Leads | CPL | Andel av forbruk |\n|---|---:|---:|---:|---:|---:|")
T = sum(v[0] for v in b.values())
for key in ["< 10 leads/uke", "10–24", "25–49", "50–99", "100+ leads/uke"]:
    if key in b: sp, ld, n = b[key]; print(f"| {key} | {n} | {fmt(sp)} | {ld} | {cpl(sp, ld)} | {fmt(sp/T*100)} % |")

# 3b. Samtidige adsett per dag vs CPL
day = collections.defaultdict(lambda: [0.0, 0, set(), set()])
for r in daily:
    d = day[r["date_start"]]; d[0] += f(r["spend"]); d[1] += act(r, "lead"); d[2].add(r["adset_id"]); d[3].add(r["ad_id"])
bb = collections.defaultdict(lambda: [0.0, 0, 0])
for dd, (sp, ld, ss, aa) in day.items():
    n = len(ss); key = "1–3 adsett" if n <= 3 else "4–6" if n <= 6 else "7–10" if n <= 10 else "11–15" if n <= 15 else "16+ adsett"
    bb[key][0] += sp; bb[key][1] += ld; bb[key][2] += 1
print("\n### 8i. Antall aktive adsett samme dag vs CPL\n\n| Aktive adsett/dag | Dager | Forbruk | Leads | CPL | Snitt forbruk per adsett/dag |\n|---|---:|---:|---:|---:|---:|")
for key in ["1–3 adsett", "4–6", "7–10", "11–15", "16+ adsett"]:
    if key in bb:
        sp, ld, n = bb[key]; nads = sum(len(v[2]) for d, v in day.items() if (("1–3 adsett" if len(v[2]) <= 3 else "4–6" if len(v[2]) <= 6 else "7–10" if len(v[2]) <= 10 else "11–15" if len(v[2]) <= 15 else "16+ adsett") == key))
        print(f"| {key} | {n} | {fmt(sp)} | {ld} | {cpl(sp, ld)} | {fmt(sp/nads)} |")

# 4. Kopier («Bản sao» / duplikater)
cop = [a for a in ads.values() if a.get("created_time", "")[:10] >= SINCE and any(m in a.get("name", "").lower() for m in KOPI_MERKER)]
n_period = sum(1 for a in ads.values() if a.get("created_time", "")[:10] >= SINCE)
print(f"\n### 8j. Kopier\n\n{len(cop)} av {n_period} annonser opprettet siden {SINCE} har kopi-navn (copy/kopi/reuse) – dvs. dupliserte annonser i nye kampanjer/adsett. Samme kreativ telles som ny annonse og må gjennom ny godkjenning og ny læring hver gang.")

# 5. Budsjettendringer per adsett
acts = D("activities")
bud = collections.Counter(); budd = collections.Counter()
for a in acts:
    if a["event_type"] in ("update_ad_set_budget", "update_campaign_budget"):
        bud[a["object_name"]] += 1; budd[a["event_time"][:10]] += 1
print(f"\n### 8k. Budsjettendringer\n\n{sum(bud.values())} budsjettendringer på {len(bud)} objekter; {len(budd)} dager med endringer; topp: " + ", ".join(f"{k[:30]} ({v})" for k, v in bud.most_common(6)))

# 6. Ukefrekvens fra adsett-uke
try:
    aw = [r for r in D("insights_adset_weekly") if r["date_start"] >= SINCE]
    fb = collections.defaultdict(lambda: [0.0, 0, 0])
    for r in aw:
        fr = f(r.get("frequency")); key = "< 1,5" if fr < 1.5 else "1,5–2" if fr < 2 else "2–2,5" if fr < 2.5 else "2,5–3" if fr < 3 else "3–4" if fr < 4 else "4+"
        fb[key][0] += f(r["spend"]); fb[key][1] += act(r, "lead"); fb[key][2] += 1
    print("\n### 7f. Ukefrekvens per adsett (visninger/rekkevidde i løpet av en uke) vs CPL\n\n| Ukefrekvens | Adsett-uker | Forbruk | Leads | CPL |\n|---|---:|---:|---:|---:|")
    for key in ["< 1,5", "1,5–2", "2–2,5", "2,5–3", "3–4", "4+"]:
        if key in fb: sp, ld, n = fb[key]; print(f"| {key} | {n} | {fmt(sp)} | {ld} | {cpl(sp, ld)} |")
except FileNotFoundError:
    print("\n(insights_adset_weekly mangler – kjør hent_meta.py)")
