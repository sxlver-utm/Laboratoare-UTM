# Raport — Laboratorul 6: Informații invizibile (forensics și steganografie)

**Disciplina:** Tehnici de programare · UTM · FCIM · Securitate informațională
**Țintele:** generate local de `probe/pregateste.py` (se lucrează doar pe fișiere proprii).

---

## Lucrarea A — Decoderul universal (`arsenal/forensics/decode.py`)

### A2–A4. Recunoaștere și desfacere pe straturi — `probe/mesaj.txt`
Mesajul era îngropat sub **trei straturi**: `base64 → base64 → hex`.
Bucla de unwrap continuă cât timp rezultatul mai aparține unui alfabet de
codare cunoscut și se oprește la textul care nu mai e o codare (flag-ul,
care conține `{ } _`).

| Pas | Strat recunoscut |
|-----|------------------|
| 1 | base64 |
| 2 | base64 |
| 3 | hex |

**Rezultat:** `FLAG{straturi_de_encoding}`

### A5. Spargere XOR cu cheie de un octet — `probe/xor.bin`
Toate cele 256 de chei încercate; una singură produce text imprimabil.

- **Cheie găsită:** `128` (`0x80`)
- **Text clar:** `Un singur octet tine tot secretul... gaseste-l! FLAG{xor_un_octet}`

### A6. Spargere hash prin dicționar — `probe/hashuri.txt`
Lungimea de 32 hex → **MD5**. Fiecare cuvânt din wordlist e hash-uit și
comparat (nu se „decriptează" hash-ul).

| Hash MD5 | Parolă |
|----------|--------|
| 5f4dcc3b5aa765d61d8327deb882cf99 | password |
| 8621ffdbc5698829397d97767ac13db3 | dragon |
| d8578edf8458ce06fbc5bb76a58c5ca4 | qwerty |
| 0d107d09f5bbe40cade3de5c71e9e9b7 | letmein |
| d0763edaa9d9bd2a9516280e9044d885 | monkey |

### A7. Unealtă + fișă + test
- CLI cu `argparse`: `python arsenal/forensics/decode.py "<sir>"` sau `... <cale> --fisier`.
- Rezultatul se salvează în `arsenal/forensics/fisa.json`.
- `teste/test_decode.py`: **8 teste, toate trec** (`pytest -q` → `8 passed`).

---

## Lucrarea B — Forensics pe fișiere și mesaj ascuns (`forensics.py`, `stego.py`)

### B1. Magic bytes (tip real vs extensie)
| Fișier | Primii octeți | Tip real |
|--------|---------------|----------|
| foto.jpg | `FF D8` | jpeg |
| ascuns.png | `89 50 4E 47` | png |
| mesaj.txt | — | text (base64, nu binar cu semnătură) |

### B2. Strings din `ascuns.png`
Printre secvențele imprimabile apar `secret.txt` și
`FLAG{ascuns_prin_carving}` — indiciul că la coada PNG-ului e lipit un ZIP.

### B3. Metadate EXIF + GPS din `foto.jpg`
- **Make / Model:** Apple / iPhone 13
- **DateTime:** 2026:09:14 10:30:00
- **GPS (zecimal):** `47.016667, 28.8575` → **Chișinău**
- Hartă: `https://www.openstreetmap.org/?mlat=47.016667&mlon=28.8575`

Observație OSINT: coordonatele din EXIF dezvăluie locul exact — de aceea
EXIF-ul se șterge înainte de publicarea unei poze.

### B4. File carving din `ascuns.png`
Semnătura ZIP (`PK\x03\x04`) găsită la **octetul 779**; coada extrasă în
`probe/gasit.zip`. Conținut:

- `secret.txt` → `FLAG{ascuns_prin_carving}`

### B5–B6. Steganografie LSB
Mesaj ascuns în ultimul bit al canalelor R,G,B din `foto.jpg`, salvat
`probe/stego.png` (PNG, fără pierdere; JPG ar distruge biții). Terminator:
un octet `0`.

- **Ascuns:** `FLAG{ascuns_in_pixeli}` (184 biți)
- **Dezvăluit înapoi:** `FLAG{ascuns_in_pixeli}` — coincide (verificat cu `assert`).

---

## Pentru vârful sălii — `probe/challenge.bin`
Lanț complet: **base64 peste un XOR cu cheie de un octet**.

1. `base64.b64decode` → octeți cifrați
2. brute-force XOR pe un octet → **cheie `128` (0x80)**
3. text clar: `FLAG{lant_complet_despicat}`
4. verificare: `md5(clar) = 8c4eb02d9dcef7d0ff91d8e4c7fea91b` — identic cu cel din `challenge_hint.txt`. ✔

---

## Flag-uri recuperate (sumar)
| Sursă | Flag |
|-------|------|
| mesaj.txt (straturi) | `FLAG{straturi_de_encoding}` |
| xor.bin | `FLAG{xor_un_octet}` |
| ascuns.png (carving) | `FLAG{ascuns_prin_carving}` |
| stego.png (LSB) | `FLAG{ascuns_in_pixeli}` |
| challenge.bin | `FLAG{lant_complet_despicat}` |
