import pytest
from morocco_fiscal_toolkit import (
    decode_qr,
    generate_simpl_tva_qr,
    generate_fatourati_qr,
    WaslQrDecoder,
    InvoiceQrService,
)

def test_simpl_tva_qr_roundtrip():
    payload = generate_simpl_tva_qr(
        seller_name="Maroc Telecom SA",
        seller_ice="001526374000195",
        issue_datetime="2026-09-27T12:00:00Z",
        total_ttc=12000.0,
        total_tva=2000.0,
        clearance_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        clearance_ref="IRN-2026-001"
    )
    res = decode_qr(payload)
    assert res["is_valid"] is True
    assert res["format"] == "SIMPL_TVA_CLEARANCE"
    assert res["total_ttc_mad"] == 12000.0
    assert res["issuer_ice"] == "001526374000195"

def test_fatourati_qr_roundtrip():
    payload = generate_fatourati_qr(
        merchant_ice="001526374000195",
        invoice_id="FAC-2026-0099",
        amount=5400.50
    )
    res = decode_qr(payload)
    assert res["is_valid"] is True
    assert res["format"] == "FATOURATI_CMI_PAYMENT"
    assert res["issuer_ice"] == "001526374000195"
    assert res["total_ttc_mad"] == 5400.50
