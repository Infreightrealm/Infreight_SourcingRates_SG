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


def test_one_breakdown_parsing():
    import re
    from services.charge_classifier import classify_charge
    from services.normalizer import normalize_quote

    # Simulated implementation of ONE Connector's extract_charge_breakdown on polluted text
    text = """
BASIC OCEAN FREIGHT
Basic Ocean Freight
DRY 20 x 1 (USD 350.00)                        USD 350.00
FREIGHT CHARGE
Emergency Fuel Surcharge
DRY 20 x 1 (USD 60.00)                         USD 60.00
Origin
2026-06-11
1 day(s)
Direct
Destination
2026-06-12
Service Lane/Vessel Voyage
KCS / YM COOPERATION (058N)
POL
SINGAPORE (SGSIN)
POD
PORT KLANG (MYPKG)
Status
Available
USD 799.95
Accept
"""
    if "BASIC OCEAN FREIGHT" in text.upper():
        idx_bof = text.upper().find("BASIC OCEAN FREIGHT")
        text = text[idx_bof:]

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    amount_pattern = re.compile(r"(?:^|\s)([A-Z]{3})\s*([\d,]+\.\d{2})$")

    def is_section_heading(line: str) -> bool:
        normalized = line.strip().lower()
        return normalized in {
            "freight charge",
            "origin charge",
            "destination charge",
            "special promotion service",
            "promotion",
        } or normalized.startswith("what is special promotion service")

    def is_container_line(line: str) -> bool:
        return "x" in line and "(" in line and ")" in line

    def is_stop_line(line: str) -> bool:
        normalized = line.strip().lower()
        if normalized in {"pol", "pod", "accept", "details", "origin", "destination"}:
            return True
        if "service lane" in normalized or "vessel voyage" in normalized:
            return True
        if re.match(r"^\d{4}-\d{2}-\d{2}$", normalized):
            return True
        return False

    charges = []
    for index, line in enumerate(lines):
        if is_stop_line(line):
            break
        amount_match = amount_pattern.search(line)
        if not amount_match:
            continue

        currency = amount_match.group(1)
        amount = float(amount_match.group(2).replace(",", ""))

        remaining_line = line[:amount_match.start()].strip()
        name = ""

        if remaining_line and not is_container_line(remaining_line) and not is_section_heading(remaining_line):
            name = remaining_line
        else:
            name_index = index - 1
            while name_index >= 0:
                candidate = lines[name_index]
                if not candidate or is_section_heading(candidate) or is_container_line(candidate):
                    name_index -= 1
                    continue
                if amount_pattern.search(candidate):
                    name_index -= 1
                    continue
                break

            name = lines[name_index] if name_index >= 0 else f"Charge {len(charges) + 1}"

        section_heading = "unknown"
        sec_index = index - 1
        while sec_index >= 0:
            candidate = lines[sec_index]
            if is_section_heading(candidate):
                section_heading = candidate.strip().lower()
                break
            sec_index -= 1

        category, reason = classify_charge(name, amount, section_heading)
        charges.append({
            "name": name,
            "amount": amount,
            "currency": currency,
            "category": category.value,
            "reason": reason,
        })

    # Ensure stop condition successfully ignored the subsequent card header (which has USD 799.95)
    assert len(charges) == 2, f"Expected 2 charges, got {len(charges)}: {charges}"
    assert charges[0]["name"] == "Basic Ocean Freight"
    assert charges[0]["amount"] == 350.0
    assert charges[0]["category"] == "BASIC_OCEAN_FREIGHT"

    assert charges[1]["name"] == "Emergency Fuel Surcharge"
    assert charges[1]["amount"] == 60.0
    assert charges[1]["category"] == "FREIGHT_SURCHARGE_INCLUDED"

    # Test full normalization integration
    raw_quote = {
        "etd": "2026-06-11",
        "eta": "2026-06-12",
        "transit_time_days": 1,
        "service_name": "KCS / YM COOPERATION (058N)",
        "vessel": "YM COOPERATION (058N)",
        "total_price": 410.0,
    }
    normalized = normalize_quote("ONE", raw_quote, charges)
    assert normalized.etd == "11 Jun 2026", f"Expected '11 Jun 2026', got '{normalized.etd}'"
    assert normalized.eta == "12 Jun 2026", f"Expected '12 Jun 2026', got '{normalized.eta}'"
    assert normalized.basic_ocean_freight == 350.0
    assert normalized.final_freight_value == 410.0
    assert len(normalized.included_freight_surcharges) == 1
    assert normalized.included_freight_surcharges[0].name == "Emergency Fuel Surcharge"
    assert normalized.included_freight_surcharges[0].amount == 60.0


if __name__ == "__main__":
    test_basic_calculation()
    test_positive_discount_normalized()
    test_no_charges()
    test_only_excluded()
    test_classify_and_organize()
    test_date_standardization()
    test_one_breakdown_parsing()
    print("All normalizer tests passed!")
