"""
Morocco Fiscal Toolkit (Maroc Fiscal API) — Main FastAPI Application
====================================================================
Open-source API for Moroccan tax, DGI e-invoicing, VAT, banking, payroll,
and B2B fiscal compliance.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from morocco_fiscal_toolkit.routers import all_routers
from morocco_fiscal_toolkit import __version__

tags_metadata = [
    {
        "name": "🏢 Identifiants Entreprise (ICE, IF, RC, CNSS)",
        "description": "Validation structurelle Modulo-97, détection de succursales et requêtes OMPIC DirectInfo.",
    },
    {
        "name": "🏦 Banque & RIB/IBAN (GPBM / Bank Al-Maghrib)",
        "description": "Validation du RIB à 24 chiffres, identification des banques marocaines (GPBM) et conversion IBAN ISO 13616 (MA28).",
    },
    {
        "name": "🧾 TVA & Taxe sur la Valeur Ajoutée (CGI)",
        "description": "Recherche de taux (20%, 14%, 10%, 7%, 0%) par secteur et calculs bidirectionnels HT ↔ TTC.",
    },
    {
        "name": "💼 Paie & Salaire Brut / Net (CNSS, AMO, IR 2026)",
        "description": "Calculateur de paie conforme à la Loi de Finances 2026 : CNSS, AMO, CIMR, frais pro et barème IR progressif.",
    },
    {
        "name": "🏛️ Facturation Électronique DGI & Simpl-TVA",
        "description": "Calculateur de vagues Simpl-TVA (Phase 1/2/3), calendrier officiel et observatoire technique.",
    },
    {
        "name": "⚖️ Délais de Paiement & Loi 69-21 (Pénalités)",
        "description": "Audit du risque, calcul des pénalités de retard et génération d'état certifié pour la télédéclaration DGI.",
    },
    {
        "name": "🛡️ Conformité Facturation & Mentions Légales (Art. 145 CGI)",
        "description": "Audit des 10 mentions obligatoires et générateur de numérotation séquentielle continue.",
    },
    {
        "name": "💡 Simulateurs Fiscaux & Régimes (AE, CPU, SARL)",
        "description": "Comparateur d'imposition globale : Auto-Entrepreneur vs CPU vs Société (SARL/IS).",
    },
    {
        "name": "💸 Retenue à la Source (RAS)",
        "description": "Calculateur officiel des retenues à la source (honoraires, dividendes, royalties) selon le CGI.",
    },
    {
        "name": "🏙️ Géographie & Codes Postaux (Barid Al-Maghrib)",
        "description": "Annuaire officiel des codes postaux marocains : ville, province, région et arabe.",
    },
    {
        "name": "📱 Télécoms & Téléphonie (ANRT)",
        "description": "Identification des opérateurs (Maroc Telecom, Orange, Inwi) et classification des lignes.",
    },
    {
        "name": "📷 QR Codes Fiscaux & Paiement (Simpl-TVA & CMI Fatourati)",
        "description": "Décodeur et générateur de QR codes de visa DGI Simpl-TVA et de paiement Fatourati.",
    },
    {
        "name": "🚚 E-commerce & Bordereaux Courier (COD/CRBT)",
        "description": "Extraction et réconciliation des bordereaux de remise d'espèces (Amana, CTM, Cathedis, Speedy).",
    },
    {
        "name": "📅 Échéancier & Calendrier Fiscal Officiel",
        "description": "Calendrier complet des échéances fiscales marocaines (IS, TVA, IR, TP, CNSS).",
    },
]

app = FastAPI(
    title="Morocco Fiscal Toolkit (Maroc Fiscal API)",
    description="""
# 🇲🇦 Morocco Fiscal Toolkit — Open Source Fiscal, Banking & Tax API

Une suite complète de microservices et de calculateurs pour l'écosystème fiscal, bancaire et commercial marocain :

* **Conformité Fiscale** : ICE Modulo 97, IF, RC, CNSS, OMPIC DirectInfo, Audit Article 145 CGI.
* **Facturation Électronique** : Simulateur de vagues DGI Simpl-TVA, QR Code Wasl, Numérotation continue.
* **Fintech & Banque** : RIB 24 chiffres Modulo 97 GPBM, conversion IBAN MA28, SWIFT BIC.
* **TVA & Impôts** : Catalogue des taux CGI 2026, Retenue à la Source (RAS), Simulateur de régimes fiscaux.
* **Loi 69-21** : Calculateur des pénalités de retard interentreprises et générateur d'état détaillé.
* **Paie & RH** : Salaire Brut ↔ Net, barème progressif IR 2026, cotisations CNSS et AMO.
* **Services Utilitaires** : Codes postaux (Barid Al-Maghrib), Validation téléphonique (ANRT), Réconciliation Courier COD.

---
**Open Source — Licence MIT**  
GitHub : [https://github.com/n4ouri/morocco-fiscal-toolkit](https://github.com/n4ouri/morocco-fiscal-toolkit)
""",
    version=__version__,
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Open CORS for all clients (Web apps, ERPs, SaaS, Mobile)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all routers
for router in all_routers:
    app.include_router(router)


@app.get("/", summary="ℹ️ Informations et statut de l'API")
def root_info():
    return {
        "name": "Morocco Fiscal Toolkit API",
        "alias": "Maroc Fiscal API",
        "version": __version__,
        "documentation": "/docs",
        "redoc": "/redoc",
        "openapi_schema": "/openapi.json",
        "license": "MIT",
        "repository": "https://github.com/n4ouri/morocco-fiscal-toolkit",
        "endpoints_count": 28,
        "status": "online"
    }


@app.get("/health", summary="🩺 Bilan de santé du serveur")
def health_check():
    return {"status": "healthy", "version": __version__}


def start():
    """Entrypoint for uvicorn execution."""
    import uvicorn
    uvicorn.run("morocco_fiscal_toolkit.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    start()
