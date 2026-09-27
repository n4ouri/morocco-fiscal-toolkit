import unicodedata
from typing import Dict, Any, List

class MoroccanTvaCatalog:
    """
    Searchable Catalog & Calculator for Moroccan Value-Added Tax (TVA) Rates.
    Reflects the unified reform trajectory under the Code Général des Impôts (CGI 2026).
    """

    CATEGORIES = [
        {
            "id": "services-info",
            "name": "Services Informatiques, Conseil & Ingénierie",
            "rate": 0.20,
            "rate_label": "20% (Taux Normal)",
            "cgi_article": "Article 98-1° du CGI",
            "deductible": True,
            "keywords": ["logiciel", "saas", "developpement", "informatique", "conseil", "consulting", "marketing", "publicite", "design", "maintenance", "audit", "comptabilite", "juridique"],
            "description": "Prestations de services immatérielles, honoraires professionnels et travaux informatiques.",
            "caveats": "Droit à déduction total de la TVA supportée sur les intrants d'exploitation."
        },
        {
            "id": "commerce-industrie",
            "name": "Biens d'Équipement, Matériel & Industrie",
            "rate": 0.20,
            "rate_label": "20% (Taux Normal)",
            "cgi_article": "Article 98-1° du CGI",
            "deductible": True,
            "keywords": ["materiel", "machines", "equipement", "outillage", "vehicules utilitaires", "electronique", "mobilier", "quincaillerie"],
            "description": "Ventes de biens mobiliers d'investissement et équipements d'entreprise.",
            "caveats": "Les biens d'investissement ouvrent droit à déduction sur 5 ans (règle de régularisation des 5 ans - Art. 102 CGI)."
        },
        {
            "id": "transport-marchandises",
            "name": "Transport de Voyageurs et de Marchandises",
            "rate": 0.14,
            "rate_label": "14% (Taux Intermédiaire)",
            "cgi_article": "Article 98-2° du CGI",
            "deductible": True,
            "keywords": ["transport", "fret", "messagerie", "livraison", "logistique", "camionnage", "autocar", "taxi", "ctm"],
            "description": "Opérations de transport routier, ferroviaire ou maritime intérieur.",
            "caveats": "Le transport international de marchandises et voyageurs à destination de l'étranger est exonéré avec droit à déduction (Art. 92-I-22°)."
        },
        {
            "id": "electricite-energie",
            "name": "Énergie Électrique & Énergies Renouvelables",
            "rate": 0.14,
            "rate_label": "14% (Taux Intermédiaire)",
            "cgi_article": "Article 98-2° du CGI",
            "deductible": True,
            "keywords": ["electricite", "energie", "solaire", "panneaux photovoltaiques", "onee", "compteur"],
            "description": "Fourniture d'énergie électrique moyenne et haute tension, matériel de captage solaire.",
            "caveats": "La basse tension à usage domestique fait l'objet de tranches spécifiques selon la Loi de Finances."
        },
        {
            "id": "hotellerie-restauration",
            "name": "Hôtellerie, Hébergement & Restauration",
            "rate": 0.10,
            "rate_label": "10% (Taux Réduit)",
            "cgi_article": "Article 99-1° du CGI",
            "deductible": True,
            "keywords": ["hotel", "hebergement", "chambre", "riad", "restaurant", "traiteur", "repas", "tourisme", "cafe"],
            "description": "Prestations d'hébergement touristique classé et restauration fournie sur place.",
            "caveats": "La taxe de séjour et les boissons alcoolisées sont assujetties à des règles d'imposition distinctes."
        },
        {
            "id": "banques-finances",
            "name": "Banques, Crédit & Opérations Financières",
            "rate": 0.10,
            "rate_label": "10% (Taux Réduit)",
            "cgi_article": "Article 99-1° du CGI",
            "deductible": True,
            "keywords": ["banque", "interet", "agios", "commission bancaire", "credit", "emprunt", "frais de tenue de compte", "virement"],
            "description": "Commissions et agios bancaires, opérations d'intermédiation financière.",
            "caveats": "Les intérêts de prêts pour acquisition de logements sociaux bénéficient de régimes préférentiels."
        },
        {
            "id": "alimentation-base-10",
            "name": "Huiles Fluides Alimentaires & Pâtes Alimentaires",
            "rate": 0.10,
            "rate_label": "10% (Taux Réduit)",
            "cgi_article": "Article 99-1° du CGI",
            "deductible": True,
            "keywords": ["huile", "pates", "couscous transforme", "sel de cuisine", "riz", "farine speciale"],
            "description": "Produits agroalimentaires de grande consommation préparés industriellement.",
            "caveats": "Les graines oléagineuses brutes sont exonérées en amont."
        },
        {
            "id": "eau-potable",
            "name": "Distribution d'Eau Potable & Assainissement",
            "rate": 0.07,
            "rate_label": "7% (Taux Super-Réduit)",
            "cgi_article": "Article 98-3° du CGI",
            "deductible": True,
            "keywords": ["eau", "eau potable", "radeec", "lydec", "redal", "amendis", "compteur eau", "assainissement"],
            "description": "Opérations de distribution d'eau potable fournies par les régies et concessionnaires.",
            "caveats": "Les travaux de branchement social sont éligibles au taux réduit."
        },
        {
            "id": "fournitures-scolaires",
            "name": "Fournitures Scolaires & Manuels",
            "rate": 0.07,
            "rate_label": "7% (Taux Super-Réduit)",
            "cgi_article": "Article 98-3° du CGI",
            "deductible": True,
            "keywords": ["cahier", "stylo", "fournitures scolaires", "manuel scolaire", "cartable", "classeur", "papeterie scolaire"],
            "description": "Articles et fournitures destinés exclusivement à l'enseignement et aux élèves.",
            "caveats": "La papeterie générale de bureau reste soumise au taux normal de 20%."
        },
        {
            "id": "pharmacie-base",
            "name": "Médicaments & Produits Pharmaceutiques de Base",
            "rate": 0.07,
            "rate_label": "7% (Taux Super-Réduit)",
            "cgi_article": "Article 98-3° du CGI",
            "deductible": True,
            "keywords": ["medicament", "pharmacie", "vaccin", "insuline", "sirop", "comprime", "pansement"],
            "description": "Médicaments essentiels inscrits sur la liste du Ministère de la Santé.",
            "caveats": "Certains médicaments contre les maladies chroniques ou coûteux sont exonérés à 0% sans droit à déduction."
        },
        {
            "id": "exportations",
            "name": "Exportations de Produits et Services",
            "rate": 0.00,
            "rate_label": "0% (Exonéré AVEC droit à déduction)",
            "cgi_article": "Article 92-I-1° du CGI",
            "deductible": True,
            "keywords": ["export", "etranger", "client etranger", "devises", "prestation a l etranger", "vente internationale", "portnet"],
            "description": "Ventes de biens expédiés hors du territoire marocain ou prestations exploitées à l'étranger.",
            "caveats": "Droit complet à remboursement de la TVA (crédit de TVA / procédure de remboursement accéléré DGI sous 30 jours)."
        },
        {
            "id": "agriculture-engrais",
            "name": "Engrais, Produits Phytosanitaires & Matériel Agricole",
            "rate": 0.00,
            "rate_label": "0% (Exonéré AVEC droit à déduction)",
            "cgi_article": "Article 92-I-4° du CGI",
            "deductible": True,
            "keywords": ["agriculture", "engrais", "tracteur", "phytosanitaire", "semences", "irrigation", "goutte a goutte"],
            "description": "Intrants agricoles et équipements d'irrigation favorisant la production rurale.",
            "caveats": "Nécessite la conservation des attestations d'exonération de la DGI."
        },
        {
            "id": "sante-medecins",
            "name": "Actes Médicaux & Soins de Santé",
            "rate": 0.00,
            "rate_label": "Exonéré SANS droit à déduction",
            "cgi_article": "Article 91-I-1° du CGI",
            "deductible": False,
            "keywords": ["medecin", "docteur", "chirurgien", "dentiste", "clinique", "hopital", "consultation medicale", "laboratoire d analyse"],
            "description": "Prestations de soins médicaux et d'hospitalisation fournies par les professionnels de santé.",
            "caveats": "Pas de récupération de la TVA supportée sur les achats de matériel médical (la TVA constitue un coût définitif)."
        },
        {
            "id": "enseignement-prive",
            "name": "Établissements d'Enseignement Privé & Formation",
            "rate": 0.00,
            "rate_label": "Exonéré SANS droit à déduction",
            "cgi_article": "Article 91-I-6° du CGI",
            "deductible": False,
            "keywords": ["ecole", "universite", "scolarite", "creche", "lycee", "maternelle", "formation initiale"],
            "description": "Enseignement préscolaire, primaire, secondaire, supérieur et formation professionnelle autorisée.",
            "caveats": "La formation continue pour le compte des entreprises relève en revanche du taux de 20%."
        },
        {
            "id": "denrees-vitales",
            "name": "Pain, Lait Frais, Viande Fraîche & Couscous Artisanal",
            "rate": 0.00,
            "rate_label": "Exonéré SANS droit à déduction",
            "cgi_article": "Article 91-I-2° du CGI",
            "deductible": False,
            "keywords": ["pain", "lait", "lait frais", "viande", "boucherie", "poisson frais", "cereales non transformees"],
            "description": "Produits alimentaires de première nécessité non préparés industriellement.",
            "caveats": "Régime protecteur du pouvoir d'achat des ménages sans droit à déduction de TVA."
        }
    ]

    @classmethod
    def _normalize(cls, text: str) -> str:
        s = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")
        return s.lower()

    @classmethod
    def search(cls, query: str = "") -> List[Dict[str, Any]]:
        """Searches categories by text, keyword, or article."""
        q = cls._normalize(query.strip())
        if not q:
            return cls.CATEGORIES

        results = []
        for cat in cls.CATEGORIES:
            name_norm = cls._normalize(cat["name"])
            desc_norm = cls._normalize(cat["description"])
            art_norm = cls._normalize(cat["cgi_article"])
            kw_match = any(q in cls._normalize(kw) for kw in cat["keywords"])

            if q in name_norm or q in desc_norm or q in art_norm or kw_match:
                results.append(cat)

        return results

    @classmethod
    def calculate_simulation(cls, amount: float, rate: float, is_ttc: bool = False) -> Dict[str, Any]:
        """Calculates HT, TVA and TTC given an amount and rate."""
        amt = max(0.0, float(amount))
        r = float(rate)

        if is_ttc:
            ttc = amt
            ht = round(ttc / (1.0 + r), 2)
            tva = round(ttc - ht, 2)
        else:
            ht = amt
            tva = round(ht * r, 2)
            ttc = round(ht + tva, 2)

        return {
            "amount_input": amt,
            "input_mode": "TTC" if is_ttc else "HT",
            "rate_applied": r,
            "rate_percentage": f"{int(r * 100)}%",
            "amount_ht": ht,
            "amount_tva": tva,
            "amount_ttc": ttc
        }
