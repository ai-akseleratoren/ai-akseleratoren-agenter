#!/usr/bin/env python3
"""Hent det Pakkeren trenger fra YouTube: dagens tittel/beskrivelse/tagger og transkript.

Bruk:  python3 hent.py                 # hele spillelista (sett PAKKEREN_SPILLELISTE først)
       python3 hent.py <video-id|url>  # én eller flere episoder
       python3 hent.py --sok "ditt søkeord" "et til"   # hva folk søker på YouTube (Norge; bytt hl og gl i sok() for andre land)

Skriver episoder/<id>/naa.md (slik episoden ligger ute i dag) og
episoder/<id>/transkript.txt (YouTubes autoteksting, tidsstemplet per ~10 sek).
Krever yt-dlp på PATH. Leser kun offentlige data, ingen nøkler.
"""
import html, json, os, re, subprocess, sys, tempfile, urllib.parse, urllib.request

SPILLELISTE = os.environ.get("PAKKEREN_SPILLELISTE", "")   # lenka til spillelista med episodene dine
HER = os.path.dirname(os.path.abspath(__file__))
TID = re.compile(r"(\d+):(\d\d):(\d\d)\.\d+ -->")


def transkript(vtt, blokk=10):
    """Autoteksting gjentar hver linje i neste cue. Fjern gjentakelsene, samle i blokker."""
    ut, forrige, start, buf = [], None, None, []
    t = 0
    for linje in vtt.splitlines():
        m = TID.match(linje)
        if m:
            t = int(m[1]) * 3600 + int(m[2]) * 60 + int(m[3])
            continue
        tekst = html.unescape(re.sub(r"<[^>]+>", "", linje)).strip()
        if not tekst or tekst == forrige or tekst.startswith(("WEBVTT", "Kind:", "Language:")):
            continue
        forrige = tekst
        if start is None:
            start = t
        buf.append(tekst)
        if t - start >= blokk:
            ut.append(f"[{start // 60:02d}:{start % 60:02d}] {' '.join(buf)}")
            start, buf = None, []
    if buf:
        ut.append(f"[{start // 60:02d}:{start % 60:02d}] {' '.join(buf)}")
    return "\n".join(ut) + "\n"


def hent(maal):
    with tempfile.TemporaryDirectory() as tmp:
        ut = subprocess.run(
            ["yt-dlp", "--no-simulate", "--skip-download", "-j", "--write-subs", "--write-auto-subs",
             "--sub-langs", "no-orig,no,nb", "--sub-format", "vtt", "-o", f"{tmp}/%(id)s", *maal],
            capture_output=True, text=True)
        if not ut.stdout.strip():
            sys.exit(ut.stderr[-2000:])
        for rad in ut.stdout.splitlines():
            v = json.loads(rad)
            mappe = os.path.join(HER, "episoder", v["id"])
            os.makedirs(mappe, exist_ok=True)
            kapitler = "\n".join(f"- {int(k['start_time']) // 60:02d}:{int(k['start_time']) % 60:02d} {k['title']}"
                                 for k in v.get("chapters") or []) or "(ingen)"
            with open(os.path.join(mappe, "naa.md"), "w") as f:
                f.write(f"# {v['title']}\n\n"
                        f"- URL: https://www.youtube.com/watch?v={v['id']}\n"
                        f"- Publisert: {v.get('upload_date')}  Lengde: {v.get('duration_string')}\n"
                        f"- Visninger: {v.get('view_count')}  Likes: {v.get('like_count')}  Kommentarer: {v.get('comment_count')}\n"
                        f"- Tagger: {', '.join(v.get('tags') or []) or '(ingen)'}\n\n"
                        f"## Kapitler\n{kapitler}\n\n## Beskrivelse\n{v.get('description') or '(tom)'}\n")
            vtt = next((os.path.join(tmp, n) for n in sorted(os.listdir(tmp))
                        if n.startswith(v["id"]) and n.endswith(".vtt")), None)
            if vtt:
                with open(os.path.join(mappe, "transkript.txt"), "w") as f:
                    f.write(transkript(open(vtt).read()))
            print(v["id"], "ok" if vtt else "UTEN TEKSTING", v["title"])


def sok(ordene):
    """YouTubes egne søkeforslag. Viser hva folk skriver, ikke hvor mange som søker."""
    for q in ordene:
        url = "https://suggestqueries.google.com/complete/search?" + urllib.parse.urlencode(
            {"client": "firefox", "ds": "yt", "hl": "no", "gl": "NO", "q": q})
        with urllib.request.urlopen(url, timeout=20) as r:
            svar = r.read().decode(r.headers.get_content_charset() or "utf-8", "replace")
        print(f"{q}: {', '.join(json.loads(svar)[1]) or '(ingen forslag)'}")


if __name__ == "__main__":
    demo = "WEBVTT\n\n00:00:01.000 --> 00:00:03.000\nhei <c>og</c> velkommen\n\n00:00:03.000 --> 00:00:05.000\nhei og velkommen\ntil podkasten\n"
    assert transkript(demo) == "[00:01] hei og velkommen til podkasten\n", transkript(demo)
    if sys.argv[1:2] == ["--sok"]:
        sok(sys.argv[2:])
    else:
        maal = sys.argv[1:] or ([SPILLELISTE] if SPILLELISTE else [])
        if not maal:
            sys.exit("Gi en video-id eller lenke, eller sett PAKKEREN_SPILLELISTE til lenka til spillelista di.")
        hent(maal)
