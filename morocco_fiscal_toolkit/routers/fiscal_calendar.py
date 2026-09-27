from datetime import date
from fastapi import APIRouter, Query
from morocco_fiscal_toolkit.services.fiscal_calendar import MoroccanFiscalCalendar

router = APIRouter(prefix="/public", tags=["📅 Échéancier & Calendrier Fiscal Officiel"])

@router.get("/fiscal-year/deadlines", summary="📅 Calendrier complet des déclarations et paiements d'impôts")
def get_fiscal_deadlines(
    year: int = Query(default=0, description="Année fiscale (défaut: année courante)"),
    regime: str = Query("SARL", description="Régime: SARL, SA, AUTO_ENTREPRENEUR, CPU, PERSONNE_PHYSIQUE"),
    tva_regime: str = Query("MENSUEL", description="Périodicité TVA: MENSUEL, TRIMESTRIEL, EXONERE")
):
    """
    **Calendrier Fiscal Marocain Personnalisé.**
    Génère l'échéancier officiel des déclarations et règlements fiscaux pour l'année sélectionnée :
    - Acomptes et solde de l'Impôt sur les Sociétés (IS)
    - Déclarations de TVA (mensuelles ou trimestrielles)
    - Retenues sur salaires (IR) et bordereaux CNSS / AMO
    - Taxe Professionnelle et Taxe de Services Communaux
    - Déclarations Loi 69-21 (Délais de paiement)
    - Facturation électronique Simpl-TVA.
    """
    y = year if year > 2000 else date.today().year
    return MoroccanFiscalCalendar.get_calendar(year=y, regime=regime, tva_regime=tva_regime)
