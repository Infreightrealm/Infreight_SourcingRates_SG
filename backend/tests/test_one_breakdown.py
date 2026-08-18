import pytest
import asyncio
from carriers.one_connector import ONEConnector
from models.schemas import RateSearchRequest, ChargeCategory

@pytest.mark.asyncio
async def test_one_breakdown_currency_and_arbitrary_destination_classification():
    connector = ONEConnector()
    
    sample_text = """
BASIC OCEAN FREIGHT
Basic Ocean Freight
DRY 20 x 1 (USD 775.00) USD 775.00
DRY 40 x 1 (USD 1,275.00) USD 1,275.00
DRY 40H x 1 (USD 1,275.00) USD 1,275.00

FREIGHT CHARGE
Arbitrary Tariff At Destination
DRY 20 x 1 (INR 52,000.00) INR 52,000.00
DRY 40 x 1 (INR 90,000.00) INR 90,000.00
DRY 40H x 1 (INR 83,000.00) INR 83,000.00

ORIGIN CHARGE
Doc Fee (Origin) SGD 160.00
Heavy Weight Surcharge
DRY 20 x 1 (USD 150.00) USD 150.00
Seal Fee
DRY 20 x 1 (SGD 26.00) SGD 26.00
DRY 40 x 1 (SGD 26.00) SGD 26.00
DRY 40H x 1 (SGD 26.00) SGD 26.00

DESTINATION CHARGE
Doc Fee (Dest) INR 6,500.00
"""

    # Mock page/card text reading
    class MockPage:
        async def inner_text(self):
            return sample_text
            
    connector.page = MockPage()
    connector.current_card = MockPage()
    connector.current_pol = "SINGAPORE (SGSIN)"
    connector.current_pod = "NHAVA SHEVA (INNSA)"
    
    charges = await connector.extract_charge_breakdown()
    
    # Assert container token currency is correctly extracted
    inr_charges = [c for c in charges if c["currency"] == "INR"]
    assert len(inr_charges) > 0, "INR charges should be parsed with currency 'INR', not hardcoded 'USD'"
    
    # Assert Arbitrary Tariff At Destination is classified as DESTINATION_CHARGE_EXCLUDED
    arb_dest_charges = [c for c in charges if "arbitrary tariff at destination" in c["name"].lower()]
    assert len(arb_dest_charges) > 0
    for c in arb_dest_charges:
        assert c["category"] == ChargeCategory.DESTINATION_CHARGE_EXCLUDED.value
        
    # Split quotes
    raw_quote = {
        "etd": "2026-08-22",
        "eta": "2026-09-03",
        "transit_time_days": 11,
        "service_name": "NCI",
        "vessel": "ONE THESEUS (0102W)",
        "routing": "Direct",
    }
    
    quotes = await connector._split_raw_quote_by_container_types(raw_quote, charges)
    
    # Verify split quotes for 20GP, 40GP, 40HQ
    quote_20 = next(q for q in quotes if q.container_type == "DRY 20")
    quote_40 = next(q for q in quotes if q.container_type == "DRY 40")
    quote_40h = next(q for q in quotes if q.container_type == "DRY 40H")
    
    # BOF should be pure USD Ocean Freight ($775 for 20GP, $1275 for 40GP/40HQ)
    assert quote_20.basic_ocean_freight == 775.00
    assert quote_40.basic_ocean_freight == 1275.00
    assert quote_40h.basic_ocean_freight == 1275.00
    
    # Final value for 20GP should be $775 + $150 (Heavy Weight Surcharge) = $925.00 USD (NOT $52,775!)
    assert quote_20.final_freight_value == 925.00
    # Final value for 40HQ should be $1275.00 USD (NOT $84,275!)
    assert quote_40h.final_freight_value == 1275.00

if __name__ == "__main__":
    asyncio.run(test_one_breakdown_currency_and_arbitrary_destination_classification())
