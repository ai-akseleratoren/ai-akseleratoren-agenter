#!/usr/bin/env python3
"""Messenger + Instagram-DM via Meta Graph API. Kun stdlib.

  python3 scripts/meta.py doktor                 token, side, IG-konto
  python3 scripts/meta.py sveip [--dager 3]      ubesvarte samtaler (siste melding fra kunden)
  python3 scripts/meta.py les <samtale-id>       hele samtalen
  python3 scripts/meta.py svar <samtale-id> <fil>  send svaret (KUN etter eksplisitt ja)

Regler Meta håndhever:
- Du kan svare i 24 timer etter kundens siste melding. Etter det avviser
  API-et svaret (feil #10 / 2018278) — da må kunden skrive igjen, eller du
  svarer manuelt i Meta Business Suite.
- Utkast finnes ikke i Messenger/Instagram. Agenten skriver utkast til
  utkast/<samtale-id>.txt og sender først når du sier «send».
"""
import json, os, sys, urllib.parse, urllib.request
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(__file__))
from felles import env, logg, ROT

E = env()
API = "https://graph.facebook.com/" + E.get("META_API_VERSION", "v21.0")
UTKAST = os.path.join(ROT, "utkast")


def kall(sti, params=None, data=None):
    token = E.get("META_PAGE_TOKEN") or sys.exit("META_PAGE_TOKEN mangler i .env — se README.md (Meta-tokenet)")
    params = dict(params or {}, access_token=token)
    url = API + sti + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, data=json.dumps(data).encode() if data else None,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        feil = json.load(e).get("error", {})
        sys.exit("Meta sa nei (%s): %s\nkode %s, subkode %s" % (
            e.code, feil.get("message"), feil.get("code"), feil.get("error_subcode")))


def side():
    return E.get("META_PAGE_ID") or sys.exit("META_PAGE_ID mangler i .env")


def doktor():
    meg = kall("/me", {"fields": "id,name"})
    print("Token gjelder:", meg.get("name"), meg.get("id"))
    if meg.get("id") != side():
        print("ADVARSEL: tokenet er ikke et side-token for META_PAGE_ID — se README.md (Meta-tokenet)")
    s = kall("/" + side(), {"fields": "name,instagram_business_account"})
    ig = s.get("instagram_business_account", {}).get("id")
    print("Side:", s.get("name"), "| Instagram-konto:", ig or "IKKE KOBLET (koble IG til siden i Meta Business Suite)")
    if ig and ig != E.get("META_IG_ID"):
        print("Sett META_IG_ID=%s i .env" % ig)
    for plattform in ("messenger", "instagram"):
        r = kall("/%s/conversations" % side(), {"platform": plattform, "limit": 1, "fields": "id"})
        print("%-10s samtaler leses: OK" % plattform)


def _samtaler(plattform, dager):
    r = kall("/%s/conversations" % side(), {
        "platform": plattform, "limit": 25,
        "fields": "id,updated_time,participants,messages.limit(10){id,message,from,created_time}"})
    grense = datetime.now(timezone.utc) - timedelta(days=dager)
    for s in r.get("data", []):
        oppdatert = datetime.fromisoformat(s["updated_time"].replace("+0000", "+00:00"))
        if oppdatert < grense:
            continue
        meldinger = s.get("messages", {}).get("data", [])
        if not meldinger:
            continue
        siste = meldinger[0]  # nyeste først
        if siste.get("from", {}).get("id") in (side(), E.get("META_IG_ID")):
            continue  # vi svarte sist
        kunde = siste.get("from", {})
        yield plattform, s, kunde, siste, oppdatert


def sveip(dager=3):
    n = 0
    for plattform, s, kunde, siste, oppdatert in list(_samtaler("messenger", dager)) + list(_samtaler("instagram", dager)):
        n += 1
        timer_igjen = 24 - (datetime.now(timezone.utc) - datetime.fromisoformat(siste["created_time"].replace("+0000", "+00:00"))).total_seconds() / 3600
        print("=" * 60)
        print("plattform:", plattform, "| samtale:", s["id"])
        print("fra:", kunde.get("name") or kunde.get("username", "?"), "| kunde-id:", kunde.get("id"))
        print("sist:", siste["created_time"], "| svarvindu igjen: %.1f t" % timer_igjen + (" — UTLØPT" if timer_igjen < 0 else ""))
        print("-" * 60)
        for m in reversed(s["messages"]["data"][:5]):
            hvem = "oss" if m.get("from", {}).get("id") in (side(), E.get("META_IG_ID")) else "kunde"
            print("[%s] %s" % (hvem, (m.get("message") or "(vedlegg/emoji)")[:500]))
    print("=" * 60)
    print("Ubesvarte:", n)


def les(sid):
    r = kall("/" + sid, {"fields": "messages.limit(30){message,from,created_time}"})
    for m in reversed(r["messages"]["data"]):
        hvem = "oss" if m.get("from", {}).get("id") in (side(), E.get("META_IG_ID")) else m.get("from", {}).get("name", "kunde")
        print("%s  %s: %s" % (m["created_time"], hvem, m.get("message") or "(vedlegg/emoji)"))


def svar(sid, fil):
    tekst = open(fil, encoding="utf-8").read().strip()
    r = kall("/" + sid, {"fields": "messages.limit(10){from},participants"})
    mottaker = None
    for m in r["messages"]["data"]:
        fid = m.get("from", {}).get("id")
        if fid not in (side(), E.get("META_IG_ID")):
            mottaker = fid
            break
    if not mottaker:
        sys.exit("Fant ingen kunde i samtalen — ingenting sendt")
    res = kall("/%s/messages" % side(), data={
        "recipient": {"id": mottaker}, "messaging_type": "RESPONSE", "message": {"text": tekst}})
    logg({"kanal": "meta", "hendelse": "sendt", "samtale": sid, "mottaker": mottaker, "melding_id": res.get("message_id")})
    print("Sendt til", mottaker, "— melding", res.get("message_id"))
    u = os.path.join(UTKAST, sid + ".txt")
    if os.path.exists(u):
        os.remove(u)


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: sys.exit(__doc__)
    k = a[0]
    if k == "doktor": doktor()
    elif k == "sveip": sveip(int(a[a.index("--dager") + 1]) if "--dager" in a else 3)
    elif k == "les": les(a[1])
    elif k == "svar": svar(a[1], a[2])
    else: sys.exit(__doc__)
