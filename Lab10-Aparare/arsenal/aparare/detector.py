# -*- coding: utf-8 -*-
"""detector.py - detector de brute force (Lucrarea B).

suspecti() are un prag reglabil cu valoare implicita si validare cu raise.
main() leaga functiile din parse_auth, cu argparse si raport JSON.

Rulare, din radacina depozitului:
    python -m arsenal.aparare.detector arsenal/aparare/start/auth.log
    python -m arsenal.aparare.detector arsenal/aparare/start/auth.log --prag 2 --json
"""
import re
import argparse
import json
from datetime import datetime
from collections import Counter

from arsenal.aparare.parse_auth import citeste_esecuri, esec


def suspecti(counts, prag=10):
    """Adresele cu cel putin `prag` esecuri, sortate descrescator.
    Un prag sub 1 nu are sens: oprit cu raise."""
    if prag < 1:
        raise ValueError(f"prag invalid: {prag} (cel putin 1)")
    return sorted(
        [(ip, n) for ip, n in counts.items() if n >= prag],
        key=lambda t: t[1], reverse=True,
    )


# ---------------------------------------------------------------- optional

_TS = re.compile(r"^(\w{3}\s+\d+\s+\d+:\d+:\d+)")


def _ora(linie):
    """datetime-ul dintr-un rand de syslog, sau None daca nu are ora."""
    m = _TS.match(linie)
    if not m:
        return None
    return datetime.strptime("2000 " + m.group(1), "%Y %b %d %H:%M:%S")


def esecuri_cu_timp(cale):
    """Optional 1: esecurile cu ora lor, pentru filtrarea pe fereastra."""
    out = []
    try:
        f = open(cale, encoding="utf-8")
    except FileNotFoundError:
        print("nu gasesc", cale)
        return out
    with f:
        for linie in f:
            r, t = esec(linie), _ora(linie)
            if r is not None and t is not None:
                out.append({"user": r[0], "ip": r[1], "ora": t})
    return out


def in_fereastra(esecuri_t, secunde):
    """Doar esecurile din primele `secunde` de la primul esec (atac dens in timp)."""
    if not esecuri_t:
        return []
    inceput = min(e["ora"] for e in esecuri_t)
    return [e for e in esecuri_t if (e["ora"] - inceput).total_seconds() <= secunde]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("log")
    p.add_argument("--prag", type=int, default=10)
    p.add_argument("--json", action="store_true")
    p.add_argument("--fereastra", type=int,
                   help="numara doar esecurile din primele N secunde (optional 1)")
    p.add_argument("--top", type=int,
                   help="arata doar primele N adrese dupa esecuri (optional 3)")
    a = p.parse_args()

    if a.fereastra is not None:
        esecuri = in_fereastra(esecuri_cu_timp(a.log), a.fereastra)
    else:
        esecuri = citeste_esecuri(a.log)
    counts = Counter(e["ip"] for e in esecuri)
    try:
        sus = suspecti(counts, a.prag)
    except ValueError as e:
        p.error(str(e))                # mesaj clar, fara traceback

    afisate = counts.most_common(a.top) if a.top else counts.most_common()

    if a.json:
        raport = {
            "esecuri": len(esecuri),
            "pe_ip": dict(counts),
            "suspecti": [{"ip": ip, "incercari": n} for ip, n in sus],
        }
        print(json.dumps(raport, indent=2, ensure_ascii=False))
        return

    print("Esecuri de autentificare:", len(esecuri))
    for ip, n in afisate:
        print(f"{ip}: {n}")
    print(f"Suspecti (prag {a.prag}):")
    for ip, n in sus:
        print(f"{ip} ({n} incercari) BRUTE FORCE")


if __name__ == "__main__":
    main()
