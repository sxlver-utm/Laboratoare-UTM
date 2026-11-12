# -*- coding: utf-8 -*-
"""Teste pentru decoderul universal (A7)."""
from arsenal.forensics.decode import (
    ghici_strat, desfa, citibil, desfa_straturi, sparge_xor1, sparge_hash,
)


def test_base64():
    strat, b = desfa("U2FsdXQ=")
    assert strat == "base64"
    assert b == b"Salut"


def test_ghici_strat():
    assert ghici_strat("%2Fetc") == "url"
    assert ghici_strat("48656c6c6f") == "hex"
    assert ghici_strat("U2FsdXQ=") == "base64"
    assert ghici_strat("FLAG{x}") == "necunoscut"


def test_hex():
    strat, b = desfa("48656c6c6f")
    assert strat == "hex"
    assert b == b"Hello"


def test_url():
    strat, b = desfa("%2Fetc%2Fpasswd")
    assert strat == "url"
    assert b == b"/etc/passwd"


def test_citibil():
    assert citibil(b"Salut")
    assert not citibil(b"\x00\x80\xff")


def test_straturi_multiple():
    # base64(base64(hex("53")))  -> "53" e hexul lui 'S'
    straturi, b = desfa_straturi("TkRZMFl6UXhORGMz"[:0] or
                                 "TkRZMFl6UXhORGMzWWpjek56UTNNall4"
                                 "TnpRM05UY3lOamsxWmpZME5qVTFaalkx"
                                 "Tm1VMk16Wm1OalEyT1RabE5qYzNaQT09")
    assert b == b"FLAG{straturi_de_encoding}"
    assert straturi == ["base64", "base64", "hex"]


def test_xor_un_octet():
    date = bytes(b ^ 0x80 for b in b"Hello FLAG{x}")
    cheie, clar = sparge_xor1(date)
    assert cheie == 0x80
    assert clar == b"Hello FLAG{x}"


def test_hash_dictionar(tmp_path):
    import hashlib
    wl = tmp_path / "wl.txt"
    wl.write_text("aaa\npassword\nbbb\n")
    tinta = hashlib.md5(b"password").hexdigest()
    algo, parola = sparge_hash(tinta, str(wl))
    assert algo == "md5"
    assert parola == "password"


def test_text_clar_nu_e_decodat():
    # "parola12" arata a base64, dar decodat da octeti fara sens
    straturi, b = desfa_straturi("parola12")
    assert straturi == []
    assert b == b"parola12"


def test_xor_nu_intoarce_cheia_zero():
    cheie, clar = sparge_xor1(b"deja citibil")
    assert cheie != 0


def test_lant_base64_peste_xor():
    import base64
    cifrat = bytes(c ^ 0x80 for c in b"FLAG{lant}")
    straturi, b = desfa_straturi(base64.b64encode(cifrat).decode())
    assert straturi == ["base64", "xor1(cheie=128)"]
    assert b == b"FLAG{lant}"
