import pytest
from carriers.msc_connector import parse_msc_modal_charges


def test_msc_charges_singapore_to_conakry_guinea():
    """
    Test MSC charges parsing for Singapore to Conakry, Guinea (40GP).
    Charges with 'Must follow same terms of Payment as Freight.' in Comments & Conditions
    must be included in the final freight value: 6200 USD + 160 + 105 + 2800 = 9265 USD.
    """
    popup_text = """
Charges Charge Charge Level Amount Supported Payments Comments & Conditions
Freight Charge Sea Freight (FRT) Per Equipment 6200 USD Prepaid, Collect, Elsewhere

Export Surcharges Terminal handling charge [THC] Per Equipment 370 SGD Prepaid, Collect, Elsewhere
Documentation fee [DOC] Per Bill of lading 280 SGD Prepaid, Collect, Elsewhere
Seal fee [SEL] Per Equipment 26 SGD Prepaid, Collect, Elsewhere

Import Surcharges Port surcharge [PAD] Per Equipment 160 USD Prepaid, Collect, Elsewhere Must follow same terms of Payment as Freight.
Customs duty [CUS] Per Equipment 105 USD Prepaid, Collect, Elsewhere Must follow same terms of Payment as Freight.
Emergency congestion surcharge [ECS] Per Equipment 2800 USD Prepaid, Collect, Elsewhere Must follow same terms of Payment as Freight.

Total 9,796 USD
Subject to charges calculated on percentage of cargo value which will be calculated and added at Booking/SI stage.
*Per Bill of Lading* charges will be considered only once per BL. Additional local and contingency charges may apply.
"""
    charges, total_freight, bof_value, currency = parse_msc_modal_charges(popup_text)

    assert bof_value == 6200.0
    assert total_freight == 9265.0  # 6200 + 160 + 105 + 2800
    assert currency == "USD"

    # Verify BOF charge
    bof_charges = [c for c in charges if c["category"] == "bof"]
    assert len(bof_charges) == 1
    assert bof_charges[0]["name"] == "Sea Freight (FRT)"
    assert bof_charges[0]["amount"] == 6200.0

    # Verify Included Freight Surcharges (PAD, CUS, ECS)
    included_charges = [c for c in charges if c["category"] == "included"]
    assert len(included_charges) == 3
    included_names = [c["name"] for c in included_charges]
    assert "Port Surcharge [PAD]" in included_names
    assert "Customs Duty [CUS]" in included_names
    assert "Emergency Congestion Surcharge [ECS]" in included_names

    pad = next(c for c in included_charges if "[PAD]" in c["name"])
    assert pad["amount"] == 160.0
    assert pad["currency"] == "USD"

    cus = next(c for c in included_charges if "[CUS]" in c["name"])
    assert cus["amount"] == 105.0
    assert cus["currency"] == "USD"

    ecs = next(c for c in included_charges if "[ECS]" in c["name"])
    assert ecs["amount"] == 2800.0
    assert ecs["currency"] == "USD"

    # Verify Excluded Charges (THC, DOC, SEL)
    excluded_charges = [c for c in charges if c["category"] == "excluded"]
    assert len(excluded_charges) == 3
    excluded_names = [c["name"] for c in excluded_charges]
    assert "Terminal Handling Charge [THC]" in excluded_names
    assert "Documentation Fee [DOC]" in excluded_names
    assert "Seal Fee [SEL]" in excluded_names


def test_msc_charges_mixed_conditions():
    """
    Test when only some surcharges have the payment condition.
    """
    popup_text = """
FREIGHT CHARGE
Sea Freight (FRT) Per Equipment 3000 USD Prepaid, Collect, Elsewhere

EXPORT SURCHARGES
Terminal handling charge [THC] Per Equipment 200 USD Prepaid, Collect, Elsewhere
Peak Season Surcharge [PSS] Per Equipment 500 USD Prepaid, Collect, Elsewhere Must follow same terms of Payment as Freight.

IMPORT SURCHARGES
Destination Delivery Charge [DDC] Per Equipment 150 USD Prepaid, Collect, Elsewhere
"""
    charges, total_freight, bof_value, currency = parse_msc_modal_charges(popup_text)

    assert bof_value == 3000.0
    assert total_freight == 3500.0  # 3000 (BOF) + 500 (PSS with same payment terms)
    assert currency == "USD"

    included = [c for c in charges if c["category"] == "included"]
    assert len(included) == 1
    assert "Peak Season Surcharge [PSS]" in included[0]["name"]
    assert included[0]["amount"] == 500.0

    excluded = [c for c in charges if c["category"] == "excluded"]
    assert len(excluded) == 2
    excluded_names = [c["name"] for c in excluded]
    assert "Terminal Handling Charge [THC]" in excluded_names
    assert "Destination Delivery Charge [DDC]" in excluded_names
