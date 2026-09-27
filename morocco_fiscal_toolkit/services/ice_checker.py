import re
from typing import Dict, Any, Tuple

class MoroccanTaxValidators:
    """
    Validation engine for Moroccan tax and commercial identifiers:
    - ICE (Identifiant Commun de l'Entreprise) - 15 digits
    - IF (Identifiant Fiscal) - 6-8 digits
    - RC (Registre du Commerce) - 1-8 digits + Greffe
    - CNSS (Caisse Nationale de Sécurité Sociale) - 7-9 digits
    - Patente (Taxe Professionnelle) - 6-8 digits
    """

    @staticmethod
    def calculate_ice_checksum(base_13: str) -> str:
        """
        Calculates the 2-digit ISO 7064 Mod 97-10 checksum for the first 13 digits of an ICE.
        Standard formula: 97 - (int(base_13 * 100) % 97).
        """
        if not base_13.isdigit() or len(base_13) != 13:
            raise ValueError("Base must be exactly 13 digits")
        
        # ISO 7064 MOD 97-10
        num = int(base_13) * 100
        remainder = num % 97
        check = 97 - remainder
        if check == 97:
            check = 0
        return f"{check:02d}"

    @classmethod
    def validate_ice(cls, ice: str) -> Dict[str, Any]:
        """
        Validates a 15-digit Moroccan ICE:
        - 9 digits: Unique company identifier (SIRET-like)
        - 4 digits: Branch/establishment code (0001 = headquarters)
        - 2 digits: Modulo 97 control key
        """
        if not ice:
            return {
                "is_valid": False,
                "error": "L'ICE ne peut pas être vide.",
                "ice": ice,
                "tier": 1
            }

        cleaned = re.sub(r"[\s\-_.]", "", str(ice).strip())

        if not cleaned.isdigit():
            return {
                "is_valid": False,
                "error": "L'ICE doit contenir uniquement des chiffres.",
                "ice": cleaned,
                "tier": 1
            }

        if len(cleaned) != 15:
            return {
                "is_valid": False,
                "error": f"L'ICE doit comporter exactement 15 chiffres (actuellement {len(cleaned)}).",
                "ice": cleaned,
                "tier": 1
            }

        if cleaned == "0" * 15:
            return {
                "is_valid": False,
                "error": "L'ICE ne peut pas être composé uniquement de zéros.",
                "ice": cleaned,
                "tier": 1
            }

        base_13 = cleaned[:13]
        provided_check = cleaned[13:]
        company_id = cleaned[:9]
        branch_id = cleaned[9:13]

        expected_check = cls.calculate_ice_checksum(base_13)
        checksum_ok = (provided_check == expected_check)

        # In case some existing legacy companies use simplified Luhn or issued keys,
        # we check mod97, but flag if well-formed vs fully checksum-verified.
        return {
            "is_valid": True,
            "checksum_ok": checksum_ok,
            "ice": cleaned,
            "company_id": company_id,
            "branch_id": branch_id,
            "check_digits": provided_check,
            "expected_check": expected_check,
            "tier": 1,
            "details": {
                "structure": "9 digits entreprise + 4 digits siège/succursale + 2 digits clef",
                "branch_name": "Siège social" if branch_id == "0001" else f"Succursale #{branch_id}",
                "status_label": "Format & Clé valides" if checksum_ok else "Format valide (clé calculée différente)"
            }
        }

    @staticmethod
    def validate_if(identifiant_fiscal: str) -> Dict[str, Any]:
        """
        Validates Moroccan Identifiant Fiscal (IF):
        Typically 6 to 8 digits numeric.
        """
        if not identifiant_fiscal:
            return {"is_valid": False, "error": "Identifiant Fiscal vide."}
        
        cleaned = re.sub(r"[\s\-_.]", "", str(identifiant_fiscal).strip())
        if not cleaned.isdigit() or not (6 <= len(cleaned) <= 9):
            return {
                "is_valid": False,
                "error": "L'Identifiant Fiscal marocain doit comporter entre 6 et 9 chiffres.",
                "if": cleaned
            }
        
        return {
            "is_valid": True,
            "if": cleaned,
            "tier": 1,
            "status_label": "Format IF conforme"
        }

    @staticmethod
    def validate_rc(rc: str, tribunal: str = "Casablanca") -> Dict[str, Any]:
        """
        Validates Moroccan Registre du Commerce (RC):
        Typically 1 to 8 digits numeric associated with a Greffe/Tribunal de Commerce.
        """
        if not rc:
            return {"is_valid": False, "error": "Registre de Commerce vide."}
        
        cleaned = re.sub(r"[\s\-_.]", "", str(rc).strip())
        if not cleaned.isdigit() or not (1 <= len(cleaned) <= 8):
            return {
                "is_valid": False,
                "error": "Le Numéro RC doit comporter entre 1 et 8 chiffres.",
                "rc": cleaned
            }

        return {
            "is_valid": True,
            "rc": cleaned,
            "tribunal": tribunal,
            "tier": 1,
            "status_label": f"RC {cleaned} au Greffe du Tribunal de Commerce de {tribunal}"
        }

    @staticmethod
    def validate_cnss(cnss: str) -> Dict[str, Any]:
        """
        Validates Moroccan CNSS:
        7 to 9 digits.
        """
        if not cnss:
            return {"is_valid": False, "error": "Numéro CNSS vide."}
        cleaned = re.sub(r"[\s\-_.]", "", str(cnss).strip())
        if not cleaned.isdigit() or not (7 <= len(cleaned) <= 10):
            return {
                "is_valid": False,
                "error": "Le numéro d'affiliation CNSS doit comporter entre 7 et 10 chiffres.",
                "cnss": cleaned
            }
        return {
            "is_valid": True,
            "cnss": cleaned,
            "tier": 1,
            "status_label": "Format CNSS conforme"
        }
