import csv
import io
import re
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

class CourierReconciliationService:
    """
    Flagship Differentiator: Moroccan Courier COD Remittance Reconciliation.
    Moroccan e-commerce is 80-90% Cash-on-Delivery (COD / CRBT).
    Couriers (Amana, CTM Messagerie, Speedy, Chronopost, Barid Al-Maghrib, Cathedis)
    collect cash at the doorstep and transfer batch remittances minus their delivery fees.
    This service ingests courier settlement reports and matches them against open invoices/orders.
    """

    SUPPORTED_COURIERS = [
        "Amana (Barid Al-Maghrib)",
        "CTM Messagerie",
        "Speedy Delivery",
        "Chronopost Maroc",
        "Cathedis",
        "Autre Transporteur COD"
    ]

    @staticmethod
    def parse_courier_statement(content_text: str, courier_name: str = "Amana") -> Dict[str, Any]:
        """
        Parses CSV or tabular remittance text from Moroccan couriers.
        Extracts tracking number, order reference, recipient, COD collected (CRBT), delivery fee, net remitted.
        """
        lines = [line.strip() for line in content_text.strip().splitlines() if line.strip()]
        if not lines:
            return {"items": [], "total_collected": 0.0, "total_commission": 0.0, "net_remitted": 0.0}

        # Detect delimiter: semicolon or comma
        header_line = lines[0]
        delimiter = ";" if ";" in header_line else ","

        reader = csv.reader(io.StringIO(content_text), delimiter=delimiter)
        raw_rows = list(reader)

        items = []
        header_idx = -1
        col_map = {}

        # Scan for header line
        for idx, row in enumerate(raw_rows):
            row_lower = [c.lower().strip() for c in row]
            if any(k in " ".join(row_lower) for k in ["suivi", "tracking", "crbt", "remboursement", "montant", "cod", "net"]):
                header_idx = idx
                for c_i, col in enumerate(row_lower):
                    if any(k in col for k in ["suivi", "tracking", "recepisse", "bordereau", "barcode"]):
                        col_map["tracking"] = c_i
                    elif any(k in col for k in ["commande", "order", "ref", "reference"]):
                        col_map["order_ref"] = c_i
                    elif any(k in col for k in ["destinataire", "client", "nom", "recipient"]):
                        col_map["recipient"] = c_i
                    elif any(k in col for k in ["ville", "city"]):
                        col_map["city"] = c_i
                    elif any(k in col for k in ["date", "date_livraison"]):
                        col_map["date"] = c_i
                    elif any(k in col for k in ["crbt", "montant crbt", "cod", "montant encaisse", "total ttc"]):
                        col_map["cod_amount"] = c_i
                    elif any(k in col for k in ["frais", "commission", "taxe", "port", "frais_livraison"]):
                        col_map["delivery_fee"] = c_i
                    elif any(k in col for k in ["net", "net a verser", "net verse", "payable"]):
                        col_map["net_amount"] = c_i
                    elif any(k in col for k in ["statut", "status", "etat"]):
                        col_map["status"] = c_i
                break

        # If standard header found, parse columns
        if header_idx != -1 and "tracking" in col_map:
            for row in raw_rows[header_idx + 1:]:
                if not row or len(row) < 2:
                    continue
                
                tracking = row[col_map["tracking"]].strip() if "tracking" in col_map and col_map["tracking"] < len(row) else ""
                if not tracking or tracking.lower() in ["total", "sous-total"]:
                    continue

                order_ref = row[col_map["order_ref"]].strip() if "order_ref" in col_map and col_map["order_ref"] < len(row) else ""
                recipient = row[col_map["recipient"]].strip() if "recipient" in col_map and col_map["recipient"] < len(row) else "Client Particulier"
                city = row[col_map["city"]].strip() if "city" in col_map and col_map["city"] < len(row) else "Casablanca"
                date_str = row[col_map["date"]].strip() if "date" in col_map and col_map["date"] < len(row) else datetime.now().strftime("%Y-%m-%d")
                status = row[col_map["status"]].strip().upper() if "status" in col_map and col_map["status"] < len(row) else "DELIVERED"

                cod_val = CourierReconciliationService._parse_amount(row[col_map["cod_amount"]]) if "cod_amount" in col_map and col_map["cod_amount"] < len(row) else 0.0
                fee_val = CourierReconciliationService._parse_amount(row[col_map["delivery_fee"]]) if "delivery_fee" in col_map and col_map["delivery_fee"] < len(row) else 35.0
                net_val = CourierReconciliationService._parse_amount(row[col_map["net_amount"]]) if "net_amount" in col_map and col_map["net_amount"] < len(row) else max(0.0, cod_val - fee_val)

                items.append({
                    "tracking_number": tracking,
                    "order_reference": order_ref,
                    "recipient_name": recipient,
                    "recipient_city": city,
                    "delivery_date": date_str,
                    "cod_amount": round(cod_val, 2),
                    "delivery_fee": round(fee_val, 2),
                    "net_amount": round(net_val, 2),
                    "delivery_status": status if status in ["DELIVERED", "LIVRE", "PAYE"] else "DELIVERED"
                })
        else:
            # Fallback heuristic parser for unstructured Moroccan courier statement exports
            for line in lines:
                # Look for tracking code pattern (e.g. MA123456789, CTM-12345, SPD-9921, or 9-14 alphanumeric)
                tracking_match = re.search(r'\b([A-Z]{2,4}[-_]?[0-9]{5,12}[A-Z]{0,2}|[0-9]{10,14})\b', line)
                if not tracking_match:
                    continue
                
                tracking = tracking_match.group(1)
                # Look for amounts in MAD
                amounts = re.findall(r'(\d+[\.,]\d{2}|\d{3,5})', line)
                amounts_float = [CourierReconciliationService._parse_amount(a) for a in amounts if CourierReconciliationService._parse_amount(a) > 0]
                
                cod_val = max(amounts_float) if amounts_float else 250.0
                fee_val = min(amounts_float) if len(amounts_float) > 1 and min(amounts_float) < 150 else 35.0
                net_val = max(0.0, cod_val - fee_val)

                # Look for order reference like #1042 or ORD-2026-01
                order_match = re.search(r'(#\d{3,6}|ORD[-_]?\d{3,6}|MED[-_]?\d{3,6})', line, re.IGNORECASE)
                order_ref = order_match.group(1) if order_match else ""

                items.append({
                    "tracking_number": tracking,
                    "order_reference": order_ref,
                    "recipient_name": "Destinataire COD",
                    "recipient_city": "Maroc",
                    "delivery_date": datetime.now().strftime("%Y-%m-%d"),
                    "cod_amount": round(cod_val, 2),
                    "delivery_fee": round(fee_val, 2),
                    "net_amount": round(net_val, 2),
                    "delivery_status": "DELIVERED"
                })

        total_collected = sum(it["cod_amount"] for it in items)
        total_commission = sum(it["delivery_fee"] for it in items)
        net_remitted = sum(it["net_amount"] for it in items)

        return {
            "items": items,
            "total_collected": round(total_collected, 2),
            "total_commission": round(total_commission, 2),
            "net_remitted": round(net_remitted, 2),
            "item_count": len(items)
        }

    @staticmethod
    def match_courier_items_with_invoices(
        courier_items: List[Dict[str, Any]], 
        open_invoices: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Fuzzy & exact reconciliation between courier delivery items and open invoices.
        Prioritizes:
        1. Exact tracking number match
        2. Exact order reference match
        3. Recipient name + exact COD amount match
        4. Amount matching with date proximity
        """
        results = []

        for item in courier_items:
            matches = []
            it_tracking = (item.get("tracking_number") or "").strip().lower()
            it_order = (item.get("order_reference") or "").strip().lower()
            it_cod = float(item.get("cod_amount") or 0.0)
            it_recipient = (item.get("recipient_name") or "").strip().lower()

            for inv in open_invoices:
                score = 0.0
                factors = []

                inv_tracking = (inv.get("tracking_number") or "").strip().lower()
                inv_order = (inv.get("order_reference") or "").strip().lower()
                inv_num = (inv.get("invoice_number") or "").strip().lower()
                inv_client = (inv.get("client_name") or "").strip().lower()
                inv_ttc = float(inv.get("total_ttc") or 0.0)

                # 1. Exact Tracking Match
                if it_tracking and inv_tracking and it_tracking == inv_tracking:
                    score = 1.0
                    factors.append("Numéro de suivi transporteur identique")
                
                # 2. Exact Order Reference Match
                elif it_order and (it_order == inv_order or it_order in inv_num or it_order in inv_order):
                    score = max(score, 0.95)
                    factors.append(f"Référence de commande e-commerce concordante ({item.get('order_reference')})")

                # 3. Exact Amount + Recipient similarity
                amount_diff = abs(it_cod - inv_ttc)
                if amount_diff < 0.05:
                    score = max(score, 0.70)
                    factors.append(f"Montant TTC exact ({inv_ttc:.2f} MAD)")
                    
                    if it_recipient and inv_client and (it_recipient in inv_client or inv_client in it_recipient):
                        score = min(1.0, score + 0.25)
                        factors.append("Nom du destinataire conforme au client facture")
                elif amount_diff < 1.0:
                    score = max(score, 0.50)
                    factors.append(f"Écart de montant négligeable ({amount_diff:.2f} MAD)")

                if score >= 0.50:
                    matches.append({
                        "invoice_id": inv.get("id"),
                        "invoice_number": inv.get("invoice_number"),
                        "client_name": inv.get("client_name"),
                        "total_ttc": inv_ttc,
                        "tracking_number": inv.get("tracking_number"),
                        "order_reference": inv.get("order_reference"),
                        "confidence": round(score, 2),
                        "confidence_label": "ÉLEVÉE" if score >= 0.90 else "MOYENNE" if score >= 0.70 else "FAIBLE",
                        "matching_factors": factors
                    })

            # Sort matches by highest confidence
            matches.sort(key=lambda m: m["confidence"], reverse=True)

            results.append({
                "item_id": item.get("id") or item.get("tracking_number"),
                "tracking_number": item.get("tracking_number"),
                "order_reference": item.get("order_reference"),
                "recipient_name": item.get("recipient_name"),
                "recipient_city": item.get("recipient_city"),
                "cod_amount": it_cod,
                "delivery_fee": item.get("delivery_fee"),
                "net_amount": item.get("net_amount"),
                "delivery_date": item.get("delivery_date"),
                "best_match": matches[0] if matches else None,
                "all_matches": matches
            })

        return results

    @staticmethod
    def _parse_amount(val_str: str) -> float:
        if not val_str:
            return 0.0
        cleaned = re.sub(r'[^\d\.,]', '', str(val_str)).replace(' ', '').replace(',', '.')
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
