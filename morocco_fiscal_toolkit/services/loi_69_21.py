import math
from datetime import date, datetime
from typing import Dict, Any, List, Optional

class Loi6921Service:
    """
    Compliance and Declaration Assistant for Moroccan Law 69-21 on Payment Delays.
    (Loi n° 69-21 modifiant la loi 15-95 formant code de commerce - Bulletin Officiel Juin 2023).
    Mandatory declaration for all companies with Turnover > 2M MAD since 1 Jan 2025.
    """

    DEFAULT_LEGAL_TERM_DAYS = 60
    MAX_CONTRACTUAL_TERM_DAYS = 120
    MAX_SECTORAL_TERM_DAYS = 180

    # Taux directeur Bank Al-Maghrib (BAM) + 0.85% par mois
    BAM_DIRECTOR_RATE = 0.0300  # 3.00%
    MONTHLY_SURCHARGE = 0.0085  # 0.85% per month of delay

    @classmethod
    def get_non_declaration_fine(cls, annual_turnover_mad: float) -> float:
        """Fixed fine for failure to file the annual Loi 69-21 declaration."""
        if annual_turnover_mad < 2_000_000:
            return 0.0
        elif annual_turnover_mad <= 10_000_000:
            return 5_000.0
        elif annual_turnover_mad <= 50_000_000:
            return 12_500.0
        elif annual_turnover_mad <= 100_000_000:
            return 50_000.0
        elif annual_turnover_mad <= 500_000_000:
            return 125_000.0
        else:
            return 250_000.0

    @classmethod
    def assess_risk(
        cls,
        annual_turnover_mad: float,
        total_overdue_ttc: float = 0.0,
        avg_delay_days: int = 45,
        overdue_invoices_count: int = 0
    ) -> Dict[str, Any]:
        """
        Free self-assessment checker: determines if the business is subject to Loi 69-21,
        the declaration deadline, certification requirements, and potential penalties.
        """
        turnover = float(annual_turnover_mad)
        in_scope = turnover >= 2_000_000.0
        fine_non_declaration = cls.get_non_declaration_fine(turnover)

        # Certification authority requirement
        if turnover >= 50_000_000:
            certifier = "Commissaire aux Comptes (CAC)"
            certifier_type = "CAC"
            declaration_frequency = "Trimestrielle"
            first_deadline = "Fin du mois suivant chaque trimestre"
        elif in_scope:
            certifier = "Expert-Comptable (OEC) ou Comptable Agréé"
            certifier_type = "EXPERT_COMPTABLE"
            declaration_frequency = "Annuelle"
            first_deadline = "Avant le 31 Mars 2026 (pour l'exercice 2025)"
        else:
            certifier = "Non assujetti à la déclaration obligatoire (CA < 2M MAD)"
            certifier_type = "NONE"
            declaration_frequency = "Aucune déclaration obligatoire"
            first_deadline = "N/A"

        # Calculate estimated statutory late interest on overdue invoices
        # 1 month BAM rate fraction + 0.85% for each 30 days of delay
        months_delay = max(1, math.ceil(avg_delay_days / 30)) if total_overdue_ttc > 0 and avg_delay_days > 0 else 0
        monthly_rate = (cls.BAM_DIRECTOR_RATE / 12) + cls.MONTHLY_SURCHARGE
        estimated_late_interest = round(total_overdue_ttc * monthly_rate * months_delay, 2)

        total_exposure = fine_non_declaration + estimated_late_interest

        risk_level = "ÉLEVÉ" if (in_scope and (total_overdue_ttc > 50_000 or avg_delay_days > 60)) else "MODÉRÉ" if in_scope else "FAIBLE"

        return {
            "annual_turnover_mad": turnover,
            "in_scope": in_scope,
            "scope_tier": "CA > 50M MAD" if turnover >= 50_000_000 else "CA 2M - 50M MAD" if in_scope else "CA < 2M MAD (Hors champ)",
            "risk_level": risk_level,
            "declaration_frequency": declaration_frequency,
            "declaration_deadline": first_deadline,
            "certifier_required": certifier,
            "certifier_type": certifier_type,
            "fine_non_declaration_mad": fine_non_declaration,
            "estimated_late_interest_mad": estimated_late_interest,
            "total_financial_exposure_mad": round(total_exposure, 2),
            "legal_terms": {
                "default_days": cls.DEFAULT_LEGAL_TERM_DAYS,
                "contractual_max_days": cls.MAX_CONTRACTUAL_TERM_DAYS,
                "sectoral_max_days": cls.MAX_SECTORAL_TERM_DAYS
            },
            "key_recommendation": (
                "Votre entreprise entre dans le champ d'application de la Loi 69-21. "
                f"Vous devez faire certifier votre état des factures par un {certifier} "
                f"et télédéclarer {first_deadline} sur la plateforme de la DGI / TGR."
                if in_scope else
                "Bien que votre CA soit inférieur à 2M MAD (dispense de déclaration annuelle), "
                "le délai légal de 60 jours reste applicable à vos contrats commerciaux."
            )
        }

    @classmethod
    def calculate_invoice_penalty(
        cls,
        amount_ttc: float,
        days_overdue: int
    ) -> Dict[str, Any]:
        """Calculates late payment penalty for a single invoice."""
        if days_overdue <= 0:
            return {
                "days_overdue": 0,
                "months_overdue": 0,
                "penalty_amount_mad": 0.0,
                "is_overdue": False
            }

        months_overdue = math.ceil(days_overdue / 30)
        monthly_rate = (cls.BAM_DIRECTOR_RATE / 12) + cls.MONTHLY_SURCHARGE
        penalty_amount = round(amount_ttc * monthly_rate * months_overdue, 2)

        return {
            "days_overdue": days_overdue,
            "months_overdue": months_overdue,
            "monthly_rate_pct": round(monthly_rate * 100, 3),
            "penalty_amount_mad": penalty_amount,
            "is_overdue": True
        }

    @classmethod
    def generate_detailed_declaration_report(
        cls,
        invoices: List[Dict[str, Any]],
        company_ice: str,
        company_name: str,
        fiscal_year: int = 2025
    ) -> Dict[str, Any]:
        """
        Generates the certified 'État Détaillé des Factures' required for the Loi 69-21 declaration.
        """
        processed_items = []
        total_overdue_ttc = 0.0
        total_penalties = 0.0

        for inv in invoices:
            amount_ttc = float(inv.get("total_ttc") or 0.0)
            term_days = int(inv.get("term_days") or cls.DEFAULT_LEGAL_TERM_DAYS)
            
            # Days overdue computation: use provided days_overdue if present, else calculate
            if inv.get("days_overdue") is not None:
                days_overdue = int(inv["days_overdue"])
            elif "issue_date" in inv:
                try:
                    d_issue = datetime.strptime(inv["issue_date"][:10], "%Y-%m-%d").date()
                    d_due = d_issue.toordinal() + term_days
                    d_pay = datetime.strptime(inv["payment_date"][:10], "%Y-%m-%d").date() if inv.get("payment_date") else date.today()
                    days_overdue = max(0, d_pay.toordinal() - d_due)
                except Exception:
                    days_overdue = 0
            else:
                days_overdue = 0

            penalty_calc = cls.calculate_invoice_penalty(amount_ttc, days_overdue)
            is_breached = days_overdue > 0

            if is_breached:
                total_overdue_ttc += amount_ttc
                total_penalties += penalty_calc["penalty_amount_mad"]

            processed_items.append({
                "invoice_number": inv.get("invoice_number", "FAC-000"),
                "supplier_ice": inv.get("supplier_ice", "N/A"),
                "supplier_name": inv.get("supplier_name", "Fournisseur"),
                "issue_date": inv.get("issue_date", "2025-01-01"),
                "legal_term_days": term_days,
                "amount_ttc": amount_ttc,
                "days_overdue": days_overdue,
                "penalty_amount_mad": penalty_calc["penalty_amount_mad"],
                "status": "EN_RETARD" if is_breached else "CONFORME",
                "payment_status": inv.get("payment_status", "IMPAYEE")
            })

        return {
            "fiscal_year": fiscal_year,
            "company_name": company_name,
            "company_ice": company_ice,
            "declaration_title": f"État Détaillé des Délais de Paiement - Exercice {fiscal_year} (Loi 69-21)",
            "legal_basis": "Loi 69-21 modifiant la loi 15-95 formant code de commerce (BO Juin 2023)",
            "summary": {
                "total_invoices_audited": len(invoices),
                "overdue_invoices_count": sum(1 for it in processed_items if it["days_overdue"] > 0),
                "total_overdue_ttc_mad": round(total_overdue_ttc, 2),
                "total_penalties_due_mad": round(total_penalties, 2)
            },
            "items": processed_items,
            "certification_statement": (
                f"Je soussigné, Expert-Comptable / Commissaire aux Comptes, atteste avoir procédé aux vérifications "
                f"nécessaires de l'état détaillé des factures de la société {company_name} (ICE: {company_ice}) "
                f"conformément aux dispositions de la Loi 69-21 relative aux délais de paiement."
            )
        }
