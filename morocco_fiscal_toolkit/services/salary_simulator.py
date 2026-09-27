import math
from typing import Dict, Any, Optional

class MoroccanSalarySimulator:
    """
    Gross ↔ Net salary simulator for Moroccan employees.
    Applies official CNSS, AMO, IR barème, and optional CIMR deductions.

    Inspired by India's salary calculators (ClearTax) and Brazil's CLT net salary tools.
    Rates updated per Loi de Finances 2026 and CNSS circular 2025.

    Components:
    - CNSS (employee share): 4.48% on gross (plafond: 6 000 MAD/month)
    - AMO (CNSS): 2.26% on gross (no plafond)
    - CIMR (optional retraite complémentaire): configurable rate
    - Frais professionnels (FP): 20% of (gross - CNSS - AMO), capped at 2 500 MAD/month
    - IR: Progressive barème on net after FP deduction
    """

    # CNSS monthly plafond
    CNSS_RATE = 0.0448
    CNSS_PLAFOND_MONTHLY = 6_000.0
    AMO_RATE = 0.0226
    CIMR_DEFAULT_RATE = 0.03  # optional private pension

    # IR monthly barème (annual divided by 12)
    IR_BRACKETS_ANNUAL = [
        (30_000,   0.00, 0),
        (50_000,   0.10, 0),
        (60_000,   0.15, 0),
        (80_000,   0.20, 0),
        (180_000,  0.30, 0),
        (float("inf"), 0.34, 0),
    ]

    @classmethod
    def compute_ir_annual(cls, taxable_annual: float) -> float:
        """Computes annual IR using the 2026 progressive barème."""
        if taxable_annual <= 0:
            return 0.0

        # Build bracket table with deductions
        brackets = [
            (30_000,    0.00,  0.0),
            (50_000,    0.10,  3_000.0),
            (60_000,    0.15,  5_500.0),
            (80_000,    0.20,  8_500.0),
            (180_000,   0.30, 16_500.0),
            (float("inf"), 0.34, 23_700.0),
        ]

        ir = 0.0
        for ceiling, rate, deduction in brackets:
            if taxable_annual <= ceiling:
                ir = taxable_annual * rate - deduction
                break

        return round(max(0.0, ir), 2)

    @classmethod
    def gross_to_net(
        cls,
        gross_monthly: float,
        include_cimr: bool = False,
        cimr_rate: Optional[float] = None,
        dependents: int = 0,
    ) -> Dict[str, Any]:
        """
        Computes net salary from gross monthly salary (MAD).

        :param gross_monthly: Gross monthly salary in MAD
        :param include_cimr: Include CIMR private pension contribution
        :param cimr_rate: CIMR rate (default 3%)
        :param dependents: Number of dependent children (2 500 MAD/year per child, max 6)
        """
        gross = max(0.0, float(gross_monthly))

        # 1. CNSS (capped at 6 000 MAD/month base)
        cnss_base = min(gross, cls.CNSS_PLAFOND_MONTHLY)
        cnss_deduction = round(cnss_base * cls.CNSS_RATE, 2)

        # 2. AMO (no cap)
        amo_deduction = round(gross * cls.AMO_RATE, 2)

        # 3. CIMR (optional)
        cimr_r = float(cimr_rate or cls.CIMR_DEFAULT_RATE) if include_cimr else 0.0
        cimr_deduction = round(gross * cimr_r, 2) if include_cimr else 0.0

        # 4. Frais Professionnels (FP): 20% of (gross - CNSS - AMO), capped 2500/month
        base_fp = gross - cnss_deduction - amo_deduction - cimr_deduction
        fp_raw = base_fp * 0.20
        fp_deduction = round(min(fp_raw, 2_500.0), 2)

        # 5. Dependent allowance (deducted from IR base)
        dep_allowance_annual = min(dependents, 6) * 2_500.0
        dep_allowance_monthly = round(dep_allowance_annual / 12, 2)

        # 6. IR taxable base
        ir_base_monthly = base_fp - fp_deduction - dep_allowance_monthly
        ir_base_annual = ir_base_monthly * 12

        ir_annual = cls.compute_ir_annual(ir_base_annual)
        ir_monthly = round(ir_annual / 12, 2)

        # 7. Net salary
        total_deductions = cnss_deduction + amo_deduction + cimr_deduction + ir_monthly
        net_monthly = round(gross - total_deductions, 2)

        effective_rate = round((total_deductions / gross * 100), 2) if gross else 0.0

        return {
            "gross_monthly_mad": round(gross, 2),
            "net_monthly_mad": net_monthly,
            "net_annual_mad": round(net_monthly * 12, 2),
            "deductions": {
                "cnss_mad": cnss_deduction,
                "cnss_rate": f"{cls.CNSS_RATE * 100:.2f}% (plafonné à {cls.CNSS_PLAFOND_MONTHLY:,.0f} MAD/mois)",
                "amo_mad": amo_deduction,
                "amo_rate": f"{cls.AMO_RATE * 100:.2f}%",
                "cimr_mad": cimr_deduction,
                "cimr_rate": f"{cimr_r * 100:.1f}%" if include_cimr else "Non inclus",
                "frais_professionnels_mad": fp_deduction,
                "frais_professionnels_note": "20% plafonné à 2 500 MAD/mois",
                "ir_monthly_mad": ir_monthly,
                "ir_annual_mad": ir_annual,
                "ir_base_annual_mad": round(ir_base_annual, 2),
                "dependents": dependents,
                "dep_allowance_monthly_mad": dep_allowance_monthly,
            },
            "total_deductions_monthly_mad": round(total_deductions, 2),
            "effective_tax_rate_pct": effective_rate,
            "legal_basis": "CNSS Circulaire 2025 + Barème IR LF 2026 (DGI Maroc)",
            "disclaimer": (
                "Simulation indicative. La retenue à la source IR réelle peut varier "
                "selon les allocations familiales CNSS, les déductions complémentaires "
                "et les conventions fiscales applicables."
            )
        }

    @classmethod
    def net_to_gross(cls, net_monthly: float, dependents: int = 0) -> Dict[str, Any]:
        """
        Reverse calculation: estimates gross salary from desired net using iterative convergence.
        Accuracy: ±5 MAD (sufficient for simulation purposes).
        """
        net = max(0.0, float(net_monthly))
        # Initial estimate using approximate 85% take-home rate
        estimate = net / 0.78
        for _ in range(30):
            result = cls.gross_to_net(estimate, dependents=dependents)
            diff = net - result["net_monthly_mad"]
            if abs(diff) < 1.0:
                break
            estimate += diff * 0.9

        result = cls.gross_to_net(estimate, dependents=dependents)
        result["requested_net_monthly_mad"] = net
        result["estimated_gross_monthly_mad"] = round(estimate, 2)
        result["convergence_note"] = "Estimation par itération (précision ±5 MAD)"
        return result
