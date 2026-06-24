"""
Unit test for ONE connector and charge classifier Premium Cargo Service override.
"""
import sys
import os
import asyncio

# Add backend root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from carriers.one_connector import ONEConnector
from models.schemas import ChargeCategory
from services.charge_classifier import classify_charge

class MockCard:
    def __init__(self, text):
        self._text = text
    async def inner_text(self):
        return self._text

async def test_premium_cargo_service_override():
    connector = ONEConnector()
    connector.current_pol = "SINGAPORE (SGSIN)"
    connector.current_pod = "BEIRUT (LBBEY)"
    
    mock_text = """
    BASIC OCEAN FREIGHT USD 7,000.00
    Origin Charge
    Premium Cargo Service USD 350.00
    Emergency Fuel OriginRail USD 20.00
    Origin LandfreightRail USD 160.00
    Local Origin Fee USD 50.00
    Destination Charge
    Import THC USD 200.00
    """
    connector.current_card = MockCard(mock_text)
    
    charges = await connector.extract_charge_breakdown()
    print("Extracted charges in ONE unit test:")
    found_premium = False
    found_emergency_rail = False
    found_landfreight_rail = False
    for c in charges:
        print(c)
        if c["name"] == "Premium Cargo Service":
            assert c["category"] == ChargeCategory.FREIGHT_SURCHARGE_INCLUDED.value
            assert "Forced" in c["reason"]
            found_premium = True
        elif c["name"] == "Emergency Fuel OriginRail":
            assert c["category"] == ChargeCategory.FREIGHT_SURCHARGE_INCLUDED.value
            assert "Forced" in c["reason"]
            found_emergency_rail = True
        elif c["name"] == "Origin LandfreightRail":
            assert c["category"] == ChargeCategory.FREIGHT_SURCHARGE_INCLUDED.value
            assert "Forced" in c["reason"]
            found_landfreight_rail = True
        elif c["name"] == "Local Origin Fee":
            assert c["category"] == ChargeCategory.ORIGIN_CHARGE_EXCLUDED.value
        elif c["name"] == "Import THC":
            assert c["category"] == ChargeCategory.DESTINATION_CHARGE_EXCLUDED.value

    assert found_premium, "Did not find Premium Cargo Service in parsed charges!"
    assert found_emergency_rail, "Did not find Emergency Fuel OriginRail in parsed charges!"
    assert found_landfreight_rail, "Did not find Origin LandfreightRail in parsed charges!"
    
    # Test classifier directly
    category, reason = classify_charge("Premium Cargo Service", 350.00)
    assert category == ChargeCategory.FREIGHT_SURCHARGE_INCLUDED
    assert "Forced" in reason
    
    category, reason = classify_charge("Emergency  Fuel OriginRail", 20.00)
    assert category == ChargeCategory.FREIGHT_SURCHARGE_INCLUDED
    assert "Forced" in reason
    
    category, reason = classify_charge("Origin LandfreightRail", 160.00)
    assert category == ChargeCategory.FREIGHT_SURCHARGE_INCLUDED
    assert "Forced" in reason
    
    print("ONE override unit tests passed successfully!")

if __name__ == "__main__":
    asyncio.run(test_premium_cargo_service_override())
