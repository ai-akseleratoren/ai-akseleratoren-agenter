#!/usr/bin/env python3
"""Klonen: en video der en klone av deg leser manuset, med lysark ved siden av.

    python3 klone_video.py stemme opptak.mp3   # én gang: kloner stemmen din fra ca. ett minutt fri tale
    python3 klone_video.py tts                 # stemme per avsnitt + kontrollutskrift av hva som faktisk ble sagt
    python3 klone_video.py avatar              # avatar per avsnitt (koster ca. 6 cent per sekund hos fal.ai)
    python3 klone_video.py bygg                # lysark + ferdig video (klone-video.mp4)
Hvert steg hopper over det som alt er laget, så det kan kjøres på nytt. Slett lyd/NN.mp3 og av/NN.mp4
for å lage ett avsnitt om igjen.

Du trenger: FAL_KEY i .env, et stillbilde av deg som heter ansikt.jpg (stående, 9:16) i denne mappa,
ffmpeg (miljøvariabelen FFMPEG eller i PATH) og Google Chrome (CHROME, hvis den ikke ligger på standardplassen).
Lysarket merker hele videoen «AI-avatar og klonet stemme». La den merkingen stå.
"""
import html, json, os, pathlib, shutil, subprocess, sys, time, urllib.request
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from video import hent_nøkkel, kall

S = pathlib.Path(__file__).resolve().parent
FF = os.environ.get("FFMPEG") or shutil.which("ffmpeg") or "ffmpeg"
FFPROBE = os.environ.get("FFPROBE") or shutil.which("ffprobe") or FF.replace("ffmpeg", "ffprobe")
CHROME = os.environ.get("CHROME") or "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# (tekst som leses, overskrift på lysarket, punkter på lysarket). Bytt ut med ditt eget manus.
# <#0.4#> er en pause i sekunder. Ord stemmen uttaler feil, skriver du slik de skal høres ut:
# hos oss ble «agent» riktig først da vi skrev «a-gent». Lysarket bruker din vanlige skrivemåte.
AVSNITT = [
    ("Dette er ikke meg. <#0.4#> Stemmen er klonet fra ett minutt der jeg snakker fritt, og ansiktet er laget av ett stillbilde.",
     "Dette er ikke meg", ["Stemmen: ett minutt opptak", "Ansiktet: ett stillbilde"]),
    ("Jeg skal vise deg tre ting. Hva som ble laget. Hvordan du setter opp det samme. Og hva som gikk galt underveis.",
     "Tre ting", ["1. Hva som ble laget", "2. Slik setter du opp det samme", "3. Hva som gikk galt"]),
    ("Jeg ser gjennom denne videoen før den legges ut. Den jobben er fortsatt min.",
     "Jeg ser gjennom den først", ["En klone kan lese et manus", "Den kan ikke svare deg"]),
]


def opp(sti, typ):
    svar = kall("https://rest.alpha.fal.ai/storage/upload/initiate", N, {"content_type": typ, "file_name": pathlib.Path(sti).name})
    urllib.request.urlopen(urllib.request.Request(svar["upload_url"], data=pathlib.Path(sti).read_bytes(), method="PUT",
                                                  headers={"Content-Type": typ})).read()
    return svar["file_url"]


def vent(jobber):
    """jobber: {navn: jobb}. Returnerer {navn: svar}; en jobb som feiler blir stående som None."""
    ut = {}
    while len(ut) < len(jobber):
        for navn, j in jobber.items():
            if navn in ut: continue
            st = kall(j["status_url"], N)["status"]
            if st == "COMPLETED": ut[navn] = kall(j["response_url"], N)
            elif st not in ("IN_QUEUE", "IN_PROGRESS"): ut[navn] = None; print("FEIL", navn, st, flush=True)
        time.sleep(5)
    return ut


def stemme(opptak):
    """Kloner stemmen fra en lydfil (mp3, ca. ett minutt der du snakker fritt, uten musikk) og lagrer voice_id.txt."""
    tekst = "Dette er en test av den klonede stemmen min. Hører du at det er meg?"
    jobb = kall("https://queue.fal.run/fal-ai/minimax/voice-clone", N,
                {"audio_url": opp(opptak, "audio/mpeg"), "model": "speech-02-hd", "noise_reduction": False, "text": tekst})
    r = vent({"klone": jobb})["klone"]
    if not r: raise SystemExit("Kloningen feilet. Prøv et renere opptak.")
    (S / "voice_id.txt").write_text(r["custom_voice_id"]); print("stemmen er klonet, id lagret i voice_id.txt")


def tts():
    (S / "lyd").mkdir(exist_ok=True)
    stemme = (S / "voice_id.txt").read_text().strip()
    jobber = {}
    for i, (tekst, _, _) in enumerate(AVSNITT):
        if (S / f"lyd/{i:02d}.mp3").exists(): continue
        jobber[i] = kall("https://queue.fal.run/fal-ai/minimax/speech-2.8-hd", N, {
            "prompt": tekst, "language_boost": "Norwegian", "output_format": "url",
            "voice_setting": {"voice_id": stemme, "speed": 0.95, "emotion": "neutral"}})
    for i, r in vent(jobber).items():
        if r: urllib.request.urlretrieve(r["audio"]["url"], S / f"lyd/{i:02d}.mp3")
    # kontroll: skriv lyden ut igjen som tekst, så feiluttale synes uten at noen må høre gjennom alt
    jobber = {i: kall("https://queue.fal.run/fal-ai/whisper", N, {"audio_url": opp(S / f"lyd/{i:02d}.mp3", "audio/mpeg"),
                                                                    "task": "transcribe", "language": "no", "chunk_level": "segment"})
              for i in range(len(AVSNITT)) if (S / f"lyd/{i:02d}.mp3").exists()}
    total = 0
    for i, r in sorted(vent(jobber).items()):
        d = float(subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of",
                                  "csv=p=0", str(S / f"lyd/{i:02d}.mp3")], capture_output=True, text=True).stdout)
        total += d
        print(f"{i:02d} {d:5.1f}s  {(r or {}).get('text', 'INGEN TEKST').strip()}", flush=True)
    print(f"sum {total:.0f} s, avatar ca. {total * 0.0562:.1f} dollar")


def avatar():
    (S / "av").mkdir(exist_ok=True)
    bilde = opp(S / "ansikt.jpg", "image/jpeg")
    jobber = {}
    for i in range(len(AVSNITT)):
        if (S / f"av/{i:02d}.mp4").exists(): continue
        jobber[i] = kall("https://queue.fal.run/fal-ai/kling-video/ai-avatar/v2/standard", N, {
            "image_url": bilde, "audio_url": opp(S / f"lyd/{i:02d}.mp3", "audio/mpeg"),
            "prompt": "A person talks calmly to the camera, natural small head movements, static camera."})
        print("sendt", i, flush=True)
    for i, r in vent(jobber).items():
        if r: urllib.request.urlretrieve(r["video"]["url"], S / f"av/{i:02d}.mp4"); print("hentet", i, flush=True)


ARK = """<!doctype html><meta charset="utf-8"><style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,800&family=Instrument+Sans:wght@400;600&display=swap');
body{{margin:0;width:1312px;height:1080px;background:#15130f;color:#f4eee5;font-family:'Instrument Sans',Arial,sans-serif;
display:flex;flex-direction:column;justify-content:center;padding:0 96px;box-sizing:border-box}}
.m{{position:absolute;top:56px;left:96px;font:600 24px 'Instrument Sans',Arial;letter-spacing:4px;color:#e8613c;text-transform:uppercase}}
.n{{position:absolute;top:56px;right:96px;font:600 24px 'Instrument Sans',Arial;color:#8d8376}}
h1{{font:800 76px/1.06 'Bricolage Grotesque',Arial,sans-serif;margin:0 0 48px;letter-spacing:-1px}}
p{{font-size:40px;line-height:1.3;margin:0 0 22px;padding-left:28px;border-left:6px solid #e8613c;color:#e9e1d5}}
</style><div class="m">AI-avatar og klonet stemme</div><div class="n">{nr} / {ant}</div><h1>{tittel}</h1>{punkter}"""


def bygg():
    (S / "ark").mkdir(exist_ok=True); (S / "del").mkdir(exist_ok=True)
    deler = []
    for i, (_, tittel, punkter) in enumerate(AVSNITT):
        h = S / f"ark/{i:02d}.html"; png = S / f"ark/{i:02d}.png"
        h.write_text(ARK.format(nr=i + 1, ant=len(AVSNITT), tittel=html.escape(tittel),
                                punkter="".join(f"<p>{html.escape(p)}</p>" for p in punkter)))
        for forsøk in range(4):   # Chrome uten vindu feiler av og til (status 2) når vanlig Chrome er opptatt: prøv igjen
            r = subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars", "--window-size=1312,1080",
                                "--virtual-time-budget=4000", f"--screenshot={png}", h.as_uri()], capture_output=True)
            if r.returncode == 0: break
            time.sleep(3)
        else:
            raise SystemExit(f"lysark {i:02d} lot seg ikke lage: {r.stderr[-200:]!r}")
        ut = S / f"del/{i:02d}.mp4"
        # avataren kommer ofte tilbake et par sekunder lengre enn lyden: klipp ved lydens slutt pluss litt luft
        lengde = float(subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of",
                                       "csv=p=0", str(S / f"lyd/{i:02d}.mp3")], capture_output=True, text=True).stdout) + 0.35
        # avataren (720x1280) til venstre i 608x1080, lysarket til høyre; 0,35 s luft etter hvert avsnitt
        subprocess.run(["nice", FF, "-hide_banner", "-loglevel", "error", "-y", "-i", str(S / f"av/{i:02d}.mp4"), "-loop", "1", "-i", str(png),
                        "-filter_complex", "[0:v]scale=608:1080:force_original_aspect_ratio=increase,crop=608:1080,tpad=stop_mode=clone:stop_duration=0.35[a];"
                        "[1:v]scale=1312:1080[b];[a][b]hstack=inputs=2:shortest=1,fps=25,format=yuv420p[v];[0:a]apad=pad_dur=0.35,aresample=48000[l]",
                        "-map", "[v]", "-map", "[l]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "aac", "-b:a", "160k",
                        "-ac", "2", "-video_track_timescale", "12800", "-t", f"{lengde:.2f}", "-threads", "4", str(ut)], check=True)
        deler.append(ut); print("ok", ut.name, flush=True)
    (S / "del/liste.txt").write_text("".join(f"file '{d.name}'\n" for d in deler))
    subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(S / "del/liste.txt"),
                    "-c", "copy", "-movflags", "+faststart", str(S / "klone-video.mp4")], check=True)
    print("ferdig: klone-video.mp4")


if __name__ == "__main__":
    N = hent_nøkkel()
    if sys.argv[1] == "stemme": stemme(sys.argv[2])
    else: {"tts": tts, "avatar": avatar, "bygg": bygg}[sys.argv[1]]()
