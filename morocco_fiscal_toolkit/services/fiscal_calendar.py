from datetime import date, datetime
from typing import Dict, Any, List, Optional

class MoroccanFiscalCalendar:
    """
    Complete Moroccan fiscal deadlines calendar for a given year.

    Inspired by UAE FTA's free tax compliance calendar and India's GST due-date tracker —
    both massively popular tools embedded in accounting software and startup dashboards.

    Covers:
    - Impôt sur les Sociétés (IS): acomptes provisionnels + solde
    - TVA: mensuelles / trimestrielles
    - IR Employés (Retenue à la Source)
    - Taxe Professionnelle (TP / Patente)
    - CNSS declarations
    - Loi 69-21 (déclaration annuelle / trimestrielle)
    - Liasse fiscale (bilan + CPC)
    """

    @classmethod
    def get_calendar(cls, year: int = 2026, regime: str = "SARL", tva_regime: str = "MENSUEL") -> Dict[str, Any]:
        """
        Returns all fiscal deadlines for the given year.
        :param year: Fiscal year (e.g. 2026)
        :param regime: SARL, SA, AUTO_ENTREPRENEUR, CPU, PERSONNE_PHYSIQUE
        :param tva_regime: MENSUEL, TRIMESTRIEL, EXONERE
        """
        deadlines: List[Dict[str, Any]] = []

        def add(month: int, day: int, label: str, category: str, urgency: str, note: str = "", article: str = ""):
            try:
                d = date(year, month, day)
            except ValueError:
                d = date(year, month, 28)
            deadlines.append({
                "date": d.isoformat(),
                "date_label": d.strftime("%d %B %Y"),
                "label": label,
                "category": category,
                "urgency": urgency,
                "note": note,
                "article": article,
                "is_past": d < date.today(),
                "days_remaining": max(0, (d - date.today()).days),
            })

        # ─── IS — Impôt sur les Sociétés (4 acomptes de 25% de l'IS N-1) ────
        if regime in ("SARL", "SA"):
            for (m, d_day, n) in [(3, 31, "1er"), (6, 30, "2ème"), (9, 30, "3ème"), (12, 31, "4ème")]:
                add(m, d_day, f"IS — {n} Acompte provisionnel 25%",
                    "IS", "HIGH",
                    "25% de l'IS de l'exercice précédent (déclaration DAE ou formulaire DGI)",
                    "Art. 170 CGI")
            add(3, 31, f"IS — Solde et Liasse Fiscale (exercice {year - 1})",
                "IS", "CRITICAL",
                f"Dépôt de la déclaration de résultat (Bilan + CPC + Liasse) au titre de l'exercice {year - 1}.",
                "Art. 150 CGI")

        # ─── TVA ─────────────────────────────────────────────────────────────
        if tva_regime == "MENSUEL":
            for m in range(1, 13):
                add(m, 20, f"TVA mensuelle (opérations de {date(year, m, 1).strftime('%B %Y')})",
                    "TVA", "HIGH",
                    "Télédéclaration et télépaiement TVA sur portail Simpl-TVA ou Damancom.",
                    "Art. 110 CGI")
        elif tva_regime == "TRIMESTRIEL":
            for (m, d_day, label) in [(4, 20, "T1 (Jan-Mar)"), (7, 20, "T2 (Avr-Jun)"),
                                       (10, 20, "T3 (Jui-Sep)"), (1, 20, "T4 (Oct-Déc) de l'année suivante")]:
                ym = year if m != 1 else year + 1
                try:
                    add(m, d_day, f"TVA trimestrielle — {label}", "TVA", "HIGH",
                        "Télédéclaration trimestrielle sur Damancom / DGI.", "Art. 110 CGI")
                except Exception:
                    pass

        # ─── IR Employés (mensuel — Retenue à la Source) ─────────────────────
        if regime in ("SARL", "SA", "PERSONNE_PHYSIQUE"):
            for m in range(1, 13):
                add(m, 20, f"IR Salariés — Retenue à la source (Mois {m:02d})",
                    "IR_SALARIES", "MEDIUM",
                    "Déclaration et versement de l'IR retenu sur les salaires du mois précédent.",
                    "Art. 174 CGI")

        # ─── Taxe Professionnelle (Patente) ───────────────────────────────────
        add(1, 31, "Déclaration d'existence / Taxe Professionnelle (TP)",
            "TAXE_PROFESSIONNELLE", "MEDIUM",
            "Déclaration annuelle des locaux et activités professionnelles.",
            "Art. 197 CGI")
        add(2, 28, f"Paiement Taxe Professionnelle — Exercice {year}",
            "TAXE_PROFESSIONNELLE", "HIGH",
            "Règlement de la Taxe Professionnelle auprès de la DGI / CRI.",
            "Art. 197 CGI")

        # ─── CNSS / AMO ───────────────────────────────────────────────────────
        for m in range(1, 13):
            add(m, 10, f"CNSS — Déclaration mensuelle (Mois {m:02d})",
                "CNSS", "HIGH",
                "Bordereau de déclaration et paiement des cotisations CNSS + AMO employeur/salarié.",
                "CNSS Circulaire 2025")

        # ─── Loi 69-21 ────────────────────────────────────────────────────────
        add(3, 31, f"Loi 69-21 — Déclaration annuelle délais de paiement (exercice {year - 1})",
            "LOI_69_21", "CRITICAL",
            f"Dépôt de l'état certifié des factures en retard pour l'exercice {year - 1} (Expert-Comptable ou CAC).",
            "Loi 69-21 art. 12")

        for (m, d_day, q) in [(1, 31, "T4"), (4, 30, "T1"), (7, 31, "T2"), (10, 31, "T3")]:
            add(m, d_day, f"Loi 69-21 — Déclaration trimestrielle {q} (CA > 50M MAD)",
                "LOI_69_21", "HIGH",
                "Entreprises réalisant un CA > 50M MAD : déclaration trimestrielle obligatoire.",
                "Loi 69-21 art. 12 al.2")

        # ─── Simpl-TVA (DGI e-invoicing) ─────────────────────────────────────
        add(1, 1, f"Simpl-TVA — Entrée en vigueur Phase 2 (CA > 20M MAD)",
            "SIMPL_TVA", "CRITICAL",
            "Les entreprises avec CA > 20M MAD doivent émettre toutes leurs factures via Simpl-TVA.",
            "Art. 145 CGI — Loi de Finances 2026")

        # Sort by date
        deadlines.sort(key=lambda x: x["date"])

        return {
            "year": year,
            "regime": regime,
            "tva_regime": tva_regime,
            "generated_for": date.today().isoformat(),
            "total_deadlines": len(deadlines),
            "deadlines": deadlines,
            "key_alerts": [
                {"label": "Liasse Fiscale IS", "date": f"31/03/{year}", "article": "Art. 150 CGI"},
                {"label": "Loi 69-21 (annuelle)", "date": f"31/03/{year}", "article": "Loi 69-21"},
                {"label": "TVA mensuelle", "date": "20 de chaque mois", "article": "Art. 110 CGI"},
                {"label": "CNSS mensuelle", "date": "10 de chaque mois", "article": "CNSS Circ. 2025"},
            ]
        }
