from fastapi import APIRouter
from pydantic import BaseModel, Field
from morocco_fiscal_toolkit.services.courier_reconciliation import CourierReconciliationService

router = APIRouter(prefix="/public", tags=["🚚 E-commerce & Bordereaux Courier (COD/CRBT)"])

class CourierStatementRequest(BaseModel):
    content_text: str = Field(..., description="Texte brut copié ou extrait du bordereau de remise de fonds")
    courier_name: str = Field("Amana", description="Nom du transporteur: Amana, CTM, Cathedis, Speedy, etc.")

@router.post("/courier-cod/parse", summary="🚚 Parser un bordereau de remise courier (Cash-on-Delivery)")
def parse_courier_remittance(req: CourierStatementRequest):
    """
    **Parseur de Bordereaux de Paiement Contre Remboursement (CRBT / COD).**
    Extrait automatiquement les numéros de suivi, montants collectés en espèces, commissions de livraison, et solde net viré en compte.
    """
    return CourierReconciliationService.parse_courier_statement(
        content_text=req.content_text,
        courier_name=req.courier_name
    )
