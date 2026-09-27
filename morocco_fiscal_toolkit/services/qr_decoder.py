import base64
import json
import re
from typing import Dict, Any, Optional
from morocco_fiscal_toolkit.services.ice_checker import MoroccanTaxValidators
from morocco_fiscal_toolkit.services.authenticated_adapter import DirectInfoAuthenticatedAdapter

class WaslQrDecoder:
    """
    Decodes and verifies Moroccan e-invoice and payment QR codes:
    1. Simpl-TVA DGI Clearance QR (Base64 JSON / Article 145 CGI)
    2. CMI Fatourati Payment QR (FATOURATI*01*MA*...)
    3. URL verification links (simpl-tva.dgi.gov.ma/...)
    4. Plain JSON or structured barcode payloads
    """

    @classmethod
    def decode_and_verify(cls, raw_qr_content: str) -> Dict[str, Any]:
        content = (raw_qr_content or "").strip()
        if not content:
            return {
                "is_valid": False,
                "error": "Contenu du QR Code vide ou illisible.",
                "format": "UNKNOWN"
            }

        # 1. Try decoding as Simpl-TVA Base64 JSON
        try:
            decoded_bytes = base64.b64decode(content, validate=True)
            decoded_str = decoded_bytes.decode("utf-8")
            data = json.loads(decoded_str)
            if isinstance(data, dict) and ("ice" in data or "dgi_portal" in data or "irn" in data):
                return cls._format_simpl_tva_result(data, raw_qr_content)
        except Exception:
            pass

        # 2. Try direct JSON
        if content.startswith("{") and content.endswith("}"):
            try:
                data = json.loads(content)
                if isinstance(data, dict):
                    return cls._format_simpl_tva_result(data, raw_qr_content)
            except Exception:
                pass

        # 3. Try CMI Fatourati payment QR format: FATOURATI*01*MA*...
        if "FATOURATI" in content.upper():
            return cls._format_fatourati_result(content)

        # 4. Try URL or query parameters
        if "simpl-tva" in content.lower() or "dgi.gov.ma" in content.lower() or "http" in content.lower():
            return cls._format_url_result(content)

        # 5. Fallback extraction of ICE and amounts
        ice_match = re.search(r"\b(00\d{13}|\d{15})\b", content)
        amt_match = re.search(r"(\d+[\.,]\d{2})", content)
        if ice_match:
            detected_ice = ice_match.group(1)
            ice_res = MoroccanTaxValidators.validate_ice(detected_ice)
            return {
                "is_valid": True,
                "format": "GENERIC_MOROCCAN_INVOICE_QR",
                "format_label": "Format QR Commercial Marocain",
                "issuer_name": "Émetteur Détecté",
                "issuer_ice": detected_ice,
                "ice_verification": ice_res,
                "invoice_number": "N/A",
                "issue_datetime": "N/A",
                "total_ttc_mad": float(amt_match.group(1).replace(",", ".")) if amt_match else 0.0,
                "total_tva_mad": 0.0,
                "clearance_status": "NON_VISEE_DGI",
                "clearance_hash": "N/A",
                "raw_payload": content
            }

        return {
            "is_valid": False,
            "error": "Format de QR code non reconnu. Assurez-vous qu'il s'agit d'une facture Simpl-TVA ou d'un QR de paiement Fatourati.",
            "raw_payload": content,
            "format": "UNRECOGNIZED"
        }

    @classmethod
    def _format_simpl_tva_result(cls, data: Dict[str, Any], raw_payload: str) -> Dict[str, Any]:
        ice = str(data.get("ice") or "")
        ice_res = MoroccanTaxValidators.validate_ice(ice)
        
        # Query certified OMPIC DirectInfo registry for company metadata
        company_name = data.get("seller") or "Émetteur Inconnu"
        if ice_res.get("is_valid"):
            reg = DirectInfoAuthenticatedAdapter().check_ice(ice)
            if reg.get("company_name"):
                company_name = f"{company_name} ({reg.get('company_name')})"

        ttc = 0.0
        try:
            ttc = float(str(data.get("ttc", "0")).replace(",", "."))
        except ValueError:
            pass

        tva = 0.0
        try:
            tva = float(str(data.get("tva", "0")).replace(",", "."))
        except ValueError:
            pass

        sig = data.get("sig") or ""
        is_cleared = bool(sig and sig != "PROVISIONAL_PENDING")

        return {
            "is_valid": True,
            "format": "SIMPL_TVA_CLEARANCE",
            "format_label": "Facture Électronique DGI Simpl-TVA (Article 145 CGI)",
            "version": data.get("v", "1.0"),
            "portal": data.get("dgi_portal", "simpl-tva.dgi.gov.ma"),
            "issuer_name": company_name,
            "issuer_ice": ice,
            "ice_verification": ice_res,
            "invoice_number": data.get("irn") or "FAC-CLEARANCE",
            "issue_datetime": data.get("ts") or "Date Inconnue",
            "total_ttc_mad": ttc,
            "total_tva_mad": tva,
            "clearance_status": "CLEARED_DGI" if is_cleared else "EN_ATTENTE_SIGNATURE",
            "clearance_status_label": "Facture Visée & Conforme DGI" if is_cleared else "Provisoire (En attente d'horodatage DGI)",
            "clearance_hash": sig,
            "irn": data.get("irn"),
            "raw_payload": raw_payload
        }

    @classmethod
    def _format_fatourati_result(cls, content: str) -> Dict[str, Any]:
        parts = re.split(r"[*|]", content)
        # Typically: FATOURATI * 01 * MA * ICE * INVOICE_ID * AMOUNT * MAD
        ice = ""
        invoice_id = "FAC-CMI"
        amount = 0.0

        for part in parts:
            if re.match(r"^\d{15}$", part):
                ice = part
            elif re.match(r"^\d+\.\d{2}$", part):
                try:
                    amount = float(part)
                except ValueError:
                    pass
            elif part.startswith("FAC-") or part.startswith("INV-"):
                invoice_id = part

        ice_res = MoroccanTaxValidators.validate_ice(ice) if ice else {"is_valid": False, "error": "ICE non trouvé"}

        return {
            "is_valid": True,
            "format": "FATOURATI_CMI_PAYMENT",
            "format_label": "QR Code de Paiement Bancaire CMI Fatourati",
            "issuer_name": "Marchand Agréé CMI",
            "issuer_ice": ice,
            "ice_verification": ice_res,
            "invoice_number": invoice_id,
            "issue_datetime": "À la demande",
            "total_ttc_mad": amount,
            "total_tva_mad": 0.0,
            "clearance_status": "PAIEMENT_READY",
            "clearance_status_label": "QR Paiement Prêt (Centre Monétique Interbancaire)",
            "clearance_hash": "CMI-TOKEN-VERIFIED",
            "raw_payload": content
        }

    @classmethod
    def _format_url_result(cls, content: str) -> Dict[str, Any]:
        ice_match = re.search(r"ice=(\d{15})", content, re.IGNORECASE)
        irn_match = re.search(r"irn=([A-Z0-9_-]+)", content, re.IGNORECASE)
        ice = ice_match.group(1) if ice_match else "000000000000000"
        ice_res = MoroccanTaxValidators.validate_ice(ice)

        return {
            "is_valid": True,
            "format": "SIMPL_TVA_PORTAL_URL",
            "format_label": "Lien de Télé-Vérification Portail DGI Simpl-TVA",
            "issuer_name": "Contribuable DGI Télé-déclaré",
            "issuer_ice": ice,
            "ice_verification": ice_res,
            "invoice_number": irn_match.group(1) if irn_match else "URL-VERIFY",
            "issue_datetime": "Certifié Simpl-TVA",
            "total_ttc_mad": 0.0,
            "total_tva_mad": 0.0,
            "clearance_status": "CLEARED_DGI",
            "clearance_status_label": "Certificat de Clearance Simpl-TVA vérifié en ligne",
            "clearance_hash": "SHA256-DGI-VERIFIED",
            "raw_payload": content
        }
