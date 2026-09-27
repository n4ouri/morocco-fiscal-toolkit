import re
from typing import Dict, Any

class MoroccanPhoneValidator:
    """
    Parser and classifier for Moroccan telephone numbers.
    Handles local (06/07/05) and international (+212) formats.
    Identifies operator, line type (mobile/fixed/MVNO/toll-free), and city zone (fixed lines).

    Inspired by India's TRAI telecom API and Brazil's Anatel line checker.
    """

    # Mobile operator prefix mapping (first 6 digits after country code)
    MOBILE_PREFIXES: Dict[str, Dict[str, str]] = {
        # Maroc Telecom (IAM)
        "0600": {"operator": "Maroc Telecom (IAM)", "type": "MOBILE", "technology": "4G/5G"},
        "0601": {"operator": "Maroc Telecom (IAM)", "type": "MOBILE", "technology": "4G/5G"},
        "0602": {"operator": "Maroc Telecom (IAM)", "type": "MOBILE", "technology": "4G/5G"},
        "0603": {"operator": "Maroc Telecom (IAM)", "type": "MOBILE", "technology": "4G/5G"},
        "0604": {"operator": "Maroc Telecom (IAM)", "type": "MOBILE", "technology": "4G/5G"},
        "0605": {"operator": "Maroc Telecom (IAM)", "type": "MOBILE", "technology": "4G/5G"},
        "0606": {"operator": "Maroc Telecom (IAM)", "type": "MOBILE", "technology": "4G/5G"},
        "0607": {"operator": "Maroc Telecom (IAM)", "type": "MOBILE", "technology": "4G/5G"},
        "0608": {"operator": "Maroc Telecom (IAM)", "type": "MOBILE", "technology": "4G/5G"},
        "0609": {"operator": "Maroc Telecom (IAM)", "type": "MOBILE", "technology": "4G/5G"},
        "0610": {"operator": "Maroc Telecom (IAM)", "type": "MOBILE", "technology": "4G/5G"},
        "0611": {"operator": "Maroc Telecom (IAM)", "type": "MOBILE", "technology": "4G/5G"},
        "0612": {"operator": "Maroc Telecom (IAM)", "type": "MOBILE", "technology": "4G/5G"},
        "0613": {"operator": "Maroc Telecom (IAM)", "type": "MOBILE", "technology": "4G/5G"},
        "0614": {"operator": "Maroc Telecom (IAM)", "type": "MOBILE", "technology": "4G/5G"},
        "0615": {"operator": "Maroc Telecom (IAM)", "type": "MOBILE", "technology": "4G/5G"},
        "0616": {"operator": "Maroc Telecom (IAM)", "type": "MOBILE", "technology": "4G/5G"},
        "0617": {"operator": "Maroc Telecom (IAM)", "type": "MOBILE", "technology": "4G/5G"},
        "0618": {"operator": "Maroc Telecom (IAM)", "type": "MOBILE", "technology": "4G/5G"},
        "0619": {"operator": "Maroc Telecom (IAM)", "type": "MOBILE", "technology": "4G/5G"},
        "0620": {"operator": "Maroc Telecom (IAM)", "type": "MOBILE", "technology": "4G/5G"},
        "0621": {"operator": "Maroc Telecom (IAM)", "type": "MOBILE", "technology": "4G/5G"},
        "0622": {"operator": "Maroc Telecom (IAM)", "type": "MOBILE", "technology": "4G/5G"},
        "0623": {"operator": "Maroc Telecom (IAM)", "type": "MOBILE", "technology": "4G/5G"},
        "0624": {"operator": "Maroc Telecom (IAM)", "type": "MOBILE", "technology": "4G/5G"},
        # Orange Maroc
        "0650": {"operator": "Orange Maroc", "type": "MOBILE", "technology": "4G/5G"},
        "0651": {"operator": "Orange Maroc", "type": "MOBILE", "technology": "4G/5G"},
        "0652": {"operator": "Orange Maroc", "type": "MOBILE", "technology": "4G/5G"},
        "0653": {"operator": "Orange Maroc", "type": "MOBILE", "technology": "4G/5G"},
        "0654": {"operator": "Orange Maroc", "type": "MOBILE", "technology": "4G/5G"},
        "0655": {"operator": "Orange Maroc", "type": "MOBILE", "technology": "4G/5G"},
        "0656": {"operator": "Orange Maroc", "type": "MOBILE", "technology": "4G/5G"},
        "0657": {"operator": "Orange Maroc", "type": "MOBILE", "technology": "4G/5G"},
        "0658": {"operator": "Orange Maroc", "type": "MOBILE", "technology": "4G/5G"},
        "0659": {"operator": "Orange Maroc", "type": "MOBILE", "technology": "4G/5G"},
        "0660": {"operator": "Orange Maroc", "type": "MOBILE", "technology": "4G/5G"},
        "0661": {"operator": "Orange Maroc", "type": "MOBILE", "technology": "4G/5G"},
        "0662": {"operator": "Orange Maroc", "type": "MOBILE", "technology": "4G/5G"},
        "0663": {"operator": "Orange Maroc", "type": "MOBILE", "technology": "4G/5G"},
        "0664": {"operator": "Orange Maroc", "type": "MOBILE", "technology": "4G/5G"},
        "0665": {"operator": "Orange Maroc", "type": "MOBILE", "technology": "4G/5G"},
        "0666": {"operator": "Orange Maroc", "type": "MOBILE", "technology": "4G/5G"},
        # Inwi
        "0670": {"operator": "Inwi (WANA Corporate)", "type": "MOBILE", "technology": "4G"},
        "0671": {"operator": "Inwi (WANA Corporate)", "type": "MOBILE", "technology": "4G"},
        "0672": {"operator": "Inwi (WANA Corporate)", "type": "MOBILE", "technology": "4G"},
        "0673": {"operator": "Inwi (WANA Corporate)", "type": "MOBILE", "technology": "4G"},
        "0674": {"operator": "Inwi (WANA Corporate)", "type": "MOBILE", "technology": "4G"},
        "0675": {"operator": "Inwi (WANA Corporate)", "type": "MOBILE", "technology": "4G"},
        "0676": {"operator": "Inwi (WANA Corporate)", "type": "MOBILE", "technology": "4G"},
        "0677": {"operator": "Inwi (WANA Corporate)", "type": "MOBILE", "technology": "4G"},
        "0678": {"operator": "Inwi (WANA Corporate)", "type": "MOBILE", "technology": "4G"},
        "0679": {"operator": "Inwi (WANA Corporate)", "type": "MOBILE", "technology": "4G"},
        "0680": {"operator": "Inwi (WANA Corporate)", "type": "MOBILE", "technology": "4G"},
        "0681": {"operator": "Inwi (WANA Corporate)", "type": "MOBILE", "technology": "4G"},
        "0682": {"operator": "Inwi (WANA Corporate)", "type": "MOBILE", "technology": "4G"},
        "0683": {"operator": "Inwi (WANA Corporate)", "type": "MOBILE", "technology": "4G"},
    }

    # Fixed-line city zone prefixes (05XX)
    FIXED_ZONES: Dict[str, str] = {
        "0522": "Casablanca (Grand Casablanca)",
        "0523": "Casablanca (Périphérie)",
        "0524": "Marrakech & Tensift Al Haouz",
        "0525": "Beni Mellal & Khénifra",
        "0526": "Agadir & Souss-Massa",
        "0527": "Ouarzazate & Draa-Tafilalet",
        "0528": "Agadir (Zone Souss)",
        "0535": "Fès & Meknès",
        "0536": "Oujda & Oriental",
        "0537": "Rabat-Salé-Kénitra",
        "0538": "Kénitra & Gharb",
        "0539": "Tanger-Tétouan-Al Hoceima",
        "0548": "Laâyoune & Sahara",
    }

    @classmethod
    def normalize(cls, raw: str) -> str:
        """Strips formatting and converts +212 / 00212 to 0X format."""
        cleaned = re.sub(r"[\s\-\.\(\)/]", "", str(raw).strip())
        if cleaned.startswith("+212"):
            cleaned = "0" + cleaned[4:]
        elif cleaned.startswith("00212"):
            cleaned = "0" + cleaned[5:]
        return cleaned

    @classmethod
    def validate(cls, raw_phone: str) -> Dict[str, Any]:
        """
        Validates and classifies a Moroccan phone number.
        Returns operator, type (MOBILE/FIXED/TOLL_FREE), region, and international format.
        """
        if not raw_phone:
            return {"is_valid": False, "error": "Numéro de téléphone vide."}

        normalized = cls.normalize(raw_phone)

        # Must be 10 digits starting with 0
        if not re.fullmatch(r"0\d{9}", normalized):
            return {
                "is_valid": False,
                "error": f"Format invalide. Le numéro marocain doit comporter 10 chiffres commençant par 0 (reçu: {normalized}).",
                "raw": raw_phone,
                "normalized": normalized
            }

        prefix4 = normalized[:4]
        prefix3 = normalized[:4]  # kept for clarity

        # Toll-free / premium
        if normalized.startswith("080"):
            return cls._build_result(normalized, raw_phone, "Numéro Vert / Gratuit", "TOLL_FREE", "N/A", "4G/N/A")
        if normalized.startswith("089") or normalized.startswith("090"):
            return cls._build_result(normalized, raw_phone, "Numéro Surtaxé", "PREMIUM", "N/A", "N/A")

        # Mobile
        if prefix4 in cls.MOBILE_PREFIXES:
            info = cls.MOBILE_PREFIXES[prefix4]
            return cls._build_result(normalized, raw_phone, info["operator"], info["type"], "National", info["technology"])

        # Generic mobile by first 2 digits
        first2 = normalized[:2]
        if first2 in ("06", "07"):
            operator = "Opérateur Mobile Marocain (Préfixe non cartographié ANRT)"
            return cls._build_result(normalized, raw_phone, operator, "MOBILE", "National", "4G")

        # Fixed
        if normalized.startswith("05"):
            zone = cls.FIXED_ZONES.get(prefix4)
            region = zone or "Zone Fixe Marocaine (Préfixe non cartographié ANRT)"
            return cls._build_result(normalized, raw_phone, "Maroc Telecom / Opérateur Fixe", "FIXED", region, "ADSL/Fibre")

        return {
            "is_valid": False,
            "error": f"Préfixe non reconnu par l'ANRT Maroc ({normalized[:4]}).",
            "raw": raw_phone,
            "normalized": normalized
        }

    @classmethod
    def _build_result(cls, normalized: str, raw: str, operator: str, line_type: str, region: str, technology: str) -> Dict[str, Any]:
        international = "+212" + normalized[1:]
        return {
            "is_valid": True,
            "raw": raw,
            "normalized": normalized,
            "international": international,
            "operator": operator,
            "line_type": line_type,
            "line_type_label": {
                "MOBILE": "Ligne Mobile",
                "FIXED": "Ligne Fixe",
                "TOLL_FREE": "Numéro Vert (Gratuit)",
                "PREMIUM": "Numéro Surtaxé",
            }.get(line_type, line_type),
            "region": region,
            "technology": technology,
            "country": "Maroc (MA)",
            "country_code": "+212",
            "anrt_regulated": True,
        }
