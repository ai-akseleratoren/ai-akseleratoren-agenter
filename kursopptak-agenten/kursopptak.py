#!/usr/bin/env python3
"""Kursopptak: hent Zoom-opptak, chat og transkript fra sendingene dine.

Bruk:
  python3 kursopptak.py liste [--dager 60]
  python3 kursopptak.py hent siste [--uten-video]
  python3 kursopptak.py hent <møte-id> --dato 2026-08-18
  python3 kursopptak.py pakke opptak/<dato>-<id> [--transkript-url URL] [--video-url URL]
  python3 kursopptak.py test                        # selvsjekk av chat-tolkningen

Sendingene kjøres ofte fra en annen Zoom-bruker enn din egen (en felles
support-bruker, en kollega). En Server-to-Server-app med
cloud_recording:read:admin kan lese opptak per bruker, men har ofte IKKE
/meetings/{id}/recordings og ikke brukerlisting. Derfor skanner skriptet en
fast liste med vertskontoer (ZOOM_VERTER).

Leser .env i mappa du kjører fra (eller miljøvariabler):
  ZOOM_ACCOUNT_ID, ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET
  ZOOM_VERTER     kommaseparerte e-poster til Zoom-brukerne som kan være vert
  SENDING_EMNER   kommaseparerte ord i møtetittelen som betyr «kurssending»
  OPPTAK_MAPPE    hvor opptakene lagres (standard: ./opptak)
"""
import argparse, base64, json, os, re, shutil, sys, urllib.request, urllib.error
from datetime import datetime, timedelta, timezone

env = dict(os.environ)
if os.path.exists(".env"):
    with open(".env") as f:
        for line in f:
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.strip().split("=", 1)
                env.setdefault(k, v)

UT = os.path.abspath(env.get("OPPTAK_MAPPE") or "opptak")


def _liste(navn):
    return [x.strip().lower() for x in env.get(navn, "").split(",") if x.strip()]


# Zoom-brukere som kan være vert. API-et mangler ofte scope for å liste brukere,
# så lista vedlikeholdes manuelt. Flyttes sendinga til en ny vert: utvid den.
HOSTS = _liste("ZOOM_VERTER")

# Ord i møtetittelen som betyr at det er en kurssending.
EMNE_ORD = tuple(_liste("SENDING_EMNER")) or ("kurs", "labs", "velkommen", "bonus")


def token():
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
    r = urllib.request.urlopen(req, timeout=120)
    return r.read().decode("utf-8", "replace") if raw else json.load(r)


def finn(tok, dager):
    """Alle kursopptak siste N dager, nyeste forst."""
    if not HOSTS:
        sys.exit("ZOOM_VERTER mangler i .env — list Zoom-brukerne som kan være vert.")
    to = datetime.now(timezone.utc).date()
    frm = to - timedelta(days=dager)
    treff = []
    for u in HOSTS:
        try:
            d = zget(tok, f"/users/{u}/recordings?from={frm}&to={to}&page_size=100")
        except urllib.error.HTTPError as e:
            if e.code == 404:      # bruker finnes ikke lenger
                continue
            raise
        for m in d.get("meetings", []):
            if any(o in m["topic"].lower() for o in EMNE_ORD):
                m["_host"] = u
                treff.append(m)
    return sorted(treff, key=lambda m: m["start_time"], reverse=True)


def last_ned(tok, url, mal):
    """Streamer fila til disk. Zoom vil ha access_token som query-parameter."""
    sep = "&" if "?" in url else "?"
    req = urllib.request.Request(url + sep + "access_token=" + tok)
    with urllib.request.urlopen(req, timeout=900) as r, open(mal, "wb") as f:
        shutil.copyfileobj(r, f, 1024 * 1024)
    return os.path.getsize(mal)


def parse_chat(tekst):
    """Zoom-format: 'HH:MM:SS\\tNavn:\\tmelding'. Fortsettelseslinjer mangler tid."""
    ut = []
    for line in (tekst or "").splitlines():
        m = re.match(r"^(\d{2}:\d{2}:\d{2})\t(.+?):\t(.*)$", line)
        if m:
            ut.append({"tid": m.group(1), "navn": m.group(2).strip(), "tekst": m.group(3)})
        elif ut and line.strip():
            ut[-1]["tekst"] += " " + line.strip()
    return ut


BOT = ("fireflies", "notetaker", "otter.ai", "read.ai", "fathom", "meeting notes")


def sekunder(t):
    h, m, s = (int(x) for x in t.split(":"))
    return h * 3600 + m * 60 + s


def info_md(m, meldinger, filer):
    start = datetime.fromisoformat(m["start_time"].replace("Z", "+00:00"))
    ekte = [c for c in meldinger if not any(b in c["navn"].lower() for b in BOT)]
    slutt = max((sekunder(c["tid"]) for c in ekte), default=0)
    hale = [c for c in ekte if sekunder(c["tid"]) >= slutt - 600]
    sporsmal = [c for c in ekte if "?" in c["tekst"]]

    L = [f'# {m["topic"]}', "",
         f'- **Dato:** {start.strftime("%Y-%m-%d %H:%M")} UTC',
         f'- **Varighet:** {m.get("duration")} min',
         f'- **Zoom-ID:** {m["id"]}  ·  **Vert:** {m["_host"]}',
         f'- **Delelenke:** {m.get("share_url", "—")}',
         f'- **Filer:** ' + (", ".join(filer) if filer else "—"), "",
         "## Til Skool", "",
         "- [ ] Video lastet opp (YouTube unlisted / Skool classroom)",
         "- [ ] Leksjon opprettet i classroom",
         "- [ ] Chat + sporsmal limt inn i leksjonsteksten", "",
         f"## Sporsmal i chatten ({len(sporsmal)})", ""]
    L += [f'- **{c["navn"]}** ({c["tid"]}): {c["tekst"]}' for c in sporsmal] or ["_ingen_"]
    L += ["", "## Siste 10 minutter av chatten", ""]
    L += [f'- **{c["navn"]}** ({c["tid"]}): {c["tekst"]}' for c in hale] or ["_ingen_"]
    L += ["", "## Hele chatten", ""]
    L += [f'- **{c["navn"]}** ({c["tid"]}): {c["tekst"]}' for c in ekte] or ["_ingen_"]
    return "\n".join(L) + "\n"


def hent(tok, m, uten_video):
    dato = m["start_time"][:10]
    mappe = os.path.join(UT, f'{dato}-{m["id"]}')
    os.makedirs(mappe, exist_ok=True)
    navn = {"MP4": "video.mp4", "M4A": "lyd.m4a", "CHAT": "chat.txt",
            "TRANSCRIPT": "transkript.vtt", "CC": "undertekst.vtt"}
    filer, chat_tekst = [], ""
    for f in m.get("recording_files", []):
        ft = f.get("file_type")
        if ft not in navn or (uten_video and ft in ("MP4", "M4A")):
            continue
        if ft == "MP4" and f.get("recording_type") != "shared_screen_with_speaker_view" \
                and any(x.get("file_type") == "MP4" and
                        x.get("recording_type") == "shared_screen_with_speaker_view"
                        for x in m["recording_files"]):
            continue                      # ta bare hovedvideoen naar den finnes
        mal = os.path.join(mappe, navn[ft])
        n = last_ned(tok, f["download_url"], mal)
        filer.append(f"{navn[ft]} ({n/1e6:.1f} MB)")
        print(f"  lastet ned {navn[ft]}  {n/1e6:.1f} MB")
        if ft == "CHAT":
            chat_tekst = open(mal, encoding="utf-8", errors="replace").read()

    with open(os.path.join(mappe, "INFO.md"), "w", encoding="utf-8") as f:
        f.write(info_md(m, parse_chat(chat_tekst), filer))
    print(f"  INFO.md skrevet\n→ {mappe}")
    return mappe


def vtt_ren(sti):
    """VTT -> [(tid, taler, tekst)], sammenslatt per taler."""
    if not os.path.exists(sti):
        return []
    ut, tid = [], ""
    for line in open(sti, encoding="utf-8", errors="replace"):
        line = line.strip()
        m = re.match(r"^(\d{2}:\d{2}):\d{2}\.\d+ -->", line)
        if m:
            tid = m.group(1); continue
        if not line or line == "WEBVTT" or line.isdigit():
            continue
        taler, _, tekst = line.partition(": ")
        if not tekst:
            taler, tekst = "", line
        if ut and ut[-1][1] == taler:
            ut[-1][2] += " " + tekst
        else:
            ut.append([tid, taler, tekst])
    return ut


def pakke(mappe, transkript_url=None, video_url=None):
    """Skriver SKOOL.md — alt som trengs for a lage leksjonen."""
    info = os.path.join(mappe, "INFO.md")
    if not os.path.exists(info):
        sys.exit(f"Fant ingen INFO.md i {mappe}. Kjor 'hent' forst.")
    tekst = open(info, encoding="utf-8").read()

    def felt(navn):
        m = re.search(rf"\*\*{navn}:\*\* (.+)", tekst)
        return m.group(1).strip() if m else "—"

    tittel = tekst.splitlines()[0].lstrip("# ").strip()
    sporsmal = re.search(r"## Sporsmal i chatten \((\d+)\)\n\n(.*?)\n\n## ", tekst, re.S)
    q_antall = sporsmal.group(1) if sporsmal else "0"
    q_liste = sporsmal.group(2) if sporsmal else "_ingen_"

    linjer = vtt_ren(os.path.join(mappe, "transkript.vtt"))
    if linjer:
        with open(os.path.join(mappe, "transkript.txt"), "w", encoding="utf-8") as f:
            for tid, taler, t in linjer:
                f.write(f"[{tid}] {taler + ': ' if taler else ''}{t}\n")

    med = [n for n in ("video.mp4", "lyd.m4a") if os.path.exists(os.path.join(mappe, n))]
    L = [f"# Leksjonspakke — {tittel}", "",
         "Video-URL settes inn nar opptaket er lastet opp (YouTube unlisted, Vimeo).",
         "Alt annet er ferdig.", "",
         "## Metadata", "",
         f"- **Dato:** {felt('Dato')}",
         f"- **Varighet:** {felt('Varighet')}",
         f"- **Zoom-ID:** {felt('Zoom-ID')}",
         f"- **Video-URL:** " + (video_url or "`<fylles inn etter opplasting>`"),
         f"- **Lokal fil:** {', '.join(f'`{mappe}/{n}`' for n in med) or '—'}",
         f"- **Transkript (riktig norsk):** "
         + (transkript_url or "`<lenke til transkript fra Whisper/møteverktøy>`"), "",
         "> **NB om Zoom-transkriptet:** Zooms egen tekst gjør norsk tale til vrovl",
         "> (ASR-en står på engelsk). Bruk et transkript som kan norsk.", "",
         "## Leksjonsbeskrivelse (forslag)", "",
         f"Opptak av {tittel}. <Hva vi gikk gjennom, 1-2 setninger.> Under finner du alle",
         f"sporsmalene som kom i chatten ({q_antall} stk) med tidsstempel, sa du kan hoppe",
         "rett til det du lurer pa.", "",
         f"## Sporsmal fra chatten ({q_antall})", "", q_liste, ""]

    with open(os.path.join(mappe, "SKOOL.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print(f"  SKOOL.md skrevet ({q_antall} sporsmal"
          + (f", transkript.txt {len(linjer)} replikker)" if linjer else ", uten transkript)"))
    return os.path.join(mappe, "SKOOL.md")


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("liste"); a.add_argument("--dager", type=int, default=60)
    b = sub.add_parser("hent")
    b.add_argument("id", help="Zoom meeting-id, eller 'siste'")
    b.add_argument("--dato", help="YYYY-MM-DD — noedvendig naar samme PMI er brukt flere ganger")
    b.add_argument("--dager", type=int, default=60)
    b.add_argument("--uten-video", action="store_true", help="bare chat og transkript")
    c = sub.add_parser("pakke", help="bygg SKOOL.md paa nytt fra en ferdig hentet mappe")
    c.add_argument("mappe", help="sti til opptak/<dato>-<id>")
    c.add_argument("--transkript-url", help="lenke til et transkript som kan norsk")
    c.add_argument("--video-url", help="URL til opplastet video (YouTube/Vimeo)")
    sub.add_parser("test", help="selvsjekk av chat-tolkningen")
    args = p.parse_args()

    if args.cmd == "test":
        c = parse_chat("10:00:01\tKari:\tHei?\nfortsetter her\n10:05:00\tOla:\tTakk")
        assert [x["navn"] for x in c] == ["Kari", "Ola"], c
        assert c[0]["tekst"] == "Hei? fortsetter her", c
        assert sekunder("01:02:03") == 3723
        print("OK"); return

    if args.cmd == "pakke":
        pakke(os.path.abspath(args.mappe), args.transkript_url, args.video_url); return

    tok = token()
    treff = finn(tok, args.dager)
    if not treff:
        print("Fant ingen kursopptak i perioden."); return

    if args.cmd == "liste":
        for m in treff:
            ft = ",".join(sorted({f.get("file_type") for f in m.get("recording_files", [])}))
            print(f'{m["start_time"][:16]}  id={m["id"]:<12} {m.get("duration"):>3} min  '
                  f'[{ft}]  {m["topic"]}')
        return

    if args.id == "siste":
        valgt = treff[0]
    else:
        kand = [m for m in treff if str(m["id"]) == args.id
                and (not args.dato or m["start_time"].startswith(args.dato))]
        if len(kand) != 1:
            print(f"Fant {len(kand)} opptak for id={args.id}"
                  f'{" dato=" + args.dato if args.dato else ""}. Bruk --dato.')
            for m in kand:
                print(f'  {m["start_time"][:16]}  {m["topic"]}')
            sys.exit(1)
        valgt = kand[0]

    print(f'{valgt["topic"]}  ({valgt["start_time"][:16]}, {valgt.get("duration")} min)')
    hent(tok, valgt, args.uten_video)


if __name__ == "__main__":
    main()
