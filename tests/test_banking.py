import pytest
from morocco_fiscal_toolkit import (
    validate_rib,
    calculate_moroccan_iban,
    MoroccanRibValidator,
)

def test_valid_rib_attijari():
    # Attijariwafa bank code 007
    raw_rib = "007780000123456789012345"
    res = validate_rib(raw_rib)
    assert res["is_valid"] is True
    assert res["bank_code"] == "007"
    assert "Attijariwafa" in res["bank_name"]
    assert res["iban"].startswith("MA")
    assert len(res["iban"]) == 28

def test_valid_rib_cih():
    # CIH bank code 230
    raw_rib = "230780000123456789012345"
    res = validate_rib(raw_rib)
    assert res["is_valid"] is True
    assert res["bank_code"] == "230"
    assert "CIH" in res["bank_name"]

def test_rib_with_spaces_and_dashes():
    rib = "007 780 0001234567890123 45"
    res = validate_rib(rib)
    assert res["is_valid"] is True
    assert res["rib"] == "007780000123456789012345"

def test_iban_input_handling():
    iban = "MA64007780000123456789012345"
    res = validate_rib(iban)
    assert res["is_valid"] is True
    assert res["rib"] == "007780000123456789012345"

def test_invalid_rib_length():
    res = validate_rib("0077800001234")
    assert res["is_valid"] is False
    assert "24 chiffres" in res["error"]

def test_mod97_calculation():
    base_22 = "0077800001234567890123"
    key = MoroccanRibValidator.calculate_mod97_key(base_22)
    assert len(key) == 2
    assert key.isdigit()
