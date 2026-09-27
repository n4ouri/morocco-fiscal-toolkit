"""
morocco-fiscal-toolkit (maroc-fiscal-api)
=========================================
Open-source Moroccan Tax, DGI E-Invoicing, TVA, Banking & Fiscal Compliance Engine.

Modules & Capabilities:
- ICE (Identifiant Commun de l'Entreprise) Modulo 97 & OMPIC Registry Lookup
- IF (Identifiant Fiscal), RC (Registre du Commerce), CNSS affiliation
- GPBM 24-digit RIB & Moroccan IBAN (MA28) Modulo 97 validation and bank lookup
- Moroccan TVA / VAT Rates Catalog & Calculations (CGI 2026 - 20%, 14%, 10%, 7%, 0%)
- DGI Simpl-TVA E-Invoicing Mandate Wave Calculator & Official Rollout Calendar
- Loi 69-21 Late Payment Penalties & Statutory Payment Deadlines
- Invoice Legal Mentions Compliance Auditor (Article 145 CGI) & Sequential Numbering
- Gross ↔ Net Salary & Payroll Simulator (LF 2026 progressive IR barème, CNSS, AMO, CIMR)
- Tax Regime Simulator (Auto-Entrepreneur vs CPU vs SARL IS)
- Retenue à la Source (RAS / Withholding Tax) Calculator
- 5-digit Moroccan Postal Code Lookup (Barid Al-Maghrib / HCP)
- Moroccan Phone Number Parser & Telecom Operator Classifier (IAM, Orange, Inwi)
- Simpl-TVA Wasl & CMI Fatourati QR Code Decoder & Generator
- Annual Fiscal Calendar by Regime & Frequency
- Courier COD/CRBT Settlement Statement Parser (Amana, CTM, Speedy)
"""

__version__ = "1.0.0"
__author__ = "n4ouri"
__license__ = "MIT"

# Services
from morocco_fiscal_toolkit.services.ice_checker import MoroccanTaxValidators
from morocco_fiscal_toolkit.services.authenticated_adapter import DirectInfoAuthenticatedAdapter, KNOWN_AUTHENTICATED_REGISTRY
from morocco_fiscal_toolkit.services.rib_validator import MoroccanRibValidator
from morocco_fiscal_toolkit.services.tva_finder import MoroccanTvaCatalog
from morocco_fiscal_toolkit.services.salary_simulator import MoroccanSalarySimulator
from morocco_fiscal_toolkit.services.dgi_calculator import DgiMandateCalculator
from morocco_fiscal_toolkit.services.loi_69_21 import Loi6921Service
from morocco_fiscal_toolkit.services.compliance_checker import InvoiceComplianceChecker
from morocco_fiscal_toolkit.services.cpu_simulator import MoroccanTaxRegimeSimulator
from morocco_fiscal_toolkit.services.withholding_tax import MoroccanWithholdingTax
from morocco_fiscal_toolkit.services.postal_lookup import MoroccanPostalLookup
from morocco_fiscal_toolkit.services.phone_validator import MoroccanPhoneValidator
from morocco_fiscal_toolkit.services.qr_decoder import WaslQrDecoder
from morocco_fiscal_toolkit.services.qr_generator import InvoiceQrService
from morocco_fiscal_toolkit.services.fiscal_calendar import MoroccanFiscalCalendar
from morocco_fiscal_toolkit.services.courier_reconciliation import CourierReconciliationService

# Top-level functional shortcuts for Python library usage
validate_ice = MoroccanTaxValidators.validate_ice
validate_if = MoroccanTaxValidators.validate_if
validate_rc = MoroccanTaxValidators.validate_rc
validate_cnss = MoroccanTaxValidators.validate_cnss
validate_rib = MoroccanRibValidator.validate_rib
calculate_moroccan_iban = MoroccanRibValidator.calculate_moroccan_iban

search_tva = MoroccanTvaCatalog.search
calculate_tva = MoroccanTvaCatalog.calculate_simulation

calculate_salary_net = MoroccanSalarySimulator.gross_to_net
calculate_salary_gross = MoroccanSalarySimulator.net_to_gross

calculate_dgi_wave = DgiMandateCalculator.calculate_wave
calculate_loi_69_21_penalty = Loi6921Service.calculate_invoice_penalty
check_loi_69_21_risk = Loi6921Service.assess_risk

audit_invoice_compliance = InvoiceComplianceChecker.audit_invoice
simulate_tax_regime = MoroccanTaxRegimeSimulator.simulate
compute_withholding_tax = MoroccanWithholdingTax.compute

lookup_postal_code = MoroccanPostalLookup.lookup
parse_phone_number = MoroccanPhoneValidator.validate

decode_qr = WaslQrDecoder.decode_and_verify
generate_simpl_tva_qr = InvoiceQrService.generate_simpl_tva_payload
generate_fatourati_qr = InvoiceQrService.generate_fatourati_payment_qr
get_fiscal_calendar = MoroccanFiscalCalendar.get_calendar
parse_courier_statement = CourierReconciliationService.parse_courier_statement

__all__ = [
    # Top-level functions
    "validate_ice",
    "validate_if",
    "validate_rc",
    "validate_cnss",
    "validate_rib",
    "calculate_moroccan_iban",
    "search_tva",
    "calculate_tva",
    "calculate_salary_net",
    "calculate_salary_gross",
    "calculate_dgi_wave",
    "calculate_loi_69_21_penalty",
    "check_loi_69_21_risk",
    "audit_invoice_compliance",
    "simulate_tax_regime",
    "compute_withholding_tax",
    "lookup_postal_code",
    "parse_phone_number",
    "decode_qr",
    "generate_simpl_tva_qr",
    "generate_fatourati_qr",
    "get_fiscal_calendar",
    "parse_courier_statement",
    # Service classes
    "MoroccanTaxValidators",
    "DirectInfoAuthenticatedAdapter",
    "KNOWN_AUTHENTICATED_REGISTRY",
    "MoroccanRibValidator",
    "MoroccanTvaCatalog",
    "MoroccanSalarySimulator",
    "DgiMandateCalculator",
    "Loi6921Service",
    "InvoiceComplianceChecker",
    "MoroccanTaxRegimeSimulator",
    "MoroccanWithholdingTax",
    "MoroccanPostalLookup",
    "MoroccanPhoneValidator",
    "WaslQrDecoder",
    "InvoiceQrService",
    "MoroccanFiscalCalendar",
    "CourierReconciliationService",
]
