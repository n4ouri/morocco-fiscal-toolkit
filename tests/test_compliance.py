import pytest
from morocco_fiscal_toolkit import (
    audit_invoice_compliance,
    InvoiceComplianceChecker,
)

def test_invoice_compliance_valid():
    invoice_data = {
        "seller_ice": "001526374000195",
        "buyer_ice": "001524368000042",
        "seller_if": "01085203",
        "rc": "48154",
        "tribunal": "Rabat",
        "cnss": "1849201",
        "invoice_number": "FAC-2026-0001",
        "issue_date": "2026-09-27",
        "tva_rate": 0.20,
        "total_ht": 10000.0,
        "total_tva": 2000.0,
        "total_ttc": 12000.0,
        "unit_prices": [10000.0],
        "payment_method": "VIREMENT",
    }
    res = audit_invoice_compliance(invoice_data)
    assert res["score"] >= 70
    assert "badge" in res

def test_invoice_compliance_missing_ice():
    invoice_data = {
        "invoice_number": "FAC-2026-0001",
        "issue_date": "2026-09-27",
        "total_ttc": 500.0
    }
    res = audit_invoice_compliance(invoice_data)
    assert res["score"] < 50
    assert any(c["id"] == "seller_ice" and not c["is_valid"] for c in res["checks"])
