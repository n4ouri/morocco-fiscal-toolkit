import pytest
from morocco_fiscal_toolkit import (
    calculate_salary_net,
    calculate_salary_gross,
    MoroccanSalarySimulator,
)

def test_gross_to_net_low_salary():
    res = calculate_salary_net(gross_monthly=3500.0)
    assert res["gross_monthly_mad"] == 3500.0
    assert res["deductions"]["cnss_mad"] > 0
    assert res["deductions"]["amo_mad"] > 0
    assert res["net_monthly_mad"] < 3500.0

def test_cnss_ceiling():
    # CNSS is capped at 6000 MAD / month
    res = calculate_salary_net(gross_monthly=20000.0)
    assert res["deductions"]["cnss_mad"] == round(6000.0 * 0.0448, 2)
    # AMO is uncapped
    assert res["deductions"]["amo_mad"] == round(20000.0 * 0.0226, 2)

def test_reversible_net_to_gross():
    # Calculate net from 15000 MAD gross, then convert back
    forward = calculate_salary_net(gross_monthly=15000.0)
    target_net = forward["net_monthly_mad"]

    reverse = calculate_salary_gross(net_monthly=target_net)
    assert abs(reverse["estimated_gross_monthly_mad"] - 15000.0) < 5.0

def test_dependents_tax_credit():
    res_no_dep = calculate_salary_net(gross_monthly=12000.0, dependents=0)
    res_with_dep = calculate_salary_net(gross_monthly=12000.0, dependents=3)
    assert res_with_dep["net_monthly_mad"] > res_no_dep["net_monthly_mad"]
