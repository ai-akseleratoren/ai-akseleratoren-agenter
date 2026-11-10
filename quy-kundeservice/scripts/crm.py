#!/usr/bin/env python3
"""CRM-oppslag: hvem er kunden, hva har hun kjøpt. Kun lesing. Kun stdlib.

  python3 scripts/crm.py doktor              er nøkkelen gyldig?
  python3 scripts/crm.py slaa_opp <epost>    kontakt + kjøp/saker som JSON

CRM velges med CRM=ghl|hubspot|salesforce|kajabi|ingen i .env.
Skriptet endrer ALDRI noe i CRM-et.
"""
import json, os, sys, urllib.parse, urllib.request

sys.path.insert(0, os.path.dirname(__file__))
from felles import env

E = env()
UA = {"User-Agent": "quy-kundeservice/1.0"}


def _get(url, headers=None, data=None, form=False):
    if data is not None and not form:
        data = json.dumps(data).encode()
        headers = dict(headers or {}, **{"Content-Type": "application/json"})
    elif data is not None:
        data = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=data, headers=dict(UA, **(headers or {})))
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit("%s svarte %s: %s" % (url.split("/")[2], e.code, e.read()[:300].decode("utf-8", "replace")))


def _trenger(*nokler):
    for n in nokler:
        if not E.get(n):
            sys.exit("%s mangler i .env — se README.md (Kom i gang)" % n)


# --- GoHighLevel -------------------------------------------------------------
def ghl(epost):
    _trenger("GHL_TOKEN", "GHL_LOCATION_ID")
    h = {"Authorization": "Bearer " + E["GHL_TOKEN"], "Version": "2021-07-28"}
    r = _get("https://services.leadconnectorhq.com/contacts/?" + urllib.parse.urlencode(
        {"locationId": E["GHL_LOCATION_ID"], "query": epost, "limit": 5}), h)
    treff = [c for c in r.get("contacts", []) if (c.get("email") or "").lower() == epost.lower()]
    if not treff:
        return {"funnet": False}
    c = treff[0]
    return {"funnet": True, "navn": c.get("contactName") or (c.get("firstName", "") + " " + c.get("lastName", "")).strip(),
            "epost": c.get("email"), "telefon": c.get("phone"), "tagger": c.get("tags", []),
            "opprettet": c.get("dateAdded"), "id": c.get("id")}


# --- HubSpot -----------------------------------------------------------------
def hubspot(epost):
    _trenger("HUBSPOT_TOKEN")
    h = {"Authorization": "Bearer " + E["HUBSPOT_TOKEN"]}
    r = _get("https://api.hubapi.com/crm/v3/objects/contacts/search", h, {
        "filterGroups": [{"filters": [{"propertyName": "email", "operator": "EQ", "value": epost}]}],
        "properties": ["firstname", "lastname", "email", "phone", "lifecyclestage", "company", "createdate"]})
    if not r.get("results"):
        return {"funnet": False}
    p = r["results"][0]["properties"]
    ut = {"funnet": True, "navn": ((p.get("firstname") or "") + " " + (p.get("lastname") or "")).strip(),
          "epost": p.get("email"), "telefon": p.get("phone"), "fase": p.get("lifecyclestage"),
          "firma": p.get("company"), "opprettet": p.get("createdate"), "id": r["results"][0]["id"]}
    d = _get("https://api.hubapi.com/crm/v4/objects/contacts/%s/associations/deals" % ut["id"], h)
    ut["antall_deals"] = len(d.get("results", []))
    return ut


# --- Salesforce (client credentials-flyt) -----------------------------------
def _sf_token():
    _trenger("SALESFORCE_DOMENE", "SALESFORCE_CLIENT_ID", "SALESFORCE_CLIENT_SECRET")
    r = _get("https://%s/services/oauth2/token" % E["SALESFORCE_DOMENE"], data={
        "grant_type": "client_credentials", "client_id": E["SALESFORCE_CLIENT_ID"],
        "client_secret": E["SALESFORCE_CLIENT_SECRET"]}, form=True)
    return r["access_token"], r["instance_url"]


def _soql(token, base, q):
    return _get(base + "/services/data/v60.0/query?" + urllib.parse.urlencode({"q": q}),
                {"Authorization": "Bearer " + token}).get("records", [])


def salesforce(epost):
    token, base = _sf_token()
    e = epost.replace("'", "\\'")
    k = _soql(token, base, "SELECT Id,Name,Email,Phone,Account.Name FROM Contact WHERE Email='%s' LIMIT 1" % e)
    if not k:
        return {"funnet": False}
    k = k[0]
    saker = _soql(token, base, "SELECT Id,CaseNumber,Subject,Status,CreatedDate FROM Case WHERE ContactId='%s' ORDER BY CreatedDate DESC LIMIT 5" % k["Id"])
    return {"funnet": True, "navn": k.get("Name"), "epost": k.get("Email"), "telefon": k.get("Phone"),
            "konto": (k.get("Account") or {}).get("Name"), "id": k["Id"],
            "saker": [{"nr": s["CaseNumber"], "emne": s["Subject"], "status": s["Status"]} for s in saker]}


# --- Kajabi ------------------------------------------------------------------
def kajabi(epost):
    # ponytail: Kajabis offentlige API er ny og endrer seg — verifiser stien mot developers.kajabi.com ved første kjøring
    _trenger("KAJABI_TOKEN")
    h = {"Authorization": "Bearer " + E["KAJABI_TOKEN"], "Accept": "application/vnd.api+json"}
    r = _get("https://api.kajabi.com/v1/contacts?" + urllib.parse.urlencode({"filter[email]": epost}), h)
    if not r.get("data"):
        return {"funnet": False}
    c = r["data"][0]
    a = c.get("attributes", {})
    return {"funnet": True, "navn": a.get("name"), "epost": a.get("email"), "id": c.get("id"),
            "opprettet": a.get("created_at"), "tagger": a.get("tags", [])}


def ingen(epost):
    return {"funnet": None, "merknad": "CRM=ingen — agenten bruker bare e-posthistorikken"}


CRM = {"ghl": ghl, "hubspot": hubspot, "salesforce": salesforce, "kajabi": kajabi, "ingen": ingen}


def slaa_opp(epost):
    valg = (E.get("CRM") or "ingen").lower()
    if valg not in CRM:
        sys.exit("CRM=%s er ukjent. Bruk en av: %s" % (valg, ", ".join(CRM)))
    print(json.dumps(CRM[valg](epost), ensure_ascii=False, indent=2))


def doktor():
    valg = (E.get("CRM") or "ingen").lower()
    print("CRM:", valg)
    if valg == "ingen":
        return
    CRM[valg]("doktor@eksempel.invalid")
    print("OK — nøkkelen virker (oppslag på tulleadresse ga tomt svar, ingen feil)")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: sys.exit(__doc__)
    if a[0] == "doktor": doktor()
    elif a[0] == "slaa_opp": slaa_opp(a[1])
    else: sys.exit(__doc__)
