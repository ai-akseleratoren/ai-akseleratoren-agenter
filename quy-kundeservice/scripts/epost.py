#!/usr/bin/env python3
"""E-postkanalen: IMAP + SMTP med app-passord. Kun stdlib.

  python3 scripts/epost.py doktor              er koblingen frisk?
  python3 scripts/epost.py sveip [--dager 7]   ubesvarte i innboksen
  python3 scripts/epost.py les <uid>           hele meldingen
  python3 scripts/epost.py utkast <uid> <fil>  legg svar i Utkast-mappa (du sender selv)
  python3 scripts/epost.py svar <uid> <fil>    send svaret nå (kun etter eksplisitt ja)

«Ubesvart» = i innboksen, nyere enn N dager, og ingenting sendt til avsender
etter at meldingen kom. Lest/ulest er likegyldig.

Skriptet klassifiserer ingenting og skriver ingen tekst — det gjør agenten
i Claude Code ut fra kunnskap/. Skriptet er bare hendene.
"""
import email, email.message, email.utils, imaplib, smtplib, sys
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText

sys.path.insert(0, __import__("os").path.dirname(__file__))
from felles import env, logg

E = env()
HODER = "FROM TO SUBJECT DATE MESSAGE-ID IN-REPLY-TO REFERENCES"


class Boks:
    def __init__(self):
        self.bruker = E.get("EPOST_USER") or sys.exit("EPOST_USER mangler i .env")
        passord = (E.get("EPOST_APP_PASSWORD") or "").replace(" ", "")
        if not passord:
            sys.exit("EPOST_APP_PASSWORD mangler i .env — se README.md (Kom i gang)")
        try:
            self.M = imaplib.IMAP4_SSL(E.get("EPOST_IMAP", "imap.gmail.com"))
            self.M.login(self.bruker, passord)
        except imaplib.IMAP4.error as e:
            sys.exit("IMAP-innlogging feilet: %s\nVanligste årsak: 2-trinns ikke på, "
                     "app-passord feil, eller IMAP skrudd av i innstillingene." % e)
        self.utkast_mappe = E.get("EPOST_UTKAST_MAPPE", "[Gmail]/Drafts")
        self.sendt_mappe = E.get("EPOST_SENDT_MAPPE", "[Gmail]/Sent Mail")
        self.M.select('"INBOX"', readonly=True)

    def _sok(self, *krit):
        _, d = self.M.uid("search", None, *krit)
        return [u.decode() for u in d[0].split()]

    def innboks(self, dager):
        siden = (datetime.now(timezone.utc) - timedelta(days=dager)).strftime("%d-%b-%Y")
        return self._sok('SINCE "%s"' % siden)

    def hoder(self, uid):
        _, d = self.M.uid("fetch", uid, "(BODY.PEEK[HEADER.FIELDS (%s)])" % HODER)
        return email.message_from_bytes(d[0][1]) if d and d[0] else email.message.Message()

    def tekst(self, uid):
        _, d = self.M.uid("fetch", uid, "(BODY.PEEK[])")
        m = email.message_from_bytes(d[0][1])
        for part in m.walk():
            if part.get_content_type() == "text/plain":
                return part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8", "replace")
        for part in m.walk():
            if part.get_content_type() == "text/html":
                import re, html
                h = part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8", "replace")
                return html.unescape(re.sub(r"<[^>]+>", " ", h))
        return "(ingen tekst i meldingen)"

    def svart_etter(self, adresse, dt):
        self.M.select('"%s"' % self.sendt_mappe, readonly=True)
        try:
            return bool(self._sok('TO "%s"' % adresse, 'SINCE "%s"' % dt.strftime("%d-%b-%Y")))
        finally:
            self.M.select('"INBOX"', readonly=True)

    def _svarmelding(self, uid, brodtekst):
        h = self.hoder(uid)
        m = MIMEText(brodtekst, "plain", "utf-8")
        m["From"] = self.bruker
        m["To"] = h.get("Reply-To") or h.get("From")
        emne = h.get("Subject", "")
        m["Subject"] = emne if emne.lower().startswith("re:") else "Re: " + emne
        if h.get("Message-ID"):
            m["In-Reply-To"] = h["Message-ID"]
            m["References"] = ((h.get("References") or "") + " " + h["Message-ID"]).strip()
        m["Date"] = email.utils.formatdate(localtime=True)
        return m

    def utkast(self, uid, brodtekst):
        m = self._svarmelding(uid, brodtekst)
        self.M.append('"%s"' % self.utkast_mappe, "(\\Draft)", imaplib.Time2Internaldate(datetime.now().timestamp()), m.as_bytes())
        return m["To"], m["Subject"]

    def send(self, uid, brodtekst):
        m = self._svarmelding(uid, brodtekst)
        with smtplib.SMTP_SSL(E.get("EPOST_SMTP", "smtp.gmail.com"), 465) as s:
            s.login(self.bruker, E["EPOST_APP_PASSWORD"].replace(" ", ""))
            s.sendmail(self.bruker, [email.utils.parseaddr(m["To"])[1]], m.as_bytes())
        if "gmail" not in E.get("EPOST_SMTP", "smtp.gmail.com"):  # Gmail legger i Sendt selv
            self.M.append('"%s"' % self.sendt_mappe, "(\\Seen)", imaplib.Time2Internaldate(datetime.now().timestamp()), m.as_bytes())
        return m["To"], m["Subject"]

    def ferdig(self):
        try: self.M.logout()
        except Exception: pass


def doktor():
    b = Boks()
    print("OK — koblet som", b.bruker)
    print("Meldinger siste 7 dager:", len(b.innboks(7)))
    for mappe in (b.utkast_mappe, b.sendt_mappe):
        rc, _ = b.M.select('"%s"' % mappe, readonly=True)
        print("Mappe %-22s %s" % (mappe, "OK" if rc == "OK" else "FINNES IKKE — rett EPOST_*_MAPPE i .env"))
    b.ferdig()


def sveip(dager=7):
    b = Boks()
    n = 0
    for uid in b.innboks(dager):
        h = b.hoder(uid)
        fra = email.utils.parseaddr(h.get("From", ""))[1]
        dt = email.utils.parsedate_to_datetime(h["Date"]) if h.get("Date") else None
        if fra.lower() == b.bruker.lower():
            continue
        if fra and dt and b.svart_etter(fra, dt):
            continue
        n += 1
        print("=" * 60)
        print("uid:", uid)
        print("fra:", h.get("From", "?"))
        print("emne:", h.get("Subject", "(uten emne)"))
        print("dato:", h.get("Date", "?"))
        print("-" * 60)
        print(b.tekst(uid)[:1500])
    print("=" * 60)
    print("Ubesvarte:", n)
    b.ferdig()


def les(uid):
    b = Boks()
    h = b.hoder(uid)
    for felt in ("From", "To", "Subject", "Date"):
        print(felt + ":", h.get(felt, ""))
    print("-" * 60)
    print(b.tekst(uid))
    b.ferdig()


def utkast(uid, fil):
    b = Boks()
    til, emne = b.utkast(uid, open(fil, encoding="utf-8").read())
    logg({"kanal": "epost", "hendelse": "utkast", "uid": uid, "til": til, "emne": emne})
    print("Utkast lagt i %s: %s — %s" % (b.utkast_mappe, til, emne))
    b.ferdig()


def svar(uid, fil):
    b = Boks()
    til, emne = b.send(uid, open(fil, encoding="utf-8").read())
    logg({"kanal": "epost", "hendelse": "sendt", "uid": uid, "til": til, "emne": emne})
    print("Sendt: %s — %s" % (til, emne))
    b.ferdig()


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: sys.exit(__doc__)
    k = a[0]
    if k == "doktor": doktor()
    elif k == "sveip": sveip(int(a[a.index("--dager") + 1]) if "--dager" in a else 7)
    elif k == "les": les(a[1])
    elif k == "utkast": utkast(a[1], a[2])
    elif k == "svar": svar(a[1], a[2])
    else: sys.exit(__doc__)
