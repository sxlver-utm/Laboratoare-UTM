# -*- coding: utf-8 -*-
"""Teste pentru detectorul de brute force (Lucrarea B)."""
from collections import Counter

import pytest

from arsenal.aparare.detector import suspecti


def test_pragul_taie():
    c = Counter({"a": 13, "b": 2})
    assert suspecti(c, 10) == [("a", 13)]


def test_prag_invalid():
    with pytest.raises(ValueError):
        suspecti({}, 0)
