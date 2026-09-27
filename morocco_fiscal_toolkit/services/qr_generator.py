import io
import json
import base64
import qrcode
from typing import Dict, Any

class InvoiceQrService:
    """
    QR Code Generator for Moroccan Invoices:
    1. Simpl-TVA Clearance QR Code (Article 145 CGI - DGI Verification)
    2. CMI Fatourati-compatible Payment QR Code
    """

    @classmethod
    def generate_simpl_tva_payload(
        cls,
        seller_name: str,
        seller_ice: str,
        issue_datetime: str,
        total_ttc: float,
        total_tva: float,
        clearance_hash: str,
        clearance_ref: str
    ) -> str:
        """
        Builds the standard clearance QR payload.
        Encodes seller ICE, issue date, TTC, TVA, and DGI clearance signature hash.
        """
        payload_data = {
            "v": "1.0",
            "dgi_portal": "simpl-tva.dgi.gov.ma",
            "seller": seller_name,
            "ice": seller_ice,
            "ts": issue_datetime,
            "ttc": f"{total_ttc:.2f}",
            "tva": f"{total_tva:.2f}",
            "irn": clearance_ref,
            "sig": clearance_hash[:32] if clearance_hash else "PROVISIONAL_PENDING"
        }
        json_str = json.dumps(payload_data, separators=(",", ":"))
        return base64.b64encode(json_str.encode("utf-8")).decode("utf-8")

    @classmethod
    def generate_fatourati_payment_qr(
        cls,
        merchant_ice: str,
        invoice_id: str,
        amount: float,
        merchant_name: str = "Fatoura Partner"
    ) -> str:
        """
        Generates CMI Fatourati-compatible payment payload format:
        e.g., FATOURATI|ICE|INVOICE_ID|AMOUNT|MAD
        """
        raw = f"FATOURATI*01*MA*{merchant_ice}*{invoice_id}*{amount:.2f}*MAD"
        return raw

    @classmethod
    def render_qr_image_bytes(cls, payload: str) -> bytes:
        """Renders QR code to PNG image bytes."""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=6,
            border=2,
        )
        qr.add_data(payload)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

    @classmethod
    def render_qr_base64_data_uri(cls, payload: str) -> str:
        """Returns base64 data URI for inline HTML / React rendering."""
        img_bytes = cls.render_qr_image_bytes(payload)
        b64 = base64.b64encode(img_bytes).decode("utf-8")
        return f"data:image/png;base64,{b64}"
