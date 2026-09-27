# 🇲🇦 Morocco Fiscal Toolkit (`maroc-fiscal-api`)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Tests: 57 Passing](https://img.shields.io/badge/Tests-57%20Passed-success.svg?logo=pytest&logoColor=white)](tests)
[![Conforme CGI & DGI](https://img.shields.io/badge/DGI%20Simpl--TVA-Conforme%20Art.%20145%20CGI-006233.svg)]()

> **The definitive open-source Python SDK & REST API for Moroccan Tax, Banking, DGI E-Invoicing, and Fiscal Compliance.**  
> *L'API publique et le moteur open-source de référence pour les règles fiscales, la facturation électronique DGI Simpl-TVA, le secteur bancaire GPBM et la conformité B2B au Maroc.*

---

## 🌟 Why Morocco Fiscal Toolkit?

Navigating Moroccan fiscal regulations, company tax IDs, banking formats, and e-invoicing mandates is often fragmented across ministries and circulars. **Morocco Fiscal Toolkit** unifies all official algorithms, calculators, and validators into a single, zero-dependency, production-ready Python library and REST API:

- 🏢 **Company & Tax Identifiers**: 15-digit ICE ISO 7064 Modulo-97 validation, branch detection, Identifiant Fiscal (IF), RC + Greffes, CNSS, and OMPIC DirectInfo registry lookup.
- 🏦 **GPBM Banking & IBAN**: 24-digit Moroccan RIB validation, GPBM bank identification (Attijariwafa, BCP, CIH, BMCE BOA, BMCI, CDM, SGMB, etc.), and Moroccan IBAN (MA28) generation.
- 🧾 **TVA / VAT Engine**: Reversible HT ↔ TTC tax calculation and search catalog for Moroccan VAT rates (20%, 14%, 10%, 7%, 0% CGI 2026).
- 💼 **Salary & Payroll (Loi de Finances 2026)**: Gross ↔ Net salary simulator with CNSS (4.48% capped at 6,000 MAD), AMO (2.26%), CIMR, Frais Professionnels (20% capped at 2,500 MAD), and progressive IR barème.
- 🏛️ **DGI Simpl-TVA Mandate Calculator**: Personalized wave eligibility (Phase 1/2/3), countdown timer, and official rollout calendar for the 2026–2028 e-invoicing reform.
- ⚖️ **Loi 69-21 Late Payment Penalties**: Statutory interest computation (Bank Al-Maghrib rate + 0.85%/month), risk assessment, legal payment deadlines, and certified declaration report generation.
- 🛡️ **Invoice Compliance Auditor (Art. 145 CGI)**: 10 mandatory legal mentions validator and sequential chronologic invoice numbering.
- 💸 **Withholding Tax (Retenue à la Source - RAS)**: Official computation for services (10%), dividends (15%), royalties, and bilateral tax treaty overrides.
- 💡 **Tax Regime Simulator**: Comprehensive comparison between Auto-Entrepreneur (1%-2%), CPU (Contribution Professionnelle Unique), and SARL (IS).
- 🏙️ **Postal Codes & Geo**: 5-digit Moroccan Postal code → City, Province, Region, and Arabic name (Barid Al-Maghrib / HCP).
- 📱 **ANRT Phone Classifier**: Telecom operator classification (Maroc Telecom, Orange, Inwi), fixed geographic zones, and E.164 normalization.
- 📷 **Wasl & Payment QR Code Engine**: Decode and generate DGI Simpl-TVA Clearance QR codes and CMI Fatourati interbank payment QR codes.
- 🚚 **Courier COD Reconciliation**: Automated settlement report parser for Cash-on-Delivery couriers (Amana, CTM, Cathedis, Speedy).

---

## 🚀 Quickstart in 30 Seconds

### 1. Installation

```bash
git clone https://github.com/n4ouri/morocco-fiscal-toolkit.git
cd morocco-fiscal-toolkit
pip install -e .
```

### 2. Launch the REST API Server

```bash
uvicorn morocco_fiscal_toolkit.main:app --reload --port 8000
```

* Interactive Swagger UI: [`http://localhost:8000/docs`](http://localhost:8000/docs)
* Interactive ReDoc: [`http://localhost:8000/redoc`](http://localhost:8000/redoc)
* OpenAPI JSON Schema: [`http://localhost:8000/openapi.json`](http://localhost:8000/openapi.json)

### 3. Launch with Docker

```bash
docker-compose up --build
```

---

## 🐍 Python SDK Usage

Use it directly in your Python applications, Odoo modules, Django backends, or data pipelines without running a server:

```python
from morocco_fiscal_toolkit import (
    validate_ice,
    validate_rib,
    calculate_tva,
    calculate_salary_net,
    calculate_dgi_wave,
    calculate_loi_69_21_penalty,
    lookup_postal_code,
    parse_phone_number,
    compute_withholding_tax,
)

# 1. Validate Moroccan ICE (Modulo 97 + OMPIC company lookup)
ice = validate_ice("001526374000195")
print(ice["is_valid"])      # True
print(ice["checksum_ok"])   # True
print(ice["company_name"])  # MAROC TELECOM (ITISSALAT AL-MAGHRIB SA)

# 2. Validate Moroccan 24-digit RIB and get Moroccan IBAN (MA28)
rib = validate_rib("007780000123456789012345")
print(rib["bank_name"])      # Attijariwafa Bank
print(rib["iban"])           # MA64007780000123456789012345
print(rib["formatted_iban"]) # MA64 007 780 0001 2345 6789 0123 45

# 3. Calculate TVA (HT -> TTC or TTC -> HT)
tva = calculate_tva(amount=1000.0, rate=0.20, is_ttc=False)
print(tva["amount_tva"])  # 200.0 MAD
print(tva["amount_ttc"])  # 1200.0 MAD

# 4. Gross to Net Salary (Loi de Finances 2026 progressive IR + CNSS + AMO)
payroll = calculate_salary_net(gross_monthly=15000.0, dependents=2)
print(payroll["net_monthly_mad"])            # 11957.50 MAD
print(payroll["deductions"]["cnss_mad"])      # 268.80 MAD (capped at 6k)
print(payroll["deductions"]["amo_mad"])       # 339.00 MAD
print(payroll["deductions"]["ir_monthly_mad"])# 2434.70 MAD

# 5. DGI Simpl-TVA E-Invoicing Mandate Wave
wave = calculate_dgi_wave(annual_turnover_mad=35_000_000, regime="RNR", legal_form="SARL")
print(wave["wave_name"])         # Phase 2 : Moyennes Entreprises
print(wave["effective_date_str"])# 01/07/2026

# 6. Loi 69-21 Late Payment Penalty
penalty = calculate_loi_69_21_penalty(amount_ttc=50000.0, days_overdue=45)
print(penalty["penalty_amount_mad"]) # 1100.0 MAD

# 7. Postal Code & City Lookup (Barid Al-Maghrib)
postal = lookup_postal_code("20000")
print(postal["city"])        # Casablanca
print(postal["arabic_name"]) # الدار البيضاء
print(postal["region"])      # Casablanca-Settat

# 8. Phone Number Operator Classifier (ANRT)
phone = parse_phone_number("0661234567")
print(phone["operator"])     # Orange Maroc / Maroc Telecom
print(phone["international"])# +212661234567

# 9. Retenue à la Source (RAS)
ras = compute_withholding_tax(income_type="HONORAIRES_SERVICES", gross_amount=20000.0)
print(ras["ras_amount_mad"]) # 2000.0 MAD (10%)
print(ras["net_amount_mad"]) # 18000.0 MAD
```

---

## 💻 Command-Line Interface (CLI)

The package includes a rich CLI tool `morocco-fiscal-toolkit` (or alias `maroc-fiscal`):

```bash
# Verify ICE
morocco-fiscal-toolkit check-ice 001526374000195

# Validate RIB and output bank details
morocco-fiscal-toolkit validate-rib 007780000123456789012345

# Convert RIB to Moroccan IBAN
morocco-fiscal-toolkit rib-to-iban 007780000123456789012345

# Calculate Net Salary from Gross (MAD)
morocco-fiscal-toolkit calculate-salary 15000 --dependents 2

# Search TVA rate by keyword
morocco-fiscal-toolkit search-tva "transport"

# Lookup postal code
morocco-fiscal-toolkit postal-lookup 20000

# Parse phone number
morocco-fiscal-toolkit phone-parse 0661234567

# Calculate Loi 69-21 late payment penalty
morocco-fiscal-toolkit loi-69-21-penalty 50000 45

# Start REST API server
morocco-fiscal-toolkit serve --port 8000
```

---

## 📡 REST API Reference

| Category | Method | Endpoint | Description |
|---|---|---|---|
| **Company & Tax** | `GET` | `/public/check-ice?ice=...` | Validates 15-digit ICE Mod-97 + OMPIC company lookup |
| **Company & Tax** | `GET` | `/public/validate-if?if=...` | Validates Moroccan Identifiant Fiscal (IF) |
| **Company & Tax** | `GET` | `/public/validate-rc?rc=...&tribunal=...` | Validates Registre du Commerce + Greffe |
| **Company & Tax** | `GET` | `/public/validate-cnss?cnss=...` | Validates CNSS affiliation number |
| **Company & Tax** | `GET` | `/public/registry/search?q=...` | Searches OMPIC company registry by denomination |
| **Company & Tax** | `POST`| `/public/batch/validate-ices` | Batch validates up to 50 ICEs in one call |
| **Banking** | `GET` | `/public/validate-rib?rib=...` | Validates 24-digit RIB, detects bank, returns IBAN MA28 |
| **Banking** | `GET` | `/public/bank/rib-to-iban?rib=...` | Direct conversion of 24-digit RIB to Moroccan IBAN |
| **TVA / VAT** | `GET` | `/public/tva-rates/search?q=...` | Searches VAT rates by keyword/product (CGI 2026) |
| **TVA / VAT** | `POST`| `/public/tva-rates/calculate` | Calculates HT ↔ TVA ↔ TTC for any VAT rate |
| **Payroll / HR** | `POST`| `/public/salary/net-brut` | Gross ↔ Net salary simulator (CNSS, AMO, CIMR, IR 2026) |
| **DGI Simpl-TVA**| `POST`| `/public/dgi-wave-calculator` | Calculates Simpl-TVA mandate wave (Phase 1/2/3) & countdown |
| **DGI Simpl-TVA**| `GET` | `/public/dgi-calendar` | Official DGI e-invoicing rollout calendar |
| **DGI Simpl-TVA**| `GET` | `/public/simpl-tva-status` | Live status tracker of Simpl-TVA platform specifications |
| **Loi 69-21** | `POST`| `/public/loi-69-21/risk-check` | Assesses risk of late payment penalties (5k–250k MAD) |
| **Loi 69-21** | `POST`| `/public/loi-69-21/invoice-penalty` | Computes statutory late payment penalty on an invoice |
| **Loi 69-21** | `POST`| `/public/loi-69-21/payment-deadline`| Computes legal payment deadline (capped at 120 days) |
| **Loi 69-21** | `POST`| `/public/loi-69-21/generate-declaration`| Generates official detailed overdue invoices report |
| **Compliance** | `POST`| `/public/invoice-compliance/audit` | Audits invoice against 10 mandatory legal mentions (Art. 145 CGI) |
| **Compliance** | `POST`| `/public/invoice-number/generate` | Generates chronological DGI-compliant invoice number |
| **Tax Simulation**| `POST`| `/public/tax-regime/simulate` | Simulates Auto-Entrepreneur vs CPU vs SARL IS |
| **Withholding** | `GET` | `/public/withholding-tax/types` | Lists all Moroccan Retenue à la Source (RAS) types |
| **Withholding** | `POST`| `/public/withholding-tax/compute` | Computes Retenue à la Source (RAS) amount |
| **Geography** | `GET` | `/public/postal/city?zip=...` | Moroccan Postal code → City, Province, Region, Arabic name |
| **Telecoms** | `GET` | `/public/phone/parse?phone=...` | Parses phone number, detects operator (IAM, Orange, Inwi) |
| **QR Codes** | `POST`| `/public/qr-invoice/decode` | Decodes Simpl-TVA / Fatourati QR codes |
| **QR Codes** | `GET` | `/public/qr-invoice/demo-sample` | Generates sample QR codes with base64 PNG images |
| **Courier / COD** | `POST`| `/public/courier-cod/parse` | Parses courier COD settlement slip (Amana, CTM, Speedy) |
| **Fiscal Year** | `GET` | `/public/fiscal-year/deadlines` | Comprehensive tax deadlines by regime & frequency |

---

## 🧪 Running Tests

```bash
pytest tests -v
```

All 57 unit and integration tests validate the Modulo-97 algorithm, bank codes, VAT formulas, LF 2026 progressive brackets, and REST endpoints.

---

## 🚢 Production Deployment

### Docker

```bash
docker run -d -p 8000:8000 --name morocco-fiscal-toolkit n4ouri/morocco-fiscal-toolkit
```

### Cloud / PaaS
Ready to deploy on **Render**, **Railway**, **Fly.io**, or **Vercel** (with standard ASGI runtime).

---

## 📄 License

Distributed under the **MIT License**. Free for commercial and open-source use. See [`LICENSE`](LICENSE) for details.

*Maintained by [@n4ouri](https://github.com/n4ouri) in partnership with the [Fatoura.ma](https://fatoura.ma) ecosystem.*
