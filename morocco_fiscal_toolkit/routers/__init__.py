from morocco_fiscal_toolkit.routers.ice import router as ice_router
from morocco_fiscal_toolkit.routers.banking import router as banking_router
from morocco_fiscal_toolkit.routers.tva import router as tva_router
from morocco_fiscal_toolkit.routers.salary import router as salary_router
from morocco_fiscal_toolkit.routers.dgi import router as dgi_router
from morocco_fiscal_toolkit.routers.loi_69_21 import router as loi_69_21_router
from morocco_fiscal_toolkit.routers.compliance import router as compliance_router
from morocco_fiscal_toolkit.routers.tax_regime import router as tax_regime_router
from morocco_fiscal_toolkit.routers.withholding_tax import router as withholding_tax_router
from morocco_fiscal_toolkit.routers.postal import router as postal_router
from morocco_fiscal_toolkit.routers.phone import router as phone_router
from morocco_fiscal_toolkit.routers.qr import router as qr_router
from morocco_fiscal_toolkit.routers.courier import router as courier_router
from morocco_fiscal_toolkit.routers.fiscal_calendar import router as fiscal_calendar_router

all_routers = [
    ice_router,
    banking_router,
    tva_router,
    salary_router,
    dgi_router,
    loi_69_21_router,
    compliance_router,
    tax_regime_router,
    withholding_tax_router,
    postal_router,
    phone_router,
    qr_router,
    courier_router,
    fiscal_calendar_router,
]
