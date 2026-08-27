#!/usr/bin/env python3
"""Dyp analyse av en Meta-annonsekonto (siste 12-13 mnd) fra data/*.json.
Skriver rapporter/analyse-YYYY-MM-DD.md + data/analyse.json (tallgrunnlag).
Kun stdlib. Lead = action_type 'lead'. Kjøp = 'purchase'. Beløp i kontoens valuta.
"""
import json, os, sys, collections, statistics, hashlib, re
from datetime import date, datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATADIR = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "data")
D = lambda n: json.load(open(os.path.join(DATADIR, f"{n}.json")))
LEAD, BUY = "lead", "purchase"
SINCE = sys.argv[1] if len(sys.argv) > 1 else str(date.today() - timedelta(days=365))

def act(row, t):
    return sum(int(a["value"]) for a in row.get("actions", []) if a["action_type"] == t)
def f(x): return float(x or 0)
def div(a, b): return a / b if b else None
def fmt(x, d=0):
    if x is None: return "–"
    return f"{x:,.{d}f}".replace(",", " ").replace(".", ",")
def cpl(s, l): return fmt(div(s, l)) if l else "–"

class Agg:
    __slots__ = ("spend", "imp", "reach", "clicks", "lclicks", "leads", "buys", "lpv", "days", "first", "last", "n")
    def __init__(s):
        s.spend = s.imp = s.reach = s.clicks = s.lclicks = s.leads = s.buys = s.lpv = 0; s.days = set(); s.first = s.last = None; s.n = 0
    def add(s, r):
        s.spend += f(r.get("spend")); s.imp += int(r.get("impressions", 0) or 0); s.reach += int(r.get("reach", 0) or 0)
        s.clicks += int(r.get("clicks", 0) or 0); s.lclicks += int(r.get("inline_link_clicks", 0) or 0)
        s.leads += act(r, LEAD); s.buys += act(r, BUY); s.lpv += act(r, "landing_page_view"); s.n += 1
        d = r.get("date_start")
        if d:
            s.days.add(d); s.first = min(s.first or d, d); s.last = max(s.last or d, d)
    @property
    def cpl(s): return div(s.spend, s.leads)
    @property
    def cpm(s): return div(s.spend * 1000, s.imp)
    @property
    def ctr(s): return div(s.lclicks * 100, s.imp)
    @property
    def cvr(s): return div(s.leads * 100, s.lclicks)   # lead per lenkeklikk
    @property
    def lpv_rate(s): return div(s.lpv * 100, s.lclicks)
    @property
    def freq(s): return div(s.imp, s.reach)
    def row(s, name, extra=""):
        return f"| {name} | {fmt(s.spend)} | {s.leads} | {cpl(s.spend, s.leads)} | {fmt(s.cpm, 0)} | {fmt(s.ctr, 2)} | {fmt(s.cvr, 1)} | {s.buys} {extra}|"
HDR = "| Slice | Forbruk | Leads | CPL | CPM | CTR % | Lead/klikk % | Kjøp |\n|---|---:|---:|---:|---:|---:|---:|---:|"

def group(rows, key):
    g = collections.defaultdict(Agg)
    for r in rows: g[key(r)].add(r)
    return g

daily = [r for r in D("insights_ad_daily") if r["date_start"] >= SINCE]
ads = {a["id"]: a for a in D("ads")}
adsets = {a["id"]: a for a in D("adsets")}
camps = {c["id"]: c for c in D("campaigns")}
acts = D("activities")
out = {"since": SINCE, "until": max(r["date_start"] for r in daily)}
L = []
P = L.append

tot = Agg()
for r in daily: tot.add(r)
P(f"# Dypanalyse av annonsekontoen\n\nPeriode **{SINCE} – {out['until']}** (konto {os.environ.get('META_AD_ACCOUNT', '<konto>')}, valuta fra kontoen). Kilde: Meta Marketing API, annonsenivå per dag. Lead = Meta-pikselens `lead`, kjøp = `purchase`. Pikseltall, ikke CRM-tall – bruk som relative mål.\n")
P(f"**Totalt:** {fmt(tot.spend)} kr · {tot.leads} leads · CPL {fmt(tot.cpl)} kr · {tot.buys} kjøp · CPA {fmt(div(tot.spend, tot.buys))} kr · CPM {fmt(tot.cpm)} · CTR {fmt(tot.ctr,2)} % · lead/klikk {fmt(tot.cvr,1)} % · {len(tot.days)} dager med forbruk av {(date.fromisoformat(out['until'])-date.fromisoformat(SINCE)).days+1}\n")

# ---------- 1. Måned for måned ----------
P("\n## 1. Måned for måned\n\n" + HDR.replace("Slice", "Måned"))
months = group(daily, lambda r: r["date_start"][:7])
camp_by_month = collections.defaultdict(set); ads_by_month = collections.defaultdict(set)
for r in daily: camp_by_month[r["date_start"][:7]].add(r["campaign_id"]); ads_by_month[r["date_start"][:7]].add(r["ad_id"])
for m in sorted(months):
    a = months[m]; P(a.row(m, f"| {len(camp_by_month[m])} kamp / {len(ads_by_month[m])} ann. "))
P("\n(siste kolonne: antall kampanjer / annonser med forbruk den måneden)")
out["months"] = {m: dict(spend=a.spend, leads=a.leads, cpl=a.cpl, buys=a.buys) for m, a in months.items()}

# ---------- 2. Kampanjer ----------
P("\n## 2. Kampanjer (sortert på forbruk)\n\n| Kampanje | Start–slutt (forbruk) | Dager | Forbruk | Leads | CPL | Kjøp | Annonser |\n|---|---|---:|---:|---:|---:|---:|---:|")
cg = group(daily, lambda r: r["campaign_id"])
ads_in_camp = collections.defaultdict(set)
for r in daily: ads_in_camp[r["campaign_id"]].add(r["ad_id"])
for cid, a in sorted(cg.items(), key=lambda x: -x[1].spend):
    if a.spend < 5000: continue
    P(f"| {camps.get(cid,{}).get('name',cid)[:45]} | {a.first}–{a.last} | {len(a.days)} | {fmt(a.spend)} | {a.leads} | {cpl(a.spend,a.leads)} | {a.buys} | {len(ads_in_camp[cid])} |")
out["campaigns"] = {camps.get(c,{}).get("name",c): dict(spend=a.spend, leads=a.leads, cpl=a.cpl, first=a.first, last=a.last, days=len(a.days)) for c, a in cg.items()}

# ---------- 3. Plassering ----------
P("\n## 3. Plasseringer (publisher × posisjon)\n")
pl_ad = D("insights_placement_ad")
pl_ad = [r for r in pl_ad]  # hele perioden (time_range fra hent)
def plkey(r): return f"{r.get('publisher_platform','?')} / {r.get('platform_position','?')}"
pg = group(pl_ad, plkey)
P("### 3a. Hele perioden\n\n" + HDR.replace("Slice", "Plassering"))
for k, a in sorted(pg.items(), key=lambda x: -x[1].spend):
    if a.spend < 2000: continue
    P(a.row(k))
out["placements"] = {k: dict(spend=a.spend, leads=a.leads, cpl=a.cpl, ctr=a.ctr, cvr=a.cvr) for k, a in pg.items()}
# per måned (kampanjenivå, med impression_device)
plm = D("insights_placement_monthly")
P("\n### 3b. Plassering per måned – CPL (kun plasseringer > 3 000 kr i måneden)\n")
pm = collections.defaultdict(Agg)
for r in plm:
    if r["date_start"] >= SINCE: pm[(r["date_start"][:7], plkey(r))].add(r)
allm = sorted({k[0] for k in pm}); top = [k for k, a in sorted(pg.items(), key=lambda x: -x[1].spend)[:8]]
P("| Måned | " + " | ".join(t.replace("instagram","IG").replace("facebook","FB").replace("audience_network","AN")[:28] for t in top) + " |\n|---|" + "---:|" * len(top))
for m in allm:
    cells = []
    for t in top:
        a = pm.get((m, t))
        cells.append(f"{cpl(a.spend,a.leads)} ({fmt(a.spend/1000)}k)" if a and a.spend >= 3000 else "·")
    P(f"| {m} | " + " | ".join(cells) + " |")
P("\n(CPL i kr, forbruk i parentes i tusen)")
# enhet
dev = collections.defaultdict(Agg)
for r in plm:
    if r["date_start"] >= SINCE: dev[r.get("impression_device","?")].add(r)
P("\n### 3c. Enhet (impression_device)\n\n" + HDR.replace("Slice", "Enhet"))
for k, a in sorted(dev.items(), key=lambda x: -x[1].spend):
    if a.spend > 2000: P(a.row(k))
# adsett: manuell vs Advantage+ plasseringer
P("\n### 3d. Plasseringsvalg på adsett-nivå (Advantage+ vs manuell)\n\n" + HDR.replace("Slice", "Adsett-plasseringsvalg"))
def adset_placement_mode(s):
    t = s.get("targeting", {})
    if t.get("publisher_platforms"): return "Manuell: " + "+".join(t["publisher_platforms"]) + (" (" + ",".join(t.get("facebook_positions", []) + t.get("instagram_positions", []))[:50] + ")" if t.get("facebook_positions") or t.get("instagram_positions") else "")
    return "Advantage+ (alle plasseringer)"
apm = group(daily, lambda r: adset_placement_mode(adsets.get(r["adset_id"], {})))
for k, a in sorted(apm.items(), key=lambda x: -x[1].spend): P(a.row(k[:70]))

# ---------- 4. Målgruppe / alder / kjønn / land ----------
P("\n## 4. Målgrupper\n")
def audience_type(s):
    t = s.get("targeting", {}); n = s.get("name", "").lower()
    if t.get("custom_audiences"):
        names = " ".join(c.get("name", "") for c in t["custom_audiences"]).lower()
        if "lookalike" in names or "ll " in names or "lal" in names or re.search(r"\d%", names): return "Lookalike"
        return "Retargeting/kundeliste"
    if t.get("flexible_spec") or t.get("interests"): return "Interesser"
    if t.get("targeting_automation", {}).get("advantage_audience"): return "Advantage+ audience (bred)"
    return "Bred (ingen målretting)"
ag = group(daily, lambda r: audience_type(adsets.get(r["adset_id"], {})))
P("### 4a. Målgruppetype (fra adsettets targeting)\n\n" + HDR.replace("Slice", "Målgruppetype"))
for k, a in sorted(ag.items(), key=lambda x: -x[1].spend): P(a.row(k))
out["audience_types"] = {k: dict(spend=a.spend, leads=a.leads, cpl=a.cpl) for k, a in ag.items()}
# Adsett-topp
P("\n### 4b. Adsett med mest forbruk\n\n| Adsett | Kampanje | Type | Forbruk | Leads | CPL | Opt.mål | Budsjett/dag |\n|---|---|---|---:|---:|---:|---|---:|")
sg = group(daily, lambda r: r["adset_id"])
for sid, a in sorted(sg.items(), key=lambda x: -x[1].spend)[:25]:
    s = adsets.get(sid, {})
    P(f"| {s.get('name',sid)[:40]} | {camps.get(s.get('campaign_id'),{}).get('name','')[:30]} | {audience_type(s)} | {fmt(a.spend)} | {a.leads} | {cpl(a.spend,a.leads)} | {s.get('optimization_goal','')} | {fmt(f(s.get('daily_budget'))/100)} |")
agm = [r for r in D("insights_agegender_monthly") if r["date_start"] >= SINCE]
P("\n### 4c. Alder × kjønn\n\n" + HDR.replace("Slice", "Alder/kjønn"))
ag2 = group(agm, lambda r: f"{r.get('age')} {r.get('gender')}")
for k, a in sorted(ag2.items(), key=lambda x: x[0]):
    if a.spend > 5000: P(a.row(k))
ctm = [r for r in D("insights_country_monthly") if r["date_start"] >= SINCE]
P("\n### 4d. Land\n\n" + HDR.replace("Slice", "Land"))
for k, a in sorted(group(ctm, lambda r: r.get("country")).items(), key=lambda x: -x[1].spend):
    if a.spend > 1000: P(a.row(k))

# ---------- 5. Annonsetype / kreativ ----------
P("\n## 5. Annonsetyper og kreativer\n")
def creative_type(ad):
    c = ad.get("creative", {}); oss = c.get("object_story_spec", {}); afs = c.get("asset_feed_spec", {})
    if c.get("object_type") == "VIDEO" or c.get("video_id") or oss.get("video_data"): base = "Video"
    elif afs.get("images") and len(afs.get("images", [])) > 1 and not afs.get("videos"): base = "Bilde (flere)"
    elif oss.get("link_data", {}).get("child_attachments"): base = "Karusell"
    elif oss.get("link_data", {}).get("image_hash") or oss.get("photo_data") or afs.get("images"): base = "Bilde"
    elif afs.get("videos"): base = "Video"
    else: base = c.get("object_type", "Ukjent")
    if afs.get("bodies") and len(afs["bodies"]) > 1 or afs.get("titles") and len(afs["titles"]) > 1: base += " + flere tekster (dyn.)"
    return base
def body_of(ad):
    c = ad.get("creative", {}); oss = c.get("object_story_spec", {}); afs = c.get("asset_feed_spec", {})
    if c.get("body"): return c["body"]
    for k in ("video_data", "link_data"):
        if oss.get(k, {}).get("message"): return oss[k]["message"]
    if afs.get("bodies"): return afs["bodies"][0].get("text", "")
    return ""
def title_of(ad):
    c = ad.get("creative", {}); oss = c.get("object_story_spec", {}); afs = c.get("asset_feed_spec", {})
    if c.get("title"): return c["title"]
    for k in ("video_data", "link_data"):
        if oss.get(k, {}).get("title") or oss.get(k, {}).get("name"): return oss[k].get("title") or oss[k].get("name")
    if afs.get("titles"): return afs["titles"][0].get("text", "")
    return ""
def video_of(ad):
    c = ad.get("creative", {}); oss = c.get("object_story_spec", {}); afs = c.get("asset_feed_spec", {})
    return c.get("video_id") or oss.get("video_data", {}).get("video_id") or (afs.get("videos") or [{}])[0].get("video_id")
ctg = group(daily, lambda r: creative_type(ads.get(r["ad_id"], {})))
P("### 5a. Format\n\n" + HDR.replace("Slice", "Format"))
for k, a in sorted(ctg.items(), key=lambda x: -x[1].spend): P(a.row(k))
out["formats"] = {k: dict(spend=a.spend, leads=a.leads, cpl=a.cpl) for k, a in ctg.items()}
# Tekstlengde
def lenbucket(ad):
    n = len(body_of(ad))
    return "Kort (<300 tegn)" if n < 300 else "Middels (300–800)" if n < 800 else "Lang (800–1500)" if n < 1500 else "Svært lang (>1500)"
P("\n### 5b. Lengde på primærtekst\n\n" + HDR.replace("Slice", "Tekstlengde"))
for k, a in sorted(group(daily, lambda r: lenbucket(ads.get(r["ad_id"], {}))).items(), key=lambda x: -x[1].spend): P(a.row(k))
# CTA
P("\n### 5c. CTA-knapp\n\n" + HDR.replace("Slice", "CTA"))
def cta(ad):
    c = ad.get("creative", {}); oss = c.get("object_story_spec", {})
    return c.get("call_to_action_type") or oss.get("video_data", {}).get("call_to_action", {}).get("type") or oss.get("link_data", {}).get("call_to_action", {}).get("type") or "?"
for k, a in sorted(group(daily, lambda r: cta(ads.get(r["ad_id"], {}))).items(), key=lambda x: -x[1].spend):
    if a.spend > 2000: P(a.row(k))

# ---------- 6. Enkeltannonser og kreativ-gjenbruk ----------
adg = group(daily, lambda r: r["ad_id"])
# samle på kreativ-identitet: video_id eller hash av body
def cre_key(ad):
    v = video_of(ad); b = body_of(ad)
    return ("video:" + v) if v else ("body:" + hashlib.md5(b.encode()).hexdigest()[:10])
cre = collections.defaultdict(lambda: {"agg": Agg(), "ads": set(), "camps": set(), "names": set(), "first_created": None})
for aid, a in adg.items():
    ad = ads.get(aid, {}); k = cre_key(ad)
    c = cre[k]; c["ads"].add(aid); c["camps"].add(ad.get("campaign_id")); c["names"].add(ad.get("name", aid))
    ct = ad.get("created_time", "")[:10]
    if ct: c["first_created"] = min(c["first_created"] or ct, ct)
for r in daily: cre[cre_key(ads.get(r["ad_id"], {}))]["agg"].add(r)
P("\n## 6. Kreativer – vinnere, tapere og gjenbruk\n\nSamme video/tekst dukker ofte opp som flere «annonser» i nye kampanjer. Her er de slått sammen per kreativ.\n")
P("### 6a. Topp 25 kreativer på leads\n\n| Kreativ (annonsenavn) | Format | Forbruk | Leads | CPL | Kjøp | Første–siste dag | Dager m/forbruk | Ant. annonser/kampanjer | Tittel |\n|---|---|---:|---:|---:|---:|---|---:|---:|---|")
for k, c in sorted(cre.items(), key=lambda x: -x[1]["agg"].leads)[:25]:
    a = c["agg"]; ad0 = ads.get(next(iter(c["ads"])), {})
    P(f"| {sorted(c['names'])[0][:40]} | {creative_type(ad0)[:14]} | {fmt(a.spend)} | {a.leads} | {cpl(a.spend,a.leads)} | {a.buys} | {a.first}–{a.last} | {len(a.days)} | {len(c['ads'])}/{len(c['camps'])} | {title_of(ad0)[:40]} |")
P("\n### 6b. Billigste kreativer (CPL, min. 15 leads)\n\n| Kreativ | Format | Forbruk | Leads | CPL | Dager | Tittel | Start på tekst |\n|---|---|---:|---:|---:|---:|---|---|")
goods = [(k, c) for k, c in cre.items() if c["agg"].leads >= 15]
for k, c in sorted(goods, key=lambda x: x[1]["agg"].cpl)[:20]:
    a = c["agg"]; ad0 = ads.get(next(iter(c["ads"])), {})
    P(f"| {sorted(c['names'])[0][:40]} | {creative_type(ad0)[:14]} | {fmt(a.spend)} | {a.leads} | {cpl(a.spend,a.leads)} | {len(a.days)} | {title_of(ad0)[:35]} | {body_of(ad0)[:90].replace(chr(10),' ')} |")
P("\n### 6c. Dyreste kreativer (CPL, min. 5 000 kr forbruk)\n\n| Kreativ | Format | Forbruk | Leads | CPL | Dager | Tittel |\n|---|---|---:|---:|---:|---:|---|")
bads = [(k, c) for k, c in cre.items() if c["agg"].spend >= 5000]
for k, c in sorted(bads, key=lambda x: -(x[1]["agg"].cpl or 9e9))[:20]:
    a = c["agg"]; ad0 = ads.get(next(iter(c["ads"])), {})
    P(f"| {sorted(c['names'])[0][:40]} | {creative_type(ad0)[:14]} | {fmt(a.spend)} | {a.leads} | {cpl(a.spend,a.leads)} | {len(a.days)} | {title_of(ad0)[:35]} |")
# gjenbruk vs ny
reuse = Agg(); fresh = Agg()
for k, c in cre.items():
    (reuse if len(c["camps"]) > 1 else fresh).spend += c["agg"].spend
    (reuse if len(c["camps"]) > 1 else fresh).leads += c["agg"].leads
P(f"\n### 6d. Gjenbrukte vs. nye kreativer\n\n- Kreativer brukt i **flere kampanjer**: {sum(1 for c in cre.values() if len(c['camps'])>1)} stk, {fmt(reuse.spend)} kr, {reuse.leads} leads, CPL {cpl(reuse.spend, reuse.leads)}\n- Kreativer brukt i **én kampanje**: {sum(1 for c in cre.values() if len(c['camps'])==1)} stk, {fmt(fresh.spend)} kr, {fresh.leads} leads, CPL {cpl(fresh.spend, fresh.leads)}")
out["creatives"] = {sorted(c["names"])[0]: dict(spend=c["agg"].spend, leads=c["agg"].leads, cpl=c["agg"].cpl, days=len(c["agg"].days), first=c["agg"].first, last=c["agg"].last, n_ads=len(c["ads"]), n_camps=len(c["camps"])) for k, c in cre.items()}

# ---------- 7. Levetid og slitasje ----------
P("\n## 7. Levetid og slitasje (ad fatigue)\n")
# per kreativ: CPL per leveuke (uke siden første forbruksdag for kreativen)
life = collections.defaultdict(Agg)
cre_first = {k: c["agg"].first for k, c in cre.items()}
for r in daily:
    k = cre_key(ads.get(r["ad_id"], {})); d0 = date.fromisoformat(cre_first[k]); d = date.fromisoformat(r["date_start"])
    w = (d - d0).days // 7
    b = f"Uke {w+1}" if w < 8 else "Uke 9–12" if w < 12 else "Uke 13–26" if w < 26 else "Uke 27+"
    life[b].add(r)
P("### 7a. CPL etter kreativens alder (uker siden første visning, alle kreativer samlet)\n\n| Leveuke | Forbruk | Leads | CPL | CPM | CTR % | Lead/klikk % | Frekvens |\n|---|---:|---:|---:|---:|---:|---:|---:|")
order = [f"Uke {i}" for i in range(1, 9)] + ["Uke 9–12", "Uke 13–26", "Uke 27+"]
for b in order:
    a = life.get(b)
    if a: P(f"| {b} | {fmt(a.spend)} | {a.leads} | {cpl(a.spend,a.leads)} | {fmt(a.cpm)} | {fmt(a.ctr,2)} | {fmt(a.cvr,1)} | {fmt(a.freq,2)} |")
out["life_weeks"] = {b: dict(spend=a.spend, leads=a.leads, cpl=a.cpl) for b, a in life.items()}
# Levetidsfordeling
spans = [(len(c["agg"].days), c["agg"].spend, c["agg"].leads, c["agg"].cpl) for c in cre.values() if c["agg"].spend > 500]
buckets = [("1–3 dager", 0, 3), ("4–7 dager", 4, 7), ("8–14 dager", 8, 14), ("15–30 dager", 15, 30), ("31–60 dager", 31, 60), ("61–120 dager", 61, 120), ("121+ dager", 121, 9999)]
P("\n### 7b. Hvor lenge lever en kreativ? (kreativer med > 500 kr forbruk)\n\n| Dager med forbruk | Antall kreativer | Forbruk | Leads | CPL |\n|---|---:|---:|---:|---:|")
for name, lo, hi in buckets:
    sel = [s for s in spans if lo <= s[0] <= hi]
    sp = sum(s[1] for s in sel); ld = sum(s[2] for s in sel)
    P(f"| {name} | {len(sel)} | {fmt(sp)} | {ld} | {cpl(sp, ld)} |")
# Frekvens-bucket på adsett/dag
P("\n### 7c. CPL ved ulik frekvens (adsett-dag-rader, frekvens = visninger/rekkevidde den dagen)\n\n| Frekvens | Forbruk | Leads | CPL |\n|---|---:|---:|---:|")
fb = collections.defaultdict(Agg)
for r in daily:
    fr = f(r.get("frequency"))
    b = "<1,2" if fr < 1.2 else "1,2–1,5" if fr < 1.5 else "1,5–2" if fr < 2 else "2–3" if fr < 3 else "3+"
    fb[b].add(r)
for b in ["<1,2", "1,2–1,5", "1,5–2", "2–3", "3+"]:
    a = fb.get(b)
    if a: P(f"| {b} | {fmt(a.spend)} | {a.leads} | {cpl(a.spend,a.leads)} |")

# ---------- 8. Av/på, læringsfase, kontinuitet ----------
P("\n## 8. Av/på-mønster, læringsfase og kontinuitet\n")
acc = collections.defaultdict(Agg)
for r in daily: acc[r["date_start"]].add(r)
alld = sorted(acc)
d0, d1 = date.fromisoformat(SINCE), date.fromisoformat(out["until"])
zero_days = [(d0 + timedelta(i)).isoformat() for i in range((d1 - d0).days + 1) if (d0 + timedelta(i)).isoformat() not in acc]
# pauser (sammenhengende nulldager)
gaps = []; run = []
for i in range((d1 - d0).days + 1):
    dd = (d0 + timedelta(i)).isoformat()
    if dd not in acc: run.append(dd)
    elif run: gaps.append((run[0], run[-1], len(run))); run = []
if run: gaps.append((run[0], run[-1], len(run)))
P(f"- Dager uten forbruk: **{len(zero_days)}** av {(d1-d0).days+1}. Pauser ≥ 3 dager: " + (", ".join(f"{g[0]}→{g[1]} ({g[2]} d)" for g in gaps if g[2] >= 3) or "ingen"))
# daglig forbruk-variasjon
sp = [acc[d].spend for d in alld]
P(f"- Daglig forbruk: median {fmt(statistics.median(sp))} kr, snitt {fmt(statistics.mean(sp))} kr, maks {fmt(max(sp))} kr, min (dager m/forbruk) {fmt(min(sp))} kr. Standardavvik {fmt(statistics.pstdev(sp))} kr → variasjonskoeffisient {fmt(statistics.pstdev(sp)/statistics.mean(sp)*100)} %.")
# CPL etter dag i kampanjens liv (kampanjestart = første forbruksdag)
cf = {c: a.first for c, a in cg.items()}
cl = collections.defaultdict(Agg)
for r in daily:
    dd = (date.fromisoformat(r["date_start"]) - date.fromisoformat(cf[r["campaign_id"]])).days
    b = "Dag 1–3" if dd < 3 else "Dag 4–7" if dd < 7 else "Dag 8–14" if dd < 14 else "Dag 15–30" if dd < 30 else "Dag 31–60" if dd < 60 else "Dag 61+"
    cl[b].add(r)
P("\n### 8a. CPL etter kampanjens alder (læringsfase-effekt)\n\n| Kampanjealder | Forbruk | Leads | CPL | CPM |\n|---|---:|---:|---:|---:|")
for b in ["Dag 1–3", "Dag 4–7", "Dag 8–14", "Dag 15–30", "Dag 31–60", "Dag 61+"]:
    a = cl.get(b)
    if a: P(f"| {b} | {fmt(a.spend)} | {a.leads} | {cpl(a.spend,a.leads)} | {fmt(a.cpm)} |")
out["campaign_age"] = {b: dict(spend=a.spend, leads=a.leads, cpl=a.cpl) for b, a in cl.items()}
# adsett-alder
sf = {s: a.first for s, a in sg.items()}
sl = collections.defaultdict(Agg)
for r in daily:
    dd = (date.fromisoformat(r["date_start"]) - date.fromisoformat(sf[r["adset_id"]])).days
    b = "Dag 1–3" if dd < 3 else "Dag 4–7" if dd < 7 else "Dag 8–14" if dd < 14 else "Dag 15–30" if dd < 30 else "Dag 31+"
    sl[b].add(r)
P("\n### 8b. CPL etter adsettets alder\n\n| Adsett-alder | Forbruk | Leads | CPL |\n|---|---:|---:|---:|")
for b in ["Dag 1–3", "Dag 4–7", "Dag 8–14", "Dag 15–30", "Dag 31+"]:
    a = sl.get(b)
    if a: P(f"| {b} | {fmt(a.spend)} | {a.leads} | {cpl(a.spend,a.leads)} |")
# Antall nye kampanjer/adsett/annonser per måned
P("\n### 8c. Hvor ofte startes nytt? (første forbruksdag)\n\n| Måned | Nye kampanjer | Nye adsett | Nye annonser | Nye kreativer |\n|---|---:|---:|---:|---:|")
newc = collections.Counter(a.first[:7] for a in cg.values()); news = collections.Counter(a.first[:7] for a in sg.values()); newa = collections.Counter(a.first[:7] for a in adg.values()); newk = collections.Counter(c["agg"].first[:7] for c in cre.values())
for m in sorted(months): P(f"| {m} | {newc[m]} | {news[m]} | {newa[m]} | {newk[m]} |")
# Aktivitetslogg
if acts:
    ev = collections.Counter(); actor = collections.Counter(); evm = collections.defaultdict(collections.Counter)
    for a in acts:
        ev[a.get("event_type")] += 1; actor[a.get("actor_name", "?")] += 1; evm[a.get("event_time", "")[:7]][a.get("event_type")] += 1
    P(f"\n### 8d. Aktivitetslogg (endringer i kontoen, {len(acts)} hendelser)\n\nVanligste hendelser: " + ", ".join(f"{k} ({v})" for k, v in ev.most_common(12)))
    P("\nHvem: " + ", ".join(f"{k} ({v})" for k, v in actor.most_common(8)))
    keys = ["update_ad_set_run_status", "update_campaign_run_status", "update_ad_run_status", "update_ad_set_budget", "update_campaign_budget", "create_ad", "create_ad_set", "create_campaign", "update_ad_creative"]
    keys = [k for k in keys if ev.get(k)]
    P("\n| Måned | " + " | ".join(k.replace("update_", "").replace("_run_status", " av/på").replace("_", " ") for k in keys) + " |\n|---|" + "---:|" * len(keys))
    for m in sorted(evm):
        if m >= SINCE[:7]: P(f"| {m} | " + " | ".join(str(evm[m].get(k, 0)) for k in keys) + " |")
# Budsjett-nivå vs CPL (daglig kontoforbruk i bucket)
P("\n### 8e. Dagsforbruk vs CPL (hele kontoen per dag)\n\n| Dagsforbruk | Dager | Forbruk | Leads | CPL |\n|---|---:|---:|---:|---:|")
bb = collections.defaultdict(lambda: [0, Agg()])
for d in alld:
    s = acc[d].spend
    b = "< 2 000" if s < 2000 else "2–5 000" if s < 5000 else "5–10 000" if s < 10000 else "10–15 000" if s < 15000 else "15–25 000" if s < 25000 else "25 000+"
    bb[b][0] += 1
    for r in [x for x in daily if x["date_start"] == d]: bb[b][1].add(r)
for b in ["< 2 000", "2–5 000", "5–10 000", "10–15 000", "15–25 000", "25 000+"]:
    if b in bb: n, a = bb[b]; P(f"| {b} | {n} | {fmt(a.spend)} | {a.leads} | {cpl(a.spend,a.leads)} |")
# Ukedag
P("\n### 8f. Ukedag\n\n| Ukedag | Forbruk | Leads | CPL |\n|---|---:|---:|---:|")
wd = collections.defaultdict(Agg); names = ["Man", "Tir", "Ons", "Tor", "Fre", "Lør", "Søn"]
for r in daily: wd[date.fromisoformat(r["date_start"]).weekday()].add(r)
for i in range(7):
    a = wd.get(i)
    if a: P(f"| {names[i]} | {fmt(a.spend)} | {a.leads} | {cpl(a.spend,a.leads)} |")
# Time på døgnet
hr = D("insights_hourly")
P("\n### 8g. Time på døgnet (hele perioden)\n\n| Time | Forbruk | Leads | CPL |\n|---|---:|---:|---:|")
for k, a in sorted(group(hr, lambda r: r.get("hourly_stats_aggregated_by_advertiser_time_zone", "?")[:5]).items()):
    P(f"| {k} | {fmt(a.spend)} | {a.leads} | {cpl(a.spend,a.leads)} |")

# ---------- 9. Optimaliseringsmål / budstrategi ----------
P("\n## 9. Optimaliseringsmål, budstrategi og konverteringsevent\n\n" + HDR.replace("Slice", "Opt.mål / bud / event"))
def og(s):
    po = s.get("promoted_object", {})
    return f"{s.get('optimization_goal','?')} / {s.get('bid_strategy','?')} / {po.get('custom_event_type') or po.get('custom_conversion_id') or ''}"
for k, a in sorted(group(daily, lambda r: og(adsets.get(r["adset_id"], {}))).items(), key=lambda x: -x[1].spend):
    if a.spend > 2000: P(a.row(k))
P("\n### Kampanjemål\n\n" + HDR.replace("Slice", "Objective"))
for k, a in sorted(group(daily, lambda r: camps.get(r["campaign_id"], {}).get("objective", "?")).items(), key=lambda x: -x[1].spend): P(a.row(k))

json.dump(out, open(os.path.join(DATADIR, "analyse.json"), "w"), ensure_ascii=False, indent=1, default=str)
fn = os.path.join(ROOT, "rapporter", f"tallgrunnlag-{SINCE}_{out['until']}.md")
open(fn, "w").write("\n".join(L) + "\n")
print(fn)
