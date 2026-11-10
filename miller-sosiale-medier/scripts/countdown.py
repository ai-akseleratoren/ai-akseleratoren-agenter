#!/usr/bin/env python3
"""Nedtellingsbilde («47 DAGER til …») over et foto.

Dagene regnes fra --date (dagen posten PUBLISERES) til --target, så tallet stemmer
for plassen i køen, ikke for dagen du lager bildet.

    python3 scripts/countdown.py assets/foto.jpg --date 2026-11-02 --target 2026-12-01 \
        --line "TIL DØRENE ÅPNER" --footer "DITT FIRMA" --out assets/countdown/2026-11-02.jpg
    (legg til --story for 9:16 i stedet for 4:5)

Font: --font, ellers env FONT, ellers en vanlig systemfont. Krever Pillow.
"""
import argparse
import datetime as dt
import os
import pathlib

from PIL import Image, ImageDraw, ImageFont, ImageOps

FONTER = [os.environ.get("FONT", ""), "/System/Library/Fonts/Supplemental/Futura.ttc",
          "/System/Library/Fonts/Helvetica.ttc", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
          "C:/Windows/Fonts/arialbd.ttf"]


def font(sti, størrelse):
    for f in [sti] + FONTER:
        if f and pathlib.Path(f).exists():
            return ImageFont.truetype(f, størrelse)
    return ImageFont.load_default(størrelse)


def dager(publisering, mål):
    return (mål - publisering).days


def render(photo, date, target, out, story=False, line="", footer="", fontsti="", ordet="DAGER"):
    n = dager(date, target)
    size = (1080, 1920) if story else (1080, 1350)
    im = ImageOps.fit(Image.open(photo).convert("RGB"), size)
    # mørk gradient over nedre halvdel, så hvit tekst leses også på lyse bilder
    shade = Image.new("L", (1, size[1]))
    for y in range(size[1]):
        shade.putpixel((0, y), int(170 * max(0, (y / size[1] - 0.4) / 0.6)))
    im.paste(Image.new("RGB", size, "black"), mask=shade.resize(size))
    d = ImageDraw.Draw(im)
    w, h = size
    base = h - (560 if story else 470)
    d.text((w // 2, base), str(n), font=font(fontsti, 330 if story else 300), fill="white", anchor="ms")
    d.text((w // 2, base + 80), ordet, font=font(fontsti, 64), fill="white", anchor="ms")
    if line:
        d.text((w // 2, base + 150), line, font=font(fontsti, 36), fill="white", anchor="ms")
    if footer:
        d.text((w // 2, h - (220 if story else 60)), footer, font=font(fontsti, 36), fill="white", anchor="ms")
    pathlib.Path(out).parent.mkdir(parents=True, exist_ok=True)
    im.save(out, "JPEG", quality=90)
    return n


if __name__ == "__main__":
    assert dager(dt.date(2026, 10, 12), dt.date(2026, 11, 28)) == 47  # sjekk av datoregningen
    p = argparse.ArgumentParser()
    p.add_argument("photo")
    p.add_argument("--date", required=True, type=dt.date.fromisoformat, help="publiseringsdato")
    p.add_argument("--target", required=True, type=dt.date.fromisoformat, help="dagen det telles ned til")
    p.add_argument("--out", required=True)
    p.add_argument("--story", action="store_true", help="9:16 i stedet for 4:5")
    p.add_argument("--line", default="")
    p.add_argument("--footer", default="")
    p.add_argument("--word", default="DAGER")
    p.add_argument("--font", default="")
    a = p.parse_args()
    print(render(a.photo, a.date, a.target, a.out, a.story, a.line, a.footer, a.font, a.word), "dager")
