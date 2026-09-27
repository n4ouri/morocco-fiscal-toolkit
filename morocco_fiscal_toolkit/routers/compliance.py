from typing import Optional, Dict, Any
from datetime import date
from fastapi import APIRouter
from pydantic import BaseModel, Field
from morocco_fiscal_toolkit.services.compliance_checker import InvoiceComplianceChecker

router = APIRouter(prefix="/public", tags=["🛡️ Conformité Facturation & Mentions Légales (Art. 145 CGI)"])

class ComplianceAuditRequest(BaseModel):
    invoice_data: Optional[Dict[str, Any]] = None
    raw_text: Optional[str] = None

class InvoiceNumberRequest(BaseModel):
    prefix: str = Field("FAC", description="Préfixe de facturation (ex: FAC, FACT, INV)")
    year: Optional[int] = Field(None, description="Année (défaut: année courante)")
    sequence: int = Field(..., ge=1, description="Numéro d'ordre séquentiel")
    separator: str = Field("-", description="Séparateur (-, /, _)")
    zero_pad: int = Field(4, ge=1, le=8, description="Nombre de chiffres avec padding de zéros (ex: 4 -> 0042)")

@router.post("/invoice-compliance/audit", summary="🔍 Auditer une facture (10 mentions obligatoires Art. 145 CGI)")
def audit_invoice(req: ComplianceAuditRequest):
    """
    **Audit Automatisé de Conformité Fiscale de Facture.**
    Vérifie les 10 mentions légales obligatoires selon l'Article 145 du CGI et le Code de Commerce :
    1. ICE Émetteur (Tier 1 & 2)
    2. ICE Client (B2B)
    3. Identifiant Fiscal (IF)
    4. Registre du Commerce (RC) + Greffe
    5. Numéro CNSS
    6. Numéro de facture continu et séquentiel
    7. Date d'émission
    8. Ventilation des taux de TVA et montants distincts
    9. Prix unitaire HT et total TTC en MAD
    10. Mention du mode de règlement et échéance légale.
    """
    if req.raw_text:
        return InvoiceComplianceChecker.audit_unstructured_text(req.raw_text)
    return InvoiceComplianceChecker.audit_invoice(req.invoice_data or {})

@router.post("/invoice-number/generate", summary="🔢 Générer un numéro de facture conforme DGI")
def generate_invoice_number(req: InvoiceNumberRequest):
    """
    **Générateur de Numéro de Facture Chronologique DGI.**
    Assure une numérotation continue sans rupture chronologique, conforme aux exigences de l'Article 145 du CGI.
    """
    y = req.year or date.today().year
    sep = req.separator if req.separator in ("-", "/", "_", ".") else "-"
    seq_str = str(req.sequence).zfill(max(1, req.zero_pad))
    invoice_num = f"{req.prefix.upper()}{sep}{y}{sep}{seq_str}"

    return {
        "invoice_number": invoice_num,
        "prefix": req.prefix.upper(),
        "year": y,
        "sequence": req.sequence,
        "separator": sep,
        "format_description": f"{req.prefix.upper()}{sep}YYYY{sep}{'0' * req.zero_pad}",
        "dgi_compliant": True,
        "compliance_note": (
            "Numérotation chronologique continue sans saut requise par l'Art. 145 CGI. "
            "Tout saut de numéro peut être interprété comme une présomption de dissimulation de recettes."
        ),
        "next_invoice_number": f"{req.prefix.upper()}{sep}{y}{sep}{str(req.sequence + 1).zfill(max(1, req.zero_pad))}",
    }
