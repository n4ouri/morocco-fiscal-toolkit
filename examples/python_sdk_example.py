"""
Example: Using morocco-fiscal-toolkit as a pure Python library
"""

from morocco_fiscal_toolkit import (
    validate_ice,
    validate_rib,
    calculate_moroccan_iban,
    search_tva,
    calculate_tva,
    calculate_salary_net,
    calculate_salary_gross,
    calculate_dgi_wave,
    calculate_loi_69_21_penalty,
    audit_invoice_compliance,
    compute_withholding_tax,
    lookup_postal_code,
    parse_phone_number,
    generate_simpl_tva_qr,
    decode_qr,
)

print("=== 1. ICE & Modulo 97 Verification ===")
ice_res = validate_ice("001526374000195")
print(f"ICE: {ice_res['ice']} | Valid: {ice_res['is_valid']} | Checksum OK: {ice_res['checksum_ok']}")
print(f"Company: {ice_res.get('company_name')} | Form: {ice_res.get('legal_form')}")

print("\n=== 2. Banking: RIB 24 digits to Moroccan IBAN ===")
rib_res = validate_rib("007780000123456789012345")
print(f"Bank: {rib_res['bank_name']} (SWIFT: {rib_res['swift_bic']})")
print(f"Formatted RIB:  {rib_res['formatted_rib']}")
print(f"Moroccan IBAN:  {rib_res['formatted_iban']}")

print("\n=== 3. TVA Search & Reversible Calculation ===")
tva_calc = calculate_tva(amount=1000.0, rate=0.20, is_ttc=False)
print(f"1,000 MAD HT @ 20% -> TVA: {tva_calc['amount_tva']} MAD | TTC: {tva_calc['amount_ttc']} MAD")

print("\n=== 4. Salary Simulator (Loi de Finances 2026) ===")
salary_res = calculate_salary_net(gross_monthly=15000.0, dependents=2)
print(f"Gross: 15,000 MAD -> Net: {salary_res['net_monthly_mad']} MAD/month")
print(f"CNSS: {salary_res['deductions']['cnss_mad']} MAD | AMO: {salary_res['deductions']['amo_mad']} MAD | IR: {salary_res['deductions']['ir_monthly_mad']} MAD")

print("\n=== 5. DGI Simpl-TVA Mandate Wave ===")
dgi_wave = calculate_dgi_wave(annual_turnover_mad=15_000_000.0, regime="RNR", legal_form="SARL")
print(f"Mandate: {dgi_wave['wave_name']} (Target date: {dgi_wave['effective_date_str']})")

print("\n=== 6. Postal Code & Phone Lookup ===")
postal = lookup_postal_code("20000")
print(f"Code Postal 20000 -> {postal['city']} ({postal['arabic_name']}), {postal['region']}")

phone = parse_phone_number("0661234567")
print(f"Phone 0661234567 -> Operator: {phone['operator']} | Type: {phone['line_type_label']} | Int: {phone['international']}")

print("\n=== 7. Withholding Tax (Retenue à la Source RAS) ===")
ras = compute_withholding_tax(income_type="HONORAIRES_SERVICES", gross_amount=25000.0)
print(f"Honoraires 25,000 MAD -> RAS 10%: {ras['ras_amount_mad']} MAD | Net to pay: {ras['net_amount_mad']} MAD")
