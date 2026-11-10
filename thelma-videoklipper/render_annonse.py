#!/usr/bin/env python3
"""Render en annonse-plan rett til MP4 med ffmpeg — uten CapCut.

    <capcutapi>/.venv/bin/python render_annonse.py plan.json ut.mp4 [--fra 0 --til 12]
    <capcutapi>/.venv/bin/python render_annonse.py --demo   (venv: bygg_annonse trekker inn capcutapi)

Samme plan.json som bygg_annonse.py. A-rollen beskjæres til 9:16 (1080x1920),
b-rollen legges oppå i kuttene, teksting/statements/sluttkort brennes inn som
ASS-undertekster (libass), sluttkortet hektes på til slutt.
ffmpeg: miljøvariabelen FFMPEG, ellers ffmpeg i PATH (f.eks. npm-pakken ffmpeg-static).
ffmpeg-en må ha libass (subtitles/ass-filteret). Fontene leses fra macOS sin fontmappe.
"""

import json
import os
import pathlib
import shutil
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from bygg_annonse import (MAKS_TEGN, MAKS_TEGN_STOR, SLUTTKORT, bryt,   # noqa: E402
                          teksting_fra_ord)
from til_capcut import mål_fil                                        # noqa: E402

FFMPEG = os.environ.get("FFMPEG") or shutil.which("ffmpeg") or "ffmpeg"
FONT = "Arial"
# CapCut-størrelse -> piksler i 1920 høyt bilde (kalibrert mot draften)
PX = {7: 54, 12: 60, 14: 66, 16: 72, 18: 80, 22: 96}
# CapCut transform_y -> ASS-marginer (0 = midten, -1 = bunnen)
STIL = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Statement,{font},{stor},&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,6,3,2,90,90,{stat_v},1
Style: Teksting,{font},{liten},&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,4,2,2,90,90,{tekst_v},1
Style: Sluttkort,{font},{kort},&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,0,4,5,90,90,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def avbildning(biter):
    """Kildetid -> utstid når a-rollen består av bitene [[start, slutt], ...].

    Tid i en bortklippet pause lander på starten av neste bit.
    """
    def ut(t):
        løpt = 0.0
        for start, slutt in biter:
            if t < start:
                return løpt
            if t <= slutt:
                return løpt + (t - start)
            løpt += slutt - start
        return løpt
    return ut


def px(størrelse):
    return PX.get(størrelse, round(størrelse * 4.4))


def ass_tid(s):
    cs = int(round(s * 100))
    return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"


def hendelse(stil, start, slutt, tekst):
    tekst = tekst.replace("\n", "\\N")
    return f"Dialogue: 0,{ass_tid(start)},{ass_tid(slutt)},{stil},,0,0,0,,{tekst}"


def lag_ass(plan, total, kort_lengde, ut=lambda t: t):
    """Alle tekstene i planen som én ASS-fil. total = a-rollens lengde (etter klipp).

    Tidene i planen er kildetid; `ut` gjør dem om til utstid.
    """
    statements = plan.get("tekst", [])
    stor = px(statements[0].get("størrelse", 12)) if statements else 72
    # transform_y -0.6 = 60 % fra midten mot bunnen -> avstand fra bunnen
    stat_v = round(1920 * (1 - 0.6) / 2)   # 384 px fra bunnen (tekstblokk over)
    tekst_v = round(1920 * (1 - 0.82) / 2)  # 173 px fra bunnen
    kort = plan.get("sluttkort") or {}
    linjer = [STIL.format(font=FONT, stor=stor, liten=px(plan.get("tekststørrelse", 7)),
                          kort=px(kort.get("størrelse", 16)), stat_v=stat_v, tekst_v=tekst_v)]
    for t in statements:
        s = t.get("størrelse", 12)
        a, b = ut(t["start"]), min(ut(t["slutt"]), total)
        if b - a > 0.2:
            linjer.append(hendelse("Statement", a, b,
                                   bryt(t["tekst"], MAKS_TEGN_STOR if s >= 16 else MAKS_TEGN)))
    if plan.get("teksting"):
        for start, slutt, linje in teksting_fra_ord(pathlib.Path(plan["teksting"]).read_text()):
            a, b = ut(start), min(ut(slutt), total)
            if b - a > 0.2:
                linjer.append(hendelse("Teksting", a, b, linje))
    if kort:
        linjer.append(hendelse("Sluttkort", total, total + kort_lengde,
                               bryt(kort["tekst"], MAKS_TEGN_STOR)))
    return "\n".join(linjer) + "\n"


def zoomfilter(plan):
    """"zoom": [[start, slutt, faktor], ...] i utstid = hopp inn på ansiktet.

    "zoom_y": hvor i høyden ansiktet er (0 = toppen). Bare a-rollen zoomes.
    """
    if not plan.get("zoom"):
        return ""
    z = "1"
    for a, b, f in reversed(plan["zoom"]):
        z = f"if(between(in_time,{a},{b}),{f},{z})"
    y = plan.get("zoom_y", 0.35)
    return f",zoompan=z='{z}':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)*{y}':d=1:s=1080x1920:fps=30"


def filtergraf(plan, total, kort_fil, kort_lengde, ass, biter=None, ut=lambda t: t):
    """ffmpeg-inputs og filter_complex for planen.

    `biter` = [[start, slutt], ...] i kildetid som beholdes av a-rollen
    (pauser og omstarter klippes bort). Uten biter brukes 0..total.
    """
    inputs = ["-i", plan.get("aroll") or plan["lyd"]]
    biter = biter or [[0, total]]
    n_b = len(biter)
    if plan.get("aroll"):
        f = [f"[0:v]split={n_b}" + "".join(f"[s{j}v]" for j in range(n_b)),
             f"[0:a]asplit={n_b}" + "".join(f"[s{j}a]" for j in range(n_b))]
        deler = []
        for j, (start, slutt) in enumerate(biter):
            f.append(f"[s{j}v]trim={start}:{slutt},setpts=PTS-STARTPTS[p{j}v]")
            f.append(f"[s{j}a]atrim={start}:{slutt},asetpts=PTS-STARTPTS[p{j}a]")
            deler.append(f"[p{j}v][p{j}a]")
        f.append("".join(deler) + f"concat=n={len(biter)}:v=1:a=1[ar][aa]")
        # "crop_x": hvor i bredden du står (0 = venstre kant, 0.5 = midten)
        cx = plan.get("crop_x", 0.5)
        f.append(f"[ar]crop=ih*9/16:ih:(iw-ih*9/16)*{cx}:0,scale=1080:1920,setsar=1{zoomfilter(plan)}[v0]")
    else:
        # ren stemme: svart bunn, klippene i "kutt" fyller hele bildet
        f = [f"color=c=black:s=1080x1920:r=30:d={total}[v0]",
             f"[0:a]atrim=0:{total},asetpts=PTS-STARTPTS[aa]"]
    siste = "v0"
    for i, k in enumerate(plan.get("kutt", []), start=1):
        inputs += ["-i", k["fil"]]
        a, b = round(ut(k["start"]), 2), round(ut(k["slutt"]), 2)
        if b - a < 0.5:
            continue
        f.append(f"[{i}:v]trim=0:{b - a},setpts=PTS-STARTPTS+{a}/TB,"
                 f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1[b{i}]")
        f.append(f"[{siste}][b{i}]overlay=eof_action=pass:enable='between(t,{a},{b})'[v{i}]")
        siste = f"v{i}"
    n = len(plan.get("kutt", [])) + 1
    if kort_fil:
        inputs += ["-i", kort_fil]
        f.append(f"[{n}:v]trim=0:{kort_lengde},setpts=PTS-STARTPTS,"
                 f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1[k]")
        f.append(f"[{siste}][k]concat=n=2:v=1:a=0[vc]")
        siste = "vc"
    f.append(f"[{siste}]ass='{ass}':fontsdir=/System/Library/Fonts/Supplemental[vut]")
    slutt = total + kort_lengde
    musikk = plan.get("musikk")
    if musikk:
        inputs += ["-stream_loop", "-1", "-i", musikk["fil"]]
        m = inputs.count("-i") - 1
        f.append(f"[{m}:a]atrim=0:{slutt},asetpts=PTS-STARTPTS,volume={musikk.get('volum', 0.12)},"
                 f"afade=t=in:d=1,afade=t=out:st={slutt - 2}:d=2[mus]")
        f.append(f"[aa]apad=whole_dur={slutt}[tale]")
        f.append(f"[tale][mus]amix=inputs=2:duration=first:normalize=0[aut]")
    else:
        f.append(f"[aa]apad=whole_dur={slutt}[aut]")
    return inputs, ";".join(f)


def render(plan, ut, fra=None, til=None):
    aroll = plan.get("aroll") or plan["lyd"]
    lengde = mål_fil(aroll)[0] / 1e6
    # "biter": [[start, slutt], ...] i kildetid som beholdes (klipper bort
    # pauser/omstarter). Ellers 0..aroll_slutt.
    biter = plan.get("biter") or [[0, min(lengde, plan.get("aroll_slutt", 1e9))]]
    ut_tid = avbildning(biter)
    total = sum(b - a for a, b in biter)
    kort = plan.get("sluttkort")
    kort_fil = kort.get("fil", str(SLUTTKORT)) if kort else None
    kort_lengde = min(kort.get("lengde", 3), mål_fil(kort_fil)[0] / 1e6) if kort else 0
    # "ass_fil": ferdig tekstlag fra kinetisk.py i stedet for standardteksten
    ass = pathlib.Path(plan["ass_fil"]) if plan.get("ass_fil") else pathlib.Path(ut).with_suffix(".ass")
    if not plan.get("ass_fil"):
        ass.write_text(lag_ass(plan, total, kort_lengde, ut_tid))
    inputs, graf = filtergraf(plan, total, kort_fil, kort_lengde,
                              str(ass).replace(":", "\\:"), biter, ut_tid)
    kutt = ["-ss", str(fra), "-to", str(til)] if fra is not None else []
    cmd = [str(FFMPEG), "-y", "-hide_banner", "-loglevel", "error", *inputs,
           "-filter_complex", graf, "-map", "[vut]", "-map", "[aut]",
           *kutt, "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(ut)]
    subprocess.run(cmd, check=True)
    return ut, total + kort_lengde


def demo():
    plan = {"aroll": "/x/a.mp4", "kutt": [{"fil": "/x/b.mp4", "start": 4.0, "slutt": 8.5}],
            "tekst": [{"tekst": "Dobla konverteringen", "start": 1, "slutt": 5, "størrelse": 18}],
            "sluttkort": {"tekst": "Trykk på lenken og meld deg på", "lengde": 3.5}}
    a = lag_ass(plan, 60.0, 3.5)
    assert "Style: Statement,Arial,80," in a, a
    assert "Dialogue: 0,0:00:01.00,0:00:05.00,Statement,,0,0,0,,Dobla\\Nkonverteringen" in a, a
    assert "0:01:00.00,0:01:03.50,Sluttkort" in a, a
    inputs, graf = filtergraf(plan, 60.0, "/x/k.mp4", 3.5, "/x/u.ass")
    assert inputs == ["-i", "/x/a.mp4", "-i", "/x/b.mp4", "-i", "/x/k.mp4"], inputs
    assert "between(t,4.0,8.5)" in graf and "concat=n=2" in graf and "apad=whole_dur=63.5" in graf, graf
    assert ass_tid(3661.234) == "1:01:01.23"

    # klipp: bit 0-10 og 20-30 -> kildetid 25 = utstid 15, tid i pausen = 10
    u = avbildning([[0, 10], [20, 30]])
    assert u(5) == 5 and u(25) == 15 and u(15) == 10 and u(40) == 20, [u(t) for t in (5, 25, 15, 40)]
    a2 = lag_ass({"tekst": [{"tekst": "Hei", "start": 22, "slutt": 28, "størrelse": 18}]}, 20, 0, u)
    assert "0:00:12.00,0:00:18.00,Statement" in a2, a2
    _, g2 = filtergraf({"aroll": "/x/a.mp4", "kutt": [{"fil": "/x/b.mp4", "start": 22, "slutt": 26}]},
                       20, None, 0, "/x/u.ass", [[0, 10], [20, 30]], u)
    assert "trim=20:30" in g2 and "concat=n=2:v=1:a=1" in g2 and "between(t,12.0,16.0)" in g2, g2
    assert "[0:v]split=2[s0v][s1v]" in g2, g2
    _, g5 = filtergraf({"lyd": "/x/s.m4a", "kutt": [{"fil": "/x/b.mp4", "start": 0, "slutt": 5}]}, 20, None, 0, "/x/u.ass")
    assert "color=c=black:s=1080x1920" in g5 and "[0:a]atrim=0:20" in g5 and "between(t,0,5)" in g5, g5
    _, g4 = filtergraf({"aroll": "/x/a.mp4", "crop_x": 0.44}, 20, None, 0, "/x/u.ass")
    assert "crop=ih*9/16:ih:(iw-ih*9/16)*0.44:0" in g4, g4
    i3, g3 = filtergraf({"aroll": "/x/a.mp4", "musikk": {"fil": "/x/m.mp3", "volum": 0.1}}, 20, None, 0, "/x/u.ass")
    assert i3[-1] == "/x/m.mp3" and "-stream_loop" in i3 and "[1:a]atrim=0:20" in g3 and "amix" in g3, (i3, g3)
    _, g6 = filtergraf({"aroll": "/x/a.mp4", "zoom": [[1, 2, 1.2]], "zoom_y": 0.3}, 20, None, 0, "/x/u.ass")
    assert "zoompan=z='if(between(in_time,1,2),1.2,1)'" in g6 and "*0.3'" in g6, g6
    print("demo ok")


if __name__ == "__main__":
    if "--demo" in sys.argv:
        demo()
    elif len(sys.argv) >= 3:
        a = sys.argv
        fra = float(a[a.index("--fra") + 1]) if "--fra" in a else None
        til = float(a[a.index("--til") + 1]) if "--til" in a else None
        plan = json.loads(pathlib.Path(a[1]).read_text())
        ut, lengde = render(plan, a[2], fra, til)
        print(f"{lengde:.1f} sek -> {ut}")
    else:
        sys.exit(__doc__)
