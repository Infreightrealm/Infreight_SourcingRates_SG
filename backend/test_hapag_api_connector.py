# -*- coding: utf-8 -*-
"""
Standalone Test & Verification Suite for Hapag-Lloyd Prices REST API Connector.

Tests:
1. UN/LOCODE resolution
2. OpenAPI OfferRequest payload generation
3. OfferResponse parsing & charge normalization (BOF, EMA, MFR, Surcharges)
4. Free Time resolution (e.g. DEHAM -> 4 days)
5. Multi-container compatibility matching Frontend Table & Excel Export
"""
import sys
import os
import json
import asyncio
from datetime import datetime, timezone, timedelta

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from models.schemas import RateSearchRequest, CarrierResultStatus, QuoteSchema
from carriers.hapag_lloyd_api_connector import (
    HapagLloydAPIConnector,
    CONTAINER_TO_ISO,
    ISO_TO_CONTAINER
)
from carriers.registry import get_connector


# Sample realistic OfferResponse JSON from OpenAPI v2.1.4 specification
SAMPLE_HAPAG_OFFER_RESPONSE = {
    "carrierPriceRequestReference": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "offers": [
        {
            "productIdentifier": "QUICK_QUOTES",
            "placeOfReceipt": "SGSIN",
            "placeOfReceiptDate": "2026-09-11T00:00:00.000Z",
            "placeOfDelivery": "DEHAM",
            "placeOfDeliveryDateTime": "2026-10-19T00:00:00.000Z",
            "portOfLoading": "SGSIN",
            "portOfLoadingDateTime": "2026-09-11T00:00:00.000Z",
            "portOfDischarge": "DEHAM",
            "portOfDischargeDateTime": "2026-10-19T00:00:00.000Z",
            "transitTime": 38,
            "offerValidTo": "2026-09-30T23:59:59.000Z",
            "potentialQuotationValidTo": "2026-09-30",
            "legs": [
                {
                    "modeOfTransport": "VESSEL",
                    "departureLocation": "SGSIN",
                    "departureDateTime": "2026-09-11T12:00:00.000Z",
                    "arrivalLocation": "MYTPP",
                    "arrivalDateTime": "2026-09-12T18:00:00.000Z",
                    "vesselName": "Hapag Vessel",
                    "scheduleVoyageNumber": "",
                    "carrierServiceName": "FE4"
                },
                {
                    "modeOfTransport": "VESSEL",
                    "departureLocation": "MYTPP",
                    "departureDateTime": "2026-09-14T08:00:00.000Z",
                    "arrivalLocation": "DEHAM",
                    "arrivalDateTime": "2026-10-19T14:00:00.000Z",
                    "vesselName": "Hapag Vessel",
                    "scheduleVoyageNumber": "2638W",
                    "carrierServiceName": "FE4"
                }
            ],
            "equipments": [
                {
                    "requestedEquipment": {
                        "requestedEquipmentSizeType": "45GP",
                        "requestedEquipmentUnits": 1,
                        "isNonOperatingReefer": False,
                        "shippersOwnedContainer": False
                    },
                    "rates": [
                        {
                            "chargeTypeCode": "BAS",
                            "chargeTypeShortDescription": "Basic Ocean Freight",
                            "amount": 2622.00,
                            "currency": "USD",
                            "seaFreightIndicator": True,
                            "included": True,
                            "chargeTypeClass": 1
                        },
                        {
                            "chargeTypeCode": "EMA",
                            "chargeTypeShortDescription": "Emission Allowance",
                            "amount": 176.00,
                            "currency": "USD",
                            "seaFreightIndicator": False,
                            "included": False,
                            "locationProposal": "MAIN_CARRIAGE",
                            "chargeTypeClass": 2
                        },
                        {
                            "chargeTypeCode": "MFR",
                            "chargeTypeShortDescription": "Marine Fuel Recovery",
                            "amount": 1178.00,
                            "currency": "USD",
                            "seaFreightIndicator": False,
                            "included": False,
                            "locationProposal": "MAIN_CARRIAGE",
                            "chargeTypeClass": 2
                        },
                        {
                            "chargeTypeCode": "THD",
                            "chargeTypeShortDescription": "Terminal Handling Charge Destination",
                            "amount": 285.00,
                            "currency": "EUR",
                            "seaFreightIndicator": False,
                            "included": False,
                            "chargeTypeClass": 3
                        }
                    ]
                }
            ]
        },
        {
            "productIdentifier": "QUICK_QUOTES_SPOT",
            "placeOfReceipt": "SGSIN",
            "placeOfReceiptDate": "2026-09-11T00:00:00.000Z",
            "placeOfDelivery": "DEHAM",
            "placeOfDeliveryDateTime": "2026-10-19T00:00:00.000Z",
            "transitTime": 38,
            "offerValidTo": "2026-09-30T23:59:59.000Z",
            "potentialQuotationValidTo": "2026-09-30",
            "legs": [
                {
                    "modeOfTransport": "VESSEL",
                    "departureLocation": "SGSIN",
                    "departureDateTime": "2026-09-11T12:00:00.000Z",
                    "arrivalLocation": "MYTPP",
                    "arrivalDateTime": "2026-09-12T18:00:00.000Z",
                    "vesselName": "Hapag Vessel",
                    "scheduleVoyageNumber": "",
                    "carrierServiceName": "FE4"
                },
                {
                    "modeOfTransport": "VESSEL",
                    "departureLocation": "MYTPP",
                    "departureDateTime": "2026-09-14T08:00:00.000Z",
                    "arrivalLocation": "DEHAM",
                    "arrivalDateTime": "2026-10-19T14:00:00.000Z",
                    "vesselName": "Hapag Vessel",
                    "scheduleVoyageNumber": "2638W",
                    "carrierServiceName": "FE4"
                }
            ],
            "equipments": [
                {
                    "requestedEquipment": {
                        "requestedEquipmentSizeType": "45GP",
                        "requestedEquipmentUnits": 1,
                        "isNonOperatingReefer": False,
                        "shippersOwnedContainer": False
                    },
                    "rates": [
                        {
                            "chargeTypeCode": "BAS",
                            "chargeTypeShortDescription": "Basic Ocean Freight",
                            "amount": 2622.00,
                            "currency": "USD",
                            "seaFreightIndicator": True,
                            "included": True,
                            "chargeTypeClass": 1
                        },
                        {
                            "chargeTypeCode": "EMA",
                            "chargeTypeShortDescription": "Emission Allowance",
                            "amount": 176.00,
                            "currency": "USD",
                            "seaFreightIndicator": False,
                            "included": False,
                            "locationProposal": "MAIN_CARRIAGE",
                            "chargeTypeClass": 2
                        },
                        {
                            "chargeTypeCode": "MFR",
                            "chargeTypeShortDescription": "Marine Fuel Recovery",
                            "amount": 1178.00,
                            "currency": "USD",
                            "seaFreightIndicator": False,
                            "included": False,
                            "locationProposal": "MAIN_CARRIAGE",
                            "chargeTypeClass": 2
                        }
                    ]
                }
            ]
        }
    ]
}


async def test_locode_resolution():
    print("\n--- TEST 1: UN/LOCODE Resolution ---")
    connector = HapagLloydAPIConnector()
    test_cases = [
        ("Singapore", "SGSIN"),
        ("Singapore, Singapore [SGSIN]", "SGSIN"),
        ("Hamburg, Germany [DEHAM]", "DEHAM"),
        ("DEHAM", "DEHAM"),
        ("Shanghai, China", "CNSHA"),
        ("Port Klang", "MYPKG"),
    ]
    all_passed = True
    for input_str, expected in test_cases:
        res = connector.resolve_locode(input_str)
        matched = (res == expected) or (res in ("MYPKG", "MYLPK") and expected == "MYPKG")
        print(f"  Input: '{input_str}' -> Resolved: '{res}' (Expected: '{expected}') => {'[PASS]' if matched else '[FAIL]'}")
        if not matched:
            all_passed = False
    assert all_passed, "LOCODE resolution test failed"
    print("  [OK] UN/LOCODE resolution passed.")


async def test_payload_generation():
    print("\n--- TEST 2: OpenAPI OfferRequest Payload Generation ---")
    connector = HapagLloydAPIConnector()
    payload = connector.build_offer_request_payload(
        origin_locode="SGSIN",
        destination_locode="DEHAM",
        container_iso="45GP",
        quantity=1,
        weight_kg=20000.0,
        earliest_departure_date="2026-09-11",
        commodity_group="FAK"
    )
    print("  Generated Payload:")
    print(json.dumps(payload, indent=4))

    assert payload["placeOfReceipt"]["locode"] == "SGSIN"
    assert payload["placeOfDelivery"]["locode"] == "DEHAM"
    assert payload["requestedEquipment"]["requestedEquipmentSizeType"] == "45GP"
    assert payload["commodity"]["cargoGrossWeight"] == 20000
    assert "QUICK_QUOTES" in payload["productIdentifiers"]
    assert "QUICK_QUOTES_SPOT" in payload["productIdentifiers"]
    print("  [OK] Payload structure is valid.")


async def test_response_parsing_and_normalization():
    print("\n--- TEST 3: Response Parsing & Charge Normalization ---")
    connector = HapagLloydAPIConnector()
    quotes = connector._parse_offer_response_to_quotes(
        api_data=SAMPLE_HAPAG_OFFER_RESPONSE,
        requested_container_type="DRY 40H",
        destination_locode="DEHAM",
        destination_name="Hamburg, Germany"
    )

    print(f"  Parsed {len(quotes)} quotes from OfferResponse:")
    for idx, q in enumerate(quotes):
        print(f"\n  Quote #{idx+1}:")
        print(f"    Product / Service: {q.service_name}")
        print(f"    Vessel:            {q.vessel}")
        print(f"    Container:         {q.container_type}")
        print(f"    ETD -> ETA:        {q.etd} -> {q.eta} ({q.transit_time_days} days)")
        print(f"    Validity:          {q.validity_till}")
        print(f"    Free Time:         {q.free_time}")
        print(f"    Basic Ocean Freight: ${q.basic_ocean_freight:.2f}")
        print(f"    Surcharges:        ${sum(c.amount for c in q.included_freight_surcharges):.2f}")
        for s in q.included_freight_surcharges:
            print(f"      - {s.name}: ${s.amount:.2f} {s.currency}")
        print(f"    Final Freight Value: ${q.final_freight_value:.2f} {q.currency}")

    assert len(quotes) == 2, f"Expected 2 quotes, got {len(quotes)}"
    
    # Check QQ quote
    qq_quote = quotes[0]
    assert qq_quote.container_type == "DRY 40H"
    assert qq_quote.basic_ocean_freight == 2622.00
    assert qq_quote.currency == "USD"
    assert qq_quote.final_freight_value == 3976.00  # 2622 + 176 (EMA) + 1178 (MFR)
    assert qq_quote.free_time == "4 days"
    assert "Tanjung Pelepas" in qq_quote.service_name or qq_quote.routing == "Tanjung Pelepas" or "MYTPP" in str(qq_quote.service_name)
    
    # Check Spot quote
    spot_quote = quotes[1]
    assert "(SPOT)" in spot_quote.vessel
    assert spot_quote.currency == "USD"
    assert spot_quote.final_freight_value == 3976.00

    print("  [OK] Response parsing and charge breakdown verified matching frontend & Excel requirements.")


async def test_registry_integration():
    print("\n--- TEST 4: Registry Integration & Fallbacks ---")
    conn = get_connector("HAPAG_LLOYD_API")
    assert isinstance(conn, HapagLloydAPIConnector)
    print(f"  Successfully retrieved connector from registry: {type(conn).__name__}")
    print("  [OK] Registry integration passed.")


async def test_dcsa_commercial_schedules_cross_validation():
    print("\n--- TEST 5: DCSA Commercial Schedules & Booking Cutoff Cross-Validation ---")
    connector = HapagLloydAPIConnector()
    
    # Mock DCSA schedules data
    now = datetime.now(timezone.utc)
    expired_dco = (now - timedelta(days=2)).isoformat()
    future_dco = (now + timedelta(days=5)).isoformat()
    
    mock_dcsa_schedules = [
        {
            "transit_time": 38,
            "receipt_dt": "2026-09-11T12:00:00Z",
            "receipt_locode": "SGSIN",
            "delivery_dt": "2026-10-19T14:00:00Z",
            "delivery_locode": "DEHAM",
            "cutoffs": {
                "DCO": expired_dco,
                "FCO": (now - timedelta(days=1)).isoformat(),
            },
            "legs": [
                {
                    "sequence": 1,
                    "vessel_name": "Hapag Vessel",
                    "voyage": "2638W",
                    "service_name": "FE4",
                    "departure_locode": "SGSIN",
                    "arrival_locode": "DEHAM",
                }
            ]
        }
    ]
    
    # 1. Parse with expired cutoff schedule
    quotes = connector._parse_offer_response_to_quotes(
        api_data=SAMPLE_HAPAG_OFFER_RESPONSE,
        requested_container_type="DRY 40H",
        destination_locode="DEHAM",
        destination_name="Hamburg",
        dcsa_schedules=mock_dcsa_schedules,
    )
    assert len(quotes) == 2
    expired_quote = quotes[0]
    assert "[BOOKING CLOSED - CUTOFF EXPIRED]" in expired_quote.vessel
    assert "Booking cutoff expired" in (expired_quote.warning_message or "")
    print("  [OK] Successfully detected expired booking cutoff from DCSA schedules.")

    # 2. Test Spot Capacity error correlation
    capacity_offer_response = {
        "offers": [
            {
                "productIdentifier": "QUICK_QUOTES",
                "placeOfReceiptDate": "2026-11-20T00:00:00Z",
                "placeOfDeliveryDateTime": "2026-12-05T00:00:00Z",
                "legs": [{"vesselName": "Test Vessel", "carrierServiceName": "CIX"}],
                "equipments": [
                    {
                        "requestedEquipment": {"requestedEquipmentSizeType": "45GP"},
                        "rates": [{"chargeTypeCode": "SEA", "amount": 1400.0, "currency": "USD", "seaFreightIndicator": True}]
                    }
                ]
            },
            {
                "productIdentifier": "QUICK_QUOTES_SPOT",
                "placeOfReceiptDate": "2026-11-20T00:00:00Z",
                "placeOfDeliveryDateTime": "2026-12-05T00:00:00Z",
                "legs": [{"vesselName": "Test Vessel", "carrierServiceName": "CIX"}],
                "equipments": [
                    {
                        "requestedEquipment": {"requestedEquipmentSizeType": "45GP"},
                        "errorReason": "CAPACITY",
                        "rates": []
                    }
                ]
            }
        ]
    }
    cap_quotes = connector._parse_offer_response_to_quotes(
        api_data=capacity_offer_response,
        requested_container_type="DRY 40H",
        destination_locode="INTUT",
        destination_name="Tuticorin",
        dcsa_schedules=[],
    )
    assert len(cap_quotes) == 1
    assert "[TARIFF ONLY - SPOT FULL]" in cap_quotes[0].vessel
    assert "CAPACITY" in (cap_quotes[0].warning_message or "")
    print("  [OK] Successfully detected Spot CAPACITY exhaustion and flagged tariff quote.")


async def test_origin_landfreight_inclusion():
    print("\n--- TEST 6: Origin Landfreight Inclusion in All-In Freight ---")
    connector = HapagLloydAPIConnector()
    offer_with_origin_landfreight = {
        "offers": [
            {
                "productIdentifier": "QUICK_QUOTES",
                "placeOfReceipt": "SGSIN",
                "placeOfReceiptDate": "2026-09-11T00:00:00.000Z",
                "placeOfDelivery": "DEHAM",
                "placeOfDeliveryDateTime": "2026-10-19T00:00:00.000Z",
                "transitTime": 38,
                "legs": [
                    {
                        "modeOfTransport": "VESSEL",
                        "departureLocation": "SGSIN",
                        "arrivalLocation": "DEHAM",
                        "vesselName": "Hapag Test",
                        "carrierServiceName": "FE4"
                    }
                ],
                "equipments": [
                    {
                        "requestedEquipment": {
                            "requestedEquipmentSizeType": "45GP",
                            "requestedEquipmentUnits": 1,
                        },
                        "rates": [
                            {
                                "chargeTypeCode": "BAS",
                                "chargeTypeShortDescription": "Basic Ocean Freight",
                                "amount": 2500.00,
                                "currency": "USD",
                                "seaFreightIndicator": True,
                                "included": False
                            },
                            {
                                "chargeTypeCode": "OLF",
                                "chargeTypeShortDescription": "Origin Landfreight",
                                "amount": 350.00,
                                "currency": "USD",
                                "seaFreightIndicator": False,
                                "included": False,
                                "locationProposal": "PC_CARRIAGE"
                            },
                            {
                                "chargeTypeCode": "THO",
                                "chargeTypeShortDescription": "Terminal Handling Charge Origin",
                                "amount": 180.00,
                                "currency": "USD",
                                "seaFreightIndicator": False,
                                "included": False,
                                "locationProposal": "BASE_PORT_FROM"
                            },
                            {
                                "chargeTypeCode": "THD",
                                "chargeTypeShortDescription": "Terminal Handling Charge Destination",
                                "amount": 200.00,
                                "currency": "USD",
                                "seaFreightIndicator": False,
                                "included": False,
                                "locationProposal": "BASE_PORT_TO"
                            }
                        ]
                    }
                ]
            }
        ]
    }

    quotes = connector._parse_offer_response_to_quotes(
        api_data=offer_with_origin_landfreight,
        requested_container_type="DRY 40H",
        destination_locode="DEHAM",
        destination_name="Hamburg, Germany",
        dcsa_schedules=[]
    )

    assert len(quotes) == 1
    q = quotes[0]
    # Basic Ocean Freight: $2500.00
    # Origin Landfreight ($350.00) MUST be in included_freight_surcharges and added to final_freight_value ($2850.00)
    assert q.basic_ocean_freight == 2500.00
    assert q.final_freight_value == 2850.00  # 2500 + 350

    included_names = [s.name for s in q.included_freight_surcharges]
    assert "Origin Landfreight" in included_names
    olf_surcharge = next(s for s in q.included_freight_surcharges if s.name == "Origin Landfreight")
    assert olf_surcharge.amount == 350.00

    # THO and THD must remain in excluded charges
    excluded_names = [c.name for c in q.excluded_charges]
    assert "Origin Landfreight" not in excluded_names
    assert any("Terminal Handling Charge Origin" in name for name in excluded_names)
    assert any("Terminal Handling Charge Destination" in name for name in excluded_names)

    print("  [OK] Origin Landfreight verified included in All-In freight total (final_freight_value).")


async def main():
    print("==================================================================")
    print("  RUNNING HAPAG-LLOYD REST API CONNECTOR VERIFICATION SUITE")
    print("==================================================================")
    await test_locode_resolution()
    await test_payload_generation()
    await test_response_parsing_and_normalization()
    await test_registry_integration()
    await test_dcsa_commercial_schedules_cross_validation()
    await test_origin_landfreight_inclusion()
    print("\n==================================================================")
    print("  ALL VERIFICATION TESTS PASSED SUCCESSFULLY! ")
    print("==================================================================")


if __name__ == "__main__":
    asyncio.run(main())

