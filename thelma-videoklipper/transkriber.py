#!/usr/bin/env python3
"""Transkriber en lydfil med fal-ai/whisper og skriv hvert ord med tidspunkt.

    python3 transkriber.py stemme.m4a            # skriver til stemme.txt (norsk)
    python3 transkriber.py stemme.m4a --sprak en # engelsk
    python3 transkriber.py --demo

Video må først bli lyd. På Mac uten ffmpeg:
    afconvert -f m4af -d aac -b 96000 film.mp4 stemme.m4a
Med ffmpeg: ffmpeg -i film.mp4 -vn -c:a aac -b:a 96k stemme.m4a
"""

import json
import pathlib
import sys
import time
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from video import hent_nøkkel, kall  # noqa: E402


def last_opp(sti, nøkkel):
    svar = kall("https://rest.alpha.fal.ai/storage/upload/initiate", nøkkel,
                {"content_type": "audio/mp4", "file_name": pathlib.Path(sti).name})
    req = urllib.request.Request(svar["upload_url"], data=pathlib.Path(sti).read_bytes(),
                                 method="PUT", headers={"Content-Type": "audio/mp4"})
    urllib.request.urlopen(req).read()
    return svar["file_url"]


def transkriber(sti, nøkkel, språk="no"):
    url = last_opp(sti, nøkkel)
    # wizper gir bare segmenter på 15-30 sek; whisper gir ord, som kuttene trenger
    jobb = kall("https://queue.fal.run/fal-ai/whisper", nøkkel,
                {"audio_url": url, "task": "transcribe", "language": språk,
                 "chunk_level": "word"})
    while True:
        status = kall(jobb["status_url"], nøkkel)
        if status["status"] == "COMPLETED":
            return kall(jobb["response_url"], nøkkel)
        time.sleep(3)


def formater(svar):
    """Ett ord per token med starttid: «Jeg[1.5] holdt[3.8] ...», linjeskift ved punktum."""
    ut, linje = [], []
    for c in svar["chunks"]:
        ord_ = c["text"].strip()
        linje.append(f"{ord_}[{c['timestamp'][0]:.1f}]")
        if ord_.endswith((".", "?", "!")):
            ut.append(" ".join(linje)); linje = []
    if linje:
        ut.append(" ".join(linje))
    return "\n".join(ut)


def demo():
    ut = formater({"chunks": [{"timestamp": [0.0, 0.4], "text": " Hei "},
                              {"timestamp": [0.4, 1.0], "text": "du."},
                              {"timestamp": [2.5, 3.0], "text": "Så"}]})
    assert ut == "Hei[0.0] du.[0.4]\nSå[2.5]", ut
    print("demo ok")


if __name__ == "__main__":
    if "--demo" in sys.argv:
        demo()
    elif len(sys.argv) >= 2:
        a = sys.argv
        språk = a[a.index("--sprak") + 1] if "--sprak" in a else "no"
        sti = pathlib.Path(a[1])
        svar = transkriber(sti, hent_nøkkel(), språk)
        ut = sti.with_suffix(".txt")
        ut.write_text(formater(svar) + "\n")
        print(formater(svar))
        print(f"-> {ut}")
    else:
        sys.exit(__doc__)
