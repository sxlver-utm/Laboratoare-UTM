# -*- coding: utf-8 -*-
"""parse_auth.py - scoate si numara esecurile de autentificare (Lucrarea A).

Fiecare functie INTOARCE un rezultat (fisa, lista, numaratoare) - nu tipareste.
Robust: un rand stricat nu opreste parcurgerea.

Rulare, din radacina depozitului:
    python -m arsenal.aparare.parse_auth arsenal/aparare/start/auth.log
"""
import re
import argparse
from collections import Counter

TIPAR = re.compile(r"Failed password for (?:invalid user )?(\S+) from (\S+) port")


def esec(linie):
    """Intoarce (user, ip) daca randul e un esec de login, altfel None."""
    m = TIPAR.search(linie)
    if m is None:
        return None
    return (m.group(1), m.group(2))


def citeste_esecuri(cale):
    """Lista de fise {user, ip} pentru esecuri. Sare peste randurile stricate.
    Un fisier lipsa da un mesaj clar, nu un traceback."""
    esecuri = []
    try:
        f = open(cale, encoding="utf-8")
    except FileNotFoundError:
        print("nu gasesc", cale)
        return esecuri
    with f:
        for linie in f:
            r = esec(linie)
            if r is not None:
                esecuri.append({"user": r[0], "ip": r[1]})
    return esecuri


def pe_ip(esecuri):
    """Intoarce un Counter al adreselor din esecuri."""
    return Counter(e["ip"] for e in esecuri)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("log")
    a = p.parse_args()

    esecuri = citeste_esecuri(a.log)
    print("Esecuri de autentificare:", len(esecuri))
    for ip, n in pe_ip(esecuri).most_common():
        print(f"{ip}: {n}")


if __name__ == "__main__":
    main()
