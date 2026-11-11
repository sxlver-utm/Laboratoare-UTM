# -*- coding: utf-8 -*-
"""enum.py - enumerare spre root (Lucrarea A).

Citeste capturile SUID / sudo / cron, aseaza constatarile in colectii
(lista, tuplu, multime, dictionar) si scoate un rezumat plus un raport JSON.

Rulare, din radacina depozitului:
    python -m arsenal.privesc.enum arsenal/privesc/start
    python -m arsenal.privesc.enum arsenal/privesc/start --json
"""
import argparse
import json
import os
import subprocess


def citeste_linii(cale):
    """Liniile curate dintr-un fisier: .strip(), fara goluri, fara comentarii (#)."""
    with open(cale, encoding="utf-8") as f:
        linii = []
        for ln in f:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                linii.append(ln)
        return linii


def nume(cale):
    """Numele fisierului: ce e dupa ultimul '/'."""
    return cale.rsplit("/", 1)[-1]


# binare cunoscute ca scapari spre root (stil GTFOBins)
GTFO = {"find", "vim.basic", "vim", "nmap", "cp", "bash",
        "less", "awk", "python3", "perl"}


def suid_constatari(cale):
    """Lista de dicte {cale, nume, risc} pentru caile UNICE, in ordine sortata."""
    cai = citeste_linii(cale)
    out = []
    for c in sorted(set(cai)):
        out.append({
            "cale": c,
            "nume": nume(c),
            "risc": "mare" if nume(c) in GTFO else "normal",
        })
    return out


def sudo_constatari(cale):
    """O linie 'user : drept' -> dict {user, drept, risc}."""
    out = []
    for ln in citeste_linii(cale):
        user, drept = ln.split(" : ", 1)          # despachetare in tuplu
        out.append({
            "user": user.strip(),
            "drept": drept.strip(),
            "risc": "mare" if "NOPASSWD" in drept else "normal",
        })
    return out


def cron_constatari(cale):
    """O linie de crontab -> dict {user, comanda}."""
    out = []
    for ln in citeste_linii(cale):
        campuri = ln.split()
        user = campuri[5]
        comanda = " ".join(campuri[6:])
        out.append({"user": user, "comanda": comanda})
    return out


def enumereaza(d):
    """Grupeaza totul intr-un dictionar: o cheie pe categorie, valoarea = lista ei."""
    return {
        "suid": suid_constatari(os.path.join(d, "suid.txt")),
        "sudo": sudo_constatari(os.path.join(d, "sudo.txt")),
        "cron": cron_constatari(os.path.join(d, "crontab.txt")),
    }


# ---------------------------------------------------------------- optional

def scaneaza_suid_live():
    """Optional 2: SUID direct de la sistem, nu dintr-un fisier.

    ATENTIE: a rula enumerare pe un sistem presupune permisiunea ta.
    Foloseste asta DOAR pe masina de laborator izolata (Kali/Metasploitable).
    Intoarce aceeasi lista de dicte ca suid_constatari.
    """
    rez = subprocess.run(
        ["find", "/", "-perm", "-4000", "-type", "f"],
        capture_output=True, text=True,
    )
    cai = [ln.strip() for ln in rez.stdout.splitlines() if ln.strip()]
    out = []
    for c in sorted(set(cai)):
        out.append({"cale": c, "nume": nume(c),
                    "risc": "mare" if nume(c) in GTFO else "normal"})
    return out


def doar_risc(raport, nivel):
    """Optional 1: pastreaza din fiecare categorie doar constatarile cu riscul dat."""
    return {cat: [c for c in lista if c.get("risc") == nivel]
            for cat, lista in raport.items()}


def grupare_dupa_risc(raport):
    """Optional 3: dict risc -> lista de nume, din toate categoriile, cu .setdefault."""
    grupe = {}
    for lista in raport.values():
        for c in lista:
            eticheta = c.get("nume", c.get("user"))
            grupe.setdefault(c.get("risc", "normal"), []).append(eticheta)
    return {r: sorted(set(v)) for r, v in grupe.items()}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("capturi")
    p.add_argument("--json", action="store_true")
    p.add_argument("--risc", choices=["mare", "normal"],
                   help="arata doar constatarile cu acest risc (optional 1)")
    p.add_argument("--grupare", action="store_true",
                   help="grupeaza numele pe risc, din toate categoriile (optional 3)")
    p.add_argument("--live", action="store_true",
                   help="SUID de la sistem, nu din fisier - DOAR pe masina de laborator (optional 2)")
    a = p.parse_args()

    raport = enumereaza(a.capturi)
    if a.live:
        raport["suid"] = scaneaza_suid_live()
    if a.risc:
        raport = doar_risc(raport, a.risc)

    if a.json:
        print(json.dumps(raport, indent=2, ensure_ascii=False))
        return

    for categorie, lista in raport.items():
        mari = [c for c in lista if c.get("risc") == "mare"]
        print(f"{categorie}: {len(lista)} gasite, {len(mari)} cu risc mare")

    # utilizatorii implicati = multimea userilor din sudo REUNITA cu cei din cron
    utilizatori = {c["user"] for c in raport["sudo"]} | {c["user"] for c in raport["cron"]}
    print("utilizatori implicati:", ", ".join(sorted(utilizatori)))

    if a.grupare:
        print("grupare dupa risc:", grupare_dupa_risc(raport))

    with open("enum.json", "w", encoding="utf-8") as f:
        json.dump(raport, f, indent=2, ensure_ascii=False)
    print("Raport salvat in enum.json")


if __name__ == "__main__":
    main()
