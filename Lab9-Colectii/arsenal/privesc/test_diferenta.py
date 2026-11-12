# -*- coding: utf-8 -*-
"""Teste pentru diferenta de multimi (Lucrarea B)."""
from arsenal.privesc.diferenta import cai
from arsenal.privesc.enum import nume, GTFO


def test_doar_ce_e_nou():
    acum = {"a", "b", "c"}
    baza = {"a", "b"}
    assert acum - baza == {"c"}


def test_suid_noi_periculoase_din_capturi():
    noi = cai("suid.txt") - cai("baza_suid.txt")
    periculoase = sorted(nume(c) for c in noi if nume(c) in GTFO)
    assert periculoase == ["cp", "find", "nmap", "vim.basic"]
