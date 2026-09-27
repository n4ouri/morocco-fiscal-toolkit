from fastapi import APIRouter
from pydantic import BaseModel, Field
from morocco_fiscal_toolkit.services.cpu_simulator import MoroccanTaxRegimeSimulator

router = APIRouter(prefix="/public", tags=["💡 Simulateurs Fiscaux & Régimes (AE, CPU, SARL)"])

class TaxSimulatorRequest(BaseModel):
    annual_turnover_mad: float = Field(..., description="Chiffre d'affaires annuel HT prévisionnel en MAD")
    activity_type: str = Field("SERVICES", description="Type d'activité: SERVICES, COMMERCE_INDUSTRIE, ARTISANAT")
    real_profit_margin_pct: float = Field(30.0, description="Marge nette réelle estimée en %")
    annual_expenses_mad: float = Field(0.0, description="Charges réelles annuelles déductibles (loyer, salaires, achats)")

@router.post("/tax-regime/simulate", summary="💡 Comparer Auto-Entrepreneur vs CPU vs SARL (IS)")
def simulate_tax_regime(req: TaxSimulatorRequest):
    """
    **Comparateur de Régimes Fiscaux Marocains.**
    Compare l'imposition globale (impôts directs + cotisations sociales AMO/CNSS) entre :
    1. Statut Auto-Entrepreneur (1% ou 2% du CA selon activité)
    2. CPU (Contribution Professionnelle Unique - coefficient de marge)
    3. Société à Responsabilité Limitée (SARL - barème IS + dividende).
    """
    return MoroccanTaxRegimeSimulator.simulate(
        annual_turnover_mad=req.annual_turnover_mad,
        activity_type=req.activity_type,
        real_profit_margin_pct=req.real_profit_margin_pct,
        annual_expenses_mad=req.annual_expenses_mad
    )
