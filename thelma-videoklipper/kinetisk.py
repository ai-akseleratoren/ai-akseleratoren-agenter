#!/usr/bin/env python3
"""Levende tekst til talking-head-annonser: ferdig ASS-fil som render_annonse.py brenner inn.

Tre stiler (laget fordi standardteksten var for liten og for stille):
  stor   kjempetekst ord for ord som hopper rundt i bildet (Impact), full teksting i seg selv
  lapp   håndskrevet huskelapp der oppgaver hukes av (Marker Felt) + teksting
  tv     golf-TV-grafikk: resultattavle med teller + fargebokser som glir inn (Arial Black)

Planen får  "ass_fil": sti  og  "zoom": [[start, slutt, faktor], ...]  (se render_annonse.py).
Aldri versaler. Soner er per film: hold teksten unna munnen.

    python3 kinetisk.py --demo
"""

import re
import sys

ORD = re.compile(r"(\S+?)\[(\d+(?:\.\d+)?)\]")
GUL, HVIT, SVART, RØD = "&H0000E6FF&", "&H00FFFFFF&", "&H00000000&", "&H002B2BE8&"
BLEK, BLEKK, GRØNN, GRØNN_LYS = "&H00C4F4FF&", "&H00402A16&", "&H00264A10&", "&H0042C87A&"
HODE = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Stor,Impact,200,&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,0,0,0,0,100,100,0,0,1,11,6,5,40,40,0,1
Style: Hand,Marker Felt,98,&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,6,3,5,40,40,0,1
Style: Lapp,Marker Felt,78,&H00402A16,&H00402A16,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,0,0,0,7,0,0,0,1
Style: Boks,Arial Black,84,&H00000000,&H00000000,&H0000E6FF,&H00000000,0,0,0,0,100,100,0,0,3,20,0,5,40,40,0,1
Style: Tekst,Arial Black,72,&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,0,0,0,0,100,100,0,0,1,5,2,5,40,40,0,1
Style: Tavle,Arial Black,54,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,0,0,0,5,0,0,0,1
Style: Flate,Arial,10,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,0,0,0,7,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def tid(s):
    cs = int(round(s * 100))
    return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"


def linje(a, b, stil, tekst, lag=1):
    return f"Dialogue: {lag},{tid(a)},{tid(b)},{stil},,0,0,0,,{tekst}"


def ordene(transkript):
    """[(tid, ord)] fra transkriber.py-formatet. Blanke \\u200b-tegn faller bort."""
    return [(float(t), o) for o, t in ORD.findall(transkript.replace("​", ""))]


def grupper(ord_, maks_ord=3, maks_tegn=15, slutt=1e9):
    """Del tale i små støt: nytt støt ved tegnsetting, tre ord eller femten tegn."""
    støt, bit = [], []
    for t, o in ord_:
        if bit and (len(bit) >= maks_ord or len(" ".join(x for _, x in bit) + o) >= maks_tegn
                    or bit[-1][1].endswith((".", ",", "?", "!"))):
            støt.append(bit); bit = []
        bit.append((t, o))
    if bit:
        støt.append(bit)
    ut = []
    for i, b in enumerate(støt):
        if b[0][0] >= slutt:
            break
        neste = støt[i + 1][0][0] if i + 1 < len(støt) else b[-1][0] + 1.0
        ut.append((b[0][0], min(neste, b[-1][0] + 1.3, slutt), [o for _, o in b]))
    return ut


def stable(ord_, maks=11):
    """Stable ordene i linjer på maks tegn. Lengste linje avgjør skriftstørrelsen."""
    linjer, nå = [], ""
    for o in ord_:
        if nå and len(nå) + 1 + len(o) > maks:
            linjer.append(nå); nå = o
        else:
            nå = f"{nå} {o}".strip()
    return linjer + [nå] if nå else linjer


def størrelse(lengste, maks=235, bredde=980, snitt=0.47):
    return min(maks, int(bredde / (max(lengste, 1) * snitt)))


def stor(ord_, soner, nøkkel=(), fra_til=None, maks=260, slutt=1e9):
    """Kjempetekst. soner = [(t0, t1, [(x, y), ...]), ...]; plass går i ring innen sonen."""
    ut, teller = [], 0
    for a, b, ordliste in grupper(ord_, slutt=slutt):
        if fra_til and not (fra_til[0] <= a < fra_til[1]):
            continue
        sone = next((s for s in soner if s[0] <= a < s[1]), None)
        if not sone:
            continue
        x, y = sone[2][teller % len(sone[2])]
        teller += 1
        linjer = stable([o.rstrip(".,?!") for o in ordliste])
        # hver linje fyller bredden: nøkkelord størst, fyllord mindre (plakatstabel)
        mål = []
        for l in linjer:
            har_nøkkel = any(w.lower() in nøkkel for w in l.split())
            mål.append((l, størrelse(len(l), maks if har_nøkkel else int(maks * 0.72))))
        bredest = max(st * len(l) * 0.47 for l, st in mål)
        høyde = sum(st * 1.12 for _, st in mål)
        x = max(bredest / 2 + 40, min(x, 1040 - bredest / 2))
        y = max(y, 130 + høyde / 2) if y < 960 else min(y, 1800 - høyde / 2)
        vri = (-3, 2, -2, 3)[teller % 4]
        tegnet = []
        for l, st in mål:
            ord_i = [f"{{\\c{GUL}}}{w}{{\\c{HVIT}}}" if w.lower() in nøkkel else w for w in l.split()]
            tegnet.append(f"{{\\fs{st}}}" + " ".join(ord_i))
        tag = (f"{{\\an5\\pos({x:.0f},{y:.0f})\\frz{vri}\\fscx128\\fscy128"
               f"\\t(0,90,\\fscx100\\fscy100)}}")
        ut.append(linje(a, b, "Stor", tag + "\\N".join(tegnet), 3))
    return ut


def stempel(a, b, tekst, x, y, s=170, farge=GUL, vri=-4, stil="Stor"):
    """Enkelt stort utsagn med pop."""
    tag = (f"{{\\an5\\pos({x},{y})\\fs{s}\\frz{vri}\\c{farge}\\fscx140\\fscy140"
           f"\\t(0,110,\\fscx100\\fscy100)}}")
    return linje(a, b, stil, tag + tekst.replace("\n", "\\N"), 4)


def teksting(ord_, a0=0, b0=1e9, x=540, y=1560, stil="Hand", maks_ord=3, maks_tegn=18, slutt=1e9):
    ut = []
    for a, b, o in grupper(ord_, maks_ord, maks_tegn, slutt):
        if a0 <= a < b0:
            ut.append(linje(a, b, stil, f"{{\\an5\\pos({x},{y})}}" + " ".join(o), 2))
    return ut


def hake(x, y):
    return f"{{\\an7\\pos({x},{y})\\p1\\c{GRØNN}\\bord0\\shad0}}m 0 36 l 14 26 l 28 50 l 66 0 l 78 10 l 30 78 l 0 36{{\\p0}}"


def kryss(x, y):
    return (f"{{\\an7\\pos({x},{y})\\p1\\c{RØD}\\bord0\\shad0}}m 0 10 l 10 0 l 38 28 l 66 0 l 76 10 l 48 38 "
            f"l 76 66 l 66 76 l 38 48 l 10 76 l 0 66 l 28 38 l 0 10{{\\p0}}")


def lapp(a, b, tittel, rader, x=50, y=270, bredde=800, vri=-2, fs=96, kolonner=1, hake_x=92):
    """Huskelapp. rader = [(t, tekst, 'hake'|'kryss'|None)]; rad dukker opp ved t."""
    rad_h, topp = int(fs * 1.16), int(fs * 1.5)
    rekker = (len(rader) + kolonner - 1) // kolonner
    høyde = topp + 30 + rad_h * rekker
    org = f"\\org({x + bredde // 2},{y + høyde // 2})\\frz{vri}"
    flate = f"m 0 0 l {bredde} 0 l {bredde} {høyde} l 0 {høyde}"
    ut = [linje(a, b, "Flate", f"{{\\an7\\pos({x + 12},{y + 14}){org}\\p1\\c{SVART}\\alpha&HB0&}}{flate}{{\\p0}}", 5),
          linje(a, b, "Flate", f"{{\\an7\\pos({x},{y}){org}\\p1\\c{BLEK}}}{flate}{{\\p0}}", 6),
          linje(a, b, "Lapp", f"{{\\an7\\pos({x + 34},{y + 24}){org}\\fs{fs}\\c{RØD}}}{tittel}", 7)]
    kol_b = (bredde - 40) // kolonner
    for i, (t, tekst, merke) in enumerate(rader):
        rx = x + 34 + kol_b * (i % kolonner)
        ry = y + topp + rad_h * (i // kolonner)
        ut.append(linje(t, b, "Lapp", f"{{\\an7\\pos({rx},{ry}){org}\\fs{fs}\\fad(120,0)}}{tekst}", 7))
        if merke:
            tegn = hake if merke == "hake" else kryss
            mx = rx + kol_b - hake_x
            ut.append(linje(t + 0.35, b, "Flate", tegn(mx, ry + 6).replace(
                "\\p1", org + "\\fscx150\\fscy150\\t(0,120,\\fscx110\\fscy110)\\p1", 1), 8))
    return ut


def tavle(a, b, etikett, verdi, y=240, x=50, bredde=980, pop=True):
    """Resultattavle øverst, som på golf-TV: liten etikett, stor verdi under."""
    flate = f"m 0 0 l {bredde} 0 l {bredde} 210 l 0 210"
    ut = [linje(a, b, "Flate", f"{{\\an7\\pos({x},{y})\\p1\\c{GRØNN}\\alpha&H10&}}{flate}{{\\p0}}", 5),
          linje(a, b, "Flate", f"{{\\an7\\pos({x},{y + 210})\\p1\\c{GUL}}}m 0 0 l {bredde} 0 l {bredde} 12 l 0 12{{\\p0}}", 5),
          linje(a, b, "Tavle", f"{{\\an4\\pos({x + 34},{y + 56})}}{etikett}", 6)]
    s = "\\fscx130\\fscy130\\t(0,160,\\fscx100\\fscy100)" if pop else ""
    ut.append(linje(a, b, "Tavle", f"{{\\an4\\pos({x + 34},{y + 146})\\fs104\\c{GUL}{s}}}{verdi}", 6))
    return ut


def boks(a, b, tekst, x, y, side=1, farge=GUL, ink=SVART, s=116, vri=-2):
    """Fargeboks som glir inn fra siden (side -1 = venstre, 1 = høyre)."""
    start = x + side * 1100
    tag = (f"{{\\an5\\move({start},{y},{x},{y},0,170)\\frz{vri}\\fs{s}\\c{ink}\\3c{farge}}}")
    return linje(a, b, "Boks", tag + tekst.replace("\n", "\\N"), 4)


def sluttkort(a, b, tekst, stil="Stor", s=150):
    tag = f"{{\\an5\\pos(540,900)\\fs{s}\\fscx125\\fscy125\\t(0,120,\\fscx100\\fscy100)}}"
    return linje(a, b, stil, tag + tekst.replace("\n", "\\N"), 5)


def skriv(sti, linjer):
    open(sti, "w", encoding="utf-8").write(HODE + "\n".join(linjer) + "\n")


def demo():
    o = ordene("Det[0.0] er[0.1] golfsvinget,[0.5] mitt.[1.0]\n​[7.0]\nMen[14.6]")
    assert o[0] == (0.0, "Det") and o[-1] == (14.6, "Men") and len(o) == 5, o
    g = grupper(o)
    assert g[0][2] == ["Det", "er"] and g[1][2] == ["golfsvinget,"], g
    gs = grupper(o, slutt=1.2)
    assert gs[-1] == (1.0, 1.2, ['mitt.']), gs
    assert stable(["kundeservice", "og", "mer"]) == ["kundeservice", "og mer"]
    assert størrelse(20) < størrelse(5) <= 235
    a = "\n".join(stor(o, [(0, 2, [(540, 300)])], nøkkel={"golfsvinget"}))
    assert "\\pos(540,300)" in a and GUL in a and "Men" not in a, a
    assert tid(61.5) == "0:01:01.50"
    r = lapp(0, 5, "Tittel", [(1, "Mailen", "hake")])
    assert len(r) == 5 and "\\p1" in r[-1], r
    print("demo ok")


if __name__ == "__main__":
    demo() if "--demo" in sys.argv else sys.exit(__doc__)
