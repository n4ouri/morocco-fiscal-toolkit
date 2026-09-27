import pytest
from fastapi.testclient import TestClient
from morocco_fiscal_toolkit.main import app

client = TestClient(app)

def test_root_info():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "Morocco Fiscal Toolkit" in data["name"]

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_endpoint_check_ice():
    response = client.get("/public/check-ice?ice=001526374000195")
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is True
    assert "MAROC TELECOM" in data.get("company_name", "")

def test_endpoint_validate_if():
    response = client.get("/public/validate-if?if=01085203")
    assert response.status_code == 200
    assert response.json()["is_valid"] is True

def test_endpoint_validate_rc():
    response = client.get("/public/validate-rc?rc=48154&tribunal=Rabat")
    assert response.status_code == 200
    assert response.json()["is_valid"] is True

def test_endpoint_validate_cnss():
    response = client.get("/public/validate-cnss?cnss=1849201")
    assert response.status_code == 200
    assert response.json()["is_valid"] is True

def test_endpoint_validate_rib():
    response = client.get("/public/validate-rib?rib=007780000123456789012345")
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is True
    assert "Attijariwafa" in data["bank_name"]

def test_endpoint_rib_to_iban():
    response = client.get("/public/bank/rib-to-iban?rib=007780000123456789012345")
    assert response.status_code == 200
    data = response.json()
    assert data["iban"].startswith("MA")

def test_endpoint_search_tva():
    response = client.get("/public/tva-rates/search?q=informatique")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_endpoint_calculate_tva():
    response = client.post("/public/tva-rates/calculate", json={"amount": 1000, "rate": 0.20, "is_ttc": False})
    assert response.status_code == 200
    data = response.json()
    assert data["amount_ttc"] == 1200.0

def test_endpoint_salary_calculator():
    response = client.post("/public/salary/net-brut", json={"gross_salary_mad": 10000.0, "dependents": 2})
    assert response.status_code == 200
    data = response.json()
    assert data["net_monthly_mad"] > 0

def test_endpoint_dgi_wave():
    response = client.post("/public/dgi-wave-calculator", json={"annual_turnover_mad": 150000000, "regime": "RNR", "legal_form": "SA"})
    assert response.status_code == 200
    assert response.json()["wave_id"] == "PHASE_1"

def test_endpoint_dgi_calendar():
    response = client.get("/public/dgi-calendar")
    assert response.status_code == 200
    assert len(response.json()["waves"]) == 3

def test_endpoint_postal():
    response = client.get("/public/postal/city?zip=20000")
    assert response.status_code == 200
    assert response.json()["city"] == "Casablanca"

def test_endpoint_phone():
    response = client.get("/public/phone/parse?phone=0661234567")
    assert response.status_code == 200
    assert response.json()["is_valid"] is True

def test_endpoint_withholding():
    response = client.post("/public/withholding-tax/compute", json={"income_type": "HONORAIRES_SERVICES", "gross_amount": 10000})
    assert response.status_code == 200
    assert response.json()["ras_amount_mad"] == 1000.0
