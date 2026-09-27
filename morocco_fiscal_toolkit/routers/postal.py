from fastapi import APIRouter, Query
from morocco_fiscal_toolkit.services.postal_lookup import MoroccanPostalLookup

router = APIRouter(prefix="/public", tags=["🏙️ Géographie & Codes Postaux (Barid Al-Maghrib)"])

@router.get("/postal/city", summary="🏙️ Code postal → Ville, Province & Région")
def lookup_postal_code(
    zip: str = Query(..., description="Code postal marocain à 5 chiffres (ex: 20000, 10000, 40000, 90000)")
):
    """
    **Annuaire des Codes Postaux du Maroc (Barid Al-Maghrib / HCP).**
    Retourne la ville, la province, la région administrative et la transcription arabe officielle.
    """
    return MoroccanPostalLookup.lookup(zip)
