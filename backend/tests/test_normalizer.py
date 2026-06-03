"""
Tests for normalizer / final freight value calculator.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.normalizer import calculate_final_freight_value, classify_and_organize_charges, standardize_date_string, normalize_quote
from models.schemas import ChargeCategory


def test_basic_calculation():
    charges = [
        {"name": "BOF", "amount": 1500, "category": ChargeCategory.BASIC_OCEAN_FREIGHT},
        {"name": "Discount", "amount": -100, "category": ChargeCategory.DISCOUNT},
        {"name": "Fuel", "amount": 150, "category": ChargeCategory.FREIGHT_SURCHARGE_INCLUDED},
        {"name": "Env", "amount": 80, "category": ChargeCategory.FREIGHT_SURCHARGE_INCLUDED},
        {"name": "Origin THC", "amount": 300, "category": ChargeCategory.ORIGIN_CHARGE_EXCLUDED},
        {"name": "Dest THC", "amount": 320, "category": ChargeCategory.DESTINATION_CHARGE_EXCLUDED},
    ]
    result = calculate_final_freight_value(charges)
    # 1500 + (-100) + 150 + 80 = 1630
    assert result == 1630.0, f"Expected 1630, got {result}"


def test_positive_discount_normalized():
    charges = [
        {"name": "BOF", "amount": 1000, "category": ChargeCategory.BASIC_OCEAN_FREIGHT},
        {"name": "Discount", "amount": 200, "category": ChargeCategory.DISCOUNT},  # positive
    ]
    result = calculate_final_freight_value(charges)
    # 1000 - 200 = 800
    assert result == 800.0, f"Expected 800, got {result}"


def test_no_charges():
    result = calculate_final_freight_value([])
    assert result == 0.0


def test_only_excluded():
    charges = [
        {"name": "Origin THC", "amount": 300, "category": ChargeCategory.ORIGIN_CHARGE_EXCLUDED},
        {"name": "Dest THC", "amount": 320, "category": ChargeCategory.DESTINATION_CHARGE_EXCLUDED},
        {"name": "Unknown", "amount": 50, "category": ChargeCategory.UNCERTAIN_EXCLUDED},
    ]
    result = calculate_final_freight_value(charges)
    assert result == 0.0


def test_classify_and_organize():
    raw_charges = [
        {"name": "Basic Ocean Freight", "amount": 1450, "currency": "USD"},
        {"name": "Maersk Discount", "amount": -100, "currency": "USD"},
        {"name": "Emergency Fuel Surcharge", "amount": 165, "currency": "USD"},
        {"name": "Europe Environment Surcharge", "amount": 85, "currency": "USD"},
        {"name": "Origin THC", "amount": 280, "currency": "USD"},
        {"name": "Destination THC", "amount": 320, "currency": "USD"},
        {"name": "Random Charge", "amount": 50, "currency": "USD"},
    ]
    result = classify_and_organize_charges(raw_charges)
    assert result["basic_ocean_freight"] == 1450
    assert result["discount"] == -100
    assert len(result["included_freight_surcharges"]) == 2
    assert len(result["excluded_charges"]) == 2
    assert len(result["uncertain_charges"]) == 1


def test_date_standardization():
    # 1. YYYY-MM-DD
    assert standardize_date_string("2026-06-09") == "9 Jun 2026"
    assert standardize_date_string("2026-07-03") == "3 Jul 2026"

    # 2. D MMM YYYY / DD MMM YYYY
    assert standardize_date_string("6 Jun 2026") == "6 Jun 2026"
    assert standardize_date_string("22 Jun 2026") == "22 Jun 2026"

    # 3. D/M/YYYY
    assert standardize_date_string("6/6/2026") == "6 Jun 2026"
    assert standardize_date_string("22/6/2026") == "22 Jun 2026"

    # 4. normalize_quote integration
    raw_quote = {
        "etd": "2026-06-09",
        "eta": "6/6/2026",
        "transit_time_days": 10,
        "service_name": "Test",
        "vessel": "Vessel",
        "total_price": 500.0,
    }
    normalized = normalize_quote("ONE", raw_quote, [])
    assert normalized.etd == "9 Jun 2026"
    assert normalized.eta == "6 Jun 2026"


if __name__ == "__main__":
    test_basic_calculation()
    test_positive_discount_normalized()
    test_no_charges()
    test_only_excluded()
    test_classify_and_organize()
    test_date_standardization()
    print("All normalizer tests passed!")
