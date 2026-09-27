from typing import Dict, Any, List

class MoroccanTaxRegimeSimulator:
    """
    Simulates and compares taxation and social charges across Moroccan regimes:
    1. Auto-Entrepreneur (Loi 114-13)
    2. Contribution Professionnelle Unique (CPU - Art. 40 bis CGI)
    3. Régime Réel - Société à Responsabilité Limitée (SARL / IS)
    """

    ACTIVITY_COEFFICIENTS = {
        "COMMERCE_DETAIL": {
            "label": "Commerce de détail & Négoce",
            "cpu_coeff": 0.10,
            "ae_rate": 0.01,
            "ae_ceiling": 500_000,
            "cpu_ceiling": 2_000_000
        },
        "COMMERCE_GROS": {
            "label": "Commerce de gros & Distribution",
            "cpu_coeff": 0.06,
            "ae_rate": 0.01,
            "ae_ceiling": 500_000,
            "cpu_ceiling": 2_000_000
        },
        "ARTISANAT_INDUSTRIE": {
            "label": "Artisanat de production & Petite industrie",
            "cpu_coeff": 0.15,
            "ae_rate": 0.01,
            "ae_ceiling": 500_000,
            "cpu_ceiling": 2_000_000
        },
        "SERVICES": {
            "label": "Prestations de services & Conseil",
            "cpu_coeff": 0.25,
            "ae_rate": 0.02,
            "ae_ceiling": 200_000,
            "cpu_ceiling": 500_000
        },
        "RESTAURATION_CAFE": {
            "label": "Café & Restauration rapide",
            "cpu_coeff": 0.18,
            "ae_rate": 0.01,
            "ae_ceiling": 500_000,
            "cpu_ceiling": 2_000_000
        }
    }

    @classmethod
    def simulate(
        cls,
        annual_turnover_mad: float,
        activity_type: str = "SERVICES",
        real_profit_margin_pct: float = 30.0,
        annual_expenses_mad: float = 0.0
    ) -> Dict[str, Any]:
        turnover = max(0.0, float(annual_turnover_mad))
        margin = max(1.0, min(100.0, float(real_profit_margin_pct))) / 100.0

        activity_info = cls.ACTIVITY_COEFFICIENTS.get(activity_type, cls.ACTIVITY_COEFFICIENTS["SERVICES"])

        # Calculated real profit if expenses not explicitly given
        real_net_profit = turnover - annual_expenses_mad if annual_expenses_mad > 0 else turnover * margin

        # -------------------------------------------------------------
        # 1. Régime Auto-Entrepreneur
        # -------------------------------------------------------------
        ae_ceiling = activity_info["ae_ceiling"]
        ae_eligible = turnover <= ae_ceiling
        ae_tax_rate = activity_info["ae_rate"]
        ae_tax = round(turnover * ae_tax_rate, 2)
        ae_amo_cnss = 1_800.0 if turnover > 0 else 0.0  # ~150 MAD / month
        ae_total_charges = ae_tax + ae_amo_cnss
        ae_net_income = max(0.0, real_net_profit - ae_total_charges)

        # -------------------------------------------------------------
        # 2. Régime CPU (Contribution Professionnelle Unique)
        # -------------------------------------------------------------
        cpu_ceiling = activity_info["cpu_ceiling"]
        cpu_eligible = turnover <= cpu_ceiling
        coeff = activity_info["cpu_coeff"]
        base_fiscale = turnover * coeff
        # Droit principal : 10% libératoire sur la base forfaitaire
        cpu_droit_principal = round(base_fiscale * 0.10, 2)

        # Droit complémentaire (CNSS AMO selon barème légal DGI/CNSS)
        if cpu_droit_principal <= 500:
            cpu_amo_annual = 1_200.0   # 100 MAD / mois
        elif cpu_droit_principal <= 1_000:
            cpu_amo_annual = 1_800.0   # 150 MAD / mois
        elif cpu_droit_principal <= 2_500:
            cpu_amo_annual = 2_760.0   # 230 MAD / mois
        elif cpu_droit_principal <= 5_000:
            cpu_amo_annual = 3_720.0   # 310 MAD / mois
        else:
            cpu_amo_annual = 6_000.0   # 500 MAD / mois

        cpu_total_charges = round(cpu_droit_principal + cpu_amo_annual, 2)
        cpu_net_income = max(0.0, real_net_profit - cpu_total_charges)

        # -------------------------------------------------------------
        # 3. Régime Réel - Société (SARL / IS)
        # -------------------------------------------------------------
        # Impôt sur les Sociétés (IS)
        # Barème progressif : 10% <= 300,000 MAD, 20% au-delà
        taxable_is_profit = max(0.0, real_net_profit)
        if taxable_is_profit <= 300_000:
            is_tax = taxable_is_profit * 0.10
        else:
            is_tax = (300_000 * 0.10) + ((taxable_is_profit - 300_000) * 0.20)

        # Cotisation minimale (CM) : 0.25% du CA
        cotisation_minimale = turnover * 0.0025
        final_is_tax = round(max(is_tax, cotisation_minimale), 2)

        # Cotisation gérant majoritaire / TNS CNSS
        sarl_cnss_amo = 3_600.0 if turnover > 0 else 0.0  # forfait TNS ~300 MAD/mois
        # Distribution dividendes restante soumise à TPPA (10% - 13.75%)
        distribuable = max(0.0, taxable_is_profit - final_is_tax)
        dividendes_tax = round(distribuable * 0.10, 2)

        sarl_total_taxes = round(final_is_tax + dividendes_tax + sarl_cnss_amo, 2)
        sarl_net_income = max(0.0, real_net_profit - sarl_total_taxes)

        # -------------------------------------------------------------
        # Recommendation Logic
        # -------------------------------------------------------------
        if ae_eligible:
            best_regime = "AUTO_ENTREPRENEUR"
            recommendation = (
                f"Pour un CA de {turnover:,.0f} MAD en {activity_info['label']}, le régime Auto-Entrepreneur "
                f"est optimal avec un taux de seulement {int(ae_tax_rate*100)}% et un minimum de charges administratives. "
                f"Pensez à surveiller le plafond de {ae_ceiling:,.0f} MAD."
            )
        elif cpu_eligible:
            best_regime = "CPU"
            recommendation = (
                f"Votre chiffre d'affaires dépasse le plafond Auto-Entrepreneur mais reste sous le seuil CPU "
                f"({cpu_ceiling:,.0f} MAD). La Contribution Professionnelle Unique vous permet de simplifier vos obligations "
                f"fiscales tout en bénéficiant de la couverture AMO CNSS."
            )
        else:
            best_regime = "SARL"
            recommendation = (
                f"Votre chiffre d'affaires ({turnover:,.0f} MAD) dépasse les seuils forfaitaires. La structure "
                f"SARL est obligatoire ou fortement recommandée : elle vous permet de déduire l'ensemble de vos charges "
                f"d'exploitation, de récupérer la TVA et de protéger votre patrimoine personnel."
            )

        return {
            "turnover_mad": turnover,
            "activity_type": activity_type,
            "activity_label": activity_info["label"],
            "real_profit_margin_pct": margin * 100,
            "real_net_profit_mad": round(real_net_profit, 2),
            "best_regime": best_regime,
            "recommendation": recommendation,
            "regimes": {
                "auto_entrepreneur": {
                    "name": "Auto-Entrepreneur",
                    "eligible": ae_eligible,
                    "ceiling_mad": ae_ceiling,
                    "tax_ir_mad": ae_tax,
                    "tax_rate_pct": f"{ae_tax_rate*100:.1f}%",
                    "cnss_amo_mad": ae_amo_cnss,
                    "total_charges_mad": round(ae_total_charges, 2),
                    "net_in_pocket_mad": round(ae_net_income, 2),
                    "effective_tax_rate_pct": round((ae_total_charges / turnover * 100), 2) if turnover else 0.0,
                    "pros": ["Comptabilité ultra-simplifiée", "0% TVA collectée", "Paiement trimestriel simple"],
                    "cons": [f"Plafonné à {ae_ceiling:,.0f} MAD", "Aucune déduction de charges réelles", "Pas de récupération de TVA sur achats"]
                },
                "cpu": {
                    "name": "Contribution Professionnelle Unique (CPU)",
                    "eligible": cpu_eligible,
                    "ceiling_mad": cpu_ceiling,
                    "tax_ir_mad": cpu_droit_principal,
                    "coeff_applique": f"{int(coeff*100)}%",
                    "cnss_amo_mad": cpu_amo_annual,
                    "total_charges_mad": cpu_total_charges,
                    "net_in_pocket_mad": round(cpu_net_income, 2),
                    "effective_tax_rate_pct": round((cpu_total_charges / turnover * 100), 2) if turnover else 0.0,
                    "pros": ["Remplacement avantageux du forfait", "Couverture AMO CNSS intégrée", "Plafond élevé"],
                    "cons": [f"Plafonné à {cpu_ceiling:,.0f} MAD", "Charges calculées forfaitairement selon coefficient", "Dispense de TVA conditionnée"]
                },
                "sarl": {
                    "name": "Société Réel (SARL / IS)",
                    "eligible": True,
                    "ceiling_mad": None,
                    "tax_ir_mad": final_is_tax,
                    "is_bracket": "10% (<=300k) / 20% (>300k)",
                    "dividend_tax_mad": dividendes_tax,
                    "cnss_amo_mad": sarl_cnss_amo,
                    "total_charges_mad": sarl_total_taxes,
                    "net_in_pocket_mad": round(sarl_net_income, 2),
                    "effective_tax_rate_pct": round((sarl_total_taxes / turnover * 100), 2) if turnover else 0.0,
                    "pros": ["Déductibilité intégrale des charges et salaires", "Droit complet à déduction TVA", "Plafond de CA illimité & crédibilité bancaire"],
                    "cons": ["Comptabilité générale obligatoire (Bilan, CPC)", "Obligations déclaratives accrues", "Coûts fiduciaires / expert-comptable"]
                }
            }
        }
