# -*- coding: utf-8 -*-
"""Teste pentru clasele Windows (Lucrarea B)."""
from arsenal.windows.inventar import Proces


def test_proces_din_temp_e_suspect():
    p = Proces(1, "x.exe", "ana", "C:\\Users\\ana\\AppData\\Local\\Temp\\x.exe")
    assert p.e_suspect() is True


def test_proces_din_windows_nu_e_suspect():
    p = Proces(2, "svchost.exe", "SYSTEM", "C:\\Windows\\System32\\svchost.exe")
    assert p.e_suspect() is False


def test_temp_cu_litere_mici_e_suspect():
    p = Proces(3, "y.exe", "ana", "C:\\Users\\ana\\AppData\\Local\\temp\\y.exe")
    assert p.e_suspect() is True
