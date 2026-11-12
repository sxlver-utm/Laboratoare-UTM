# -*- coding: utf-8 -*-
"""inventar.py - procese si evenimente Windows ca obiecte (Lucrarea A + B).

Proces si Eveniment sunt @dataclass cu o metoda e_suspect care raspunde singura.
Inventar este o clasa-container care se umple din JSON, interogheaza procesele
si scoate un raport de alarme.

Rulare, din radacina depozitului:
    python -m arsenal.windows.inventar arsenal/windows/start
    python -m arsenal.windows.inventar arsenal/windows/start --json
"""
from dataclasses import dataclass, asdict
import json
import argparse

CAI_SUSPECTE = ("\\Temp\\", "\\Roaming\\")
SUSPECTE_ID = {4625, 1102, 7045}

# optional 2: explicatia scurta a ID-urilor cunoscute
EXPLICATII = {
    4625: "brute force / logon esuat",
    1102: "jurnal de audit sters",
    7045: "serviciu nou instalat",
}


@dataclass
class Proces:
    pid: int
    nume: str
    user: str
    cale: str

    def e_suspect(self):
        """Un proces care ruleaza din Temp sau Roaming e un semn clasic."""
        return any(s in self.cale for s in CAI_SUSPECTE)


@dataclass
class Eveniment:
    id: int
    nivel: str
    sursa: str
    cont: str
    mesaj: str

    def e_suspect(self):
        return self.id in SUSPECTE_ID or self.nivel == "critical"

    def explica(self):
        """optional 2: text scurt pentru fiecare ID cunoscut."""
        return EXPLICATII.get(self.id, "eveniment obisnuit")


def procese_din_json(cale):
    with open(cale, encoding="utf-8") as f:
        return [Proces(**d) for d in json.load(f)]


def evenimente_din_json(cale):
    with open(cale, encoding="utf-8") as f:
        return [Eveniment(**d) for d in json.load(f)]


@dataclass
class Inventar:
    procese: list

    @classmethod
    def din_json(cls, cale):
        """Constructor alternativ: umple inventarul din JSON."""
        with open(cale, encoding="utf-8") as f:
            return cls([Proces(**d) for d in json.load(f)])

    def __len__(self):
        return len(self.procese)

    def suspecte(self):
        """Procesele care se declara suspecte."""
        return [p for p in self.procese if p.e_suspect()]

    def pe_user(self):
        """Dict user -> lista de nume de procese."""
        grupe = {}
        for p in self.procese:
            grupe.setdefault(p.user, []).append(p.nume)
        return grupe

    def scor(self, evenimente):
        """optional 3: un numar de risc = procese + evenimente de alarma."""
        return len(self.suspecte()) + sum(1 for e in evenimente if e.e_suspect())


def main():
    p = argparse.ArgumentParser()
    p.add_argument("capturi")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()

    inv = Inventar.din_json(a.capturi + "/procese.json")
    ev = evenimente_din_json(a.capturi + "/evenimente.json")
    alarma = [e for e in ev if e.e_suspect()]

    if a.json:
        raport = {
            "suspecte": [asdict(p) for p in inv.suspecte()],
            "alarma": [asdict(e) for e in alarma],
        }
        print(json.dumps(raport, indent=2, ensure_ascii=False))
        return

    print(f"Procese: {len(inv)} | suspecte: {len(inv.suspecte())}")
    for p in inv.suspecte():
        print(f"[{p.pid}] {p.nume} ({p.user}) {p.cale}")
    print(f"Evenimente: {len(ev)} | alarma: {len(alarma)}")
    for e in alarma:
        print(f"{e.id} [{e.nivel}] {e.cont}: {e.mesaj}")


if __name__ == "__main__":
    main()
