from fastapi import APIRouter
from pydantic import BaseModel, Field
from morocco_fiscal_toolkit.services.qr_decoder import WaslQrDecoder
from morocco_fiscal_toolkit.services.qr_generator import InvoiceQrService

router = APIRouter(prefix="/public", tags=["📷 QR Codes Fiscaux & Paiement (Simpl-TVA & CMI Fatourati)"])

class QrDecodeRequest(BaseModel):
    payload: str = Field(..., description="Contenu brut du QR Code scanné (Base64 Simpl-TVA ou chaîne Fatourati)")

@router.post("/qr-invoice/decode", summary="📷 Décoder & vérifier un QR Code Facture (Simpl-TVA ou Fatourati)")
def decode_qr(req: QrDecodeRequest):
    """
    **Décodeur Universel de QR Codes de Facturation Marocaine.**
    - Décode les QR codes de visa Simpl-TVA (DGI Clearance CTC - Base64 JSON).
    - Décode les QR codes de paiement interbancaire CMI Fatourati.
    - Effectue une vérification en temps réel de l'ICE de l'émetteur auprès du registre légal.
    """
    return WaslQrDecoder.decode_and_verify(req.payload)

@router.get("/qr-invoice/demo-sample", summary="🎯 Échantillons de QR Codes pour tests d'intégration")
def get_qr_demo_samples():
    """
    **Générateur d'Échantillons QR de Démonstration.**
    Génère des exemples valides avec images PNG en base64 pour tester les flux de scanning et de validation.
    """
    sample_simpl_payload = InvoiceQrService.generate_simpl_tva_payload(
        seller_name="Atlas Digital Services SARL",
        seller_ice="001524368000042",
        issue_datetime="2026-09-27T10:30:00Z",
        total_ttc=18000.00,
        total_tva=3000.00,
        clearance_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        clearance_ref="IRN-SIMPL-2026-09-00128"
    )
    simpl_qr_img = InvoiceQrService.render_qr_base64_data_uri(sample_simpl_payload)

    sample_fatourati_payload = InvoiceQrService.generate_fatourati_payment_qr(
        merchant_ice="001524368000042",
        invoice_id="FAC-2026-0042",
        amount=18000.00,
        merchant_name="Atlas Digital Services"
    )
    fatourati_qr_img = InvoiceQrService.render_qr_base64_data_uri(sample_fatourati_payload)

    return {
        "simpl_tva_sample": {
            "title": "Facture Conforme Simpl-TVA (DGI Clearance CTC)",
            "payload": sample_simpl_payload,
            "qr_image_data_uri": simpl_qr_img
        },
        "fatourati_sample": {
            "title": "Paiement CMI Fatourati Interbancaire",
            "payload": sample_fatourati_payload,
            "qr_image_data_uri": fatourati_qr_img
        }
    }
