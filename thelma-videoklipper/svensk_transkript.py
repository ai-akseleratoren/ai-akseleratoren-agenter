#!/usr/bin/env python3
"""Lag et svensk tidsatt transkript av det norske, setning for setning.

    python3 svensk_transkript.py transkript.txt svensk.txt > transkript-se.txt
    python3 svensk_transkript.py --demo

`svensk.txt` har én oversatt setning per linje, like mange som det norske
transkriptet har setninger (ord som slutter på . ? !). De svenske ordene
fordeles jevnt over tida den norske setningen tar — lyden er fortsatt norsk,
det er tekstingen som er svensk.
"""

import pathlib
import re
import sys

ORD = re.compile(r"(\S+)\[(\d+\.\d+)\]")


def setninger(tekst):
    """[(start, slutt)] for hver setning i «ord[tid]»-formatet."""
    ut, start = [], None
    for o, t in ORD.findall(tekst):
        t = float(t)
        if start is None:
            start = t
        if o.endswith((".", "?", "!")):
            ut.append((start, t)); start = None
    if start is not None:
        ut.append((start, t))
    return ut


def oversett(norsk, svensk):
    tider = setninger(norsk)
    linjer = [l.strip() for l in svensk.strip().splitlines() if l.strip()]
    if len(tider) != len(linjer):
        sys.exit(f"{len(tider)} norske setninger, {len(linjer)} svenske linjer — må være like mange")
    ut = []
    for (start, slutt), linje in zip(tider, linjer):
        ord_ = linje.split()
        steg = (slutt - start) / max(1, len(ord_) - 1) if len(ord_) > 1 else 0
        ut.append(" ".join(f"{o}[{start + i * steg:.1f}]" for i, o in enumerate(ord_)))
    return "\n".join(ut) + "\n"


def demo():
    no = "Hei[1.0] du.[2.0]\nSå[3.0] går[3.5] vi[4.0] hjem.[5.0]\n"
    sv = "Hej du.\nSen går vi hem igen.\n"
    ut = oversett(no, sv)
    assert ut == "Hej[1.0] du.[2.0]\nSen[3.0] går[3.5] vi[4.0] hem[4.5] igen.[5.0]\n", ut
    assert setninger("Ett[1.0] ord[2.0]") == [(1.0, 2.0)], "uten punktum til slutt"
    print("demo ok")


if __name__ == "__main__":
    if "--demo" in sys.argv:
        demo()
    elif len(sys.argv) == 3:
        sys.stdout.write(oversett(pathlib.Path(sys.argv[1]).read_text(),
                                  pathlib.Path(sys.argv[2]).read_text()))
    else:
        sys.exit(__doc__)
