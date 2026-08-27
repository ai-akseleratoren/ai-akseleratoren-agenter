#!/usr/bin/env python3
"""Zoom-webinar-agent: finn «ja»-leads i chat/Q&A og lag ringeliste.

Bruk:
  python3 zoom_leads.py meetings [--days 30]
  python3 zoom_leads.py harvest <meetingId> [--dry-run]
  python3 zoom_leads.py selftest

harvest gjør hele flyten: deltakere + chat + Q&A fra Zoom → «ja»-signaler →
CRM-kontaktmatch (e-post først, så navn) → opportunities til målsteget →
ringeliste i ringelister/ (+ varsel hvis SLACK_WEBHOOK_URL er satt).

Nøkler leses fra .env i mappa du kjører fra (se .env.example). Sjekk ALDRI
.env inn i git.

Skrevet mot GoHighLevel-API-et. Bruker du et annet CRM, er det bare
funksjonene under «CRM»-overskriften som må skrives om.
"""
import json, os, re, sys, base64, unicodedata, urllib.request, urllib.parse
from datetime import datetime, timedelta, timezone

ROOT = os.getcwd()
env = {}
_envfile = os.path.join(ROOT, ".env")
if not os.path.exists(_envfile):
    _envfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(_envfile):
    with open(_envfile) as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()

ZOOM_USER = env.get("ZOOM_USER_EMAIL", "")
PIPELINE_NAME = env.get("CRM_PIPELINE_NAME", "Sales Pipeline")
TARGET_STAGE = env.get("CRM_TARGET_STAGE", "Engaged")
OUTDIR = os.path.join(ROOT, env.get("OUTPUT_DIR", "ringelister"))
BOT_WORDS = ("fireflies", "notetaker", "otter.ai", "read.ai", "fathom")

# ---------- Zoom ----------

def zoom_token():
    basic = base64.b64encode(
        f"{env['ZOOM_CLIENT_ID']}:{env['ZOOM_CLIENT_SECRET']}".encode()).decode()
    req = urllib.request.Request(
        "https://zoom.us/oauth/token?grant_type=account_credentials&account_id="
        + env["ZOOM_ACCOUNT_ID"], method="POST",
        headers={"Authorization": "Basic " + basic})
    return json.load(urllib.request.urlopen(req, timeout=30))["access_token"]

def zget(tok, path, raw=False):
    url = path if path.startswith("http") else "https://api.zoom.us/v2" + path
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + tok})
    r = urllib.request.urlopen(req, timeout=60)
    return r.read().decode("utf-8", "replace") if raw else json.load(r)

def ztry(tok, path, raw=False):
    try:
        return zget(tok, path, raw)
    except urllib.error.HTTPError:
        return None

def list_meetings(tok, days):
    to = datetime.now(timezone.utc).date()
    frm = to - timedelta(days=days)
    mts, page = [], ""
    while True:
        d = zget(tok, f"/report/users/{ZOOM_USER}/meetings?from={frm}&to={to}"
                      f"&page_size=30&next_page_token={page}")
        mts += d.get("meetings", [])
        page = d.get("next_page_token", "")
        if not page:
            break
    return sorted(mts, key=lambda m: m["start_time"], reverse=True)

def get_participants(tok, mid):
    """Prøv møte-rapporten, så webinar-rapporten. Returnerer (liste, kilde)."""
    for kind in ("meetings", "webinars"):
        rows, page = [], ""
        d = ztry(tok, f"/report/{kind}/{mid}/participants?page_size=300&next_page_token={page}")
        if d is None:
            continue
        while True:
            rows += d.get("participants", [])
            page = d.get("next_page_token", "")
            if not page:
                break
            d = zget(tok, f"/report/{kind}/{mid}/participants?page_size=300&next_page_token={page}")
        # slå sammen gjeninntredener på navn
        seen = {}
        for p in rows:
            key = (p.get("name") or "").strip().lower()
            if key and key not in seen:
                seen[key] = {"name": (p.get("name") or "").strip(),
                             "email": (p.get("user_email") or "").strip().lower(),
                             "join_time": p.get("join_time", "")}
            elif key and p.get("user_email") and not seen[key]["email"]:
                seen[key]["email"] = p["user_email"].strip().lower()
        return list(seen.values()), kind
    return [], None

def get_chat_text(tok, mid, start_time):
    """CHAT-filen fra cloud recording. Direkte per møte først, så via brukerlisten
    (per-møte-opptak krever et scope mange apper ikke har)."""
    rec = ztry(tok, f"/meetings/{mid}/recordings")
    if rec is None:
        day = datetime.fromisoformat(start_time.replace("Z", "+00:00")).date()
        d = ztry(tok, f"/users/{ZOOM_USER}/recordings?from={day - timedelta(days=1)}"
                      f"&to={day + timedelta(days=1)}&page_size=30")
        for m in (d or {}).get("meetings", []):
            if str(m.get("id")) == str(mid):
                rec = m
                break
    if not rec:
        return None, None
    topic = rec.get("topic")
    chat = [f for f in rec.get("recording_files", []) if f.get("file_type") == "CHAT"]
    if not chat:
        return None, topic
    return zget(tok, chat[0]["download_url"] + "?access_token=" + tok, raw=True), topic

def parse_chat(text):
    """Zoom-format: 'HH:MM:SS\\tNavn:\\tmelding' — fortsettelseslinjer mangler tid."""
    msgs = []
    for line in (text or "").splitlines():
        m = re.match(r"^(\d{2}:\d{2}:\d{2})\t(.+?):\t(.*)$", line)
        if m:
            msgs.append({"time": m.group(1), "name": m.group(2).strip(), "text": m.group(3)})
        elif msgs and line.strip():
            msgs[-1]["text"] += " " + line.strip()
    return msgs

def get_qa(tok, mid):
    out = []
    d = ztry(tok, f"/past_meetings/{mid}/qa") or ztry(tok, f"/report/webinars/{mid}/qa") or {}
    for q in d.get("questions", []):
        name = (q.get("name") or "").strip()
        for item in q.get("question_details", []) or [{"question": q.get("question", "")}]:
            txt = item.get("question") or ""
            if name and txt:
                out.append({"time": "Q&A", "name": name, "text": txt})
    return out

# ---------- «ja»-signaler ----------

AFFIRM = {"ja", "yes", "jepp", "jess", "japp", "jo", "gjerne", "absolutt",
          "ja takk", "yes takk", "ja gjerne", "gjerne det", "ja det vil jeg",
          "yes please"}
# Interesse-signaler er like viktige som rene «ja» — uten dem glipper de fleste
# leads, fordi folk sjelden svarer «ja» på et spørsmål ingen stilte dem.
STRONG = ("ring meg", "ta en samtale", "en prat", "kontakt meg", "keen",
          "vil gjerne snakke", "book en", "ta kontakt", "slå på tråden",
          "vil ta en samtale", "snakke med deg",
          "interessert", "intresserad", "interesserad", "interested",
          "vil gjerne vite mer", "vill veta mer", "mer info", "bokning",
          "hvordan booker", "hur bokar")

def clean(txt):
    t = "".join(c for c in txt if unicodedata.category(c)[0] != "S")  # emoji vekk
    return re.sub(r"[^\wæøåäöü ]", "", t.lower(), flags=re.UNICODE).strip()

def is_signal(txt):
    c = clean(txt)
    if c in AFFIRM or c.split() and c.split()[0] in ("ja", "yes", "jepp") and len(c.split()) <= 4:
        return "ja"
    if any(p in c for p in STRONG):
        return "sterk"
    return None

def is_bot_or_host(name, email):
    n = name.lower()
    return any(b in n for b in BOT_WORDS) or (ZOOM_USER and email == ZOOM_USER.lower())

# ---------- CRM (GoHighLevel) ----------

CRM = "https://services.leadconnectorhq.com"

def crm(path, method="GET", body=None):
    # GHL blokkerer Python sin standard User-Agent — vi sender curl-UA.
    req = urllib.request.Request(CRM + path, method=method,
        data=json.dumps(body).encode() if body else None,
        headers={"Authorization": "Bearer " + env["CRM_API_TOKEN"],
                 "Version": "2021-07-28", "Accept": "application/json",
                 "Content-Type": "application/json", "User-Agent": "curl/8.4.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

DEVICE_WORDS = {"tlf", "mobil", "phone", "iphone", "ipad", "mac", "pc", "jobb", "work"}

def norm_tokens(name):
    n = re.sub(r"['’´`]n?\b", "", name.lower())  # «Geir'n» → «geir»
    return [t for t in re.sub(r"[^\wæøåäöü ]", "", n).split()
            if t and t not in DEVICE_WORDS]

def _recent(c, days=14):
    try:
        dt = datetime.fromisoformat((c.get("dateAdded") or "").replace("Z", "+00:00"))
    except ValueError:
        return False
    return (datetime.now(timezone.utc) - dt).days <= days

def _narrow(cands, toks):
    """Tiebreak: initialer i e-posten (thomas berggren → tbe...@), så fersk påmelding."""
    if len(toks) >= 2:
        f, l = toks[0][0], toks[-1]
        pref = {f + l[0], f + l[:2], f + l[:3]}
        hit = [c for c in cands
               if any(((c.get("email") or "").split("@")[0].lower()).startswith(x) for x in pref)]
        if len(hit) == 1:
            return hit[0]
    recent = [c for c in cands if _recent(c)]
    if len(recent) == 1:
        return recent[0]
    return None

def find_contact(name, email):
    """Returnerer (kontakt, status): 'match', 'ambiguous' (liste), 'none'."""
    loc = env["CRM_LOCATION_ID"]
    if email:
        d = crm(f"/contacts/?locationId={loc}&query={urllib.parse.quote(email)}&limit=5")
        hits = [c for c in d.get("contacts", [])
                if (c.get("email") or "").lower() == email]
        if len(hits) == 1:
            return hits[0], "match"
    toks = norm_tokens(name)
    if not toks or len(toks[0]) < 3:  # «B» o.l. — håpløst å søke på
        return None, "none"
    d = crm(f"/contacts/?locationId={loc}&query={urllib.parse.quote(toks[0])}&limit=20")
    pool = d.get("contacts", [])
    def cands_where(pred):
        out = []
        for c in pool:
            ctoks = norm_tokens(" ".join(filter(None, [c.get("firstName"), c.get("lastName"),
                                                       c.get("contactName")])))
            if pred(ctoks) and c.get("id") not in [x.get("id") for x in out]:
                out.append(c)
        return out
    # strengt: alle chat-navn-tokens prefikser et kontakt-token («Kristian G» → kristian g*)
    cands = cands_where(lambda ct: all(any(x.startswith(t) for x in ct) for t in toks))
    if len(cands) == 1:
        return cands[0], "match"
    if cands:
        n = _narrow(cands, toks)
        if n: return n, "match"
        return cands, "ambiguous"
    # fallback: bare fornavnet — tiebreak før vi gir opp og lister kandidater
    cands = cands_where(lambda ct: bool(ct) and ct[0] == toks[0])
    if len(cands) == 1:
        return cands[0], "match"
    if cands:
        n = _narrow(cands, toks)
        if n: return n, "match"
    if 1 < len(cands) <= 6:
        return cands, "ambiguous"
    return None, "none"

def stage_map():
    pipes = crm(f"/opportunities/pipelines?locationId={env['CRM_LOCATION_ID']}")
    for p in pipes["pipelines"]:
        if p["name"] == PIPELINE_NAME:
            order = [s["name"] for s in p["stages"]]
            ids = {s["name"]: s["id"] for s in p["stages"]}
            return p["id"], order, ids
    raise SystemExit(f"Fant ikke pipelinen «{PIPELINE_NAME}» i CRM-et")

def upsert_opportunity(contact, dry):
    """Opprett i målsteget, eller flytt dit hvis kontakten står tidligere i løpet."""
    pid, order, ids = stage_map()
    tgt_idx = order.index(TARGET_STAGE)
    loc = env["CRM_LOCATION_ID"]
    d = crm(f"/opportunities/search?location_id={loc}&contact_id={contact['id']}")
    opps = [o for o in d.get("opportunities", []) if o.get("pipelineId") == pid]
    cname = (contact.get("contactName")
             or f"{contact.get('firstName','')} {contact.get('lastName','')}".strip())
    if not opps:
        if not dry:
            crm("/opportunities/", "POST", {
                "pipelineId": pid, "locationId": loc,
                "pipelineStageId": ids[TARGET_STAGE], "contactId": contact["id"],
                "name": cname, "status": "open"})
        return f"opprettet i {TARGET_STAGE}"
    o = opps[0]
    cur = next((n for n, i in ids.items() if i == o.get("pipelineStageId")), "?")
    if cur in order and order.index(cur) < tgt_idx:
        if not dry:
            crm(f"/opportunities/{o['id']}", "PUT", {
                "pipelineId": pid, "pipelineStageId": ids[TARGET_STAGE],
                "name": o.get("name") or cname, "status": o.get("status") or "open"})
        return f"flyttet {cur} → {TARGET_STAGE}"
    return f"står allerede i {cur} — urørt"

# ---------- varsling ----------

def notify(text):
    hook = env.get("SLACK_WEBHOOK_URL")
    if not hook:
        return False
    req = urllib.request.Request(hook, method="POST",
        data=json.dumps({"text": text}).encode(),
        headers={"Content-Type": "application/json"})
    urllib.request.urlopen(req, timeout=30)
    return True

# ---------- kommandoer ----------

def cmd_meetings(days):
    tok = zoom_token()
    print(f"Siste {days} dager ({ZOOM_USER}):")
    for m in list_meetings(tok, days):
        print(f'  {m["start_time"][:16]}  id={m["id"]}  '
              f'deltakere={m.get("participants_count","?"):>3}  {m["topic"][:55]}')

def cmd_harvest(mid, dry):
    tok = zoom_token()
    # /past_meetings/{id} krever et scope mange apper mangler — /qa er som regel dekket
    info = ztry(tok, f"/past_meetings/{mid}/qa") or {}
    participants, kind = get_participants(tok, mid)
    start = (info.get("start_time")
             or min((p.get("join_time", "") for p in participants if p.get("join_time")),
                    default=datetime.now(timezone.utc).isoformat()))
    chat_text, topic = get_chat_text(tok, mid, start)
    topic = topic or info.get("topic") or f"møte {mid}"
    print(f"Høster: {topic} ({start[:16]})" + (" [DRY-RUN]" if dry else ""))
    print(f"  {len(participants)} unike deltakere (kilde: {kind or 'ukjent'})")
    emails = {p["name"].strip().lower(): p["email"] for p in participants if p.get("email")}

    msgs = parse_chat(chat_text) + get_qa(tok, mid)
    print(f"  {len(msgs)} chat/Q&A-meldinger")

    # «Zoom-bruker» o.l. som skriver navnet sitt selv i chatten → bruk det navnet
    for g, real in stated_names(msgs).items():
        print(f"  «{g}» oppga navnet sitt i chatten → {real}")
        for m in msgs:
            if m["name"].strip() == g:
                m["name"] = real

    # signaler per person
    people = {}
    for m in msgs:
        email = emails.get(m["name"].strip().lower(), "")
        if is_bot_or_host(m["name"], email):
            continue
        sig = is_signal(m["text"])
        p = people.setdefault(m["name"], {"email": email, "signals": [], "context": []})
        if sig:
            p["signals"].append((m["time"], m["text"], sig))
        elif len(m["text"]) > 60:  # lang melding = nyttig kontekst til ringelisten
            p["context"].append(m["text"])
    leads = {n: p for n, p in people.items() if p["signals"]}
    print(f"  {len(leads)} med «ja»-signal: {', '.join(leads) or '—'}")

    matched, ambiguous, unmatched = [], [], []
    for name, p in leads.items():
        contact, status = find_contact(name, p["email"])
        row = {"chat_name": name, **p}
        if status == "match":
            row["contact"] = contact
            row["crm"] = upsert_opportunity(contact, dry)
            matched.append(row)
        elif status == "ambiguous":
            row["candidates"] = contact
            ambiguous.append(row)
        else:
            unmatched.append(row)

    os.makedirs(OUTDIR, exist_ok=True)
    path = os.path.join(OUTDIR, f"{start[:10]}-{mid}.md")
    L = [f"# Ringeliste — {topic}", f"*{start[:10]} · generert av zoom_leads.py*", ""]
    L.append("## Klare til å ringes")
    for r in matched:
        c = r["contact"]
        cname = c.get("contactName") or f"{c.get('firstName','')} {c.get('lastName','')}".strip()
        L += [f"### {cname}  ·  {c.get('phone') or 'mangler tlf'}",
              f"- E-post: {c.get('email') or '—'}",
              f"- CRM: {r['crm']}",
              "- Skrev:"]
        L += [f"  - `{t}` «{txt}»" for t, txt, _ in r["signals"]]
        L += [f"- Kontekst: {ctx}" for ctx in r["context"][:3]]
        L.append("")
    if ambiguous:
        L.append("## Tvetydige — velg riktig kontakt manuelt")
        for r in ambiguous:
            L.append(f"### «{r['chat_name']}» skrev: " +
                     "; ".join(f"«{txt}»" for _, txt, _ in r["signals"]))
            L += [f"- Kandidat: {c.get('firstName','')} {c.get('lastName') or ''} "
                  f"| {c.get('email')} | {c.get('phone')}" for c in r["candidates"]]
            L += [f"- Kontekst: {ctx}" for ctx in r["context"][:3]]
            L.append("")
    if unmatched:
        L.append("## Ikke funnet i CRM-et")
        for r in unmatched:
            L.append(f"- «{r['chat_name']}»: " +
                     "; ".join(f"«{txt}»" for _, txt, _ in r["signals"]))
        L.append("")
    with open(path, "w") as f:
        f.write("\n".join(L))

    summary = (f"Zoom-leads fra «{topic}» {start[:10]}: {len(matched)} klare, "
               f"{len(ambiguous)} tvetydige, {len(unmatched)} umatchet. "
               f"Liste: {os.path.relpath(path, ROOT)}")
    print("\n" + summary)
    for r in matched:
        c = r["contact"]
        print(f"  RING: {c.get('contactName') or c.get('firstName')} "
              f"{c.get('phone') or '(mangler tlf)'} — {r['crm']}")
    if notify(summary):
        print("Varsel sendt.")
    else:
        print("(Ingen SLACK_WEBHOOK_URL i .env — del ringelisten manuelt med selgeren.)")
    return path

GENERIC_NAMES = ("zoom", "user", "användare", "bruker", "gäst", "guest", "iphone",
                 "ipad", "android")

def stated_names(msgs):
    """{«Zoom-bruker»: «Ola Nordmann»} — folk som skriver navnet sitt i chatten."""
    stated = {}
    for m in msgs:
        n = m["name"].strip()
        if any(g in n.lower() for g in GENERIC_NAMES):
            t = m["text"].strip()
            if len(t) <= 32 and re.fullmatch(
                    r"[A-ZÆØÅÄÖÜ][\wæøåäöü]+(?: [A-ZÆØÅÄÖÜ][\wæøåäöü]+){1,2}", t):
                stated[n] = t
    return stated

def selftest():
    msgs = parse_chat("10:01:02\tOla Nordmann:\tJa takk!\n"
                      "og gjerne på torsdag\n"
                      "10:02:00\tZoom-bruker:\tKari Hansen\n")
    assert [m["name"] for m in msgs] == ["Ola Nordmann", "Zoom-bruker"], msgs
    assert msgs[0]["text"] == "Ja takk! og gjerne på torsdag", msgs[0]
    assert stated_names(msgs) == {"Zoom-bruker": "Kari Hansen"}
    assert is_signal("Ja!") == "ja"
    assert is_signal("ja takk 🙌") == "ja"
    assert is_signal("Jeg er veldig interessert i dette") == "sterk"
    assert is_signal("Ring meg gjerne") == "sterk"
    assert is_signal("Hvor mange deltakere er dere?") is None
    assert is_signal("Jeg tror ikke dette er noe for meg akkurat nå") is None
    assert norm_tokens("Geir'n tlf") == ["geir"]
    assert norm_tokens("Kristian G") == ["kristian", "g"]
    print("selftest OK")

if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "selftest":
        selftest()
    elif not args or args[0] == "meetings":
        days = int(args[args.index("--days") + 1]) if "--days" in args else 30
        cmd_meetings(days)
    elif args[0] == "harvest" and len(args) > 1:
        cmd_harvest(args[1], "--dry-run" in args)
    else:
        print(__doc__)
