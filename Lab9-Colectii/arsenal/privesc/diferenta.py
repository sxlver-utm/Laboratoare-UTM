# -*- coding: utf-8 -*-
"""diferenta.py - ce e nou fata de un sistem curat (Lucrarea B).

Compara SUID-urile de acum cu o imagine curata, prin diferenta de multimi,
si scoate fisierele noi si, dintre ele, pe cele periculoase.

Rulare, din radacina depozitului:
    python -m arsenal.privesc.diferenta
"""
import os
from arsenal.privesc.enum import citeste_linii, nume, GTFO

AICI = os.path.dirname(os.path.abspath(__file__))
START = os.path.join(AICI, "start")


def cai(fisier):
    """Multimea cailor dintr-un fisier din start/."""
    return set(citeste_linii(os.path.join(START, fisier)))


def main():
    baza = cai("baza_suid.txt")
    acum = cai("suid.txt")
    print("baza:", len(baza), " acum:", len(acum))

    noi = acum - baza                              # diferenta de multimi
    print(len(noi), "SUID noi fata de sistemul curat")
    for c in sorted(noi):
        print(" ", c)

    # fisa nume -> risc pentru cele noi (dict comprehension)
    risc = {nume(c): ("mare" if nume(c) in GTFO else "normal") for c in noi}
    # doar periculoasele, sortate (list comprehension cu if)
    periculoase = [c for c in sorted(noi) if nume(c) in GTFO]
    print("periculoase NOI:", periculoase)

    return risc, periculoase


if __name__ == "__main__":
    main()
