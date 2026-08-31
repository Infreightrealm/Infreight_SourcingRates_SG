import pytest
import asyncio
import re
from models.schemas import ChargeCategory, ChargeSchema, QuoteSchema
from services.charge_classifier import classify_charge
from services.normalizer import classify_and_organize_charges, calculate_final_freight_value, normalize_quote
from carriers.oocl_connector import OOCLConnector


def test_charge_classifier_panama_canal_surcharge():
    """Verify charge_classifier classifies Panama Canal Surcharge as FREIGHT_SURCHARGE_INCLUDED."""
    cat, reason = classify_charge("Panama Canal Surcharge", 149.0)
    assert cat == ChargeCategory.FREIGHT_SURCHARGE_INCLUDED
    assert "Panama Canal Surcharge" in reason

    cat_pcs, _ = classify_charge("Panama Canal Surcharge (PCS)", 337.0)
    assert cat_pcs == ChargeCategory.FREIGHT_SURCHARGE_INCLUDED

    cat_short, _ = classify_charge("PCS", 297.0)
    assert cat_short == ChargeCategory.FREIGHT_SURCHARGE_INCLUDED


def test_normalizer_panama_canal_surcharge():
    """Verify normalizer includes Panama Canal Surcharge in final freight value and included surcharges."""
    raw_charges = [
        {"name": "Basic Ocean Freight", "amount": 2000.0, "currency": "USD"},
        {"name": "Panama Canal Surcharge (PCS)", "amount": 337.0, "currency": "USD"},
        {"name": "Origin THC", "amount": 150.0, "currency": "USD"},
    ]

    organized = classify_and_organize_charges(raw_charges)
    assert organized["basic_ocean_freight"] == 2000.0
    assert len(organized["included_freight_surcharges"]) == 1
    assert organized["included_freight_surcharges"][0].name == "Panama Canal Surcharge (PCS)"
    assert organized["included_freight_surcharges"][0].amount == 337.0

    final_val = calculate_final_freight_value(organized["all_classified"])
    assert final_val == 2337.0


def test_msc_charge_extraction_logic():
    """Verify MSC charge extraction logic parses Panama Canal Surcharge properly."""
    from carriers.msc_connector import parse_msc_modal_charges

    popup_text = """
FREIGHT CHARGE
Sea Freight (FRT) Per Equipment 2500 USD Prepaid, Collect, Elsewhere

FREIGHT SURCHARGES
Emission control areas [ECA] Per Equipment 15 USD Prepaid, Collect, Elsewhere

EXPORT SURCHARGES
Panama Canal Surcharge [PCS] Per Equipment 149 USD Prepaid, Collect, Elsewhere
Terminal handling charge [THC] Per Equipment 245 SGD Prepaid, Collect, Elsewhere
"""
    charges, total_freight, bof_value, currency = parse_msc_modal_charges(popup_text)

    included_surcharges = [c for c in charges if c["category"] == "included"]
    assert len(included_surcharges) == 2  # ECA and PCS
    pcs_charge = next(c for c in included_surcharges if "PCS" in c["name"] or "Panama" in c["name"])
    assert pcs_charge["amount"] == 149.0
    assert total_freight == 2500 + 15 + 149  # 2664.0
    assert bof_value == 2500.0



@pytest.mark.asyncio
async def test_oocl_normalize_result_with_pcs():
    """Verify OOCL normalize_result incorporates Panama Canal Surcharge (PCS)."""
    connector = OOCLConnector()

    raw_quote = {
        "container_type": "DRY 20",
        "basic_ocean_freight": 1800.0,
        "final_freight_value": 1800.0,
        "dialog_charges": {
            "DRY 20": {
                "ETS": 50.0,
                "PCS": 337.0
            }
        }
    }

    quote = await connector.normalize_result(raw_quote, [])
    assert quote.basic_ocean_freight == 1800.0
    assert quote.final_freight_value == 1800.0 + 50.0 + 337.0  # 2187.0
    assert len(quote.included_freight_surcharges) == 2

    pcs = next(s for s in quote.included_freight_surcharges if s.name == "Panama Canal Surcharge")
    assert pcs.amount == 337.0
    assert pcs.currency == "USD"


def test_container_types_standard_ordering():
    from models.schemas import sort_container_types
    input_types = ["DRY 40H", "DRY 20"]
    sorted_types = sort_container_types(input_types)
    assert sorted_types == ["DRY 20", "DRY 40H"]

    input_types_3 = ["DRY 40H", "DRY 40", "DRY 20"]
    sorted_types_3 = sort_container_types(input_types_3)
    assert sorted_types_3 == ["DRY 20", "DRY 40", "DRY 40H"]


def test_weight_surcharge_applicability_filtering():
    """Verify non-applicable weight tier surcharges are excluded from final value for 16,000 KG 20GP search."""
    from services.charge_classifier import is_weight_surcharge_applicable
    from services.normalizer import classify_and_organize_charges, calculate_final_freight_value

    c1 = "Between 20 and 34 ton container gross weight (VGM)"
    c2 = "Between 34.001 and 55 ton container gross weight (VGM)"

    is_app1, reason1 = is_weight_surcharge_applicable(c1, weight_per_container_kg=16000, container_type="DRY 20")
    assert not is_app1
    assert "outside required range" in reason1

    is_app2, reason2 = is_weight_surcharge_applicable(c2, weight_per_container_kg=16000, container_type="DRY 20")
    assert not is_app2
    assert "outside required range" in reason2

    raw_charges = [
        {"name": "Basic Ocean Freight", "amount": 2061.0, "currency": "USD", "category": "BASIC_OCEAN_FREIGHT"},
        {"name": "Emission Allowance", "amount": 88.0, "currency": "USD", "category": "FREIGHT_SURCHARGE_INCLUDED"},
        {"name": "Marine Fuel Recovery", "amount": 589.0, "currency": "USD", "category": "FREIGHT_SURCHARGE_INCLUDED"},
        {"name": "Between 20 and 34 ton container gross weight (VGM)", "amount": 400.0, "currency": "USD", "category": "FREIGHT_SURCHARGE_INCLUDED"},
        {"name": "Between 34.001 and 55 ton container gross weight (VGM)", "amount": 450.0, "currency": "USD", "category": "FREIGHT_SURCHARGE_INCLUDED"},
        {"name": "Security Manifest Document Fee", "amount": 35.0, "currency": "USD", "category": "FREIGHT_SURCHARGE_INCLUDED"},
    ]

    organized = classify_and_organize_charges(raw_charges, weight_per_container_kg=16000, container_type="DRY 20")
    
    assert len(organized["included_freight_surcharges"]) == 3
    included_names = [s.name for s in organized["included_freight_surcharges"]]
    assert c1 not in included_names
    assert c2 not in included_names

    final_val = calculate_final_freight_value(organized["all_classified"])
    assert final_val == 2061.0 + 88.0 + 589.0 + 35.0  # 2773.0 USD


def test_hapag_estimated_transportation_days_regex():
    """Verify regex extraction of Estimated Transportation Days from Hapag-Lloyd modal text."""
    modal_text_sample_1 = """
    Quick Quotes
    From PENANG TERMINAL / RAMP (POL)
    To HAMBURG TERMINAL / RAMP (POD)
    Estimated Transportation Days
    34
    """
    m1 = re.search(r"Estimated\s+Transportation\s+Days\s*[:\s]*(\d+)", modal_text_sample_1, re.IGNORECASE)
    assert m1 is not None
    assert int(m1.group(1)) == 34

    modal_text_sample_2 = """
    Estimated Transportation Days: 39
    """
    m2 = re.search(r"Estimated\s+Transportation\s+Days\s*[:\s]*(\d+)", modal_text_sample_2, re.IGNORECASE)
    assert m2 is not None
    assert int(m2.group(1)) == 39



