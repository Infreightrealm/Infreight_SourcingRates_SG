"""
Tests for charge classifier.
"""
import sys
import os

# Add backend root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Import schemas directly (not through models package which triggers DB init)
from models.schemas import ChargeCategory
from services.charge_classifier import classify_charge


def test_basic_ocean_freight():
    cat, _ = classify_charge("Basic Ocean Freight", 1500)
    assert cat == ChargeCategory.BASIC_OCEAN_FREIGHT

    cat, _ = classify_charge("Ocean Freight", 1200)
    assert cat == ChargeCategory.BASIC_OCEAN_FREIGHT

    cat, _ = classify_charge("Sea Freight", 1000)
    assert cat == ChargeCategory.BASIC_OCEAN_FREIGHT


def test_discount():
    cat, _ = classify_charge("Discount", -100)
    assert cat == ChargeCategory.DISCOUNT

    cat, _ = classify_charge("Volume Rebate", -50)
    assert cat == ChargeCategory.DISCOUNT

    cat, _ = classify_charge("Negative Adjustment", -75)
    assert cat == ChargeCategory.DISCOUNT


def test_freight_surcharges():
    surcharges = [
        ("Emergency Fuel Surcharge", 150),
        ("Europe Environment Surcharge", 85),
        ("ONE Bunker Surcharge", 175),
        ("Bunker Adjustment Factor", 95),
        ("Low Sulphur Surcharge", 120),
        ("Peak Season Surcharge", 200),
        ("War Risk Surcharge", 45),
        ("BAF", 100),
        ("General Rate Increase", 50),
    ]
    for name, amount in surcharges:
        cat, _ = classify_charge(name, amount)
        assert cat == ChargeCategory.FREIGHT_SURCHARGE_INCLUDED, f"Failed for: {name}"


def test_origin_charges():
    charges = [
        ("Origin THC", 280),
        ("Terminal Handling Origin", 280),
        ("POL THC", 250),
        ("Export Documentation Fee", 45),
        ("Pickup Fee", 100),
    ]
    for name, amount in charges:
        cat, _ = classify_charge(name, amount)
        assert cat == ChargeCategory.ORIGIN_CHARGE_EXCLUDED, f"Failed for: {name}"


def test_destination_charges():
    charges = [
        ("Destination THC", 320),
        ("Terminal Handling Destination", 310),
        ("POD THC", 300),
        ("Import Documentation Fee", 45),
        ("Delivery Fee", 150),
    ]
    for name, amount in charges:
        cat, _ = classify_charge(name, amount)
        assert cat == ChargeCategory.DESTINATION_CHARGE_EXCLUDED, f"Failed for: {name}"


def test_local_charges_excluded():
    charges = [
        ("Documentation Fee", 50),
        ("Seal Fee", 20),
        ("VGM Fee", 25),
        ("Container Cleaning Fee", 35),
        ("ISPS Fee", 15),
        ("Demurrage", 100),
        ("Detention", 200),
    ]
    for name, amount in charges:
        cat, _ = classify_charge(name, amount)
        assert cat in (ChargeCategory.ORIGIN_CHARGE_EXCLUDED,
                       ChargeCategory.DESTINATION_CHARGE_EXCLUDED), f"Failed for: {name}"


def test_uncertain():
    cat, _ = classify_charge("Random Unknown Charge XYZ", 50)
    assert cat == ChargeCategory.UNCERTAIN_EXCLUDED


if __name__ == "__main__":
    test_basic_ocean_freight()
    test_discount()
    test_freight_surcharges()
    test_origin_charges()
    test_destination_charges()
    test_local_charges_excluded()
    test_uncertain()
    print("All charge classifier tests passed!")
