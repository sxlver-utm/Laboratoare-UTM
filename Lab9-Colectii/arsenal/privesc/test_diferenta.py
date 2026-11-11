# -*- coding: utf-8 -*-
"""Test pentru diferenta de multimi (Lucrarea B)."""


def test_doar_ce_e_nou():
    acum = {"a", "b", "c"}
    baza = {"a", "b"}
    assert acum - baza == {"c"}
