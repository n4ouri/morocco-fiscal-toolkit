"""
Morocco Fiscal Toolkit CLI
==========================
Command-line utility for Moroccan tax validation, banking, and e-invoicing checks.

Usage:
  morocco-fiscal-toolkit check-ice <ICE>
  morocco-fiscal-toolkit validate-rib <RIB>
  morocco-fiscal-toolkit rib-to-iban <RIB>
  morocco-fiscal-toolkit calculate-salary <GROSS_MAD>
  morocco-fiscal-toolkit search-tva <QUERY>
  morocco-fiscal-toolkit postal-lookup <POSTAL_CODE>
  morocco-fiscal-toolkit phone-parse <PHONE>
  morocco-fiscal-toolkit serve [--port 8000]
"""

import argparse
import json
import sys

from morocco_fiscal_toolkit import (
    validate_ice,
    validate_if,
    validate_rc,
    validate_cnss,
    validate_rib,
    calculate_moroccan_iban,
    search_tva,
    calculate_tva,
    calculate_salary_net,
    calculate_salary_gross,
    calculate_dgi_wave,
    calculate_loi_69_21_penalty,
    lookup_postal_code,
    parse_phone_number,
    decode_qr,
    get_fiscal_calendar,
    __version__,
)


def _print_json(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(
        prog="morocco-fiscal-toolkit",
        description="🇲🇦 Morocco Fiscal Toolkit — CLI for Moroccan Tax, Banking & Invoicing Compliance"
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # check-ice
    p_ice = subparsers.add_parser("check-ice", help="Validate a 15-digit Moroccan ICE and Mod-97 key")
    p_ice.add_argument("ice", help="15-digit ICE")

    # validate-rib
    p_rib = subparsers.add_parser("validate-rib", help="Validate a 24-digit Moroccan RIB and identify bank")
    p_rib.add_argument("rib", help="24-digit RIB or MA IBAN")

    # rib-to-iban
    p_iban = subparsers.add_parser("rib-to-iban", help="Convert 24-digit RIB to Moroccan IBAN (MA28)")
    p_iban.add_argument("rib", help="24-digit RIB")

    # calculate-salary
    p_sal = subparsers.add_parser("calculate-salary", help="Calculate Net from Gross monthly salary (MAD)")
    p_sal.add_argument("gross", type=float, help="Gross monthly salary in MAD")
    p_sal.add_argument("--dependents", type=int, default=0, help="Number of dependents (0-6)")
    p_sal.add_argument("--cimr", type=float, default=None, help="CIMR rate (e.g. 0.03 for 3%)")

    # search-tva
    p_tva = subparsers.add_parser("search-tva", help="Search Moroccan TVA rates by product/sector")
    p_tva.add_argument("query", help="Keyword or product name")

    # postal-lookup
    p_post = subparsers.add_parser("postal-lookup", help="Lookup city and region from 5-digit Moroccan postal code")
    p_post.add_argument("zip", help="5-digit postal code (e.g. 20000)")

    # phone-parse
    p_phone = subparsers.add_parser("phone-parse", help="Parse Moroccan phone number and detect operator")
    p_phone.add_argument("phone", help="Phone number (e.g. 0661234567 or +212661234567)")

    # loi-69-21
    p_l69 = subparsers.add_parser("loi-69-21-penalty", help="Calculate Loi 69-21 late payment penalty")
    p_l69.add_argument("amount_ttc", type=float, help="Invoice TTC amount in MAD")
    p_l69.add_argument("days_overdue", type=int, help="Days overdue beyond legal term")

    # serve
    p_serve = subparsers.add_parser("serve", help="Start the FastAPI REST API server")
    p_serve.add_argument("--host", default="0.0.0.0", help="Host to bind (default: 0.0.0.0)")
    p_serve.add_argument("--port", type=int, default=8000, help="Port to listen on (default: 8000)")
    p_serve.add_argument("--reload", action="store_true", help="Enable auto-reload for development")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "check-ice":
        _print_json(validate_ice(args.ice))
    elif args.command == "validate-rib":
        _print_json(validate_rib(args.rib))
    elif args.command == "rib-to-iban":
        res = validate_rib(args.rib)
        if res.get("is_valid"):
            print(res.get("iban"))
        else:
            _print_json(res)
    elif args.command == "calculate-salary":
        _print_json(calculate_salary_net(gross_monthly=args.gross, cimr_rate=args.cimr, dependents=args.dependents))
    elif args.command == "search-tva":
        _print_json(search_tva(args.query))
    elif args.command == "postal-lookup":
        _print_json(lookup_postal_code(args.zip))
    elif args.command == "phone-parse":
        _print_json(parse_phone_number(args.phone))
    elif args.command == "loi-69-21-penalty":
        _print_json(calculate_loi_69_21_penalty(args.amount_ttc, args.days_overdue))
    elif args.command == "serve":
        import uvicorn
        print(f"🚀 Starting Morocco Fiscal Toolkit API on http://{args.host}:{args.port} (docs at /docs)...")
        uvicorn.run("morocco_fiscal_toolkit.main:app", host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()
