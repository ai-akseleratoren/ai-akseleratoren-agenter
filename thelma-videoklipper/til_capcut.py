#!/usr/bin/env python3
"""Flytt en ferdig draft fra capcutapi inn i CapCuts prosjektmappe.

    python3 til_capcut.py dfd_cat_1788053414_48332d0c "17 som aldri sover"

Draften som lages av MCP-serveren havner i repoet, og draft_meta_info.json
peker på utviklerens egen maskin. Dette skriptet kopierer mappa til CapCut og
retter stiene, slik at prosjektet dukker opp i appen.
"""

import json
import pathlib
import shutil
import struct
import sys

CAPCUT = pathlib.Path.home() / "Movies/CapCut/User Data/Projects/com.lveditor.draft"


def rett_meta(mappe, navn):
    """Sett navn og stier i draft_meta_info.json til denne maskinen."""
    fil = mappe / "draft_meta_info.json"
    meta = json.loads(fil.read_text())
    meta["draft_name"] = navn
    meta["draft_fold_path"] = str(mappe)
    meta["draft_root_path"] = str(mappe.parent)
    # MCP-en lar tm_duration stå 0; da viser CapCut «00:00» i prosjektlista
    info = mappe / "draft_info.json"
    if info.exists():
        meta["tm_duration"] = json.loads(info.read_text()).get("duration", 0)
    fil.write_text(json.dumps(meta, ensure_ascii=False))
    return meta


def mål_fil(sti):
    """Les lengde (mikrosekunder) og bildestørrelse rett ut av MP4/M4A-headeren.

    `mdls` bytter om bredde og høyde på disse filene, og ffprobe finnes ikke på
    maskinen — så vi leser boksene selv. mvhd gir tidsskala og lengde, tkhd gir
    målene (0 for ren lyd).
    """
    d = pathlib.Path(sti).read_bytes()
    # Gå toppnivåboksene til moov: d.find(b"mvhd") traff tilfeldige bytes i mdat
    # når moov ligger sist i fila (en film ble målt til 0,9 sek).
    pos = 0
    while pos + 8 <= len(d):
        størrelse, navn = struct.unpack(">I4s", d[pos:pos + 8])
        if størrelse == 1:
            størrelse = struct.unpack(">Q", d[pos + 8:pos + 16])[0]
        elif størrelse == 0:
            størrelse = len(d) - pos
        if navn == b"moov":
            d = d[pos:pos + størrelse]
            break
        if størrelse < 8:
            break
        pos += størrelse
    i = d.find(b"mvhd")
    if i < 0:
        return None, 0, 0
    versjon = d[i + 4]
    if versjon == 1:
        tidsskala, lengde = struct.unpack(">IQ", d[i + 24:i + 36])
    else:
        tidsskala, lengde = struct.unpack(">II", d[i + 16:i + 24])
    mikro = round(lengde / tidsskala * 1_000_000) if tidsskala else 0

    b, h = 0, 0
    j = d.find(b"tkhd")
    if j >= 0:
        boks = d[j + 4:j + 96]
        b = struct.unpack(">I", boks[76:80])[0] >> 16
        h = struct.unpack(">I", boks[80:84])[0] >> 16
    return mikro, b, h


def rett_medier(mappe):
    """Pek hvert medium på fila som ligger i draftens assets-mappe.

    MCP-serveren skriver den ekte stien i `remote_url` og lar `path` stå tom.
    CapCut leser `path`, ser ingenting, og viser «download media» med stille
    avspilling. Filene ER kopiert inn i assets/ — de mangler bare adressen.
    """
    fil = mappe / "draft_info.json"
    info = json.loads(fil.read_text())
    rettet = 0
    for slag, undermappe in (("videos", "video"), ("audios", "audio"),
                             ("images", "image")):
        for m in info.get("materials", {}).get(slag, []):
            navn = m.get("material_name") or m.get("name")
            if not navn:
                continue
            asset = mappe / "assets" / undermappe / navn
            kilde = m.get("remote_url") or ""
            if asset.exists():
                m["path"] = str(asset)
            elif pathlib.Path(kilde).is_file():
                m["path"] = kilde        # fall tilbake på originalen
            else:
                continue
            m["remote_url"] = ""
            # MCP-en setter duration 0 og gjetter 1920x1080. CapCut kan ikke
            # bruke et medium uten lengde — den viser «media not found».
            mikro, b, h = mål_fil(m["path"])
            if mikro:
                m["duration"] = mikro
                if b and h and slag != "audios":
                    m["width"], m["height"] = b, h
            rettet += 1
    fil.write_text(json.dumps(info, ensure_ascii=False))
    return rettet


def flytt(draft_id, navn):
    kilde = pathlib.Path.home() / "capcutapi" / draft_id
    if not kilde.is_dir():
        sys.exit(f"Fant ikke draften {draft_id}")
    mål = CAPCUT / navn
    if mål.exists():
        shutil.rmtree(mål)
    shutil.copytree(kilde, mål)
    rett_meta(mål, navn)
    print(f"{rett_medier(mål)} medier pekt på assets-mappa")
    return mål


def demo():
    import tempfile
    with tempfile.TemporaryDirectory() as t:
        m = pathlib.Path(t) / "prosjekt"
        m.mkdir()
        (m / "draft_meta_info.json").write_text(json.dumps(
            {"draft_name": "0707", "draft_fold_path": "/Users/annen/x",
             "draft_root_path": "/Users/annen", "draft_id": "ABC"}))
        meta = rett_meta(m, "prosjekt")
        assert meta["draft_name"] == "prosjekt"
        assert meta["draft_fold_path"] == str(m)
        assert meta["draft_root_path"] == str(m.parent)
        assert meta["draft_id"] == "ABC", "andre felt skal ikke røres"

        # medier: ett som finnes i assets, ett som bare finnes i originalen,
        # ett som ikke finnes noe sted og derfor skal stå urørt
        (m / "assets/video").mkdir(parents=True)
        (m / "assets/video/klipp.mp4").write_text("x")  # ikke ekte MP4: mål_fil skal gi 0
        original = m / "original.m4a"
        original.write_text("y")
        (m / "draft_info.json").write_text(json.dumps({"materials": {
            "videos": [{"material_name": "klipp.mp4", "path": "", "remote_url": "/vekk/klipp.mp4"},
                       {"material_name": "borte.mp4", "path": "", "remote_url": "/vekk/borte.mp4"}],
            "audios": [{"name": "stemme.m4a", "path": "", "remote_url": str(original)}]}}))
        assert rett_medier(m) == 2
        d = json.loads((m / "draft_info.json").read_text())
        v1, v2 = d["materials"]["videos"]
        assert v1["path"] == str(m / "assets/video/klipp.mp4") and v1["remote_url"] == ""
        assert v2["path"] == "" and v2["remote_url"] == "/vekk/borte.mp4", "ukjent medium skal stå urørt"
        assert d["materials"]["audios"][0]["path"] == str(original)
    print("demo ok")


if __name__ == "__main__":
    if "--demo" in sys.argv:
        demo()
    elif len(sys.argv) == 3:
        print(flytt(sys.argv[1], sys.argv[2]))
    else:
        sys.exit(__doc__)
