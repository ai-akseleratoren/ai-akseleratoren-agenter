#!/usr/bin/env python3
"""Website traffic: Google Search Console (what people search, clicks,
impressions, position) and GA4 (sessions by source, incl. AI assistants).

Needs a Google service account that has been added as a user in Search Console
and in the GA4 property. In .env in the project root:

    GOOGLE_SA_KEY_FILE=/absolute/path/outside/the/repo/service-account.json
    GSC_SITE=sc-domain:example.com     # Domain property; URL property = https://www.example.com/
    GA4_PROPERTY_ID=                   # optional, digits only

    python3 scripts/seo_trafikk.py [days]   # default 28

Stdlib + the openssl CLI (signs the token).
"""
import base64, datetime, json, os, subprocess, sys, tempfile, time, urllib.parse, urllib.request
from pathlib import Path

ENV = {}
_env = Path(__file__).resolve().parents[1] / ".env"
for line in (_env.read_text().splitlines() if _env.exists() else []):
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        ENV[k.strip()] = v.strip().strip('"')

ENV = {**ENV, **{k: v for k, v in os.environ.items() if k in ("GOOGLE_SA_KEY_FILE", "GSC_SITE", "GA4_PROPERTY_ID")}}
KEY_FILE, SITE, GA4 = ENV.get("GOOGLE_SA_KEY_FILE"), ENV.get("GSC_SITE"), ENV.get("GA4_PROPERTY_ID")
if not SITE:
    sys.exit("GSC_SITE missing in .env (e.g. sc-domain:example.com).")
if not KEY_FILE or not Path(KEY_FILE).exists():
    sys.exit("GOOGLE_SA_KEY_FILE missing in .env — see the docstring for setup.")
DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 28
AI_SOURCES = ("chatgpt", "openai", "perplexity", "claude", "gemini", "copilot", "bing.com/chat")

b64 = lambda b: base64.urlsafe_b64encode(b).rstrip(b"=").decode()

def token():
    sa = json.loads(Path(KEY_FILE).read_text())
    now = int(time.time())
    head = b64(json.dumps({"alg": "RS256", "typ": "JWT"}).encode())
    claims = b64(json.dumps({
        "iss": sa["client_email"], "aud": sa["token_uri"], "iat": now, "exp": now + 3600,
        "scope": "https://www.googleapis.com/auth/webmasters.readonly https://www.googleapis.com/auth/analytics.readonly",
    }).encode())
    with tempfile.NamedTemporaryFile("w", suffix=".pem", delete=True) as f:
        f.write(sa["private_key"]); f.flush()
        sig = subprocess.run(["openssl", "dgst", "-sha256", "-sign", f.name], input=f"{head}.{claims}".encode(), capture_output=True, check=True).stdout
    body = f"grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer&assertion={head}.{claims}.{b64(sig)}".encode()
    return json.load(urllib.request.urlopen(urllib.request.Request(sa["token_uri"], data=body), timeout=30))["access_token"]

TOKEN = token()
def post(url, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"})
    try:
        return json.load(urllib.request.urlopen(req, timeout=60))
    except urllib.error.HTTPError as e:
        sys.exit(f"{e.code} from {url}: {e.read().decode()[:300]}")

end = datetime.date.today() - datetime.timedelta(days=2)  # Search Console lags ~2 days
start = end - datetime.timedelta(days=DAYS - 1)
print(f"# Traffic {SITE} {start} – {end}\n")

gsc = f"https://searchconsole.googleapis.com/webmasters/v3/sites/{urllib.parse.quote(SITE, safe='')}/searchAnalytics/query"
for dim, n in (("query", 25), ("page", 15), ("country", 10)):
    rows = post(gsc, {"startDate": str(start), "endDate": str(end), "dimensions": [dim], "rowLimit": n}).get("rows", [])
    print(f"## Google search by {dim}\n\n| {dim} | clicks | impressions | CTR | position |\n|---|---|---|---|---|")
    for r in rows:
        print(f"| {r['keys'][0]} | {r['clicks']:.0f} | {r['impressions']:.0f} | {r['ctr']*100:.1f} % | {r['position']:.1f} |")
    print()

if GA4:
    ga = f"https://analyticsdata.googleapis.com/v1beta/properties/{GA4}:runReport"
    rep = post(ga, {"dateRanges": [{"startDate": f"{DAYS}daysAgo", "endDate": "yesterday"}],
                    "dimensions": [{"name": "sessionSource"}], "metrics": [{"name": "sessions"}, {"name": "activeUsers"}],
                    "orderBys": [{"metric": {"metricName": "sessions"}, "desc": True}], "limit": 30})
    print("## Sessions by source (GA4)\n\n| source | sessions | users | AI? |\n|---|---|---|---|")
    for r in rep.get("rows", []):
        src = r["dimensionValues"][0]["value"]
        s, u = (m["value"] for m in r["metricValues"])
        print(f"| {src} | {s} | {u} | {'AI' if any(a in src.lower() for a in AI_SOURCES) else ''} |")
