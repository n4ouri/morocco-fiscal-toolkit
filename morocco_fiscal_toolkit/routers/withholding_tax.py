from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field
from morocco_fiscal_toolkit.services.withholding_tax import MoroccanWithholdingTax

router = APIRouter(prefix="/public", tags=["💸 Retenue à la Source (RAS)"])

class WithholdingTaxRequest(BaseModel):
    income_type: str = Field(..., description="Type de revenu (ex: HONORAIRES_SERVICES, DIVIDENDES_RESIDENTS, ROYALTIES_ETRANGER)")
    gross_amount: float = Field(..., ge=0, description="Montant brut HT en MAD")
    convention_rate: Optional[float] = Field(None, description="Taux conventionnel réduit éventuel (convention fiscale bilatérale)")

@router.get("/withholding-tax/types", summary="📋 Liste des types de Retenue à la Source (RAS)")
def list_withholding_types():
    """
    **Référentiel des Retenues à la Source (RAS - Code Général des Impôts 2026).**
    Fournit la liste des revenus soumis à la RAS, leurs taux légaux par défaut et leurs bases juridiques (Articles 13, 14, 19, 157, 160, 161 du CGI).
    """
    return {
        "total_types": len(MoroccanWithholdingTax.INCOME_TYPES),
        "types": MoroccanWithholdingTax.get_all_types(),
        "legal_basis": "Code Général des Impôts (CGI 2026) — Arts. 13, 14, 19, 157, 160, 161"
    }

@router.post("/withholding-tax/compute", summary="💸 Calculer la Retenue à la Source (RAS)")
def compute_withholding_tax(req: WithholdingTaxRequest):
    """
    **Calculateur Officiel de Retenue à la Source (RAS).**
    Calcule le montant de la RAS prélevée à la source et le montant net à verser au prestataire/bénéficiaire.
    """
    return MoroccanWithholdingTax.compute(
        income_type=req.income_type,
        gross_amount=req.gross_amount,
        convention_rate=req.convention_rate
    )
