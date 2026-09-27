from fastapi import APIRouter, Query
from morocco_fiscal_toolkit.services.phone_validator import MoroccanPhoneValidator

router = APIRouter(prefix="/public", tags=["📱 Télécoms & Téléphonie (ANRT)"])

@router.get("/phone/parse", summary="📱 Parser & classifier un numéro de téléphone marocain")
def parse_phone(
    phone: str = Query(..., description="Numéro marocain (ex: 0661234567, +212661234567, 0522123456)")
):
    """
    **Parseur et Validateur Téléphonique Marocain (Plan National de Numérotation ANRT).**
    - Identifie l'opérateur de rattachement (Maroc Telecom / IAM, Orange Maroc, Inwi).
    - Détermine le type de ligne (Mobile, Fixe, Numéro Vert 0800, Numéro Surtaxé 0890).
    - Identifie la zone géographique pour les lignes fixes (Grand Casablanca, Rabat, Marrakech, Tanger, etc.).
    - Fournit le format international standard E.164 (+212...).
    """
    return MoroccanPhoneValidator.validate(phone)
