from fastapi import APIRouter, Query
from morocco_fiscal_toolkit.services.rib_validator import MoroccanRibValidator

router = APIRouter(prefix="/public", tags=["🏦 Banque & RIB/IBAN (GPBM / Bank Al-Maghrib)"])

@router.get("/validate-rib", summary="✅ Valider un RIB marocain (24 chiffres) → IBAN")
def validate_rib(
    rib: str = Query(..., description="RIB marocain 24 chiffres (ex: 007780000123456789012345) ou IBAN MA28")
):
    """
    **Validation RIB Marocain (24 chiffres).**
    - Identifie l'établissement bancaire affilié GPBM (Attijariwafa, BCP, CIH, BOA, BMCI, etc.).
    - Vérifie la clé de contrôle officielle Modulo-97 GPBM.
    - Génère automatiquement le code IBAN Marocain (MA + 2 check + 24 chiffres) et code SWIFT/BIC.
    """
    return MoroccanRibValidator.validate_rib(rib)

@router.get("/bank/rib-to-iban", summary="🏦 Convertir un RIB en IBAN Marocain (MA)")
def rib_to_iban(
    rib: str = Query(..., description="RIB marocain 24 chiffres")
):
    """
    **Conversion directe RIB → IBAN Marocain ISO 13616.**
    """
    res = MoroccanRibValidator.validate_rib(rib)
    if not res.get("is_valid"):
        return res
    return {
        "rib": res["rib"],
        "iban": res["iban"],
        "formatted_iban": res["formatted_iban"],
        "bank_name": res["bank_name"],
        "swift_bic": res["swift_bic"],
        "key_valid": res["key_valid"],
    }
