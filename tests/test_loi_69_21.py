import pytest
from morocco_fiscal_toolkit import (
    calculate_loi_69_21_penalty,
    check_loi_69_21_risk,
    Loi6921Service,
)

def test_calculate_loi_69_21_penalty():
    # 50,000 MAD invoice overdue by 45 days
    res = calculate_loi_69_21_penalty(amount_ttc=50000.0, days_overdue=45)
    assert res["is_overdue"] is True
    assert res["penalty_amount_mad"] > 0
    assert res["monthly_rate_pct"] > 0

def test_risk_check_subject_company():
    # Turnover > 2M MAD is subject to Loi 69-21
    res = check_loi_69_21_risk(
        annual_turnover_mad=10_000_000.0,
        total_overdue_ttc=250_000.0,
        avg_delay_days=60,
        overdue_invoices_count=5
    )
    assert res["in_scope"] is True
    assert res["risk_level"] in ("ÉLEVÉ", "MODÉRÉ", "FAIBLE")
    assert res["fine_non_declaration_mad"] > 0
