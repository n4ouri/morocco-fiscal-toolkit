import pytest
from morocco_fiscal_toolkit import (
    calculate_dgi_wave,
    DgiMandateCalculator,
)

def test_wave_large_enterprise():
    # CA > 100M MAD -> Phase 1
    res = calculate_dgi_wave(annual_turnover_mad=150_000_000, regime="RNR", legal_form="SA")
    assert res["wave_id"] == "PHASE_1"
    assert "Grandes Entreprises" in res["wave_name"]

def test_wave_medium_enterprise():
    # CA 20M - 100M MAD -> Phase 2
    res = calculate_dgi_wave(annual_turnover_mad=45_000_000, regime="RNR", legal_form="SARL")
    assert res["wave_id"] == "PHASE_2"
    assert "Moyennes Entreprises" in res["wave_name"]

def test_wave_small_enterprise():
    # CA < 20M MAD -> Phase 3
    res = calculate_dgi_wave(annual_turnover_mad=5_000_000, regime="RNR", legal_form="SARL")
    assert res["wave_id"] == "PHASE_3"
    assert "Généralisation" in res["wave_name"]
