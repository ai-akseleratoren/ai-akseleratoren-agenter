#!/usr/bin/env python3
"""Lag videoklipp med MiniMax H3 via fal.ai.

Tørrkjøring som standard — ingenting koster penger før du sender --send.

    python3 video.py prompter.txt                 # viser hva som ville blitt kjørt
    python3 video.py prompter.txt --send          # genererer og laster ned
    python3 video.py --prompt "en tom gate" --send
    python3 video.py --demo                       # selvtest, ingen nettverk

Promptfila: én prompt per blokk, blokker skilt med en linje med bare ---.
Linjer som starter med # er kommentarer.

Krever FAL_KEY i .env (hentes fra fal.ai/dashboard/keys).
"""

import argparse
import json
import os
import pathlib
import sys
import time
import urllib.error
import urllib.request

MODEL = "minimax/h3/text-to-video"
QUEUE = "https://queue.fal.run"
PRIS = {"480P": 0.05, "768P": 0.06, "2K": 0.13, "4K": 0.16}


def les_prompter(tekst):
    """Del en promptfil i enkeltprompter. Kommentarer og tomme blokker faller ut."""
    blokker = []
    for rå in tekst.split("\n---"):
        linjer = [l for l in rå.strip().splitlines() if not l.lstrip().startswith("#")]
        blokk = "\n".join(linjer).strip()
        if blokk:
            blokker.append(blokk)
    return blokker


def hent_nøkkel():
    nøkkel = os.environ.get("FAL_KEY")
    if nøkkel:
        return nøkkel
    for mappe in [pathlib.Path.cwd(), *pathlib.Path.cwd().parents]:
        env = mappe / ".env"
        if env.exists():
            for linje in env.read_text().splitlines():
                if linje.startswith("FAL_KEY="):
                    return linje.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("Fant ikke FAL_KEY. Legg FAL_KEY=... i .env, eller sett den i miljøet.")


def kall(url, nøkkel, data=None, forsøk=4):
    # fal svarer tidvis 403 eller 429 midt i en serie selv med penger på konto.
    # Det går over av seg selv — prøv igjen før du gir opp klippet.
    for n in range(forsøk):
        req = urllib.request.Request(url, method="POST" if data else "GET")
        req.add_header("Authorization", f"Key {nøkkel}")
        if data:
            req.add_header("Content-Type", "application/json")
            req.data = json.dumps(data).encode()
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code not in (403, 429, 500, 502, 503) or n == forsøk - 1:
                raise RuntimeError(f"{e.code}: {e.read()[:200].decode()}") from None
            time.sleep(20 * (n + 1))


def generer(prompt, nøkkel, args):
    svar = kall(f"{QUEUE}/{MODEL}", nøkkel, {
        "prompt": prompt,
        "duration": args.sekunder,
        "resolution": args.oppløsning,
        "aspect_ratio": args.format,
    })
    # fal svarer med ferdige URL-er — bygg dem aldri selv, stien til status
    # er ikke den samme som stien til modellen.
    req_id = svar["request_id"]
    for _ in range(120):  # opptil 20 min
        time.sleep(10)
        status = kall(svar["status_url"], nøkkel)
        if status.get("status") == "COMPLETED":
            return kall(svar["response_url"], nøkkel)["video"]["url"]
        if status.get("status") not in ("IN_QUEUE", "IN_PROGRESS"):
            raise RuntimeError(f"{req_id}: {status}")
    raise TimeoutError(f"{req_id} ble ikke ferdig på 20 minutter")


def demo():
    tekst = "# kommentar\nEn tom gate\n---\n\n---\nEt lyst rom\n# nok en kommentar\n"
    assert les_prompter(tekst) == ["En tom gate", "Et lyst rom"], les_prompter(tekst)
    assert les_prompter("") == []
    assert round(PRIS["768P"] * 6, 2) == 0.36
    print("demo ok")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("fil", nargs="?", help="promptfil, blokker skilt med ---")
    p.add_argument("--prompt", help="én enkelt prompt i stedet for fil")
    p.add_argument("--send", action="store_true", help="kjør på ekte (koster penger)")
    p.add_argument("--ut", default="klipp", help="mappe for ferdige klipp")
    p.add_argument("--sekunder", type=int, default=6)
    p.add_argument("--oppløsning", default="768P", choices=list(PRIS))
    p.add_argument("--format", default="9:16")
    p.add_argument("--fra", type=int, default=1, help="start på dette klippnummeret")
    p.add_argument("--demo", action="store_true")
    args = p.parse_args()

    if args.demo:
        return demo()

    if args.prompt:
        prompter = [args.prompt]
    elif args.fil:
        prompter = les_prompter(pathlib.Path(args.fil).read_text())
    else:
        return p.error("oppgi en promptfil eller --prompt")

    kost = len(prompter) * args.sekunder * PRIS[args.oppløsning]
    print(f"{len(prompter)} klipp à {args.sekunder} sek i {args.oppløsning} "
          f"({args.format}) — omtrent ${kost:.2f}")

    if not args.send:
        for i, prompt in enumerate(prompter, 1):
            print(f"\n[{i}] {prompt[:100]}...")
        print("\nTørrkjøring. Legg til --send for å generere.")
        return

    ut = pathlib.Path(args.ut)
    ut.mkdir(exist_ok=True)
    nøkkel = hent_nøkkel()
    for i, prompt in enumerate(prompter, 1):
        if i < args.fra:
            continue
        print(f"[{i}/{len(prompter)}] genererer ...", flush=True)
        url = generer(prompt, nøkkel, args)
        fil = ut / f"klipp-{i:02d}.mp4"
        urllib.request.urlretrieve(url, fil)
        print(f"  {fil}")


if __name__ == "__main__":
    main()
