# -*- coding: utf-8 -*-
"""Decoder universal (Lucrarea A).

Recunoaste stratul de codare al unui sir (base64 / hex / url), il desface,
desface straturi multiple intr-o bucla, si sparge un XOR cu cheie de un
octet sau un hash de parola prin dictionar.

Rulare:
    python arsenal/forensics/decode.py "NTM1OTU3NTk="
    python arsenal/forensics/decode.py probe/xor.bin --fisier
"""
import re
import json
import base64
import argparse
import hashlib
import os
from urllib.parse import unquote


# ---------------------------------------------------------------- A2
def ghici_strat(s):
    """Clasifica stratul dupa forma, fara sa decodeze.

    Ordinea conteaza: intai URL (%xx), apoi hex (alfabet strict),
    apoi base64 (alfabetul cel mai larg).
    """
    if re.search(r"%[0-9A-Fa-f]{2}", s):
        return "url"
    if re.fullmatch(r"[0-9a-fA-F]+", s) and len(s) % 2 == 0:
        return "hex"
    if re.fullmatch(r"[A-Za-z0-9+/]+={0,2}", s) and len(s) % 4 == 0:
        return "base64"
    return "necunoscut"


# ---------------------------------------------------------------- A3
def desfa(s):
    """Decodeaza un singur strat. Intoarce (strat, rezultat_bytes)."""
    strat = ghici_strat(s)
    if strat == "base64":
        return strat, base64.b64decode(s)
    if strat == "hex":
        return strat, bytes.fromhex(s)
    if strat == "url":
        return strat, unquote(s).encode()
    return strat, s.encode()


# ---------------------------------------------------------------- A4
def citibil(b):
    """True daca toti octetii sunt imprimabili ASCII (32..126)."""
    return len(b) > 0 and all(32 <= c < 127 for c in b)


def desfa_straturi(val, maxim=8):
    """Decodeaza in bucla cat timp rezultatul mai arata a strat cunoscut.

    Se opreste cand textul decodat nu mai e o codare recunoscuta (de ex.
    un FLAG{...}, care contine { } _ si iese din alfabetul base64/hex/url).
    Intoarce (lista_straturi, rezultat_bytes).
    """
    straturi = []
    b = val.encode()
    for _ in range(maxim):
        if ghici_strat(val) == "necunoscut":
            break
        strat, b = desfa(val)
        straturi.append(strat)
        try:
            val = b.decode()
        except UnicodeDecodeError:
            break
    return straturi, b


# ---------------------------------------------------------------- A5
def sparge_xor1(date):
    """Incearca toate cele 256 de chei de un octet; intoarce (cheie, clar)
    pentru prima cheie care da text citibil, altfel (None, None)."""
    for k in range(256):
        clar = bytes(b ^ k for b in date)
        if citibil(clar):
            return k, clar
    return None, None


# ---------------------------------------------------------------- A6
_ALGO_DUPA_LUNGIME = {32: "md5", 40: "sha1", 64: "sha256"}


def sparge_hash(tinta, cale_wordlist):
    """Identifica algoritmul dupa lungime si cauta parola in wordlist.
    Intoarce (algoritm, parola) sau (algoritm, None)."""
    algo = _ALGO_DUPA_LUNGIME.get(len(tinta.strip()))
    if algo is None:
        return None, None
    tinta = tinta.strip().lower()
    with open(cale_wordlist, encoding="latin1") as f:
        for cuv in f:
            cuv = cuv.strip()
            h = hashlib.new(algo, cuv.encode()).hexdigest()
            if h == tinta:
                return algo, cuv
    return algo, None


# ---------------------------------------------------------------- A7
def main():
    p = argparse.ArgumentParser(description="Decoder universal de straturi.")
    p.add_argument("intrare", help="un sir, sau o cale daca se da --fisier")
    p.add_argument("--fisier", action="store_true",
                   help="trateaza intrarea ca o cale catre un fisier binar")
    a = p.parse_args()

    if a.fisier:
        with open(a.intrare, "rb") as f:
            date = f.read()
        # pe un fisier binar incercam intai XOR pe un octet
        cheie, clar = sparge_xor1(date)
        rezultat = {
            "sursa": a.intrare,
            "metoda": "xor1",
            "cheie": cheie,
            "rezultat": clar.decode() if clar else None,
        }
    else:
        straturi, b = desfa_straturi(a.intrare)
        try:
            rez = b.decode()
        except UnicodeDecodeError:
            rez = b.hex()
        rezultat = {
            "intrare": a.intrare,
            "metoda": "straturi",
            "straturi": straturi,
            "rezultat": rez,
        }

    aici = os.path.dirname(os.path.abspath(__file__))
    cale_fisa = os.path.join(aici, "fisa.json")
    with open(cale_fisa, "w", encoding="utf-8") as f:
        json.dump(rezultat, f, ensure_ascii=False, indent=2)
    print(json.dumps(rezultat, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
