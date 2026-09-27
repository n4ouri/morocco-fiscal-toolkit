import pytest
from morocco_fiscal_toolkit import (
    search_tva,
    calculate_tva,
    MoroccanTvaCatalog,
)

def test_search_tva():
    res = search_tva("transport")
    assert len(res) > 0
    assert any(item["rate"] == 0.14 for item in res)

def test_search_tva_services():
    res = search_tva("informatique")
    assert len(res) > 0
    assert any(item["rate"] == 0.20 for item in res)

def test_calculate_tva_from_ht():
    res = calculate_tva(amount=1000.0, rate=0.20, is_ttc=False)
    assert res["amount_ht"] == 1000.0
    assert res["amount_tva"] == 200.0
    assert res["amount_ttc"] == 1200.0

def test_calculate_tva_from_ttc():
    res = calculate_tva(amount=1200.0, rate=0.20, is_ttc=True)
    assert res["amount_ttc"] == 1200.0
    assert abs(res["amount_ht"] - 1000.0) < 0.01
    assert abs(res["amount_tva"] - 200.0) < 0.01

def test_calculate_tva_reduced_rate():
    res = calculate_tva(amount=100.0, rate=0.10, is_ttc=False)
    assert res["amount_tva"] == 10.0
    assert res["amount_ttc"] == 110.0
