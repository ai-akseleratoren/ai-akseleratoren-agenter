#!/usr/bin/env python3
"""Bygg en ferdig annonse-draft: klipp etter hverandre, stemme under, tekst på.

    python3 bygg_annonse.py plan.json "Mandagsfølelsen"

Planen er JSON:

    {
      "lyd": "/sti/stemme.m4a",
      "klipp": ["/sti/1.mp4", "/sti/2.mp4"],
      "tekst": [{"tekst": "Jeg ble lei av mandager", "start": 0.5, "slutt": 4}]
    }

Klippene fordeles jevnt utover lydens lengde. Går lyden lenger enn klippene
rekker, gjentas lista fra begynnelsen — det er bedre enn sakte film.

Kjøres med repoets eget virtuelle miljø:
    ~/capcutapi/.venv/bin/python bygg_annonse.py ...
"""

import json
import pathlib
import re
import sys

# Biblioteket bor i den klonede capcutapi-mappa; vår egen kode bor her.
CAPCUTAPI = pathlib.Path.home() / "capcutapi"
sys.path.insert(0, str(CAPCUTAPI))
sys.path.insert(0, str(pathlib.Path(__file__).parent))

from add_audio_track import add_audio_track          # noqa: E402
from add_text_impl import add_text_impl              # noqa: E402
from add_video_track import add_video_track          # noqa: E402
from create_draft import create_draft                # noqa: E402
from save_draft_impl import save_draft_impl          # noqa: E402
from til_capcut import flytt, mål_fil                # noqa: E402

GLIPE = 0.01   # MCP-en avviser klipp som starter nøyaktig der forrige slutter
TEKSTBREDDE = 0.82   # andel av bildebredden teksten får bruke
MAKS_TEGN = 22       # tegn per linje før vi bryter selv (liten tekst)
MAKS_TEGN_STOR = 14  # størrelse 16+: 22 tegn rant ut av bildet (PE 3. sep 2026)


def bryt(tekst, maks=MAKS_TEGN):
    """Del teksten i korte linjer så den ikke renner ut av det stående bildet.

    Egne linjeskift respekteres, men hver linje brytes likevel om den er for lang.
    """
    if "\n" in tekst:
        return "\n".join(bryt(l, maks) for l in tekst.split("\n"))
    linjer, linje = [], ""
    for ord_ in tekst.split():
        kandidat = f"{linje} {ord_}".strip()
        if len(kandidat) > maks and linje:
            linjer.append(linje)
            linje = ord_
        else:
            linje = kandidat
    if linje:
        linjer.append(linje)
    return "\n".join(linjer)


ORD = re.compile(r"(\S+)\[(\d+\.\d+)\]")


def avbildning(biter):
    """Kildetid -> utstid når a-rollen består av bitene [[start, slutt], ...]."""
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


def teksting_fra_ord(tekst, maks_ord=4, maks_tegn=24):
    """Del transkriber.py-formatet «Jeg[1.5] holdt[3.8] ...» i tekstlinjer.

    Fire ord eller 24 tegn per linje; linja står til neste begynner.
    Returnerer [(start, slutt, tekst)]. (Bibliotekets import_srt krasjer uten
    font, så linjene legges på som vanlig tekst.)
    """
    ord_ = [(float(t), o) for o, t in ORD.findall(tekst)]
    biter, bit = [], []
    for t, o in ord_:
        kandidat = " ".join(x for _, x in bit + [(t, o)])
        if bit and (len(bit) >= maks_ord or len(kandidat) > maks_tegn
                    or bit[-1][1].endswith((".", "?", "!"))):
            biter.append(bit); bit = []
        bit.append((t, o))
    if bit:
        biter.append(bit)
    return [(b[0][0], biter[i + 1][0][0] if i + 1 < len(biter) else b[0][0] + 1.5,
             " ".join(o for _, o in b)) for i, b in enumerate(biter)]


# Valgfritt sluttkort (logo/CTA) som legges bakerst. Pek den dit din ligger,
# eller la den peke på en fil som ikke finnes — da hoppes den over.
SLUTTKORT = pathlib.Path.home() / "Desktop/sluttkort.mp4"


def klippunkter(antall, total, lengde):
    """Fordel n klipp utover total lengde. Returnerer (start, varighet)."""
    n = max(1, min(antall, int(total // 1) or 1))
    varighet = min(lengde, total / n)
    return [(i * varighet, varighet) for i in range(n)]


def bygg(plan, navn):
    # To former for plan:
    #   "lyd"   — en ren lydfil, klippene fyller hele bildet
    #   "aroll" — PEs egen film. Den ligger på spor 1 i hele lengden med lyden
    #             sin, og b-rollen legges oppå på spor 2. Da går stemmen
    #             uavbrutt, uten at vi må skille lyd fra bilde.
    aroll = plan.get("aroll")
    lyd = plan.get("lyd") or aroll
    lengde_kilde = mål_fil(lyd)[0] / 1e6
    # "aroll_slutt" klipper bort halen; "biter" [[start, slutt], ...] beholder
    # bare disse delene (pauser/omstarter bort). Tider i kutt/tekst er kildetid.
    biter = plan.get("biter") or [[0, min(lengde_kilde, plan.get("aroll_slutt", lengde_kilde))]]
    ut_tid = avbildning(biter)
    total = sum(b - a for a, b in biter)
    # "sluttkort" legger bakgrunnsvideo med stor tekst etter filmen
    kort = plan.get("sluttkort")
    klipp = plan["klipp"]
    kilde_lengde = min(mål_fil(k)[0] / 1e6 for k in klipp)

    _, draft = create_draft(1080, 1920)   # returnerer (script, draft_id)

    if aroll:
        # "skala": liggende film (16:9) må skaleres opp for å fylle det
        # stående bildet: (1920/1080) / (høyde/bredde) — 3.14 for 2688x1520
        # "crop_x": hvor i bredden PE står (0.5 = midten). Bildet flyttes
        # sideveis så han havner midt i det stående utsnittet.
        skala = plan.get("skala", 1)
        _, kb, kh = mål_fil(aroll)
        forskyv = 0.0
        if kb and kh and skala != 1:
            forskyv = (0.5 - plan.get("crop_x", 0.5)) * (kb / kh * 1920 * skala / 1080) * 2
        løpt = 0.0
        for start, slutt in biter:
            add_video_track(video_url=aroll, draft_id=draft, start=round(start, 2),
                            end=round(slutt, 2), target_start=round(løpt + (GLIPE if løpt else 0), 2),
                            volume=1, width=1080, height=1920, track_name="main",
                            scale_x=skala, scale_y=skala, transform_x=round(forskyv, 3))
            løpt += slutt - start

    # "kutt" gir eksakte tidspunkt (bildet følger stemmen); ellers fordeles
    # klippene jevnt utover lyden.
    if plan.get("kutt"):
        punkter, filer = [], []
        for k in plan["kutt"]:
            a, b = ut_tid(k["start"]), ut_tid(k["slutt"])
            if b - a >= 0.5:
                punkter.append((a, b - a)); filer.append(k["fil"])
    else:
        punkter = klippunkter(len(klipp), total, kilde_lengde)
        filer = [klipp[i % len(klipp)] for i in range(len(punkter))]

    for i, (start, varighet) in enumerate(punkter):
        add_video_track(
            video_url=filer[i],
            draft_id=draft,
            start=0,
            end=round(min(varighet, kilde_lengde), 2),
            # rekker ikke klippet hele kuttet, sakkes det ned i stedet for å
            # etterlate et svart hull i tidslinja
            speed=round(min(1.0, kilde_lengde / varighet), 3),
            target_start=round(start + (GLIPE if i else 0), 2),
            volume=0,
            width=1080,
            height=1920,
            track_name="broll" if aroll else "main",
            relative_index=1 if aroll else 0,
        )

    if not aroll:
        add_audio_track(audio_url=lyd, draft_id=draft, start=0,
                        end=round(total, 2), target_start=0, volume=1)

    for t in plan.get("tekst", []):
        størrelse = t.get("størrelse", 12)
        a, b = ut_tid(t["start"]), min(ut_tid(t["slutt"]), total)
        if b - a < 0.2:
            continue
        add_text_impl(text=bryt(t["tekst"], MAKS_TEGN_STOR if størrelse >= 16 else MAKS_TEGN),
                      start=round(a, 2), end=round(b, 2),
                      draft_id=draft, font_size=størrelse,
                      font_color="#ffffff", shadow_enabled=True,
                      border_width=8.0, border_color="#000000",
                      fixed_width=TEKSTBREDDE,
                      transform_y=t.get("y", -0.6))

    if plan.get("teksting"):
        for start, slutt, linje in teksting_fra_ord(pathlib.Path(plan["teksting"]).read_text()):
            a, b = ut_tid(start), min(ut_tid(slutt), total)
            if b - a < 0.2:
                continue
            add_text_impl(text=linje, start=round(a, 2), end=round(b, 2),
                          draft_id=draft, font_size=plan.get("tekststørrelse", 7),
                          font_color="#ffffff", shadow_enabled=True,
                          border_width=6.0, border_color="#000000",
                          fixed_width=TEKSTBREDDE, transform_y=-0.82,
                          track_name="teksting")

    if kort:
        # PNG på videosporet gir «unsupported media» i CapCut — bruk en
        # generert bakgrunnsvideo (felles for alle annonsene)
        bakgrunn = kort.get("fil", str(SLUTTKORT))
        lengde = min(kort.get("lengde", 3), mål_fil(bakgrunn)[0] / 1e6)
        add_video_track(video_url=bakgrunn, draft_id=draft, start=0, end=round(lengde, 2),
                        target_start=round(total + GLIPE, 2), volume=0,
                        width=1080, height=1920, track_name="main")
        add_text_impl(text=bryt(kort["tekst"], MAKS_TEGN_STOR), start=round(total + GLIPE, 2),
                      end=round(total + GLIPE + lengde, 2), draft_id=draft,
                      font_size=kort.get("størrelse", 16), font_color="#ffffff",
                      shadow_enabled=True, border_width=0.0,
                      fixed_width=TEKSTBREDDE, transform_y=0)
        total += lengde

    musikk = plan.get("musikk")
    if musikk:
        # mp3 har ingen mvhd-boks -> mål_fil gir None; da antar vi at musikken rekker
        mikro = mål_fil(musikk["fil"])[0]
        m_lengde = mikro / 1e6 if mikro else total
        add_audio_track(audio_url=musikk["fil"], draft_id=draft, start=0,
                        end=round(min(total, m_lengde), 2), target_start=0,
                        volume=musikk.get("volum", 0.12), track_name="musikk")

    save_draft_impl(draft)
    return draft, flytt(draft, navn), len(punkter), total


def demo():
    # 4 klipp på 6 sek som skal dekke 20 sek: fem kutt à 4 sek
    p = klippunkter(4, 20, 6)
    assert len(p) == 4 and abs(p[0][1] - 5) < 0.01, p
    assert abs(p[-1][0] - 15) < 0.01, p
    # ett klipp, kortere enn lyden: varigheten kan ikke overgå kilden
    p = klippunkter(1, 30, 6)
    assert p == [(0, 6)], p

    # tekst skal brytes før den renner ut av det stående bildet
    assert bryt("Så ansatte jeg sytten agenter") == "Så ansatte jeg sytten\nagenter"
    assert all(len(l) <= MAKS_TEGN for l in bryt(
        "Rapportene lå klare til mandagsmøtet").split("\n"))
    assert bryt("Egen\nlinjedeling") == "Egen\nlinjedeling", "egne linjeskift skal stå"
    assert bryt("Ditt webinar: 44 av 100\nDe beste: 80–90", MAKS_TEGN_STOR) == \
        "Ditt webinar:\n44 av 100\nDe beste:\n80–90", "lange egne linjer brytes også"
    assert bryt("Kort") == "Kort"

    u = avbildning([[0, 10], [20, 30]])
    assert u(5) == 5 and u(25) == 15 and u(15) == 10 and u(40) == 20

    t = teksting_fra_ord("Jeg[1.5] holdt[3.8] et[4.0] webinar[4.1] som[4.4] var.[4.8] Så[6.0]")
    assert t == [(1.5, 4.4, "Jeg holdt et webinar"), (4.4, 6.0, "som var."), (6.0, 7.5, "Så")], t
    print("demo ok")


if __name__ == "__main__":
    if "--demo" in sys.argv:
        demo()
    elif len(sys.argv) == 3:
        plan = json.loads(pathlib.Path(sys.argv[1]).read_text())
        draft, sti, n, total = bygg(plan, sys.argv[2])
        print(f"{n} kutt over {total:.1f} sek -> {sti}")
    else:
        sys.exit(__doc__)
