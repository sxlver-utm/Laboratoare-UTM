# -*- coding: utf-8 -*-
"""Steganografie LSB (Lucrarea B, B5-B6).

B5 ascunde un mesaj in ultimul bit al canalelor R,G,B ale pixelilor.
B6 il dezvaluie inapoi.
Ruleaza:  python stego.py
"""
import os
from PIL import Image

PROBE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "probe")


# ---------------------------------------------------------------- B5
def ascunde(cale_gazda, mesaj, cale_iesire):
    """Scrie mesajul in LSB-ul canalelor; adauga un octet 0 ca terminator.
    Salveaza in PNG (fara pierdere)."""
    img = Image.open(cale_gazda).convert("RGB")
    px = list(img.getdata())

    date = mesaj + b"\x00"                       # 0 = sfarsit de mesaj
    biti = "".join(f"{x:08b}" for x in date)
    if len(biti) > len(px) * 3:
        raise ValueError("mesaj prea lung pentru imaginea gazda")

    px_nou = []
    idx = 0
    for (r, g, b) in px:
        canale = [r, g, b]
        for c in range(3):
            if idx < len(biti):
                canale[c] = (canale[c] & ~1) | int(biti[idx])
                idx += 1
        px_nou.append(tuple(canale))

    img.putdata(px_nou)
    img.save(cale_iesire, "PNG")
    return cale_iesire, len(biti)


# ---------------------------------------------------------------- B6
def dezvaluie(cale_stego):
    """Citeste LSB-urile, grupeaza cate 8, se opreste la primul octet 0."""
    px = list(Image.open(cale_stego).convert("RGB").getdata())
    biti = []
    for (r, g, b) in px:
        biti.extend((r & 1, g & 1, b & 1))

    octeti = bytearray()
    for i in range(0, len(biti) - 7, 8):
        val = 0
        for bit in biti[i:i + 8]:
            val = (val << 1) | bit
        if val == 0:                              # terminator
            break
        octeti.append(val)
    return bytes(octeti)


def main():
    gazda = os.path.join(PROBE, "foto.jpg")
    iesire = os.path.join(PROBE, "stego.png")
    mesaj = b"FLAG{ascuns_in_pixeli}"

    cale, nr_biti = ascunde(gazda, mesaj, iesire)
    print(f"B5: ascuns '{mesaj.decode()}' ({nr_biti} biti) in {cale}")

    recuperat = dezvaluie(iesire)
    print(f"B6: dezvaluit -> '{recuperat.decode(errors='replace')}'")
    assert recuperat == mesaj, "mesajul recuperat nu coincide!"
    print("OK: mesajul recuperat coincide cu cel ascuns.")


if __name__ == "__main__":
    main()
