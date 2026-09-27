from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field
from morocco_fiscal_toolkit.services.salary_simulator import MoroccanSalarySimulator

router = APIRouter(prefix="/public", tags=["💼 Paie & Salaire Brut / Net (CNSS, AMO, IR 2026)"])

class SalaryRequest(BaseModel):
    gross_salary_mad: Optional[float] = Field(None, description="Salaire brut mensuel en MAD (pour calcul vers Net)")
    net_salary_mad: Optional[float] = Field(None, description="Salaire net mensuel souhaité en MAD (pour calcul vers Brut)")
    include_cimr: bool = Field(False, description="Inclure la cotisation CIMR (retraite complémentaire)")
    cimr_rate: Optional[float] = Field(None, description="Taux salarial CIMR (ex: 0.03 pour 3%)")
    dependents: int = Field(0, ge=0, le=6, description="Nombre de personnes / enfants à charge (max 6)")

@router.post("/salary/net-brut", summary="💰 Calculateur Salaire Brut ↔ Net Maroc (Loi de Finances 2026)")
def salary_calculator(req: SalaryRequest):
    """
    **Simulateur de Paie et Salaire Marocain Réversible (Brut ↔ Net).**
    Applique les taux légaux en vigueur :
    - CNSS (4.48% plafonné à 6000 MAD/mois)
    - AMO (2.26% non plafonné)
    - Frais Professionnels (20% plafonné à 2500 MAD/mois)
    - Barème progressif de l'Impôt sur le Revenu (IR / Loi de Finances 2026)
    - Déductions pour charges de famille (30 MAD/mois par personne à charge, max 6).
    """
    if req.gross_salary_mad is not None:
        return MoroccanSalarySimulator.gross_to_net(
            gross_monthly=req.gross_salary_mad,
            include_cimr=req.include_cimr,
            cimr_rate=req.cimr_rate,
            dependents=req.dependents
        )
    elif req.net_salary_mad is not None:
        return MoroccanSalarySimulator.net_to_gross(
            net_monthly=req.net_salary_mad,
            dependents=req.dependents
        )
    else:
        return {"is_valid": False, "error": "Veuillez fournir soit gross_salary_mad soit net_salary_mad."}
