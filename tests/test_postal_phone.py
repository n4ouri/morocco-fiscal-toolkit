import pytest
from morocco_fiscal_toolkit import (
    lookup_postal_code,
    parse_phone_number,
    MoroccanPostalLookup,
    MoroccanPhoneValidator,
)

def test_postal_casablanca():
    res = lookup_postal_code("20000")
    assert res["is_valid"] is True
    assert res["city"] == "Casablanca"
    assert "Casablanca-Settat" in res["region"]
    assert res["arabic_name"] == "الدار البيضاء"

def test_postal_rabat():
    res = lookup_postal_code("10000")
    assert res["is_valid"] is True
    assert res["city"] == "Rabat"

def test_postal_invalid():
    res = lookup_postal_code("123")
    assert res["is_valid"] is False

def test_phone_maroc_telecom():
    res = parse_phone_number("0661234567")
    assert res["is_valid"] is True
    assert res["line_type"] == "MOBILE"
    assert "Orange" in res["operator"] or "Maroc Telecom" in res["operator"]
    assert res["international"] == "+212661234567"

def test_phone_fixed_casablanca():
    res = parse_phone_number("0522123456")
    assert res["is_valid"] is True
    assert res["line_type"] == "FIXED"
    assert "Casablanca" in res["region"]

def test_phone_international_prefix():
    res = parse_phone_number("+212670123456")
    assert res["is_valid"] is True
    assert "Inwi" in res["operator"]
