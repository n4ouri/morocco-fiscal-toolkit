from typing import List, Optional
from fastapi import APIRouter, Query, Body
from pydantic import BaseModel, Field

from morocco_fiscal_toolkit.services.ice_checker import MoroccanTaxValidators
from morocco_fiscal_toolkit.services.authenticated_adapter import DirectInfoAuthenticatedAdapter

router = APIRouter(prefix="/public", tags=["🏢 Identifiants Entreprise (ICE, IF, RC, CNSS)"])

class BatchIceRequest(BaseModel):
    ices: List[str] = Field(..., description="Liste d'ICE à valider (max 50)", max_length=50)

@router.get("/check-ice", summary="✅ Valider un ICE marocain (15 chiffres)")
def check_ice(
    ice: str = Query(..., description="ICE marocain à 15 chiffres (ex: 001526374000085)")
):
    """
    **Validation ICE Tier 1 & Modulo 97 + Lookup Annuaire OMPIC.**
    - Vérifie la structure : 9 chiffres (entreprise) + 4 chiffres (succursale) + 2 chiffres (clé).
    - Calcule la clé de contrôle officielle Modulo-97 (ISO 7064).
    - Recherche la dénomination sociale et la forme juridique auprès du registre OMPIC DirectInfo.
    """
    res = MoroccanTaxValidators.validate_ice(ice)
    if res.get("is_valid"):
        adapter = DirectInfoAuthenticatedAdapter()
        reg = adapter.check_ice(res["ice"])
        res["company_name"] = reg.get("company_name")
        res["legal_form"] = reg.get("legal_form")
        res["badge"] = reg.get("badge", "Numéro ICE valide et structuré (Maroc)")
        res["rc"] = reg.get("rc")
        res["tribunal"] = reg.get("tribunal")
        res["activity"] = reg.get("activity")
    return res

@router.get("/validate-if", summary="✅ Valider un Identifiant Fiscal (IF)")
def validate_if(
    identifiant_fiscal: str = Query(..., alias="if", description="Identifiant Fiscal DGI (6-9 chiffres)")
):
    """
    **Validation Identifiant Fiscal (IF DGI).**
    Mention obligatoire sur toutes les factures selon l'Article 145 du CGI.
    """
    return MoroccanTaxValidators.validate_if(identifiant_fiscal)

@router.get("/validate-rc", summary="✅ Valider un Registre du Commerce (RC)")
def validate_rc(
    rc: str = Query(..., description="Numéro RC (1-8 chiffres)"),
    tribunal: str = Query("Casablanca", description="Greffe du Tribunal de Commerce")
):
    """
    **Validation Registre du Commerce (RC).**
    Conforme à l'Article 55 du Code de Commerce marocain.
    """
    return MoroccanTaxValidators.validate_rc(rc, tribunal)

@router.get("/validate-cnss", summary="✅ Valider un numéro CNSS")
def validate_cnss(
    cnss: str = Query(..., description="Numéro d'affiliation CNSS (7-10 chiffres)")
):
    """
    **Validation Numéro CNSS.**
    Vérifie le format du numéro d'affiliation à la Caisse Nationale de Sécurité Sociale.
    """
    return MoroccanTaxValidators.validate_cnss(cnss)

@router.get("/registry/search", summary="🔍 Rechercher une entreprise par nom / mot-clé (OMPIC)")
def search_registry(
    q: str = Query(..., description="Nom de l'entreprise, sigle ou mot-clé"),
    limit: int = Query(10, ge=1, le=50, description="Nombre maximum de résultats")
):
    """
    **Recherche OMPIC DirectInfo.**
    Recherche instantanée parmi le répertoire des institutions, banques, et grandes entreprises marocaines.
    """
    adapter = DirectInfoAuthenticatedAdapter()
    return adapter.search_by_name(q, limit=limit)

@router.post("/batch/validate-ices", summary="🔄 Valider jusqu'à 50 ICE en un appel (ERP Batch)")
def batch_validate_ices(req: BatchIceRequest):
    """
    **Validation par Lot d'ICE (jusqu'à 50).**
    Idéal pour les imports ERP, l'on-boarding fournisseurs et le nettoyage de bases de données.
    """
    results = []
    for ice in req.ices:
        res = MoroccanTaxValidators.validate_ice(ice)
        results.append({"ice": ice, "result": res})

    valid_count = sum(1 for r in results if r["result"].get("is_valid"))
    return {
        "total": len(results),
        "valid": valid_count,
        "invalid": len(results) - valid_count,
        "results": results
    }
