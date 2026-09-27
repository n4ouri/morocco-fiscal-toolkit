from fastapi import APIRouter
from pydantic import BaseModel, Field
from morocco_fiscal_toolkit.services.dgi_calculator import DgiMandateCalculator

router = APIRouter(prefix="/public", tags=["🏛️ Facturation Électronique DGI & Simpl-TVA"])

class DgiWaveRequest(BaseModel):
    annual_turnover_mad: float = Field(..., description="Chiffre d'affaires annuel HT en Dirhams (MAD)")
    regime: str = Field("RNR", description="Régime fiscal (RNR, RNS, CPU, AUTO_ENTREPRENEUR)")
    legal_form: str = Field("SARL", description="Forme juridique (SARL, SA, SAS, PERSONNE_PHYSIQUE)")
    is_exporter: bool = Field(False, description="Entreprise exportatrice de biens ou services")

@router.post("/dgi-wave-calculator", summary="📅 Dans quelle vague DGI Simpl-TVA suis-je ?")
def dgi_wave_calculator(req: DgiWaveRequest):
    """
    **Calculateur de Vague d'Obligation DGI Simpl-TVA.**
    Détermine la phase d'assujettissement (Phase 1 Grandes Entreprises, Phase 2 Entreprises Moyennes, Phase 3 Généralisation PME/TPE),
    le compte à rebours, et les risques de non-conformité Article 145 CGI (sanction de perte de déductibilité TVA 2027).
    """
    return DgiMandateCalculator.calculate_wave(
        annual_turnover_mad=req.annual_turnover_mad,
        regime=req.regime,
        legal_form=req.legal_form,
        is_exporter=req.is_exporter
    )

@router.get("/dgi-calendar", summary="📆 Calendrier officiel des vagues DGI e-facturation")
def dgi_rollout_calendar():
    """
    **Calendrier Officiel DGI Facturation Électronique (2025–2028).**
    Fournit les dates clés, le périmètre d'assujettissement et les échéances critiques de la réforme fiscale.
    """
    return {
        "waves": [
            {
                "wave": "Phase 1 - Pilote & Grandes Entreprises",
                "effective_date": "2025 / Début 2026",
                "scope": "Grandes entreprises au régime des grandes entreprises de la DGI (CA > 100M MAD)",
                "clearance_mode": "CTC Simpl-TVA Obligatoire",
                "status": "En cours"
            },
            {
                "wave": "Phase 2 - Entreprises Moyennes",
                "effective_date": "Mi-2026 / Fin 2026",
                "scope": "Entreprises réalisant un chiffre d'affaires > 20M MAD",
                "clearance_mode": "CTC Simpl-TVA Obligatoire",
                "status": "Préparation"
            },
            {
                "wave": "Phase 3 - Généralisation PME / TPE",
                "effective_date": "2027 – 2028",
                "scope": "Toutes personnes morales et physiques assujetties à la TVA",
                "clearance_mode": "CTC Simpl-TVA Obligatoire",
                "status": "Législatif"
            }
        ],
        "key_risk_deadline": "2027 : Perte irréversible du droit à déduction de la TVA pour toute facture non visée par la plateforme Simpl-TVA (Article 145 CGI)."
    }

@router.get("/simpl-tva-status", summary="📡 Statut technique & spécifications Simpl-TVA DGI")
def simpl_tva_status():
    """
    **Observatoire Technique Simpl-TVA.**
    Suivi public de l'état des spécifications techniques de la plateforme DGI.
    """
    return {
        "status": "DEVELOPED_AWAITING_PUBLIC_API_SPEC",
        "last_checked": "2026",
        "platform_name": "Simpl-TVA (Direction Générale des Impôts)",
        "legal_basis": "Article 145 CGI & Loi de Finances",
        "model": "Clearance / CTC (Contrôle Continu des Transactions)",
        "formats_supported": ["UBL 2.1 (OASIS)", "UN/CEFACT CII"],
        "technology_partners": [
            {
                "name": "xHub (Technopark Casablanca)",
                "contract_scope": "Développement logiciel de la plateforme Simpl-TVA",
                "contract_value": "6.3M MAD",
                "status": "Livré et validé en recette DGI"
            },
            {
                "name": "Power Maroc",
                "contract_scope": "Infrastructure matérielle, hébergement et infogérance",
                "contract_value": "> 19M MAD",
                "status": "Attribué"
            }
        ],
        "decree_status": "En cours de validation au Secrétariat Général du Gouvernement (SGG)",
        "trust_framework": "Loi 43-20 régie par l'ANRT (Prestataires de Services de Confiance Électronique)"
    }
