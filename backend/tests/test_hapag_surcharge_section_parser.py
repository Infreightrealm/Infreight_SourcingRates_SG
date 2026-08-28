"""
Unit test to verify Hapag-Lloyd Price Breakdown section classification logic.
Ensures 'Freight Surcharges' subsection is correctly identified as 'surcharges'
and not accidentally matched as 'freight_charges'.
"""
import pytest
from services.charge_classifier import classify_charge
from models.schemas import ChargeCategory


def parse_hapag_section(header_text: str) -> str:
    lowerText = header_text.strip().lower()
    
    if "export surcharges" in lowerText or "export surcharge" in lowerText:
        return "export_surcharges"
    if "import surcharges" in lowerText or "import surcharge" in lowerText:
        return "import_surcharges"
    if "freight surcharges" in lowerText or "freight surcharge" in lowerText or lowerText == "surcharges":
        return "surcharges"
    if "freight charges" in lowerText or "freight charge" in lowerText:
        return "freight_charges"
    return "unknown"


def test_hapag_section_parsing_order():
    # 1. Main Freight Charges header -> freight_charges
    assert parse_hapag_section("Freight Charges") == "freight_charges"

    # 2. Freight Surcharges subsection header -> surcharges (MUST NOT BE freight_charges!)
    assert parse_hapag_section("Freight Surcharges") == "surcharges"

    # 3. Export Surcharges subsection -> export_surcharges
    assert parse_hapag_section("Export Surcharges") == "export_surcharges"

    # 4. Import Surcharges subsection -> import_surcharges
    assert parse_hapag_section("Import Surcharges") == "import_surcharges"


def test_hapag_surcharges_classification():
    # Carrier Security Fee -> FREIGHT_SURCHARGE_INCLUDED
    cat, _ = classify_charge("Carrier Security Fee", 15.0, "surcharges")
    assert cat == ChargeCategory.FREIGHT_SURCHARGE_INCLUDED
