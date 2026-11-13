"""Finner pauser og «eh» mellom ordene i et opptak, og gir bitene som skal beholdes.

    /usr/bin/python3 stram.py film.mp4 transkript.txt [--min 0.35]
Ordene har bare starttid (transkriber.py). Slutten på hvert ord finnes i lyden: første dal i lydnivået etter at
ordet har vart sin minste lengde. Alt fra den dalen til 0,09 s før neste ord klippes når det er over --min sekunder.
Finnes det ingen dal (ord og «eh» henger sammen), klippes det ikke.
"""
import re, subprocess, sys, os
import shutil
import numpy as np
FF = os.environ.get("FFMPEG") or shutil.which("ffmpeg") or "ffmpeg"
SR, RAMME = 16000, 0.02


def nivå(fil):
    raw = subprocess.run([FF, "-loglevel", "error", "-i", fil, "-vn", "-af", "highpass=f=180,lowpass=f=3800", "-ac", "1",
                          "-ar", str(SR), "-f", "s16le", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768
    n = int(SR * RAMME); x = x[: len(x) // n * n].reshape(-1, n)
    return 20 * np.log10(np.sqrt((x ** 2).mean(axis=1)) + 1e-6)


def ordene(tekst):
    return [(float(t), o) for o, t in re.findall(r"(\S+?)\[(\d+(?:\.\d+)?)\]", tekst.replace("​", ""))]


def kutt(db, ord_, minst=0.35, slutt=None):
    tale = np.percentile(db, 80); dal = tale - 12           # en dal er 12 dB under vanlig talenivå
    i = lambda t: int(t / RAMME)
    ut = []
    for (t0, o), (t1, _) in zip(ord_, ord_[1:] + [(slutt or len(db) * RAMME, "")]):
        bokst = len(re.sub(r"\W", "", o))
        tidligst = t0 + min(0.7, max(0.16, 0.05 * bokst + 0.08))   # ordet varer minst så lenge
        if t1 - tidligst < minst: continue
        seg = db[i(tidligst): i(t1 - 0.09)]
        lave = np.where(seg < dal)[0]
        if len(lave) == 0: continue                               # ingen dal: ord og «eh» henger sammen, la stå
        a = tidligst + lave[0] * RAMME + 0.04                     # litt hale på ordet
        b = t1 - 0.09
        if b - a >= minst - 0.1:
            lyd = float((seg[lave[0]:] >= dal).mean())            # andel av det som klippes som IKKE er stille
            ut.append((round(a, 2), round(b, 2), o, "eh/lyd" if lyd > 0.45 else "pause", round(lyd, 2)))
    return ut


def biter(klipp, lengde):
    ut, t = [], 0.0
    for a, b, *_ in klipp:
        ut.append([round(t, 2), a]); t = b
    ut.append([round(t, 2), round(lengde, 2)])
    return ut


def myk_inn(db, biter, maks=0.15):
    """Flytter starten av hver bit bakover til nærmeste dal (høyst `maks` s), så første lyd i ordet ikke klippes.
    Whisper setter ofte ordstarten litt for sent. Finnes det ingen dal innen `maks`, står starten urørt:
    da er det trolig en «eh» som går rett over i ordet."""
    dal = np.percentile(db, 80) - 12
    ut = [list(biter[0])]
    for a, b in biter[1:]:
        i = int(a / RAMME); j = i
        while j > 0 and db[j] >= dal and (i - j) * RAMME < maks: j -= 1
        ny = round(j * RAMME + 0.02, 2) if db[j] < dal else a
        ut.append([max(ny, ut[-1][1] + 0.1), b])
    return ut


def demo():
    db = np.full(200, -20.0); db[100:110] = -50.0     # tale, en dal ved 2,0-2,2 s, tale igjen
    assert myk_inn(db, [[0, 1.5], [2.3, 4.0]]) == [[0, 1.5], [2.2, 4.0]], myk_inn(db, [[0, 1.5], [2.3, 4.0]])
    assert myk_inn(np.full(200, -20.0), [[0, 1.5], [2.3, 4.0]]) == [[0, 1.5], [2.3, 4.0]]   # ingen dal: urørt
    stille = np.full(200, -20.0); stille[100:146] = -50.0   # tale, stille fra 2,0 til 2,9 s, neste ord 3,0
    k = kutt(stille, [(0.0, "hei"), (3.0, "igjen")], 0.35)
    assert len(k) == 1 and abs(k[0][0] - 2.04) < 0.03 and abs(k[0][1] - 2.91) < 0.01 and k[0][3] == "pause", k
    assert kutt(db, [(0.0, "hei"), (3.0, "igjen")], 0.35)[0][3] == "eh/lyd"    # kort dal, så lyd fram til neste ord
    print("selvtest ok")


if __name__ == "__main__" and len(sys.argv) < 3:
    demo()
elif __name__ == "__main__":
    fil, tx = sys.argv[1], sys.argv[2]
    minst = float(sys.argv[sys.argv.index("--min") + 1]) if "--min" in sys.argv else 0.35
    db = nivå(fil); k = kutt(db, ordene(open(tx).read()), minst)
    for a, b, o, hva, lyd in k: print(f"  klipp {a:6.2f}-{b:6.2f} ({b - a:.2f}s) etter «{o}»  {hva} {lyd}")
    print("sum klippet:", round(sum(b - a for a, b, *_ in k), 1), "s av", round(len(db) * RAMME, 1))
    print("biter =", biter(k, len(db) * RAMME))
