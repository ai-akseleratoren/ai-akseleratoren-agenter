#!/usr/bin/env python3
"""Vinnerkreativer per periode, og om fjorårets vinnere ble gjenbrukt i år.

Bruk:
  python3 scripts/vinnere.py data 2025-08-01                          # topp 10 i én periode
  python3 scripts/vinnere.py data_i_fjor 2024-08-01 data 2025-08-01   # fjorårets vinnere + gjenbruk i år

Hent fjoråret med: python3 scripts/hent_meta.py --siden 2024-08-01 --til 2025-07-31 --data data_i_fjor
Kreativer slås sammen på video-ID, ellers primærtekst-hash, ellers bilde-hash, så
samme kreativ i fem kampanjer telles som én. Gjenbruk matches på video, tekst ELLER bilde.
Score = leads x (snitt-CPL / kreativens CPL): mange leads OG billige. Kun lesing av data/*.json.
"""
import json, collections, hashlib, sys
MIN_LEADS = 100   # kreativer med færre leads er ikke vinnere ennå. Senk for små kontoer.
def act(r,t): return sum(int(a["value"]) for a in r.get("actions",[]) if a["action_type"]==t)
def load(d, since):
    daily=[r for r in json.load(open(f"{d}/insights_ad_daily.json")) if r["date_start"]>=since]
    ads={a["id"]:a for a in json.load(open(f"{d}/ads.json"))}
    return daily, ads
def assets(ad):
    c=ad.get("creative",{}); o=c.get("object_story_spec",{}); f=c.get("asset_feed_spec",{})
    vids=set(filter(None,[c.get("video_id"), o.get("video_data",{}).get("video_id")]+[v.get("video_id") for v in f.get("videos",[])]))
    bodies=set(filter(None,[c.get("body"), o.get("video_data",{}).get("message"), o.get("link_data",{}).get("message")]+[b.get("text") for b in f.get("bodies",[])]))
    titles=set(filter(None,[c.get("title"), o.get("video_data",{}).get("title"), o.get("link_data",{}).get("name")]+[t.get("text") for t in f.get("titles",[])]))
    imgs=set(filter(None,[o.get("link_data",{}).get("image_hash"), o.get("video_data",{}).get("image_hash")]+[i.get("hash") for i in f.get("images",[])]))
    return vids, {hashlib.md5(b.strip().encode()).hexdigest()[:10] for b in bodies}, titles, imgs, bodies
def key(ad):
    v,b,t,i,_=assets(ad)
    return "v:"+min(v) if v else ("b:"+min(b) if b else "i:"+min(i) if i else "ad:"+ad.get("id","?"))
def top(d, since, n=10):
    daily, ads = load(d, since)
    agg=collections.defaultdict(lambda:{"spend":0,"leads":0,"buys":0,"days":set(),"ads":set(),"names":set()})
    for r in daily:
        ad=ads.get(r["ad_id"],{}); k=key(ad); a=agg[k]
        a["spend"]+=float(r["spend"]); a["leads"]+=act(r,"lead"); a["buys"]+=act(r,"purchase"); a["days"].add(r["date_start"]); a["ads"].add(r["ad_id"]); a["names"].add(ad.get("name",r["ad_id"]))
    tot_s=sum(a["spend"] for a in agg.values()); tot_l=sum(a["leads"] for a in agg.values()); avg=tot_s/tot_l
    # "mest billige leads": leads levert under snitt-CPL, vektet: score = leads * (avg/cpl)
    rows=[]
    for k,a in agg.items():
        if a["leads"]<MIN_LEADS: continue
        cpl=a["spend"]/a["leads"]; rows.append((a["leads"]*(avg/cpl), k, a, cpl))
    rows.sort(key=lambda x:-x[0])
    return rows[:n], agg, ads, avg
def tekst(ad):
    v,b,t,i,bodies=assets(ad)
    return (min(t) if t else next(iter(bodies),""))[:60].replace("\n"," ").replace("|","/")
def vis_topp(rows, ads, daily, avg, tittel):
    print(f"## {tittel} (snitt-CPL {avg:.0f})\n")
    print("| # | Kreativ | Forbruk | Leads | CPL | Kjøp | Dager | Tittel/tekststart | Status nå |\n|---|---|---:|---:|---:|---:|---:|---|---|")
    for n,(sc,k,a,cpl) in enumerate(rows,1):
        ad0=ads.get(next(iter(a["ads"])),{})
        status=collections.Counter(ads.get(x,{}).get("effective_status","?") for x in a["ads"])
        last=max(r["date_start"] for r in daily if r["ad_id"] in a["ads"])
        print(f"| {n} | {sorted(a['names'])[0][:45]} | {a['spend']:,.0f} | {a['leads']} | {cpl:.0f} | {a['buys']} | {len(a['days'])} | {tekst(ad0)} | {dict(status)} siste forbruk {last} |")
    print()
if __name__=="__main__":
    if len(sys.argv) not in (3, 5):
        sys.exit(__doc__)
    if len(sys.argv) == 3:
        B, aggB, adsB, avgB = top(sys.argv[1], sys.argv[2])
        vis_topp(B, adsB, load(sys.argv[1], sys.argv[2])[0], avgB, "Topp 10 vinnere")
        sys.exit()
    (dA, sA), (dB, sB) = sys.argv[1:3], sys.argv[3:5]
    A, aggA, adsA, avgA = top(dA, sA)
    B, aggB, adsB, avgB = top(dB, sB)
    # indekser på tvers: alle video-id og body-hash i B
    idxB=collections.defaultdict(set)
    for ad in adsB.values():
        v,b,t,i,_=assets(ad)
        for x in v: idxB["v:"+x].add(ad["id"])
        for x in b: idxB["b:"+x].add(ad["id"])
        for x in i: idxB["i:"+x].add(ad["id"])
    dailyB, _ = load(dB, sB)
    perAdB=collections.defaultdict(lambda:[0,0])
    for r in dailyB: perAdB[r["ad_id"]][0]+=float(r["spend"]); perAdB[r["ad_id"]][1]+=act(r,"lead")
    print(f"## Topp 10 vinnere i forrige periode (snitt-CPL {avgA:.0f}) – og gjenbruk i denne\n")
    print("| # | Kreativ (annonsenavn) | Forbruk | Leads | CPL | Kjøp | Dager | Tittel/tekststart | Gjenbrukt? | Resultat nå |\n|---|---|---:|---:|---:|---:|---:|---|---|---|")
    for n,(sc,k,a,cpl) in enumerate(A,1):
        ad0=adsA.get(next(iter(a["ads"])),{}); v,b,t,i,bodies=assets(ad0)
        # hvilke B-annonser deler video, tekst eller bilde
        hits=set()
        for x in v: hits|=idxB.get("v:"+x,set())
        for x in b: hits|=idxB.get("b:"+x,set())
        for x in i: hits|=idxB.get("i:"+x,set())
        # bare B-annonser med forbruk
        hits={h for h in hits if perAdB.get(h)}
        sp=sum(perAdB[h][0] for h in hits); ld=sum(perAdB[h][1] for h in hits)
        how=[]
        if any(idxB.get("v:"+x) for x in v): how.append("video")
        if any(idxB.get("b:"+x) for x in b): how.append("tekst")
        if any(idxB.get("i:"+x) for x in i): how.append("bilde")
        txt=(min(t) if t else next(iter(bodies),""))[:60].replace("\n"," ")
        res=f"{len(hits)} ann., {sp:,.0f}, {ld} leads, CPL {sp/ld:.0f}" if ld else (f"{len(hits)} ann., {sp:,.0f}, 0 leads" if hits else "–")
        print(f"| {n} | {sorted(a['names'])[0][:45]} | {a['spend']:,.0f} | {a['leads']} | {cpl:.0f} | {a['buys']} | {len(a['days'])} | {txt} | {'JA ('+'/'.join(how)+')' if hits else 'NEI'} | {res} |")
    print()
    vis_topp(B, adsB, dailyB, avgB, "Topp 10 vinnere i denne perioden")
