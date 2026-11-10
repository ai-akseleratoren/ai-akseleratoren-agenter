#!/usr/bin/env python3
"""Ogilvy's set-up watch: are the ads spending money set up the way they claim?

Built after a Swedish campaign was set up to deliver in Norway and spent about
EUR 2,000 in two days before anyone saw it.

For every ad that spent in the last two days or was created in the last
three, compare what the ad says it is (campaign, ad set and ad names, the
language of the text, the landing page) with where it is delivered.

    python3 oppsettvakt.py             # print findings, post nothing
    python3 oppsettvakt.py --send      # post new findings to your Slack channel
    python3 oppsettvakt.py --selftest

Also warns at 80% and over the weekly cap per country (spend by delivery country).

Env: META_ADS_TOKEN, META_AD_ACCOUNT_ID (act_...), SLACK_BOT_TOKEN, SLACK_CHANNEL_ID,
ALERT_MENTIONS (e.g. "<@U...> <@U...>"), WEEKLY_CAP (e.g. "NO:4000,SE:2000", EUR per
Monday-Sunday week), EXCLUDE_CAMPAIGNS (comma list; campaigns whose name contains
one of these are skipped, e.g. another company in the same ad account).
Country detection reads NO/SE in names, Norwegian/Swedish text and /no or /se in the URL.

Read-only in Meta: it never pauses anything. State: ~/.ogilvy/oppsettvakt.json
holds findings already posted, so each is posted once. Silent when clean.
"""
import json, os, re, sys, time, urllib.error, urllib.parse, urllib.request

GRAPH = "https://graph.facebook.com/v21.0"
KANAL = os.environ.get("SLACK_CHANNEL_ID", "")
VARSLE = os.environ.get("ALERT_MENTIONS", "")
STATE = os.path.expanduser("~/.ogilvy/oppsettvakt.json")
LAND = {"NO": "Norway", "SE": "Sweden"}
UKETAK = {l.strip().upper(): float(v) for l, v in
          (x.split(":") for x in os.environ.get("WEEKLY_CAP", "").split(",") if ":" in x)}
EKSKLUDER = tuple(x.strip().lower() for x in os.environ.get("EXCLUDE_CAMPAIGNS", "").split(",") if x.strip())


def ekskludert(kampanje):
    return any(x in kampanje.lower() for x in EKSKLUDER)

NAVN = re.compile(r"(?<![A-Za-z])(NO|SE)(?![A-Za-z])")
SV = {"och", "inte", "jag", "mig", "är", "hur", "vad", "på", "för", "att", "du", "vi", "som", "kan"} - {"du", "vi", "som", "kan", "på"}
NB = {"og", "ikke", "jeg", "meg", "er", "hvordan", "hva", "å", "fordi", "hvor", "bare", "også"}
MND = "januar|februar|mars|april|mai|juni|juli|august|september|oktober|november|desember"
DATO = re.compile(r"\b(mandag|tirsdag|onsdag|torsdag|fredag|lørdag|søndag|måndag|tisdag|lördag|söndag"
                  rf"|\d{{1,2}}\.?\s*(?:{MND}|maj|augusti|oktober|januari|februari))\b", re.I)


def navneland(*navn):
    return {m for n in navn for m in NAVN.findall(n or "")}


def tekstland(tekst):
    ord_ = re.findall(r"[a-zæøåäö]+", (tekst or "").lower())
    sv, nb = sum(o in SV for o in ord_), sum(o in NB for o in ord_)
    if sv >= nb + 3:
        return "SE"
    if nb >= sv + 3:
        return "NO"
    return None


def sideland(url):
    deler = urllib.parse.urlparse(url or "").path.lower().split("/")
    if "se" in deler or "sv" in deler:
        return "SE"
    return "NO" if "no" in deler else None


def felt(creative):
    """All text and landing links of a creative."""
    oss = creative.get("object_story_spec") or {}
    ld = oss.get("link_data") or oss.get("video_data") or {}
    afs = creative.get("asset_feed_spec") or {}
    tekst = [creative.get("body"), creative.get("title"), ld.get("message"), ld.get("name"),
             ld.get("title"), ld.get("description")]
    tekst += [x.get("text") for k in ("bodies", "titles", "descriptions") for x in afs.get(k, [])]
    lenker = [ld.get("link"), (ld.get("call_to_action") or {}).get("value", {}).get("link")]
    lenker += [u.get("website_url") for u in afs.get("link_urls", [])]
    return "\n".join(t for t in tekst if t), sorted({l for l in lenker if l})


def sjekk(ad):
    """Return [(kind, what is wrong)] for one ad."""
    c = ad.get("creative") or {}
    kampanje, adsett = ad["campaign"]["name"], ad["adset"]["name"]
    land = set((ad["adset"].get("targeting") or {}).get("geo_locations", {}).get("countries") or [])
    tekst, lenker = felt(c)
    funn, hvor = [], " + ".join(sorted(LAND.get(l, l) for l in land)) or "no country set"

    signal = {}
    for l in navneland(kampanje, adsett, ad["name"]):
        signal.setdefault(l, []).append("name")
    if tekstland(tekst):
        signal.setdefault(tekstland(tekst), []).append("text language")
    for lenke in lenker:
        if sideland(lenke):
            signal.setdefault(sideland(lenke), []).append("landing page")
    for l, kilder in sorted(signal.items()):
        if land != {l}:
            funn.append(("land", f"{LAND[l]} by its {', '.join(sorted(set(kilder)))}, but delivered to {hvor}"))
    if len(signal) > 1:
        funn.append(("blanding", "mixes countries: " + ", ".join(f"{LAND[l]} ({', '.join(sorted(set(k)))})" for l, k in sorted(signal.items()))))
    if land == {"SE"} and lenker and not any(sideland(l) == "SE" for l in lenker):
        funn.append(("side", f"delivered to Sweden, but the page has no /se: {lenker[0]}"))

    m = DATO.search(tekst)
    if m:
        funn.append(("dato", f"date or weekday in the ad: «{m.group(0)}»"))
    if lenker and not c.get("url_tags") and not any("utm_" in l for l in lenker):
        funn.append(("utm", "no UTM tags, sales can't be traced to this ad"))
    return funn


def fb(path, token, **q):
    q["access_token"] = token
    with urllib.request.urlopen(f"{GRAPH}/{path}?{urllib.parse.urlencode(q)}", timeout=90) as r:
        return json.load(r)


def ukerader(token, konto):
    return fb(f"{konto}/insights", token, level="campaign", date_preset="this_week_mon_today",
              breakdowns="country", fields="campaign_name,spend", limit=500)["data"]


def annonser(token, konto):
    felter = ("name,effective_status,created_time,campaign{name},adset{name,targeting{geo_locations{countries}}},"
              "creative{url_tags,body,title,object_story_spec,asset_feed_spec}")
    filt = json.dumps([{"field": "effective_status", "operator": "IN",
                        "value": ["ACTIVE", "PENDING_REVIEW", "IN_PROCESS", "PREAPPROVED"]}])
    ut, side = [], fb(f"{konto}/ads", token, fields=felter, filtering=filt, limit=100)
    while True:
        ut += side["data"]
        neste = side.get("paging", {}).get("next")
        if not neste:
            break
        with urllib.request.urlopen(neste, timeout=90) as r:
            side = json.load(r)
    bruk, side = {}, fb(f"{konto}/insights", token, level="ad", date_preset="today", fields="ad_id,spend", limit=500)
    for r in side["data"]:
        bruk[r["ad_id"]] = float(r["spend"])
    igaar = fb(f"{konto}/insights", token, level="ad", date_preset="yesterday", fields="ad_id,spend", limit=500)["data"]
    aktive = bruk.keys() | {r["ad_id"] for r in igaar if float(r["spend"]) > 0}
    grense = time.strftime("%Y-%m-%d", time.gmtime(time.time() - 3 * 86400))
    # ponytail: old ads whose campaign ran out still report ACTIVE, so "ACTIVE" alone means nothing
    ut = [a for a in ut if a["id"] in aktive or a["created_time"][:10] >= grense]
    return [a for a in ut if not ekskludert(a["campaign"]["name"])], bruk


def rapport(ads, bruk, kjent):
    """Group new findings per ad set. Returns (message or None, all current keys)."""
    grupper, naa = {}, set()
    for a in ads:
        for slag, tekst in sjekk(a):
            n = f"{a['adset']['id']}:{slag}:{tekst}" if "id" in a["adset"] else f"{a['id']}:{slag}:{tekst}"
            naa.add(n)
            if n not in kjent:
                g = grupper.setdefault((a["campaign"]["name"], a["adset"]["name"]), {"funn": {}, "eur": 0.0})
                g["funn"][tekst] = slag
        k = (a["campaign"]["name"], a["adset"]["name"])
        if k in grupper:
            grupper[k]["eur"] += bruk.get(a["id"], 0)
    if not grupper:
        return None, naa
    linjer = [f"🖋 *Ad set-up problem* {VARSLE}"]
    for (kampanje, adsett), g in sorted(grupper.items(), key=lambda x: -x[1]["eur"]):
        linjer.append(f"*{kampanje}* / {adsett} (EUR {g['eur']:.0f} today)")
        linjer += [f"• {t}" for t, s in sorted(g["funn"].items(), key=lambda x: x[1] != "land")]
    linjer.append("Nothing has been paused. — Ogilvy")
    return "\n".join(linjer), naa


def uketak(rader, uke):
    """rader: insights per campaign and country this week. Returns ([warning lines], keys)."""
    bruk = {}
    for r in rader:
        if not ekskludert(r["campaign_name"]):
            bruk[r["country"]] = bruk.get(r["country"], 0) + float(r["spend"])
    linjer, naa = [], set()
    for land, tak in UKETAK.items():
        eur = bruk.get(land, 0)
        for grad, tekst in ((1.0, "OVER the weekly cap"), (0.8, "at 80% of the weekly cap")):
            if eur >= tak * grad:
                naa.add(f"tak:{uke}:{land}:{grad}")
                linjer.append((f"tak:{uke}:{land}:{grad}", f"• {LAND.get(land, land)}: EUR {eur:,.0f} this week, {tekst} of EUR {tak:,.0f}"))
                break
    return linjer, naa


def post(tekst):
    req = urllib.request.Request("https://slack.com/api/chat.postMessage",
                                 json.dumps({"channel": KANAL, "text": tekst}).encode(),
                                 {"Authorization": "Bearer " + os.environ["SLACK_BOT_TOKEN"],
                                  "Content-Type": "application/json; charset=utf-8"})
    with urllib.request.urlopen(req, timeout=30) as r:
        svar = json.load(r)
    if not svar.get("ok"):
        sys.exit(f"Slack refused: {svar.get('error')}")


def selftest():
    global EKSKLUDER, UKETAK
    EKSKLUDER, UKETAK = ("otherco",), {"NO": 4000, "SE": 2000}
    def ad(kampanje, land, tekst, lenke="https://example.com/se/webinar/x", tags="utm_source=facebook", adsett="A+", navn="v1"):
        return {"id": "1", "name": navn, "campaign": {"name": kampanje},
                "adset": {"id": "9", "name": adsett, "targeting": {"geo_locations": {"countries": land}}},
                "creative": {"url_tags": tags, "object_story_spec": {"link_data": {"message": tekst, "link": lenke}}}}
    sv = "Jag vet inte hur du gör, och det är inte svårt att börja för att jag visar hur."
    nb = "Jeg vet ikke hvordan du gjør det, og det er ikke vanskelig fordi jeg viser hvordan."
    slag = lambda a: {s for s, _ in sjekk(a)}
    assert slag(ad("SE_MEMBERSHIP_NEW ADS", ["NO"], sv)) >= {"land"}, "Swedish campaign delivered to Norway"
    assert not slag(ad("SE_MEMBERSHIP", ["SE"], sv))
    assert not slag(ad("NO_WEBINAR", ["NO"], nb, "https://example.com/webinar/x"))
    assert "land" in slag(ad("EVERGREEN", ["NO"], sv, "https://example.com/"))
    assert "land" in slag(ad("AI", ["NO", "SE"], sv))
    assert "land" in slag(ad("AI", ["NO"], nb, "https://example.com/se/webinar/x"))
    assert "side" in slag(ad("SE_X", ["SE"], sv, "https://example.com/webinar/x"))
    assert "dato" in slag(ad("NO_X", ["NO"], nb + " Tirsdag 12. november", "https://a.com/"))
    assert "utm" in slag(ad("NO_X", ["NO"], nb, "https://a.com/", ""))
    assert not {"land"} & slag(ad("NOTE_X", ["SE"], sv)), "NO inside a word is no signal"
    a = ad("SE_X", ["NO"], sv)
    tekst, naa = rapport([a], {"1": 12.4}, set())
    assert "EUR 12" in tekst and "Nothing has been paused" in tekst
    assert rapport([a], {}, naa)[0] is None, "same finding is not posted twice"
    rad = lambda k, l, e: {"campaign_name": k, "country": l, "spend": str(e)}
    linjer, _ = uketak([rad("NO_A", "NO", 3000), rad("B", "NO", 1500), rad("OTHERCO x", "SE", 5000), rad("SE_A", "SE", 1700)], "2026-W45")
    assert "OVER" in linjer[0][1] and "80%" in linjer[1][1] and len(linjer) == 2
    assert uketak([rad("SE_A", "SE", 100)], "2026-W45") == ([], set())
    print("ok")


def main():
    if "--selftest" in sys.argv:
        return selftest()
    token, konto = os.environ["META_ADS_TOKEN"], os.environ["META_AD_ACCOUNT_ID"]
    try:
        ads, bruk = annonser(token, konto)
        rader = ukerader(token, konto)
    except urllib.error.HTTPError as e:
        sys.exit(f"Meta refused: {e.read().decode('utf-8', 'replace')[:200]}")
    try:
        kjent = set(json.load(open(STATE)))
    except (OSError, ValueError):
        kjent = set()
    tekst, naa = rapport(ads, bruk, kjent)
    tak, taknaa = uketak(rader, time.strftime("%G-W%V"))
    naa |= taknaa
    nye = [l for k, l in tak if k not in kjent]
    if nye:
        tekst = (tekst + "\n" if tekst else f"🖋 *Weekly ad budget* {VARSLE}\n") + "\n".join(nye) + ("" if tekst else "\nNothing has been paused. — Ogilvy")
    if "--send" not in sys.argv:
        print(tekst or f"Clean: {len(ads)} ads checked.")
        return
    if tekst:
        post(tekst)
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    with open(STATE, "w") as f:
        json.dump(sorted(naa), f)


if __name__ == "__main__":
    main()
