from fastapi import APIRouter, Query, Body
from pydantic import BaseModel, Field
from morocco_fiscal_toolkit.services.tva_finder import MoroccanTvaCatalog

router = APIRouter(prefix="/public", tags=["🧾 TVA & Taxe sur la Valeur Ajoutée (CGI)"])

class TvaCalcRequest(BaseModel):
    amount: float = Field(..., description="Montant de base (en MAD)")
    rate: float = Field(0.20, description="Taux de TVA applicable (0.20, 0.14, 0.10, 0.07, 0.0)")
    is_ttc: bool = Field(False, description="True si le montant fourni est TTC, False si HT")

@router.get("/tva-rates/search", summary="🔍 Rechercher un taux de TVA par secteur / produit")
def search_tva(
    q: str = Query("", description="Mot-clé, produit, service ou article du CGI")
):
    """
    **Moteur de recherche TVA Maroc (Code Général des Impôts 2026).**
    Recherche les taux applicables (20% normal, 14% transport/énergie, 10% tourisme/banque, 7% eau/scolaire, 0% exonéré Article 92 CGI),
    les conditions de déductibilité et les articles de loi associés.
    """
    return MoroccanTvaCatalog.search(q)

@router.post("/tva-rates/calculate", summary="🧮 Calculer HT ↔ TVA ↔ TTC")
def calculate_tva(req: TvaCalcRequest):
    """
    **Calculateur TVA Réversible.**
    Convertit automatiquement un montant HT en TTC (avec montant de TVA) ou l'inverse, selon le taux spécifié.
    """
    return MoroccanTvaCatalog.calculate_simulation(
        amount=req.amount,
        rate=req.rate,
        is_ttc=req.is_ttc
    )
