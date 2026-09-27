from typing import List, Dict, Any
from datetime import date, datetime, timedelta
from fastapi import APIRouter
from pydantic import BaseModel, Field
from morocco_fiscal_toolkit.services.loi_69_21 import Loi6921Service

router = APIRouter(prefix="/public", tags=["⚖️ Délais de Paiement & Loi 69-21 (Pénalités)"])

class Loi6921RiskRequest(BaseModel):
    annual_turnover_mad: float = Field(..., description="Chiffre d'affaires annuel en MAD")
    total_overdue_ttc: float = Field(0.0, description="Montant total TTC des factures en retard de paiement")
    avg_delay_days: int = Field(45, description="Délai moyen de retard en jours au-delà du terme légal")
    overdue_invoices_count: int = Field(0, description="Nombre de factures échues impayées")

class Loi6921PenaltyRequest(BaseModel):
    amount_ttc: float = Field(..., description="Montant TTC de la facture en MAD")
    days_overdue: int = Field(..., description="Nombre de jours de retard au-delà de l'échéance légale")

class PaymentDeadlineRequest(BaseModel):
    invoice_date: str = Field(..., description="Date de facturation (ISO 8601: YYYY-MM-DD)")
    payment_term_days: int = Field(60, description="Délai contractuel de paiement en jours (max 120j Loi 69-21)")
    amount_ttc: float = Field(0.0, description="Montant TTC optionnel (pour calcul de la pénalité)")

class Loi6921DeclarationRequest(BaseModel):
    company_name: str
    company_ice: str
    fiscal_year: int = 2025
    invoices: List[Dict[str, Any]] = Field(default_factory=list)

@router.post("/loi-69-21/risk-check", summary="⚖️ Évaluer l'exposition aux amendes Loi 69-21")
def check_risk(req: Loi6921RiskRequest):
    """
    **Audit d'exposition aux sanctions Loi 69-21.**
    Évalue l'assujettissement (CA > 2M MAD), les pénalités encourues (5 000 à 250 000 MAD d'amende forfaitaire + pénalités mensuelles)
    et les obligations de visa par un commissaire aux comptes ou expert-comptable.
    """
    return Loi6921Service.assess_risk(
        annual_turnover_mad=req.annual_turnover_mad,
        total_overdue_ttc=req.total_overdue_ttc,
        avg_delay_days=req.avg_delay_days,
        overdue_invoices_count=req.overdue_invoices_count
    )

@router.post("/loi-69-21/invoice-penalty", summary="💸 Calculer la pénalité de retard sur une facture")
def calculate_invoice_penalty(req: Loi6921PenaltyRequest):
    """
    **Calculateur officiel des pénalités Loi 69-21.**
    Applique le taux légal : (Taux directeur Bank Al-Maghrib / 12) + 0.85% par mois de retard commencé.
    """
    return Loi6921Service.calculate_invoice_penalty(
        amount_ttc=req.amount_ttc,
        days_overdue=req.days_overdue
    )

@router.post("/loi-69-21/payment-deadline", summary="📅 Calculer l'échéance légale de paiement")
def compute_payment_deadline(req: PaymentDeadlineRequest):
    """
    **Calculateur d'échéances légales Loi 69-21.**
    Contrôle le plafond légal de 120 jours (60 jours de droit commun), calcule la date limite exacte et le statut de dépassement.
    """
    try:
        invoice_dt = datetime.strptime(req.invoice_date[:10], "%Y-%m-%d").date()
    except ValueError:
        return {"is_valid": False, "error": "Format de date invalide. Utilisez YYYY-MM-DD."}

    term_days = min(max(1, req.payment_term_days), 120)
    due_date = invoice_dt + timedelta(days=term_days)
    today = date.today()
    days_overdue = max(0, (today - due_date).days)

    penalty = Loi6921Service.calculate_invoice_penalty(
        amount_ttc=req.amount_ttc,
        days_overdue=days_overdue
    ) if req.amount_ttc > 0 and days_overdue > 0 else None

    return {
        "invoice_date": invoice_dt.isoformat(),
        "payment_term_days": term_days,
        "due_date": due_date.isoformat(),
        "due_date_label": due_date.strftime("%d/%m/%Y"),
        "today": today.isoformat(),
        "days_remaining": max(0, (due_date - today).days),
        "is_overdue": days_overdue > 0,
        "days_overdue": days_overdue,
        "is_legally_capped": req.payment_term_days > 120,
        "legal_cap_note": (
            "⚠️ Le délai contractuel dépasse le plafond légal de 120 jours (Loi 69-21). "
            "Ramené automatiquement à 120 jours." if req.payment_term_days > 120 else "Délai conforme Loi 69-21."
        ),
        "penalty": penalty,
        "legal_basis": "Loi 69-21 modifiant la Loi 15-95 formant Code de Commerce"
    }

@router.post("/loi-69-21/generate-declaration", summary="📝 Générer l'état détaillé certifié des retards")
def generate_declaration(req: Loi6921DeclarationRequest):
    """
    **Générateur de l'État Détaillé des Factures Impayées.**
    Prépare le tableau officiel exigé pour la télédéclaration DGI Simpl-Adhésion / Téléservices.
    """
    return Loi6921Service.generate_detailed_declaration_report(
        invoices=req.invoices,
        company_ice=req.company_ice,
        company_name=req.company_name,
        fiscal_year=req.fiscal_year
    )
