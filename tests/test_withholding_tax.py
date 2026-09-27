import pytest
from morocco_fiscal_toolkit import (
    compute_withholding_tax,
    MoroccanWithholdingTax,
)

def test_withholding_tax_honoraires():
    # 10% default RAS on honoraires/services
    res = compute_withholding_tax(income_type="HONORAIRES_SERVICES", gross_amount=10000.0)
    assert res["is_valid"] is True
    assert res["gross_amount_mad"] == 10000.0
    assert res["ras_amount_mad"] == 1000.0
    assert res["net_amount_mad"] == 9000.0

def test_withholding_tax_dividendes():
    # 15% RAS on dividends for resident individuals
    res = compute_withholding_tax(income_type="DIVIDENDES_RESIDENTS", gross_amount=20000.0)
    assert res["standard_rate_pct"] == "15%"
    assert res["ras_amount_mad"] == 3000.0

def test_withholding_tax_convention_rate():
    # Treaty reduced rate (e.g., 5%)
    res = compute_withholding_tax(income_type="ROYALTIES_ETRANGER", gross_amount=50000.0, convention_rate=0.05)
    assert res["applied_rate_pct"] == "5.0%"
    assert res["ras_amount_mad"] == 2500.0
