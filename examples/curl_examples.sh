#!/usr/bin/env bash
# Ready-to-use cURL requests for Morocco Fiscal Toolkit API

BASE_URL="http://localhost:8000"

echo "=== 1. Validate ICE ==="
curl -s "${BASE_URL}/public/check-ice?ice=001526374000195" | jq .

echo -e "\n=== 2. Validate RIB & Convert to IBAN ==="
curl -s "${BASE_URL}/public/validate-rib?rib=007780000123456789012345" | jq .

echo -e "\n=== 3. Search TVA Rates ==="
curl -s "${BASE_URL}/public/tva-rates/search?q=informatique" | jq .

echo -e "\n=== 4. Calculate Gross to Net Salary ==="
curl -s -X POST "${BASE_URL}/public/salary/net-brut" \
  -H "Content-Type: application/json" \
  -d '{"gross_salary_mad": 15000, "dependents": 2}' | jq .

echo -e "\n=== 5. Check DGI Simpl-TVA Wave ==="
curl -s -X POST "${BASE_URL}/public/dgi-wave-calculator" \
  -H "Content-Type: application/json" \
  -d '{"annual_turnover_mad": 25000000, "regime": "RNR", "legal_form": "SARL"}' | jq .

echo -e "\n=== 6. Postal Code Lookup ==="
curl -s "${BASE_URL}/public/postal/city?zip=20000" | jq .

echo -e "\n=== 7. Phone Number Parser ==="
curl -s "${BASE_URL}/public/phone/parse?phone=0661234567" | jq .
