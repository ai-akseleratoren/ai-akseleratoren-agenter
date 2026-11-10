#!/usr/bin/env python3
"""Luca's Stripe dunning + winback list.

Usage:
  python3 scripts/stripe_purring.py            # writes faktura/stripe-purring-<date>.md
  python3 scripts/stripe_purring.py --dager 45 # look-back window (default 30)
  python3 scripts/stripe_purring.py demo       # self-check, no network

Env (.env or environment): STRIPE_API_KEY (a restricted read-only key is enough),
REBUY_URL (your checkout page for winbacks), SIGNATUR (name under the drafts).

Three piles:
  A. past due  — subscription still open, Stripe retrying. Reminder ladder by days since first failure.
  B. winback   — subscription Stripe already cancelled for failed payment. Re-buy link.
  C. one-offs  — single purchase failed, never succeeded afterwards. Invoice offer.
Message drafts are for a human to send — Luca never emails a customer.
"""
import base64, datetime, json, os, sys, time, urllib.parse, urllib.request
from collections import defaultdict

HER = os.path.dirname(os.path.abspath(__file__))
ROT = os.path.dirname(HER)
FAK = os.environ.get("FAKTURA_DIR", os.path.join(os.getcwd(), "faktura"))
NOW = int(time.time())


def env():
    d = dict(os.environ)
    for p in (os.path.join(os.getcwd(), ".env"), os.path.join(ROT, ".env")):
        if os.path.exists(p):
            for l in open(p):
                if "=" in l and not l.startswith("#"):
                    k, v = l.strip().split("=", 1); d.setdefault(k, v)
    return d


CHECKOUT = env().get("REBUY_URL", "<DIN-KJOPSSIDE>")
SIGN = env().get("SIGNATUR", "")


def stripe(path, **q):
    key = env()["STRIPE_API_KEY"]
    h = {"Authorization": "Basic " + base64.b64encode((key + ":").encode()).decode()}
    out, q["limit"] = [], 100
    while True:
        r = json.load(urllib.request.urlopen(urllib.request.Request(
            "https://api.stripe.com/v1/" + path + "?" + urllib.parse.urlencode(q, doseq=True), headers=h), timeout=60))
        out += r["data"]
        if not r.get("has_more"):
            return out
        q["starting_after"] = out[-1]["id"]


def dt(t):
    return datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%d.%m") if t else "-"


def money(a, c):
    return f"{a / 100:,.0f} {c.upper()}".replace(",", " ")


def email_of(o):
    c = o.get("customer")
    if isinstance(c, dict):
        return (c.get("email") or "").lower()
    return (o.get("customer_email") or o.get("billing_details", {}).get("email") or o.get("receipt_email") or "").lower()


def sprak(email, currency):
    """Swedish for .se addresses or SEK, Norwegian otherwise."""
    return "se" if email.endswith(".se") or currency.lower() == "sek" else "no"


def steg(dager):
    """Reminder ladder from the contract: friendly ≤7 days, factual ≤21, then a call."""
    return "friendly" if dager <= 7 else "factual" if dager <= 21 else "call"


def melding(pile, lang, navn, belop, lenke):
    fornavn = (navn or "").split()[0] if navn else ""
    hei = f"Hej {fornavn}!" if lang == "se" else f"Hei {fornavn}!"
    if pile == "A":
        if lang == "se":
            return f"{hei}\n\nBetalningen på {belop} för medlemskapet gick inte igenom (kortet avvisades). Du kan betala direkt här, med samma eller ett nytt kort: {lenke}\n\nHör av dig om något är oklart.\n\n{SIGN}"
        return f"{hei}\n\nBetalingen på {belop} for medlemskapet gikk ikke gjennom (kortet ble avvist). Du kan betale direkte her, med samme eller nytt kort: {lenke}\n\nSi fra om noe er uklart.\n\n{SIGN}"
    if pile == "B":
        if lang == "se":
            return f"{hei}\n\nDitt medlemskap avslutades eftersom kortbetalningen misslyckades flera gånger. Vill du vara med igen? Du är välkommen tillbaka här: {lenke}\n\n{SIGN}"
        return f"{hei}\n\nMedlemskapet ditt ble avsluttet fordi kortbetalingen feilet flere ganger. Vil du være med videre? Du er velkommen tilbake her: {lenke}\n\n{SIGN}"
    if lang == "se":
        return f"{hei}\n\nJag ser att kortbetalningen på {belop} inte gick igenom. Vill du hellre ha en faktura? Svara bara på det här mejlet så skickar vi den.\n\n{SIGN}"
    return f"{hei}\n\nJeg ser at kortbetalingen på {belop} ikke gikk gjennom. Vil du heller ha faktura? Bare svar på denne mailen, så sender vi den.\n\n{SIGN}"


def hent(dager):
    siden = NOW - dager * 86400
    A, B, C = [], [], []
    for st in ("past_due", "unpaid"):
        for s in stripe("subscriptions", status=st, **{"expand[]": ["data.customer", "data.latest_invoice"]}):
            p = s["items"]["data"][0]["price"]; inv = s.get("latest_invoice") or {}
            first_fail = (inv.get("status_transitions") or {}).get("finalized_at") or inv.get("created") or s.get("current_period_start")
            A.append(dict(email=email_of(s), navn=(s["customer"].get("name") if isinstance(s.get("customer"), dict) else "") or "",
                          belop=money(p["unit_amount"] or 0, p["currency"]), valuta=p["currency"], intervall=p["recurring"]["interval"],
                          forsok=inv.get("attempt_count", 0), neste=dt(inv.get("next_payment_attempt")),
                          dager=(NOW - first_fail) // 86400, lenke=inv.get("hosted_invoice_url") or ""))
    for s in stripe("subscriptions", status="canceled", **{"expand[]": ["data.customer"]}):
        if (s.get("canceled_at") or 0) >= siden and (s.get("cancellation_details") or {}).get("reason") == "payment_failed":
            p = s["items"]["data"][0]["price"]
            B.append(dict(email=email_of(s), navn=(s["customer"].get("name") if isinstance(s.get("customer"), dict) else "") or "",
                          belop=money(p["unit_amount"] or 0, p["currency"]), valuta=p["currency"], intervall=p["recurring"]["interval"],
                          dato=dt(s["canceled_at"])))
    failed, ok = defaultdict(list), defaultdict(list)
    for c in stripe("charges", **{"created[gte]": siden}):
        # key on the Stripe customer, not the email: the same person's retries can carry
        # different billing emails (seen: paid 3 minutes after three failures on another address)
        k = c.get("customer") or email_of(c)
        if not k:
            continue
        (failed if c["status"] == "failed" else ok)[k].append(c) if c["status"] in ("failed", "succeeded") else None
    a_emails = {x["email"] for x in A} | {x["email"] for x in B}
    for k, cs in failed.items():
        e = email_of(max(cs, key=lambda c: c["created"]))
        if e in a_emails or any(o["created"] >= min(c["created"] for c in cs) for o in ok.get(k, [])):
            continue
        if all(c.get("invoice") for c in cs):      # subscription invoices are pile A/B, not one-offs
            continue
        last = max(cs, key=lambda c: c["created"])
        C.append(dict(email=e, navn=(last.get("billing_details") or {}).get("name") or "", belop=money(last["amount"], last["currency"]),
                      valuta=last["currency"], forsok=len(cs), sist=dt(last["created"]), grunn=(last.get("failure_message") or "")[:60]))
    return A, B, C


def skriv(A, B, C, dager):
    dato = datetime.date.today().isoformat()
    ut = [f"# Stripe dunning + winback — {dato} (last {dager} days)\n",
          "Source: Stripe API. Drafts below are for a human to send; Luca sends nothing.\n"]
    ut.append(f"## A. Past due — still open, Stripe retrying ({len(A)})\n")
    ut.append("| Email | Name | Amount | Failures | Next retry | Days | Step |\n|---|---|---|---|---|---|---|")
    for x in sorted(A, key=lambda x: -x["dager"]):
        ut.append(f"| {x['email']} | {x['navn']} | {x['belop']}/{x['intervall']} | {x['forsok']} | {x['neste']} | {x['dager']} | {steg(x['dager'])} |")
    ut.append(f"\n## B. Winback — cancelled by Stripe for failed payment ({len(B)})\n")
    ut.append("| Date | Email | Name | Was paying |\n|---|---|---|---|")
    for x in B:
        ut.append(f"| {x['dato']} | {x['email']} | {x['navn']} | {x['belop']}/{x['intervall']} |")
    ut.append(f"\n## C. One-off purchases failed, never completed ({len(C)})\n")
    ut.append("| Email | Name | Amount | Tries | Last | Reason |\n|---|---|---|---|---|---|")
    for x in C:
        ut.append(f"| {x['email']} | {x['navn']} | {x['belop']} | {x['forsok']} | {x['sist']} | {x['grunn']} |")
    ut.append("\n## Drafts\n")
    for pile, liste in (("A", A), ("B", B), ("C", C)):
        for x in liste:
            lang = sprak(x["email"], x["valuta"])
            lenke = x.get("lenke") or CHECKOUT
            ut.append(f"### {pile} · {x['email']} · {lang.upper()}\n```\n{melding(pile, lang, x['navn'], x['belop'], lenke)}\n```\n")
    os.makedirs(FAK, exist_ok=True)
    p = os.path.join(FAK, f"stripe-purring-{dato}.md")
    open(p, "w").write("\n".join(ut))
    return p


def demo():
    assert sprak("a@b.se", "eur") == "se" and sprak("a@b.no", "sek") == "se" and sprak("a@b.no", "eur") == "no"
    assert steg(3) == "friendly" and steg(7) == "friendly" and steg(8) == "factual" and steg(22) == "call"
    assert "Hei Kari!" in melding("A", "no", "Kari Nordmann", "99 EUR", "https://x") and "https://x" in melding("A", "no", "Kari", "99 EUR", "https://x")
    assert "Hej Anna!" in melding("B", "se", "Anna", "99 EUR", CHECKOUT)
    assert money(199000, "nok") == "1 990 NOK"
    print("demo ok")


if __name__ == "__main__":
    if "demo" in sys.argv:
        demo(); sys.exit()
    dager = int(sys.argv[sys.argv.index("--dager") + 1]) if "--dager" in sys.argv else 30
    A, B, C = hent(dager)
    p = skriv(A, B, C, dager)
    print(f"A past due: {len(A)} | B winback: {len(B)} | C one-offs: {len(C)}")
    print(f"written: {p}")
