import pytest
from morocco_fiscal_toolkit import (
    validate_ice,
    validate_if,
    validate_rc,
    validate_cnss,
    MoroccanTaxValidators,
    DirectInfoAuthenticatedAdapter,
)

def test_ice_modulo97_valid():
    # Maroc Telecom headquarters ICE (branch 0001, key 95)
    res = validate_ice("001526374000195")
    assert res["is_valid"] is True
    assert res["ice"] == "001526374000195"
    assert res["company_id"] == "001526374"
    assert res["branch_id"] == "0001"
    assert res["checksum_ok"] is True

def test_ice_invalid_length():
    res = validate_ice("12345")
    assert res["is_valid"] is False
    assert "15 chiffres" in res["error"]

def test_ice_invalid_letters():
    res = validate_ice("001526374000ABC")
    assert res["is_valid"] is False
    assert "chiffres" in res["error"]

def test_ice_all_zeros():
    res = validate_ice("000000000000000")
    assert res["is_valid"] is False

def test_validate_if():
    res = validate_if("01085203")
    assert res["is_valid"] is True
    assert res["if"] == "01085203"

    res_inv = validate_if("123")
    assert res_inv["is_valid"] is False

def test_validate_rc():
    res = validate_rc("48154", "Rabat")
    assert res["is_valid"] is True
    assert res["rc"] == "48154"
    assert res["tribunal"] == "Rabat"

def test_validate_cnss():
    res = validate_cnss("1849201")
    assert res["is_valid"] is True
    assert res["cnss"] == "1849201"

def test_ompic_search():
    adapter = DirectInfoAuthenticatedAdapter()
    results = adapter.search_by_name("MAROC TELECOM", limit=5)
    assert len(results) > 0
    assert "MAROC TELECOM" in results[0]["company_name"]
