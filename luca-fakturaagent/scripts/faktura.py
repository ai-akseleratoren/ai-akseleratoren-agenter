#!/usr/bin/env python3
"""Invoicing + receivables in GoHighLevel — run by Luca, the bookkeeping agent.

Usage:
  python3 scripts/faktura.py oversikt      # AR overview + aging -> faktura/ar-YYYY-MM-DD.md
  python3 scripts/faktura.py purreliste [--min 900] [--maks-alder 365]   # overdue list to chase
  python3 scripts/faktura.py sjekk         # token + scope check (safe, writes nothing)
  python3 scripts/faktura.py mal           # copy the invoice template from your newest paid invoice
  python3 scripts/faktura.py ny --epost kunde@example.com --belop 990 --valuta EUR \
      [--firma "Firma AS" --orgnr 123456789 --adresse "Gate 1, 0150 Oslo" --land NO] \
        --tekst "Produkt - avdrag 2 av 3" [--forfall YYYY-MM-DD] [--send]
      (due date defaults to tomorrow: invoices fall due one day after they are sent)
  python3 scripts/faktura.py send --id <invoiceId>
  python3 scripts/faktura.py marker-betalt --id <invoiceId> --belop 990 --dato YYYY-MM-DD
  python3 scripts/faktura.py krediter --id <invoiceId> --grunn "..."   # void, irreversible

Rules (see SKILL.md):
  - `ny` creates a DRAFT by default. Sending happens only with --send, or via
    `send --id`, and only after a human has said yes.
  - Amounts are never invented: they come from the pipeline (Won + value), the
    payment-plan file or a named human. This script does not check that —
    Luca does, before calling it.

Keys from .env (current folder or the folder above scripts/) or the
environment: GHL_TOKEN, GHL_LOCATION_ID, INVOICE_FROM_NAME, INVOICE_FROM_EMAIL,
INVOICE_CC_EMAIL, INVOICE_DEFAULT_COUNTRY. Amounts are kept per currency and
never converted.
"""
import json, os, sys, urllib.request, urllib.parse, urllib.error
from datetime import date, datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAK = os.environ.get("FAKTURA_DIR", os.path.join(os.getcwd(), "faktura"))
os.makedirs(FAK, exist_ok=True)

env = {}
for p in (os.path.join(os.getcwd(), ".env"), os.path.join(ROOT, ".env")):
    if os.path.exists(p):
        with open(p) as f:
            for line in f:
                if "=" in line and not line.strip().startswith("#"):
                    k, v = line.strip().split("=", 1)
                    env.setdefault(k, v)
env = {**env, **os.environ}   # real environment wins (servers, password managers)

TOKEN = env["GHL_TOKEN"]
LOC = env["GHL_LOCATION_ID"]
BASE = "https://services.leadconnectorhq.com"
# NOTE: GHL blocks the default Python-urllib User-Agent with 403. Always send one.
HDR = {"Authorization": f"Bearer {TOKEN}", "Version": "2021-07-28",
       "Accept": "application/json", "User-Agent": "curl/8.7.1"}
TODAY = date.today()


def http(path, method="GET", body=None, timeout=90):
    url = path if path.startswith("http") else BASE + path
    data = json.dumps(body).encode() if body is not None else None
    h = dict(HDR)
    if data:
        h["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            raise SystemExit(f"HTTP {e.code} {method} {url}\n{json.dumps(json.loads(raw), indent=2)}")
        except json.JSONDecodeError:
            raise SystemExit(f"HTTP {e.code} {method} {url}\n{raw}")


def hent_alle():
    """Every invoice in the subaccount, oldest first."""
    ut, off = [], 0
    while True:
        q = urllib.parse.urlencode({"altId": LOC, "altType": "location",
                                    "limit": 100, "offset": off})
        d = http("/invoices/?" + q)
        ut += d.get("invoices", [])
        off += 100
        if len(ut) >= d.get("total", 0) or not d.get("invoices"):
            return ut


def dag(s):
    return (s or "")[:10]


def rest(i):
    return round((i.get("total") or 0) - (i.get("amountPaid") or 0), 2)


def alder(i):
    d = dag(i.get("dueDate"))
    if not d:
        return None
    return (TODAY - date(*map(int, d.split("-")))).days


UBETALT = ("sent", "partially_paid", "overdue")


def bøtte(dager):
    if dager is None or dager <= 0:
        return "Not due yet"
    if dager <= 30:
        return "1-30 days"
    if dager <= 90:
        return "31-90 days"
    if dager <= 365:
        return "91-365 days"
    return "Over a year (clean-up pile)"


BØTTER = ["Not due yet", "1-30 days", "31-90 days", "91-365 days",
          "Over a year (clean-up pile)"]


def penger(d):
    return ", ".join(f"{v:,.0f} {k}" for k, v in sorted(d.items(), key=lambda x: -x[1])) or "-"


def summer(liste):
    ut = {}
    for i in liste:
        ut[i.get("currency", "?")] = ut.get(i.get("currency", "?"), 0) + rest(i)
    return ut


# ---------------- oversikt ----------------
def oversikt():
    alle = hent_alle()
    ubetalt = [i for i in alle if i.get("status") in UBETALT]
    grupper = {b: [] for b in BØTTER}
    for i in ubetalt:
        grupper[bøtte(alder(i))].append(i)
    forfalt = [i for i in ubetalt if (alder(i) or 0) > 0]

    L = [f"# Receivables — {TODAY}", "",
         f"Source: GoHighLevel invoices API, pulled {datetime.now():%Y-%m-%d %H:%M}.",
         f"{len(alle)} invoices in total, {len(ubetalt)} unpaid, {len(forfalt)} past due.",
         "Amounts are outstanding balance (total minus paid), kept per currency — no FX conversion.",
         "", "## Aging", "",
         "| Age | Invoices | Outstanding |", "|---|---:|---|"]
    for b in BØTTER:
        g = grupper[b]
        if g:
            L.append(f"| {b} | {len(g)} | {penger(summer(g))} |")
    L += [f"| **Total unpaid** | **{len(ubetalt)}** | **{penger(summer(ubetalt))}** |", ""]

    ferske = [i for i in forfalt if (alder(i) or 0) <= 365]
    L += ["## Live overdue (due within the last year) — this is the collectable pile", "",
          f"{len(ferske)} invoices, {penger(summer(ferske))}", "",
          "| Due | Days | # | Customer | Amount | Status |", "|---|---:|---|---|---:|---|"]
    for i in sorted(ferske, key=lambda x: -rest(x)):
        c = i.get("contactDetails") or {}
        L.append(f"| {dag(i.get('dueDate'))} | {alder(i)} | {i.get('invoiceNumber')} | "
                 f"{c.get('name', '?')} | {rest(i):,.0f} {i.get('currency')} | {i.get('status')} |")

    gamle = [i for i in forfalt if (alder(i) or 0) > 365]
    L += ["", "## Older than a year — clean-up, not collection", "",
          f"{len(gamle)} invoices, {penger(summer(gamle))}. These skew every AR number in GHL. "
          "The bookkeeper decides per invoice: paid outside GHL (mark paid), dead (void), or still real (chase).", ""]
    kunder = {}
    for i in gamle:
        n = (i.get("contactDetails") or {}).get("name", "?")
        kunder[n] = kunder.get(n, 0) + rest(i)
    for n, v in sorted(kunder.items(), key=lambda x: -x[1])[:20]:
        L.append(f"- {n}: {v:,.0f}")

    sti = os.path.join(FAK, f"ar-{TODAY}.md")
    open(sti, "w").write("\n".join(L) + "\n")
    print("\n".join(L[:40]))
    print(f"\n-> {sti}")


# ---------------- purreliste ----------------
def purreliste():
    maks = int(arg("--maks-alder", "365"))
    minbel = float(arg("--min", "0"))
    ubetalt = [i for i in hent_alle() if i.get("status") in UBETALT]
    liste = [i for i in ubetalt if 0 < (alder(i) or 0) <= maks and rest(i) >= minbel]
    liste.sort(key=lambda x: -rest(x))
    print(f"Chase list — {len(liste)} invoices, {penger(summer(liste))} "
          f"(due in the last {maks} days, min {minbel:.0f})\n")
    for i in liste:
        c = i.get("contactDetails") or {}
        print(f"{rest(i):>9,.0f} {i.get('currency')}  {alder(i):>4}d  #{i.get('invoiceNumber')}  "
              f"{c.get('name', '?')[:34]:34}  {c.get('email', '-')}  {c.get('phoneNo', '-')}")


# ---------------- ny faktura ----------------
def finn_kontakt(epost):
    q = urllib.parse.urlencode({"locationId": LOC, "limit": 5, "query": epost})
    for c in http("/contacts/?" + q).get("contacts", []):
        if (c.get("email") or "").lower() == epost.lower():
            return c
    raise SystemExit(f"No contact in GHL with email {epost} — create the contact first, "
                     "or check the spelling. Never invoice a contact you cannot find.")


def ny():
    epost, tekst = arg("--epost"), arg("--tekst")
    if not (epost and tekst):
        raise SystemExit("ny requires --epost and --tekst (and --belop)")
    iid = lag_utkast(epost, float(arg("--belop")), arg("--valuta", "EUR"), tekst, arg("--forfall"),
                     arg("--utstedt"), arg("--firma"), arg("--orgnr"), arg("--adresse"), arg("--land"))
    if "--send" in sys.argv:
        send(iid)
    else:
        print(f"Not sent. To send:  python3 scripts/faktura.py send --id {iid}")


def lag_utkast(epost, belop, valuta, tekst, forfall=None, utstedt=None, firma=None, orgnr=None,
               adresse_linje=None, land=None):
    """Create a DRAFT invoice in GHL. Returns the invoice id."""
    valuta = valuta.upper()
    # Due one day after the invoice goes out. forfall only for a date a human names for this invoice.
    forfall = forfall or str(TODAY + timedelta(days=1))
    utstedt = utstedt or str(TODAY)
    mal = json.load(open(os.path.join(FAK, "mal.json")))
    if not logo_lever(mal["businessDetails"].get("logoUrl")):
        raise SystemExit("Logo URL in mal.json is dead — the customer would see a "
                         "broken image. Run: faktura.py mal")
    k = finn_kontakt(epost)
    firma = firma or k.get("companyName") or ""
    adresse = {"countryCode": (land or k.get("country") or env.get("INVOICE_DEFAULT_COUNTRY", "NO"))}
    if adresse_linje:
        adresse["addressLine1"] = adresse_linje
    body = {
        "altId": LOC, "altType": "location", "name": tekst,
        "currency": valuta, "liveMode": True,
        "businessDetails": mal["businessDetails"],
        "termsNotes": mal["termsNotes"],
        "discount": mal["discount"],
        "contactDetails": {
            "id": k["id"],
            "name": (k.get("contactName") or f"{k.get('firstNameRaw','')} {k.get('lastNameRaw','')}").strip(),
            "companyName": firma,
            "email": k.get("email"), "phoneNo": k.get("phone") or "",
            "address": adresse,
        },
        "issueDate": utstedt, "dueDate": forfall,
        "items": [{"name": tekst, "description": f"Org.nr {orgnr}" if orgnr else "",
                   "currency": valuta,
                   "amount": belop, "qty": 1, "taxes": [], "taxInclusive": False}],
    }
    inv = http("/invoices/", "POST", body)
    iid = inv.get("_id")
    print(f"DRAFT created: {inv.get('invoiceNumber') or iid} — {belop:,.0f} {valuta} to "
          f"{body['contactDetails']['name']} <{epost}>, due {forfall}")
    print(f"id: {iid}")
    print(f"link: {LENKE.format(iid)}")
    return iid


KOPI = env.get("INVOICE_CC_EMAIL", "")   # the bookkeeper is always on copy
# Send from an address a human actually reads: replies to an unread ar@ inbox get lost.
AVSENDER = {"fromName": env.get("INVOICE_FROM_NAME", ""), "fromEmail": env.get("INVOICE_FROM_EMAIL", "")}
LENKE = "https://link.msgsndr.com/invoice/{}"   # GHL's public invoice page


def send(iid=None):
    iid = iid or arg("--id")
    if not iid:
        raise SystemExit("send requires --id <invoiceId>")
    if not AVSENDER["fromEmail"]:
        raise SystemExit("Set INVOICE_FROM_EMAIL (and INVOICE_FROM_NAME) in .env before sending.")
    inv = http(f"/invoices/{iid}?altId={LOC}&altType=location")
    c = inv.get("contactDetails") or {}
    kopi = [e for e in [arg("--kopi", KOPI)] if e]
    # GHL answers 422 on sms_and_email when the contact has no phone
    action = "sms_and_email" if c.get("phoneNo") else "email"
    body = {"altId": LOC, "altType": "location", "action": action,
            "liveMode": True, "autoPayment": {"enable": False},
            "sentFrom": AVSENDER,
            "sentTo": {"email": [c.get("email")] if c.get("email") else [],
                       "emailCc": kopi, "emailBcc": [],
                       "phoneNo": [c.get("phoneNo")] if c.get("phoneNo") else []}}
    r = http(f"/invoices/{iid}/send", "POST", body)
    print(f"SENT: {r.get('invoiceNumber') or iid} (status {r.get('status')}) "
          f"to {c.get('email')}, cc {', '.join(kopi) or '-'}")
    print(f"Link (for WhatsApp/SMS if they say it never arrived): {LENKE.format(iid)}")


# ---------------- mal + sjekk ----------------
def marker_betalt():
    """Record a payment on an invoice — only after a human has said yes.

    NB: GHL emails the customer a receipt when you do this. Switch receipts off
    (Settings > Payments > Receipts) before any batch of old payments.

    faktura.py marker-betalt --id <invoiceId> --belop 8750 --dato 2025-12-15 \
        --notat "Wise transfer, reference names the invoice"
    """
    iid = arg("--id")
    if not iid:
        raise SystemExit("marker-betalt requires --id <invoiceId>")
    belop = arg("--belop")
    body = {"altId": LOC, "altType": "location", "mode": "bank_transfer",
            "notes": arg("--notat", "Reconciled against bank/Stripe by Luca"),
            "paymentScheduleIds": []}
    if belop:
        body["amount"] = float(belop)
    if arg("--dato"):
        body["paymentDate"] = arg("--dato")
    r = http(f"/invoices/{iid}/record-payment", "POST", body)
    print(f"MARKED PAID: {r.get('invoiceNumber') or iid} (status {r.get('status')})")


def logo_lever(url):
    """True if the logo URL actually loads for a customer opening the invoice.

    GHL stores some logos on msgsndr-private, and those objects go 404 — the
    customer then sees a broken image where the logo should be.
    """
    if not url:
        return False
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "curl/8.7.1"}, method="HEAD")
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status == 200
    except Exception:
        return False


def krediter():
    """Void an invoice — GHL's credit note. IRREVERSIBLE. Needs a human yes.

    faktura.py krediter --id <invoiceId> --grunn "billed the whole package as one invoice"
    """
    iid = arg("--id")
    if not iid:
        raise SystemExit("krediter requires --id <invoiceId>")
    inv = http(f"/invoices/{iid}?altId={LOC}&altType=location")
    if (inv.get("amountPaid") or 0) > 0:
        raise SystemExit(f"#{inv.get('invoiceNumber')} has {inv['amountPaid']} paid on it — "
                         "voiding would erase real money. The bookkeeper decides, stopping here.")
    print(f"Voiding #{inv.get('invoiceNumber')} — {inv.get('total')} {inv.get('currency')} "
          f"to {(inv.get('contactDetails') or {}).get('name')}")
    r = http(f"/invoices/{iid}/void", "POST", {"altId": LOC, "altType": "location"})
    print(f"VOIDED: #{r.get('invoiceNumber') or iid} (status {r.get('status')}) "
          f"— reason: {arg('--grunn', 'not given')}")


def mal():
    betalte = [i for i in hent_alle() if i.get("status") == "paid" and i.get("termsNotes")]
    betalte.sort(key=lambda i: dag(i.get("issueDate")))
    # Newest paid invoice whose logo still loads — never copy a dead logo forward.
    i = next((x for x in reversed(betalte)
              if logo_lever((x.get("businessDetails") or {}).get("logoUrl"))), None)
    if i is None:
        raise SystemExit("No paid invoice with a working logo URL — fix the logo in GHL first.")
    # Check that the terms text carries your org number and bank details before you rely on it.
    d = {"businessDetails": i["businessDetails"],
         "termsNotes": i["termsNotes"],
         "discount": {"type": "percentage", "value": 0},
         "_kilde": f"Copied from invoice #{i.get('invoiceNumber')} ({dag(i.get('issueDate'))})"}
    open(os.path.join(FAK, "mal.json"), "w").write(json.dumps(d, indent=2, ensure_ascii=False))
    print(f"Template refreshed from invoice #{i.get('invoiceNumber')}")


def sjekk():
    q = urllib.parse.urlencode({"altId": LOC, "altType": "location", "limit": 1, "offset": 0})
    d = http("/invoices/?" + q)
    print(f"read  invoices : OK ({d.get('total')} invoices in the subaccount)")
    try:
        http("/invoices/", "POST", {"altId": LOC, "altType": "location"})
    except SystemExit as e:
        s = str(e)
        if "HTTP 422" in s:
            print("write invoices : OK (validation reached — scope present, nothing created)")
        else:
            print("write invoices : MISSING/BLOCKED ->\n" + s)
    print(f"template       : {'OK' if os.path.exists(os.path.join(FAK, 'mal.json')) else 'MISSING - run: faktura.py mal'}")


def arg(navn, standard=None):
    if navn in sys.argv:
        i = sys.argv.index(navn)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return standard


if __name__ == "__main__":
    kmd = sys.argv[1] if len(sys.argv) > 1 else "oversikt"
    {"oversikt": oversikt, "purreliste": purreliste, "ny": ny, "send": send,
     "marker-betalt": marker_betalt, "krediter": krediter, "mal": mal, "sjekk": sjekk}.get(kmd, lambda: sys.exit(__doc__))()
