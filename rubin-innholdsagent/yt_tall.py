#!/usr/bin/env python3
"""Rubins tallagent: leser YouTube-tallene for din egen kanal og sier hva neste video bør gjøre annerledes.

    python3 yt_tall.py login            # én gang: samtykke i nettleseren, velg kanalen din
    python3 yt_tall.py rapport          # siste 28 dager -> youtube-tall/<dato>.md + kort oppsummering
    python3 yt_tall.py rapport --dager 7
    python3 yt_tall.py                  # selvtest av kurvelesingen, uten nett

Kun lesetilgang (yt-analytics.readonly + youtube.readonly). Du trenger en OAuth-klient av typen
«Desktop app» i Google Cloud, med «YouTube Data API v3» og «YouTube Analytics API» slått på i samme prosjekt.
Legg dette i .env ved siden av skriptet (aldri i git):
    GOOGLE_OAUTH_CLIENT_ID=...
    GOOGLE_OAUTH_CLIENT_SECRET=...
Tokenet lagres i ~/.rubin/youtube-token.json. Tilgangen kan trekkes på myaccount.google.com/permissions.

Klikkraten på thumbnailen (visninger -> klikk) finnes IKKE i API-et (sjekket mot
developers.google.com/youtube/analytics/metrics i november 2026). Den må leses i YouTube Studio.
Rapporten sier det, i stedet for å late som.
"""
import base64, datetime, hashlib, http.server, json, os, pathlib, re, secrets, sys, threading, time
import urllib.error, urllib.parse, urllib.request, webbrowser

HER = pathlib.Path(__file__).resolve().parent
UT = HER / "youtube-tall"
ENV = pathlib.Path(os.environ.get("RUBIN_ENV") or HER / ".env")
TOKEN = pathlib.Path(os.environ.get("RUBIN_YT_TOKEN") or pathlib.Path.home() / ".rubin/youtube-token.json")
SCOPE = "https://www.googleapis.com/auth/yt-analytics.readonly https://www.googleapis.com/auth/youtube.readonly"
TOKEN_URL = "https://oauth2.googleapis.com/token"
_cache = {}


def klient():
    e = dict(os.environ)
    if ENV.exists():
        for linje in ENV.read_text().splitlines():
            if "=" in linje and not linje.lstrip().startswith("#"):
                k, v = linje.split("=", 1); e.setdefault(k.strip(), v.strip().strip("'\""))
    cid, sec = e.get("GOOGLE_OAUTH_CLIENT_ID"), e.get("GOOGLE_OAUTH_CLIENT_SECRET")
    if not cid or not sec:
        sys.exit(f"Mangler GOOGLE_OAUTH_CLIENT_ID / GOOGLE_OAUTH_CLIENT_SECRET i {ENV}")
    return cid, sec


def _post(data):
    req = urllib.request.Request(TOKEN_URL, data=urllib.parse.urlencode(data).encode(), method="POST")
    return json.load(urllib.request.urlopen(req, timeout=30))


def login():
    """Engangs OAuth-flyt med PKCE og svar til 127.0.0.1. Kontovelgeren vises alltid, så du får valgt riktig konto."""
    cid, sec = klient()
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(48)).decode().rstrip("=")
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip("=")
    state = secrets.token_urlsafe(16)
    fanget = {}

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            fanget.update({k: v[0] for k, v in q.items()})
            ok = "code" in q and q.get("state", [None])[0] == state
            self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.end_headers()
            self.wfile.write(("<h2>%s</h2><p>Du kan lukke dette vinduet.</p>" % ("Innlogging fullført" if ok else "Innlogging feilet")).encode())

        def log_message(self, *a):
            pass

    srv = http.server.HTTPServer(("127.0.0.1", 0), Handler)
    redirect = "http://127.0.0.1:%d" % srv.server_address[1]
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode({
        "client_id": cid, "redirect_uri": redirect, "response_type": "code", "scope": SCOPE, "access_type": "offline",
        "prompt": "select_account consent", "state": state, "code_challenge": challenge, "code_challenge_method": "S256"})
    print("Åpner nettleseren. Velg Google-kontoen som eier kanalen, og kanalen din hvis Google spør.\n"
          "Kommer ikke vinduet opp, åpne denne lenken selv:\n" + url + "\n")
    threading.Thread(target=webbrowser.open, args=(url,), daemon=True).start()
    srv.handle_request(); srv.server_close()
    if fanget.get("state") != state or "code" not in fanget:
        sys.exit("Avbrutt: %s" % fanget.get("error", "ingen kode mottatt"))
    svar = _post({"code": fanget["code"], "client_id": cid, "client_secret": sec, "redirect_uri": redirect,
                  "grant_type": "authorization_code", "code_verifier": verifier})
    if "refresh_token" not in svar:
        sys.exit("Fikk ingen refresh_token. Fjern tilgangen på myaccount.google.com/permissions og prøv igjen.")
    TOKEN.parent.mkdir(parents=True, exist_ok=True); os.chmod(TOKEN.parent, 0o700)
    TOKEN.write_text(json.dumps({"refresh_token": svar["refresh_token"], "scope": svar.get("scope", SCOPE)})); os.chmod(TOKEN, 0o600)
    print("Token lagret:", TOKEN)
    k = hent("https://www.googleapis.com/youtube/v3/channels", part="snippet,statistics", mine="true")["items"]
    print("Koblet til:", ", ".join(f"{c['snippet']['title']} ({c['statistics'].get('subscriberCount', '?')} abonnenter)" for c in k))


def access_token():
    if _cache.get("t", (None, 0))[1] > time.time():
        return _cache["t"][0]
    if not TOKEN.exists():
        sys.exit("Ikke logget inn. Kjør: python3 yt_tall.py login")
    cid, sec = klient()
    svar = _post({"refresh_token": json.loads(TOKEN.read_text())["refresh_token"], "client_id": cid, "client_secret": sec,
                  "grant_type": "refresh_token"})
    _cache["t"] = (svar["access_token"], time.time() + svar.get("expires_in", 3600) - 300)
    return _cache["t"][0]


def hent(url, **p):
    req = urllib.request.Request(url + "?" + urllib.parse.urlencode(p), headers={"Authorization": "Bearer " + access_token()})
    for forsøk in range(3):   # YouTube svarer av og til 500 «Internal error» som går over av seg selv
        try:
            return json.load(urllib.request.urlopen(req, timeout=60))
        except urllib.error.HTTPError as e:
            if e.code < 500 or forsøk == 2:
                sys.exit(f"YouTube svarte {e.code}: {e.read()[:300].decode(errors='replace')}")
            time.sleep(5)


def analyse(**p):
    r = hent("https://youtubeanalytics.googleapis.com/v2/reports", ids="channel==MINE", **p)
    navn = [h["name"] for h in r.get("columnHeaders", [])]
    return [dict(zip(navn, rad)) for rad in r.get("rows", [])]


def sek(iso):
    """PT4M13S -> 253"""
    m = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    return sum(int(v or 0) * f for v, f in zip(m.groups(), (3600, 60, 1))) if m else 0


def les_kurve(punkter, lengde):
    """punkter: [(andel av videoen 0-1, andel som fortsatt ser 0-1+)] sortert. Gir de tre tingene du kan handle på.
    - etter_30s: hvor mange som er igjen etter 30 sekunder (åpningen)
    - halvert: tidspunktet der under halvparten er igjen (None hvis aldri)
    - storste_fall: (sekund, hvor mye som forsvant) for det bratteste fallet etter åpningen
    """
    if not punkter or lengde <= 0:
        return None
    ved = lambda t: min(punkter, key=lambda p: abs(p[0] * lengde - t))[1]
    halvert = next((round(a * lengde) for a, v in punkter if v < 0.5), None)
    fall = [(round(b[0] * lengde), a[1] - b[1]) for a, b in zip(punkter, punkter[1:]) if b[0] * lengde > 30]
    return {"etter_30s": ved(30), "halvert": halvert, "storste_fall": max(fall, key=lambda f: f[1]) if fall else None}


def mmss(s):
    return f"{int(s) // 60}:{int(s) % 60:02d}"


def rapport(dager):
    i_dag = datetime.date.today()
    fra, til = (i_dag - datetime.timedelta(days=dager)).isoformat(), i_dag.isoformat()
    kanal = hent("https://www.googleapis.com/youtube/v3/channels", part="snippet,statistics", mine="true")["items"][0]
    total = analyse(startDate=fra, endDate=til,
                    metrics="views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,subscribersGained,subscribersLost")
    topp = analyse(startDate=fra, endDate=til, dimensions="video", sort="-views", maxResults=10,
                   metrics="views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,subscribersGained,likes,comments,shares")
    info = {}
    if topp:
        for v in hent("https://www.googleapis.com/youtube/v3/videos", part="snippet,contentDetails",
                      id=",".join(t["video"] for t in topp))["items"]:
            info[v["id"]] = (v["snippet"]["title"], sek(v["contentDetails"]["duration"]), v["snippet"]["publishedAt"][:10])
    linjer = [f"# YouTube-tall {fra} til {til}", "",
              f"Kanal: {kanal['snippet']['title']}, {kanal['statistics'].get('subscriberCount', '?')} abonnenter.", ""]
    t = total[0] if total else {}
    if t:
        linjer += [f"- Visninger: {t['views']}", f"- Sett tid: {round(t['estimatedMinutesWatched'] / 60, 1)} timer",
                   f"- Snitt sett per visning: {mmss(t['averageViewDuration'])} ({round(t['averageViewPercentage'])} % av videoen)",
                   f"- Abonnenter: +{t['subscribersGained']} / -{t['subscribersLost']}", ""]
    linjer += ["## Videoene med flest visninger i perioden", ""]
    rad = []
    for v in topp:
        tittel, lengde, ute = info.get(v["video"], (v["video"], 0, "?"))
        linje = (f"**{tittel}** (ute {ute}, {mmss(lengde)}): {v['views']} visninger, sett {round(v['averageViewPercentage'])} % i snitt, "
                 f"+{v['subscribersGained']} abonnenter, {v['likes']} liker, {v['comments']} kommentarer")
        # Kurven hentes bare for de tre øverste, ett kall per video. Hent flere når kanalen har flere ferske videoer.
        if len(rad) < 3 and lengde:
            k = analyse(startDate=fra, endDate=til, dimensions="elapsedVideoTimeRatio", metrics="audienceWatchRatio",
                        filters=f"video=={v['video']}")
            les = les_kurve([(p["elapsedVideoTimeRatio"], p["audienceWatchRatio"]) for p in k], lengde)
            if les:
                linje += f"\n  - Igjen etter 30 sekunder: {round(les['etter_30s'] * 100)} %"
                linje += f"\n  - Under halvparten igjen fra: {mmss(les['halvert']) if les['halvert'] is not None else 'aldri'}"
                if les["storste_fall"]:
                    linje += f"\n  - Bratteste fall: ved {mmss(les['storste_fall'][0])} ({round(les['storste_fall'][1] * 100)} prosentpoeng)"
            else:
                linje += "\n  - For få visninger til at YouTube viser hvor folk faller av"
        rad.append(linje)
    linjer += [f"{n}. {r}" for n, r in enumerate(rad, 1)] or ["Ingen visninger i perioden."]
    linjer += ["", "## Det API-et ikke gir", "",
               "Klikkraten på thumbnailen står bare i YouTube Studio (Analytics -> Rekkevidde). Les den der for hver ny video."]
    UT.mkdir(parents=True, exist_ok=True)
    fil = UT / f"{til}-{dager}d.md"
    fil.write_text("\n".join(linjer) + "\n")
    print("\n".join(linjer[:12 + len(rad)]))
    print(f"\n-> {fil}")


def selvtest():
    # 4 minutter: 80 % igjen etter 30 s, faller under halvparten ved 2:00, bratteste fall mellom 1:36 og 2:00
    p = [(0.0, 1.0), (0.125, 0.8), (0.25, 0.75), (0.4, 0.7), (0.5, 0.45), (0.75, 0.4), (1.0, 0.3)]
    r = les_kurve(p, 240)
    assert r["etter_30s"] == 0.8 and r["halvert"] == 120 and r["storste_fall"][0] == 120 and abs(r["storste_fall"][1] - 0.25) < 1e-9, r
    assert les_kurve([], 240) is None and les_kurve(p, 0) is None
    assert les_kurve([(0.0, 1.0), (1.0, 0.9)], 20)["halvert"] is None       # kort video: ingen halvering, ingen fall etter 30 s
    assert sek("PT4M13S") == 253 and sek("PT1H2S") == 3602 and sek("") == 0 and mmss(125) == "2:05"
    print("selvtest ok")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: selvtest()
    elif a[0] == "login": login()
    elif a[0] == "rapport": rapport(int(a[a.index("--dager") + 1]) if "--dager" in a else 28)
    else: sys.exit(__doc__)
