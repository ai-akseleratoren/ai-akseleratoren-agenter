#!/usr/bin/env python3
"""Tagg-vakt: redd nye webinar-påmeldte fra forrige sendings e-postsekvens.

Bakgrunn: gjenbrukes påmeldingsskjemaet fra forrige webinar, tagger CRM-et
(GoHighLevel) nye påmeldte inn i den GAMLE sekvensen — de får bekreftelse
med død møtelenke. Riktig fiks er å endre tagg/workflow i CRM-et. Denne
vakta er plasteret inntil da:

  1. finner NYE innsendinger på skjemaet (via forms/submissions, ikke
     dateAdded — en gjenganger i CRM-et har gammel opprettelsesdato)
  2. legger på riktig tagg (WEBINAR_TAGG_NY)
  3. FJERNER den gamle taggen (WEBINAR_TAGG_GAMMEL) så resten av den gamle
     sekvensen ikke fortsetter å fyre
  4. printer dem, så en planlagt oppgave kan sende riktig bekreftelse

  python3 webinar_vakt.py            # vis nye, ikke rør noe (tørrkjøring)
  python3 webinar_vakt.py --fiks     # rett taggene OG marker som behandlet

Konfigureres i .env — se .env.example.
"""
import argparse, json, os, subprocess
from datetime import datetime, timezone

ROT = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(ROT, ".webinar-vakt.json")

env = {}
with open(os.path.join(ROT, ".env")) as f:
    for line in f:
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.strip().split("=", 1)
            env[k] = v

LOC = env["GHL_LOCATION_ID"]
SKJEMA = env["GHL_FORM_ID"]              # påmeldingsskjemaet
GAMMEL = env["WEBINAR_TAGG_GAMMEL"]      # f.eks. webinar-forrige-dato
RIKTIG = env["WEBINAR_TAGG_NY"]          # f.eks. webinar-neste-dato
HDR = [
    "-H", "Authorization: Bearer " + env["GHL_PIT_TOKEN"],
    "-H", "Version: 2021-07-28",
    "-H", "Content-Type: application/json",
    "-H", "Accept: application/json",
    # GHL blokkerer Python-standard-UA — bruk en nettleser-UA
    "-A", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
]


def kall(metode, url, body=None):
    cmd = ["curl", "-s", "-X", metode, url] + HDR
    if body is not None:
        cmd += ["-d", json.dumps(body)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    try:
        return json.loads(r.stdout) if r.stdout.strip() else {}
    except json.JSONDecodeError:
        return {"_rå": r.stdout[:200]}


def naar_fmt(v):
    s = str(v or "")
    return s[:16].replace("T", " ")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fiks", action="store_true",
                    help="rett taggene og marker innsendingene som behandlet")
    a = ap.parse_args()

    st = {"sett": [], "start": None}
    if os.path.exists(STATE):
        st = json.load(open(STATE))
    if not st.get("start"):
        # Første kjøring setter en grense, så gamle innsendinger aldri røres.
        st["start"] = datetime.now(timezone.utc).isoformat()
        json.dump(st, open(STATE, "w"), indent=1)
        print(f"Første kjøring — grense satt til {st['start']}.")
        print("Innsendinger FØR dette røres aldri. Ingen nye ennå.")
        return

    sett = set(st.get("sett", []))
    d = kall("GET", f"https://services.leadconnectorhq.com/forms/submissions"
                    f"?locationId={LOC}&formId={SKJEMA}&limit=25")
    nye = []
    for s in d.get("submissions", []):
        sid = s.get("id")
        naar = str(s.get("createdAt") or "")
        if sid in sett or naar <= st["start"]:
            continue
        nye.append(s)

    print(f"NYE_PAAMELDTE={len(nye)}")
    if not nye:
        print("Ingen nye påmeldinger siden sist.")
        return

    for s in nye:
        cid = s.get("contactId")
        c = kall("GET", f"https://services.leadconnectorhq.com/contacts/{cid}").get("contact", {})
        tags = c.get("tags") or []
        print("---")
        print(f'NAVN={c.get("firstName") or s.get("name") or "(ukjent)"}')
        print(f'EPOST={c.get("email") or s.get("email") or "(mangler)"}')
        print(f'KONTAKT_ID={cid}')
        print(f'PAAMELDT={naar_fmt(s.get("createdAt"))}')
        print(f'TAGGER_FOR={tags}')

        if not a.fiks:
            continue

        if RIKTIG not in tags:
            r = kall("POST", f"https://services.leadconnectorhq.com/contacts/{cid}/tags",
                     {"tags": [RIKTIG]})
            print(f'  + la på {RIKTIG}' if "tags" in r or r == {} else f'  ! tagg feilet: {r}')
        if GAMMEL in tags:
            kall("DELETE", f"https://services.leadconnectorhq.com/contacts/{cid}/tags",
                 {"tags": [GAMMEL]})
            print(f'  - fjernet {GAMMEL} (stopper resten av den gamle sekvensen)')
        sett.add(s["id"])

    if a.fiks:
        st["sett"] = sorted(sett)
        json.dump(st, open(STATE, "w"), indent=1)
        print(f"\nBehandlet {len(nye)} — lagret i {STATE}")
    else:
        print("\n(Tørrkjøring — ingenting endret. Kjør med --fiks.)")


if __name__ == "__main__":
    main()
