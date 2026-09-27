// Morocco Fiscal Toolkit - Node.js / Browser Fetch Example

const BASE_URL = "http://localhost:8000";

async function runExamples() {
  console.log("=== 1. Check ICE ===");
  const iceRes = await fetch(`${BASE_URL}/public/check-ice?ice=001526374000195`).then(r => r.json());
  console.log(`ICE Valid: ${iceRes.is_valid}, Company: ${iceRes.company_name}`);

  console.log("\n=== 2. Validate RIB ===");
  const ribRes = await fetch(`${BASE_URL}/public/validate-rib?rib=007780000123456789012345`).then(r => r.json());
  console.log(`Bank: ${ribRes.bank_name}, IBAN: ${ribRes.iban}`);

  console.log("\n=== 3. Calculate Salary ===");
  const salaryRes = await fetch(`${BASE_URL}/public/salary/net-brut`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ gross_salary_mad: 12000, dependents: 1 }),
  }).then(r => r.json());
  console.log(`Gross: 12,000 MAD -> Net: ${salaryRes.net_monthly_mad} MAD`);
}

runExamples().catch(console.error);
