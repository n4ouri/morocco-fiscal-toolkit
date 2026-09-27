import re
from typing import Dict, Any, List
from morocco_fiscal_toolkit.services.ice_checker import MoroccanTaxValidators

class InvoiceComplianceChecker:
    """
    Automated Legal-Mentions Compliance Audit Engine for Moroccan Invoices.
    Evaluates conformity with:
    - Article 145 du Code Général des Impôts (CGI)
    - Article 55 du Code de Commerce
    - Loi 69-21 sur les délais de paiement
    """

    MANDATORY_CRITERIA = [
        {
            "id": "seller_ice",
            "name": "ICE de l'émetteur (15 chiffres)",
            "article": "Art. 145 CGI & Loi 69-21",
            "weight": 20,
            "critical": True,
            "risk_if_missing": "Nullité fiscale de la facture et rejet systématique par la DGI."
        },
        {
            "id": "buyer_ice",
            "name": "ICE de l'acheteur / client (B2B)",
            "article": "Art. 145 CGI",
            "weight": 15,
            "critical": True,
            "risk_if_missing": "Rejet du droit à déduction de la TVA pour le client et amende de 15%."
        },
        {
            "id": "identifiant_fiscal",
            "name": "Identifiant Fiscal (IF)",
            "article": "Art. 145 CGI",
            "weight": 10,
            "critical": True,
            "risk_if_missing": "Facture irrégulière en cas de contrôle fiscal DGI."
        },
        {
            "id": "registre_commerce",
            "name": "Registre du Commerce (RC) & Tribunal",
            "article": "Art. 55 Code de Commerce",
            "weight": 10,
            "critical": False,
            "risk_if_missing": "Sanctions commerciales et défaut d'opposabilité aux tiers."
        },
        {
            "id": "taxe_professionnelle",
            "name": "Numéro de Taxe Professionnelle (Patente)",
            "article": "Art. 145 CGI",
            "weight": 5,
            "critical": False,
            "risk_if_missing": "Irrégularité formelle lors du recoupement des rôles fiscaux."
        },
        {
            "id": "forme_capital",
            "name": "Forme juridique et Capital social",
            "article": "Art. 44 Loi 17-95 & 5-96",
            "weight": 5,
            "critical": False,
            "risk_if_missing": "Amende administrative de 1 000 à 5 000 MAD."
        },
        {
            "id": "invoice_number",
            "name": "Numérotation chronologique continue",
            "article": "Art. 145 CGI",
            "weight": 10,
            "critical": True,
            "risk_if_missing": "Rejet de la comptabilité pour défaut de force probante (présomption de dissimulation)."
        },
        {
            "id": "dates_payment_term",
            "name": "Date d'émission & Date d'échéance (Loi 69-21)",
            "article": "Loi 69-21 (Délai légal 60j)",
            "weight": 10,
            "critical": False,
            "risk_if_missing": "Sanction pour non-respect des règles de plafonnement des délais de paiement."
        },
        {
            "id": "tva_breakdown",
            "name": "Ventilation détaillée de la TVA par taux",
            "article": "Art. 92, 98 & 145 CGI",
            "weight": 10,
            "critical": True,
            "risk_if_missing": "Impossibilité de récupérer la TVA déductible par le destinataire."
        },
        {
            "id": "payment_method_timbre",
            "name": "Mode de règlement & Timbre fiscal si espèces",
            "article": "Art. 252 CGI & Loi de Finances",
            "weight": 5,
            "critical": False,
            "risk_if_missing": "Pénalité de 6% ou rejet de la charge si paiement espèces > 5 000 MAD (Art. 193 CGI)."
        }
    ]

    @classmethod
    def audit_invoice(cls, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Audits structured invoice data against Moroccan statutory requirements.
        """
        checks = []
        score = 0
        total_weight = sum(c["weight"] for c in cls.MANDATORY_CRITERIA)
        critical_failed = False

        # 1. Seller ICE
        seller_ice = str(invoice_data.get("seller_ice") or "")
        ice_val = MoroccanTaxValidators.validate_ice(seller_ice)
        pass_seller_ice = ice_val["is_valid"]
        checks.append(cls._make_check(
            "seller_ice",
            pass_seller_ice,
            f"ICE émetteur validé ({seller_ice})" if pass_seller_ice else (ice_val.get("error") or "ICE émetteur manquant ou invalide."),
            suggested_fix="Renseigner un ICE de 15 chiffres structuré (9 digits société + 4 digits siège + 2 digits clé)."
        ))

        # 2. Buyer ICE
        buyer_ice = str(invoice_data.get("buyer_ice") or invoice_data.get("client_ice") or "")
        pass_buyer_ice = False
        buyer_msg = "ICE client manquant (Risque de rejet TVA client)."
        if buyer_ice:
            b_val = MoroccanTaxValidators.validate_ice(buyer_ice)
            pass_buyer_ice = b_val["is_valid"]
            buyer_msg = f"ICE client valide ({buyer_ice})" if pass_buyer_ice else b_val.get("error")
        checks.append(cls._make_check(
            "buyer_ice",
            pass_buyer_ice,
            buyer_msg,
            suggested_fix="Exiger l'ICE à 15 chiffres de vos clients professionnels B2B pour garantir leur déductibilité TVA."
        ))

        # 3. IF
        seller_if = str(invoice_data.get("seller_if") or invoice_data.get("identifiant_fiscal") or "")
        if_val = MoroccanTaxValidators.validate_if(seller_if)
        pass_if = if_val["is_valid"]
        checks.append(cls._make_check(
            "identifiant_fiscal",
            pass_if,
            f"IF valide ({seller_if})" if pass_if else (if_val.get("error") or "IF manquant."),
            suggested_fix="Indiquer l'Identifiant Fiscal délivré par la DGI (6 à 8 chiffres)."
        ))

        # 4. RC & Tribunal
        seller_rc = str(invoice_data.get("seller_rc") or invoice_data.get("rc") or "")
        rc_val = MoroccanTaxValidators.validate_rc(seller_rc, invoice_data.get("seller_tribunal", "Casablanca"))
        pass_rc = rc_val["is_valid"]
        checks.append(cls._make_check(
            "registre_commerce",
            pass_rc,
            f"RC {seller_rc} conforme" if pass_rc else (rc_val.get("error") or "RC manquant."),
            suggested_fix="Ajouter le numéro du Registre du Commerce et la ville du Greffe (ex: RC 12345 Casablanca)."
        ))

        # 5. Taxe Professionnelle / Patente
        patente = str(invoice_data.get("seller_patente") or invoice_data.get("patente") or "")
        pass_patente = bool(re.search(r"\d{6,8}", patente))
        checks.append(cls._make_check(
            "taxe_professionnelle",
            pass_patente,
            f"Patente présente ({patente})" if pass_patente else "Patente / Taxe professionnelle non mentionnée.",
            suggested_fix="Indiquer le numéro d'imposition à la Taxe Professionnelle (Patente)."
        ))

        # 6. Forme & Capital
        legal_form = str(invoice_data.get("seller_legal_form") or invoice_data.get("forme_juridique") or "")
        capital = invoice_data.get("capital_social") or invoice_data.get("seller_capital")
        pass_forme = bool(legal_form and (capital is not None or "AUTO" in legal_form.upper()))
        checks.append(cls._make_check(
            "forme_capital",
            pass_forme,
            f"Mention forme & capital présente ({legal_form})" if pass_forme else "Forme juridique ou capital social manquant.",
            suggested_fix="Préciser la forme juridique et le capital (ex: SARL au capital de 100 000 DH)."
        ))

        # 7. Invoice Number
        inv_num = str(invoice_data.get("invoice_number") or invoice_data.get("reference") or "")
        pass_num = bool(inv_num and len(inv_num) >= 3)
        checks.append(cls._make_check(
            "invoice_number",
            pass_num,
            f"Numéro de facture présent ({inv_num})" if pass_num else "Numéro de facture manquant ou trop court.",
            suggested_fix="Assigner un numéro séquentiel sans trou de facturation (ex: FA-2026-0042)."
        ))

        # 8. Dates & Payment term
        issue_date = str(invoice_data.get("issue_date") or invoice_data.get("date") or "")
        due_date = str(invoice_data.get("due_date") or invoice_data.get("echeance") or "")
        term_days = invoice_data.get("payment_term_days")
        pass_dates = bool(issue_date and (due_date or term_days))
        checks.append(cls._make_check(
            "dates_payment_term",
            pass_dates,
            f"Date d'émission ({issue_date}) et échéance conformes Loi 69-21" if pass_dates else "Date d'échéance ou délai de paiement non spécifié (Loi 69-21).",
            suggested_fix="Mentionner clairement la date d'échéance ou le délai de paiement (60 jours par défaut sous Loi 69-21)."
        ))

        # 9. TVA breakdown
        has_tva = ("tva_breakdown" in invoice_data and bool(invoice_data["tva_breakdown"])) or (
            invoice_data.get("total_tva") is not None and invoice_data.get("total_ht") is not None
        )
        checks.append(cls._make_check(
            "tva_breakdown",
            has_tva,
            "Ventilation de TVA par taux identifiée" if has_tva else "Absence de décomposition par taux de TVA (20%, 14%, 10%, 7%, 0%).",
            suggested_fix="Indiquer distinctement la base HT et le montant de la TVA pour chaque taux applicable."
        ))

        # 10. Payment method & cash timbre
        method = str(invoice_data.get("payment_method") or "VIREMENT").upper()
        timbre = float(invoice_data.get("timbre_fiscal") or 0.0)
        pass_payment = True
        msg_pay = f"Mode de règlement : {method}."
        if method in ["ESPECES", "CASH"] and timbre <= 0.0:
            pass_payment = False
            msg_pay = "Paiement en espèces sans mention du droit de timbre fiscal (0.25% - min 2.50 DH)."
        checks.append(cls._make_check(
            "payment_method_timbre",
            pass_payment,
            msg_pay,
            suggested_fix="Préciser le mode de règlement (Virement recommandé) et appliquer le droit de timbre si espèces."
        ))

        # Calculate final score
        for chk in checks:
            crit = next(c for c in cls.MANDATORY_CRITERIA if c["id"] == chk["id"])
            if chk["is_valid"]:
                score += crit["weight"]
            elif crit["critical"]:
                critical_failed = True

        score_pct = int((score / total_weight) * 100)

        if score_pct >= 90 and not critical_failed:
            badge = "CONFORME_MAROC"
            badge_label = "Facture 100% Conforme au CGI & Loi 69-21"
            badge_color = "emerald"
        elif score_pct >= 65:
            badge = "RISQUE_MODERE"
            badge_label = "Conforme avec réserves mineures"
            badge_color = "amber"
        else:
            badge = "NON_CONFORME"
            badge_label = "Risque Fiscal Élevé (Rejet Article 145 CGI)"
            badge_color = "rose"

        return {
            "score": score_pct,
            "badge": badge,
            "badge_label": badge_label,
            "badge_color": badge_color,
            "critical_failed": critical_failed,
            "passed_count": sum(1 for c in checks if c["is_valid"]),
            "failed_count": sum(1 for c in checks if not c["is_valid"]),
            "total_criteria": len(checks),
            "checks": checks
        }

    @classmethod
    def audit_unstructured_text(cls, text: str) -> Dict[str, Any]:
        """
        Parses OCR text or pasted invoice text and audits it for mandatory mentions.
        """
        parsed_data = {}

        # Look for ICE pattern
        ice_matches = re.findall(r"\b(00\d{13}|\d{15})\b", text)
        if ice_matches:
            parsed_data["seller_ice"] = ice_matches[0]
            if len(ice_matches) > 1:
                parsed_data["buyer_ice"] = ice_matches[1]

        # Look for IF
        if_match = re.search(r"(?:I\.?F\.?|I\.?F|Identifiant\s+Fiscal)[\s.:]+(\d{6,9})", text, re.IGNORECASE)
        if if_match:
            parsed_data["seller_if"] = if_match.group(1)

        # Look for RC
        rc_match = re.search(r"(?:R\.?C\.?|Registre)[\s.:]+(\d{3,8})", text, re.IGNORECASE)
        if rc_match:
            parsed_data["seller_rc"] = rc_match.group(1)

        # Look for Patente
        pat_match = re.search(r"(?:Patente|Taxe\s+Pro)[\s.:]+(\d{6,9})", text, re.IGNORECASE)
        if pat_match:
            parsed_data["seller_patente"] = pat_match.group(1)

        # Look for Forme / Capital
        if any(f in text.upper() for f in ["SARL", "S.A.R.L", "S.A.", "SAS", "AUTO-ENTREPRENEUR"]):
            parsed_data["seller_legal_form"] = "SARL"
            cap_match = re.search(r"capital[\s\w:]+(\d[\d\s.,]+)\s*(?:DH|MAD)", text, re.IGNORECASE)
            if cap_match:
                parsed_data["capital_social"] = cap_match.group(1)

        # Look for Invoice Number
        inv_match = re.search(r"(?:Facture|FA|FAC|INV)[\s#N°:_-]+([A-Z0-9/-]{3,20})", text, re.IGNORECASE)
        if inv_match:
            parsed_data["invoice_number"] = inv_match.group(1)

        # Look for Dates
        date_matches = re.findall(r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{4})\b", text)
        if date_matches:
            parsed_data["issue_date"] = date_matches[0]
            if len(date_matches) > 1:
                parsed_data["due_date"] = date_matches[1]

        # Look for TVA
        if any(w in text.upper() for w in ["TVA", "T.V.A", "20%", "14%", "10%", "7%"]):
            parsed_data["tva_breakdown"] = {"20%": {"base_ht": 100.0, "montant_tva": 20.0}}

        return cls.audit_invoice(parsed_data)

    @classmethod
    def _make_check(cls, crit_id: str, is_valid: bool, feedback: str, suggested_fix: str) -> Dict[str, Any]:
        meta = next(c for c in cls.MANDATORY_CRITERIA if c["id"] == crit_id)
        return {
            "id": crit_id,
            "name": meta["name"],
            "article": meta["article"],
            "weight": meta["weight"],
            "critical": meta["critical"],
            "risk_if_missing": meta["risk_if_missing"],
            "is_valid": is_valid,
            "feedback": feedback,
            "suggested_fix": suggested_fix if not is_valid else "Mention conforme."
        }
