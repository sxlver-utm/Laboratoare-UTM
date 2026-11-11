# -*- coding: utf-8 -*-
"""Forensics pe fisiere (Lucrarea B, B1-B4).

B1 magic bytes, B2 strings, B3 EXIF/GPS, B4 file carving.
Ruleaza:  python forensics.py
"""
import re
import os
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

PROBE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "probe")


# ---------------------------------------------------------------- B1
def tip_real(cale):
    """Tipul real dupa semnatura (magic bytes), nu dupa extensie."""
    with open(cale, "rb") as f:
        cap = f.read(8)
    if cap.startswith(b"%PDF"):
        return "pdf"
    if cap.startswith(b"\x89PNG"):
        return "png"
    if cap.startswith(b"\xff\xd8"):
        return "jpeg"
    if cap.startswith(b"PK\x03\x04"):
        return "zip/docx"
    return cap.hex()


# ---------------------------------------------------------------- B2
def strings(cale, minim=4):
    """Secventele de caractere imprimabile dintr-un fisier binar."""
    with open(cale, "rb") as f:
        date = f.read()
    tipar = ("[ -~]{%d,}" % minim).encode()
    return [m.decode() for m in re.findall(tipar, date)]


# ---------------------------------------------------------------- B3
def _rational(v):
    """Numarul dintr-un camp EXIF rational (IFDRational sau tuplu)."""
    try:
        return float(v)
    except (TypeError, ValueError):
        return v[0] / v[1]


def _dms_in_zecimal(dms, ref):
    grade = _rational(dms[0]) + _rational(dms[1]) / 60 + _rational(dms[2]) / 3600
    if ref in ("S", "W"):
        grade = -grade
    return round(grade, 6)


def exif_si_gps(cale):
    """Intoarce (dict_exif_lizibil, (lat, lon) sau None)."""
    img = Image.open(cale)
    brut = img._getexif() or {}
    lizibil, gps_brut = {}, {}
    for id_, val in brut.items():
        nume = TAGS.get(id_, id_)
        if nume == "GPSInfo":
            for g_id, g_val in val.items():
                gps_brut[GPSTAGS.get(g_id, g_id)] = g_val
            lizibil["GPSInfo"] = gps_brut
        else:
            lizibil[nume] = val
    coord = None
    if "GPSLatitude" in gps_brut and "GPSLongitude" in gps_brut:
        lat = _dms_in_zecimal(gps_brut["GPSLatitude"], gps_brut.get("GPSLatitudeRef", "N"))
        lon = _dms_in_zecimal(gps_brut["GPSLongitude"], gps_brut.get("GPSLongitudeRef", "E"))
        coord = (lat, lon)
    return lizibil, coord


# ---------------------------------------------------------------- B4
def carving(cale, iesire=None):
    """Extrage un ZIP lipit la coada fisierului. Intoarce (offset, cale_zip)."""
    with open(cale, "rb") as f:
        date = f.read()
    i = date.find(b"PK\x03\x04")
    if i == -1:
        return None, None
    if iesire is None:
        iesire = os.path.join(os.path.dirname(cale), "gasit.zip")
    with open(iesire, "wb") as f:
        f.write(date[i:])
    return i, iesire


def main():
    print("== B1: magic bytes (tip real vs extensie) ==")
    for nume in ("foto.jpg", "ascuns.png", "mesaj.txt"):
        cale = os.path.join(PROBE, nume)
        print(f"  {nume:12s} -> {tip_real(cale)}")

    print("\n== B2: strings din ascuns.png (indicii) ==")
    for s in strings(os.path.join(PROBE, "ascuns.png")):
        print("  ", s)

    print("\n== B3: EXIF + GPS din foto.jpg ==")
    exif, coord = exif_si_gps(os.path.join(PROBE, "foto.jpg"))
    for k, v in exif.items():
        if k != "GPSInfo":
            print(f"  {k} = {v}")
    if coord:
        lat, lon = coord
        print(f"  GPS (zecimal) = {lat}, {lon}")
        print(f"  harta         = https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=15/{lat}/{lon}")

    print("\n== B4: file carving din ascuns.png ==")
    offset, zip_cale = carving(os.path.join(PROBE, "ascuns.png"))
    if offset is not None:
        print(f"  arhiva gasita la octetul {offset} -> {zip_cale}")
        import zipfile
        with zipfile.ZipFile(zip_cale) as z:
            for info in z.infolist():
                continut = z.read(info.filename).decode(errors="replace").strip()
                print(f"  {info.filename}: {continut}")


if __name__ == "__main__":
    main()
