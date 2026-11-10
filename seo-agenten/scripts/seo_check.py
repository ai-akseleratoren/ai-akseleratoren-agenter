#!/usr/bin/env python3
"""Technical SEO and AI-crawler check for any website.

Fetches every URL in the sitemap the way search engines and AI crawlers do
(no JavaScript) and checks what they actually get: status, language, title,
description, canonical, hreflang, JSON-LD and amount of real text. Also checks
robots.txt, llms.txt and the IndexNow key file.

    python3 scripts/seo_check.py                          # live site (SITE_URL in .env)
    python3 scripts/seo_check.py http://localhost:5173    # a local build, URLs from the live sitemap
    python3 scripts/seo_check.py --save                   # also write seo/rapporter/<date>.md

.env in the project root (or environment):
    SITE_URL=https://www.example.com
    INDEXNOW_KEY=                  # optional; checks /<key>.txt is served
    SEO_MULTILANG=1                # optional; require hreflang + x-default on every page

Stdlib only. Exit code 1 if any check fails.
"""
import datetime, html, json, os, re, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV = dict(os.environ)
if (ROOT / ".env").exists():
    for line in (ROOT / ".env").read_text().splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            k, v = line.split("=", 1)
            ENV.setdefault(k.strip(), v.strip().strip('"'))
SITE = (ENV.get("SITE_URL") or sys.exit("SITE_URL missing in .env")).rstrip("/")
args = [a for a in sys.argv[1:] if not a.startswith("--")]
BASE = (args[0] if args else SITE).rstrip("/")
AI_BOTS = ["GPTBot", "OAI-SearchBot", "ClaudeBot", "PerplexityBot", "Google-Extended"]
INDEXNOW_KEY = ENV.get("INDEXNOW_KEY", "")
MULTILANG = ENV.get("SEO_MULTILANG") == "1"
MIN_WORDS = 300

def get(path, ua="Mozilla/5.0 (compatible; SEOCheck/1.0)"):
    url = path if path.startswith("http") else BASE + path
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": ua}), timeout=30) as r:
            return r.status, r.read().decode("utf-8", "replace"), r.headers.get("Content-Type", "")
    except urllib.error.HTTPError as e:
        return e.code, "", ""

def first(pattern, text):
    m = re.search(pattern, text, re.I | re.S)
    return html.unescape(m.group(1).strip()) if m else None

def words(page):
    body = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", page)
    return len(re.sub(r"<[^>]+>", " ", body).split())

results = []  # (ok, area, message)
def check(ok, area, msg):
    results.append((bool(ok), area, msg))

# robots.txt
st, robots, _ = get("/robots.txt")
check(st == 200 and "User-agent" in robots, "robots.txt", f"status {st}")
check("Sitemap:" in robots, "robots.txt", "points to the sitemap")
for bot in AI_BOTS:
    blocked = re.search(rf"User-agent:\s*{bot}\s*\n(?:[^\n]+\n)*?Disallow:\s*/\s*\n", robots + "\n", re.I)
    check(not blocked, "robots.txt", f"{bot} not blocked")

# llms.txt and IndexNow key
st, llms, ctype = get("/llms.txt")
check(st == 200 and llms.lstrip().startswith("#") and "html" not in ctype, "llms.txt", f"served as text (status {st}, {ctype or 'no type'})")
if INDEXNOW_KEY:
    st, key, _ = get(f"/{INDEXNOW_KEY}.txt")
    check(st == 200 and key.strip() == INDEXNOW_KEY, "IndexNow", "key file served")

# sitemap
st, sm, _ = get("/sitemap.xml")
urls = re.findall(r"<loc>([^<]+)</loc>", sm)
check(st == 200 and urls, "sitemap", f"{len(urls)} URLs")
urls = urls or [SITE + "/"]  # no sitemap: still check the front page

pages = {}
for url in urls:
    path = url.replace(SITE, "") or "/"
    st, page, _ = get(path, ua="Mozilla/5.0 (compatible; GPTBot/1.2; +https://openai.com/gptbot)")
    info = {
        "status": st,
        "lang": first(r'<html[^>]*\blang="([^"]+)"', page),
        "title": first(r"<title>(.*?)</title>", page),
        "desc": first(r'<meta name="description" content="([^"]*)"', page),
        "canonical": first(r'<link rel="canonical" href="([^"]+)"', page),
        "hreflang": dict(re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)"', page)),
        "jsonld": re.findall(r'<script type="application/ld\+json">(.*?)</script>', page, re.S),
        "words": words(page),
    }
    pages[url] = info
    a = path
    check(st == 200, a, f"status {st}")
    check(info["lang"] not in (None, ""), a, f"lang={info['lang']}")
    t = info["title"] or ""
    check(15 <= len(t) <= 75, a, f"title {len(t)} chars: {t[:80]}")
    d = info["desc"] or ""
    check(70 <= len(d) <= 170, a, f"description {len(d)} chars")
    check(info["canonical"] == url, a, f"canonical {info['canonical']}")
    if MULTILANG:
        check("x-default" in info["hreflang"] and len(info["hreflang"]) >= 2, a, f"hreflang {sorted(info['hreflang'])}")
    types = []
    for block in info["jsonld"]:
        try:
            data = json.loads(block)
            for node in data.get("@graph", [data]):
                types.append(node.get("@type"))
        except ValueError:
            types.append("INVALID")
    check(types and "INVALID" not in types, a, f"JSON-LD {types}")
    check(info["words"] >= MIN_WORDS, a, f"{info['words']} words of real text without JavaScript")

# hreflang must point both ways
for url, info in pages.items():
    for lang, target in info["hreflang"].items():
        if lang == "x-default" or target == url:
            continue
        back = pages.get(target, {}).get("hreflang", {})
        check(url in back.values(), url.replace(SITE, "") or "/", f"hreflang {lang} -> {target} links back")

# report
fails = [r for r in results if not r[0]]
today = datetime.date.today().isoformat()
lines = [f"# SEO check {today}", "", f"Site: {BASE}", f"Checks: {len(results)}, failed: {len(fails)}", ""]
if fails:
    lines += ["## Failed", ""] + [f"- **{a}**: {m}" for _, a, m in fails] + [""]
lines += ["## Pages", "", "| Page | Status | Lang | Words | Title |", "|---|---|---|---|---|"]
for url, i in pages.items():
    lines.append(f"| {url.replace(SITE, '') or '/'} | {i['status']} | {i['lang']} | {i['words']} | {(i['title'] or '')[:60]} |")
report = "\n".join(lines) + "\n"
print(report)
if "--save" in sys.argv:
    out = ROOT / "seo" / "rapporter" / f"{today}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report)
    print(f"saved {out}")
sys.exit(1 if fails else 0)
