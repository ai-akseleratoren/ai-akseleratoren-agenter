#!/usr/bin/env python3
"""Hent alt fra Meta Marketing API for én annonsekonto og cache som JSON.

Bruk: python3 scripts/hent_meta.py [--siden 2025-08-01] [--til 2026-08-01]
                                   [--fersk] [kun_struktur|kun_innsikt]

Leser META_ADS_TOKEN og META_AD_ACCOUNT fra .env i repo-roten (se .env.example).
Skriver til data/: campaigns, adsets, ads, activities, insights_ad_daily,
insights_placement_monthly, insights_placement_adset, insights_placement_ad,
insights_agegender_monthly, insights_device_monthly, insights_country_monthly,
insights_hourly, insights_adset_weekly, insights_account_daily.

Kun standardbiblioteket. Kontoen røres aldri — alt her er lesing.
"""
import json, os, sys, time, urllib.request, urllib.parse, urllib.error
from datetime import date, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env = dict(l.strip().split("=", 1) for l in open(os.path.join(ROOT, ".env")) if "=" in l)
TOKEN, ACC = env["META_ADS_TOKEN"], env["META_AD_ACCOUNT"]   # ACC = "act_XXXXXXXXXX"
GRAPH = "https://graph.facebook.com/v21.0"

args = sys.argv[1:]
def opt(name, default):
    return args[args.index(name) + 1] if name in args else default
DATA = opt("--data", os.path.join(ROOT, "data")); os.makedirs(DATA, exist_ok=True)
SINCE = opt("--siden", str(date.today() - timedelta(days=395)))
UNTIL = opt("--til", str(date.today()))
TR = json.dumps({"since": SINCE, "until": UNTIL})


def fb(path, method="GET", **params):
    """Ett kall mot Graph API, med backoff på rate limit og forbigående feil."""
    params["access_token"] = TOKEN
    for attempt in range(6):
        try:
            if method == "POST":
                req = urllib.request.Request(f"{GRAPH}{path}", data=urllib.parse.urlencode(params).encode(), method="POST")
            else:
                req = f"{GRAPH}{path}?{urllib.parse.urlencode(params)}"
            return json.load(urllib.request.urlopen(req, timeout=120))
        except urllib.error.HTTPError as e:
            err = json.loads(e.read().decode("utf-8", "replace")).get("error", {})
            if err.get("code") in (1, 2, 4, 17, 32, 613, 80000, 80004) and attempt < 5:
                wait = 30 * (attempt + 1)
                print(f"  rate/transient {err.get('code')}: venter {wait}s", file=sys.stderr)
                time.sleep(wait); continue
            sys.exit(f"Meta-API-feil ({err.get('code')}): {err.get('message')} [{path}]")


def page_all(path, **params):
    rows, after = [], None
    while True:
        if after: params["after"] = after
        d = fb(path, **params)
        rows += d.get("data", [])
        nxt = d.get("paging", {}).get("next")
        after = d.get("paging", {}).get("cursors", {}).get("after")
        if not nxt or not after: return rows


def insights_async(name, **params):
    """Async insights-rapport -> liste med rader. Cachet i data/{name}.json.

    Lange perioder MÅ hentes async — synkrone insights-kall timer ut.
    """
    out = os.path.join(DATA, f"{name}.json")
    if os.path.exists(out) and "--fersk" not in args:
        print(f"  {name}: cache"); return json.load(open(out))
    params.setdefault("time_range", TR)
    for attempt in range(6):
        run = fb(f"/{ACC}/insights", method="POST", **params)
        rid = run["report_run_id"]
        while True:
            st = fb(f"/{rid}")
            if st.get("async_status") in ("Job Completed", "Job Failed", "Job Skipped"): break
            time.sleep(5)
        if st.get("async_status") == "Job Completed": break
        if attempt == 5: sys.exit(f"{name}: {st}")
        print(f"  {name}: {st.get('error_user_title')} – venter 3 min", file=sys.stderr)
        time.sleep(180)
    rows = page_all(f"/{rid}/insights", limit=500)
    json.dump(rows, open(out, "w"), ensure_ascii=False)
    print(f"  {name}: {len(rows)} rader"); return rows


def save(name, rows):
    json.dump(rows, open(os.path.join(DATA, f"{name}.json"), "w"), ensure_ascii=False)
    print(f"  {name}: {len(rows)}")


mode = next((a for a in args if a in ("kun_struktur", "kun_innsikt")), None)
print(f"Periode {SINCE}..{UNTIL}, konto {ACC}")

if mode != "kun_innsikt":
    print("Struktur:")
    save("campaigns", page_all(f"/{ACC}/campaigns", limit=500, fields="name,objective,status,effective_status,created_time,start_time,stop_time,updated_time,daily_budget,lifetime_budget,buying_type,bid_strategy,special_ad_categories"))
    # targeting-feltet er det som gjør målgruppeanalysen mulig senere
    save("adsets", page_all(f"/{ACC}/adsets", limit=200, fields="name,campaign_id,status,effective_status,created_time,updated_time,start_time,end_time,daily_budget,lifetime_budget,optimization_goal,billing_event,bid_strategy,bid_amount,destination_type,promoted_object,targeting,attribution_spec,learning_stage_info"))
    import calendar, datetime as _dt
    upd = calendar.timegm(_dt.datetime.strptime(SINCE, "%Y-%m-%d").timetuple())
    save("ads", page_all(f"/{ACC}/ads", limit=50, updated_since=upd, fields="name,adset_id,campaign_id,status,effective_status,created_time,updated_time,creative{id,name,title,body,object_type,object_story_spec,asset_feed_spec,video_id,image_url,thumbnail_url,call_to_action_type,effective_object_story_id},tracking_specs"))
    # Aktivitetslogg = hvem skrudde hva av/på når. Kan mangle tilgang; da tomt.
    acts = []
    try:
        acts = page_all(f"/{ACC}/activities", limit=500, since=SINCE, until=UNTIL, fields="event_type,event_time,object_id,object_name,object_type,actor_name,extra_data,translated_event_type")
    except SystemExit as e:
        print(f"  activities feilet: {e}")
    save("activities", acts)

if mode != "kun_struktur":
    print("Innsikt:")
    BASE = "campaign_id,campaign_name,adset_id,adset_name,ad_id,ad_name,spend,impressions,reach,frequency,clicks,inline_link_clicks,actions,cost_per_action_type,video_thruplay_watched_actions,video_p25_watched_actions,video_p50_watched_actions,video_p75_watched_actions,video_p100_watched_actions,video_play_actions"
    insights_async("insights_ad_daily", level="ad", time_increment=1, fields=BASE)
    P = "campaign_id,campaign_name,adset_id,adset_name,spend,impressions,reach,clicks,inline_link_clicks,actions"
    insights_async("insights_placement_monthly", level="campaign", time_increment="monthly", breakdowns="publisher_platform,platform_position,impression_device", fields="campaign_id,campaign_name,spend,impressions,reach,clicks,inline_link_clicks,actions")
    insights_async("insights_placement_adset", level="adset", breakdowns="publisher_platform,platform_position", fields=P)
    insights_async("insights_placement_ad", level="ad", breakdowns="publisher_platform,platform_position", fields=BASE.split(",video")[0])
    insights_async("insights_agegender_monthly", level="campaign", time_increment="monthly", breakdowns="age,gender", fields="campaign_id,campaign_name,spend,impressions,reach,clicks,actions")
    insights_async("insights_device_monthly", level="campaign", time_increment="monthly", breakdowns="device_platform", fields="campaign_id,campaign_name,spend,impressions,clicks,actions")
    insights_async("insights_country_monthly", level="campaign", time_increment="monthly", breakdowns="country", fields="campaign_id,campaign_name,spend,impressions,clicks,actions")
    insights_async("insights_hourly", level="account", breakdowns="hourly_stats_aggregated_by_advertiser_time_zone", fields="spend,impressions,clicks,actions")
    insights_async("insights_adset_weekly", level="adset", time_increment=7, fields="campaign_id,campaign_name,adset_id,adset_name,spend,impressions,reach,frequency,inline_link_clicks,actions")
    insights_async("insights_account_daily", level="account", time_increment=1, fields="spend,impressions,reach,frequency,clicks,inline_link_clicks,actions,cpm")
print("Ferdig.")
