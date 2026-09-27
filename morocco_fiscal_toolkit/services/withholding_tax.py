from typing import Dict, Any

class MoroccanWithholdingTax:
    """
    Retenue à la Source (RAS) calculator for Moroccan tax law.

    Covers:
    - Services rendus par des personnes morales marocaines (Art. 157 CGI): 10%
    - Dividendes / distributions (Art. 13 CGI): 15% (résidents) / 10% (non-résidents treaty)
    - Honoraires et rémunérations (Art. 160 CGI): 10%
    - Produits de placements à revenu fixe (obligataires, dépôts) (Art. 14 CGI): 30% (personnes physiques)
    - Redevances / Royalties versées à l'étranger (Art. 19 CGI): 10%
    - Loyers versés à des personnes physiques (Art. 161 CGI): 10%
    - Produits des actions d'OPCVM actions (Art. 68 CGI): 15%

    Inspired by India's TDS section reference tool (ClearTax) and UAE FTA withholding guide.
    """

    INCOME_TYPES = {
        "HONORAIRES_SERVICES": {
            "label": "Honoraires / Rémunérations de services (Personnes Morales)",
            "rate": 0.10,
            "article": "Art. 157 CGI",
            "notes": (
                "Applicable aux sommes versées aux personnes morales marocaines pour des prestations de services. "
                "L'acheteur (débiteur) retient 10% et verse au trésor. Crédit imputable sur l'IS."
            ),
            "applies_to": "Personnes Morales (SARL, SA, SAS) résidentes",
            "exempt": False
        },
        "DIVIDENDES_RESIDENTS": {
            "label": "Dividendes distribués — Actionnaires résidents",
            "rate": 0.15,
            "article": "Art. 13 CGI",
            "notes": (
                "RAS de 15% sur les distributions de dividendes, bénéfices et réserves aux associés résidents. "
                "Retenue libératoire de l'IR ou imputée sur l'IS de la société bénéficiaire."
            ),
            "applies_to": "Personnes physiques et morales résidentes au Maroc",
            "exempt": False
        },
        "DIVIDENDES_NON_RESIDENTS": {
            "label": "Dividendes distribués — Actionnaires non-résidents",
            "rate": 0.15,
            "article": "Art. 13 & 19 CGI",
            "notes": (
                "Taux de droit commun : 15%. Peut être réduit à 10% ou 7.5% selon conventions fiscales bilatérales "
                "(France, Espagne, Allemagne, UE, Golfe). Vérifier la convention applicable."
            ),
            "applies_to": "Actionnaires non-résidents (étrangers)",
            "exempt": False
        },
        "ROYALTIES_ETRANGER": {
            "label": "Redevances / Royalties versées à l'étranger",
            "rate": 0.10,
            "article": "Art. 19 CGI",
            "notes": (
                "Retenue de 10% sur les redevances (licences logicielles, droits d'auteur, brevets) versées "
                "à des non-résidents. Peut être réduite par convention fiscale."
            ),
            "applies_to": "Prestataires non-résidents recevant des redevances de source marocaine",
            "exempt": False
        },
        "PRODUITS_FIXES_PP": {
            "label": "Produits de placements à revenu fixe — Personnes Physiques",
            "rate": 0.30,
            "article": "Art. 14 CGI",
            "notes": (
                "Retenue libératoire de 30% sur les intérêts d'obligations, dépôts bancaires, bons de caisse "
                "perçus par des personnes physiques. Non imputable sur IR annuel."
            ),
            "applies_to": "Personnes physiques résidentes percevant des intérêts de placement",
            "exempt": False
        },
        "PRODUITS_FIXES_PM": {
            "label": "Produits de placements à revenu fixe — Personnes Morales",
            "rate": 0.20,
            "article": "Art. 14 CGI",
            "notes": (
                "Retenue de 20% sur intérêts et produits similaires versés aux personnes morales. "
                "Imputable sur l'IS dû au titre de l'exercice."
            ),
            "applies_to": "Personnes morales résidentes",
            "exempt": False
        },
        "LOYERS_PP": {
            "label": "Loyers versés à des personnes physiques",
            "rate": 0.10,
            "article": "Art. 161 CGI",
            "notes": (
                "Retenue de 10% sur les loyers versés par des personnes morales à des personnes physiques. "
                "Crédit IR pour le bailleur sur sa déclaration annuelle."
            ),
            "applies_to": "Bailleurs personnes physiques recevant des loyers de personnes morales",
            "exempt": False
        },
        "OPCVM_ACTIONS": {
            "label": "Produits des OPCVM Actions",
            "rate": 0.15,
            "article": "Art. 68 CGI",
            "notes": (
                "Retenue de 15% sur les distributions des OPCVM actions. "
                "Taux réduit de 10% pour les OPCVM obligataires."
            ),
            "applies_to": "Porteurs de parts d'OPCVM",
            "exempt": False
        },
    }

    @classmethod
    def get_all_types(cls):
        """Returns all income types with their rates."""
        return [
            {
                "income_type": k,
                "label": v["label"],
                "rate_pct": f"{v['rate'] * 100:.0f}%",
                "article": v["article"],
                "applies_to": v["applies_to"],
            }
            for k, v in cls.INCOME_TYPES.items()
        ]

    @classmethod
    def compute(
        cls,
        income_type: str,
        gross_amount: float,
        convention_rate: float = None,
    ) -> Dict[str, Any]:
        """
        Computes the Retenue à la Source for a given income type and amount.

        :param income_type: One of the INCOME_TYPES keys (e.g. 'HONORAIRES_SERVICES')
        :param gross_amount: Gross amount before RAS (in MAD)
        :param convention_rate: Optional reduced treaty rate (e.g. 0.05 for 5%)
        """
        if income_type not in cls.INCOME_TYPES:
            return {
                "is_valid": False,
                "error": f"Type de revenu non reconnu: '{income_type}'. Types valides: {list(cls.INCOME_TYPES.keys())}",
                "available_types": list(cls.INCOME_TYPES.keys())
            }

        info = cls.INCOME_TYPES[income_type]
        gross = max(0.0, float(gross_amount))

        # Apply convention rate if provided (and lower than standard)
        standard_rate = info["rate"]
        applied_rate = standard_rate
        convention_note = None

        if convention_rate is not None:
            cr = float(convention_rate)
            if 0.0 <= cr < standard_rate:
                applied_rate = cr
                convention_note = (
                    f"Taux conventionnel de {cr*100:.1f}% appliqué (réduit par convention fiscale bilatérale). "
                    f"Taux de droit commun : {standard_rate*100:.0f}%."
                )

        ras_amount = round(gross * applied_rate, 2)
        net_amount = round(gross - ras_amount, 2)

        return {
            "is_valid": True,
            "income_type": income_type,
            "income_label": info["label"],
            "article": info["article"],
            "gross_amount_mad": gross,
            "standard_rate_pct": f"{standard_rate * 100:.0f}%",
            "applied_rate_pct": f"{applied_rate * 100:.1f}%",
            "ras_amount_mad": ras_amount,
            "net_amount_mad": net_amount,
            "convention_applied": convention_rate is not None and applied_rate < standard_rate,
            "convention_note": convention_note or info["notes"],
            "applies_to": info["applies_to"],
            "accounting_entry": {
                "debit": f"Charge / Achat : {gross:,.2f} MAD",
                "credit_ras": f"RAS à reverser au Trésor : {ras_amount:,.2f} MAD",
                "credit_net": f"Paiement net au prestataire : {net_amount:,.2f} MAD",
            },
            "declaration_deadline": "Le 20 du mois suivant le paiement (Formulaire DGI n°17 ou télédéclaration Simpl-RAS)",
            "legal_basis": f"{info['article']} — Code Général des Impôts (CGI 2026)"
        }
