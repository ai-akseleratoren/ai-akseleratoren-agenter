"""Self-check: python3 test_rubin_mcp.py"""
import json, os, tempfile
from datetime import datetime, timedelta, timezone

os.environ["RUBIN_HOME"] = tempfile.mkdtemp()
os.environ.pop("YOUTUBE_API_KEY", None)
import rubin_mcp as m

now = datetime(2026, 11, 9, tzinfo=timezone.utc)
vid = lambda views, age=10, secs=600: {"title": "t", "views": views, "seconds": secs, "published": now - timedelta(days=age)}

base = [vid(1000) for _ in range(9)]
hits = m.find_outliers(base + [vid(5000)], 2.5, 60, now)
assert len(hits) == 1 and hits[0]["ratio"] == 5.0 and hits[0]["channel_median"] == 1000
assert not m.find_outliers(base + [vid(5000, age=90)], 2.5, 60, now), "too old"
assert not m.find_outliers(base + [vid(5000, secs=45)], 2.5, 60, now), "Shorts don't count"
assert not m.find_outliers([vid(1000), vid(9000)], 2.5, 60, now), "too few videos to judge"

assert m.idea_add("  ").startswith("Empty")
assert m.idea_add("Agenten som leser mailen") == "Added v1: Agenten som leser mailen"
assert "now mentioned 2 times" in m.idea_add("agenten som leser MAILEN!", "fra Telegram")
m.idea_add("Noe annet")
assert m.move("v2", "manus") == "v2 is now in manus."
assert m.move("v2", "tull").startswith("Unknown") and m.move("v9", "manus").startswith("No video")
videos = json.loads(m.board_view())["videos"]
assert [v["id"] for v in videos] == ["v1", "v2"] and videos[0]["count"] == 2 and "fra Telegram" in videos[0]["note"]

m.doc_save("v1", "manus", "Krok")
assert m.doc_read("v1", "manus") == "Krok" and m.doc_read("v1", "pakking").startswith("No pakking")
try:
    m.doc_save("../../x", "manus", "ondt")
    raise SystemExit("path traversal was allowed")
except ValueError:
    pass

assert m.watch_add("nope", "x").startswith("That is not")
assert m.watch_add("UC" + "a" * 22, "Kanal").startswith("Watching")
assert m._seconds("PT1H2M3S") == 3723 and m._seconds("PT45S") == 45 and m._seconds("P0D") == 0
assert "waiting for that key" in m.outliers()
os.environ["YOUTUBE_API_KEY"] = "${YOUTUBE_API_KEY}"
assert "waiting for that key" in m.outliers(), "an unexpanded placeholder is no key"
print("ok")
