from datetime import date
from typing import Dict, Any, List

class DgiMandateCalculator:
    """
    Personalized calculator for the Moroccan DGI e-invoicing mandate wave.
    Based on Article 145 CGI, LF 2024-2026, and Simpl-TVA CTC roadmap.
    """

    @classmethod
    def calculate_wave(
        cls,
        annual_turnover_mad: float,
        regime: str = "RNR",
        legal_form: str = "SARL",
        is_exporter: bool = False
    ) -> Dict[str, Any]:
        turnover = float(annual_turnover_mad)
        today = date.today()

        if turnover > 100_000_000:
            wave_id = "PHASE_1"
            wave_name = "Phase 1 : Grandes Entreprises (DGE)"
            target_date = date(2026, 1, 1)
            is_active_now = True
            scope_description = "Entreprises réalisant un chiffre d'affaires supérieur à 100 Millions MAD."
            status = "EN_VIGUEUR"
            priority = "URGENT"
        elif turnover > 20_000_000:
            wave_id = "PHASE_2"
            wave_name = "Phase 2 : Moyennes Entreprises (ETI / PME Supérieures)"
            target_date = date(2026, 7, 1)
            is_active_now = False
            scope_description = "Entreprises réalisant un chiffre d'affaires compris entre 20 et 100 Millions MAD."
            status = "PREPARATION_ACTIVE"
            priority = "HAUTE"
        else:
            wave_id = "PHASE_3"
            wave_name = "Phase 3 : Généralisation PME, TPE & Indépendants"
            target_date = date(2027, 1, 1)
            is_active_now = False
            scope_description = "Toutes entreprises et assujettis TVA réalisant un chiffre d'affaires inférieur à 20 Millions MAD."
            status = "ANTICIPATION_LEGAL"
            priority = "PLANIFICATION"

        days_remaining = (target_date - today).days

        checklist: List[str] = [
            "Auditer la conformité des mentions légales obligatoires (ICE 15 chiffres, IF, RC)",
            "Déployer un connecteur d'émission électronique certifié conforme (UBL 2.1 / UN-CEFACT)",
            "Mettre en place la vérification automatique des ICE clients et fournisseurs (Tier 1 / Tier 2)",
            "Sécuriser la signature électronique conforme Loi 43-20 (ANRT / Barid Al-Maghrib)",
            "Anticiper le risque Article 145 CGI : rejet de déductibilité TVA sur factures non visées"
        ]

        if is_exporter:
            checklist.insert(0, "Intégration spécifique PortNet et régime d'exonération avec droit à déduction (Art. 92 CGI)")

        return {
            "turnover_mad": turnover,
            "regime": regime,
            "legal_form": legal_form,
            "wave_id": wave_id,
            "wave_name": wave_name,
            "effective_date_str": target_date.strftime("%d/%m/%Y"),
            "target_date_iso": target_date.isoformat(),
            "days_remaining": max(0, days_remaining),
            "is_in_force": is_active_now or days_remaining <= 0,
            "status": status,
            "priority": priority,
            "scope_description": scope_description,
            "clearance_model": "CTC Simpl-TVA (Article 145 CGI - Contrôle Continu des Transactions)",
            "key_risk_warning": (
                "Attention : Dès l'entrée en vigueur de votre phase, toute facture émise hors du circuit "
                "Simpl-TVA expose vos clients au rejet de la déductibilité de la TVA et à l'amende de 15% (Article 145 CGI)."
            ),
            "action_checklist": checklist
        }
