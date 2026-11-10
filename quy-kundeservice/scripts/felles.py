"""Felles småting: .env-lesing og logg. Kun stdlib."""
import json, os
from datetime import datetime, timezone

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def env():
    """Leser .env i repo-rota. Miljøvariabler vinner over fila."""
    verdier = {}
    sti = os.path.join(ROT, ".env")
    if os.path.exists(sti):
        for linje in open(sti, encoding="utf-8"):
            linje = linje.strip()
            if not linje or linje.startswith("#") or "=" not in linje:
                continue
            k, v = linje.split("=", 1)
            verdier[k.strip()] = v.strip().strip('"').strip("'")
    verdier.update({k: v for k, v in os.environ.items() if k in verdier or k.startswith(("EPOST_", "META_", "GHL_", "HUBSPOT_", "SALESFORCE_", "KAJABI_", "CRM"))})
    return verdier


def logg(hendelse):
    """Én JSON-linje per hendelse i logg/<dato>.jsonl."""
    hendelse["tid"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    os.makedirs(os.path.join(ROT, "logg"), exist_ok=True)
    sti = os.path.join(ROT, "logg", datetime.now().strftime("%Y-%m-%d") + ".jsonl")
    with open(sti, "a", encoding="utf-8") as f:
        f.write(json.dumps(hendelse, ensure_ascii=False) + "\n")
