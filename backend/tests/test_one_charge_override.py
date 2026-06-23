"""
Unit test for ONE connector charge classification override.
"""
import sys
import os
import asyncio

# Add backend root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from carriers.one_connector import ONEConnector
from models.schemas import ChargeCategory

class MockCard:
    def __init__(self, text):
        self._text = text
    async def inner_text(self):
        return self._text

async def test_emergency_surcharge_override():
    connector = ONEConnector()
    connector.current_pol = "SINGAPORE (SGSIN)"
    connector.current_pod = "JEDDAH (SAJED)"
    
    mock_text = """
    BASIC OCEAN FREIGHT USD 7,000.00
    Origin Charge
    Emergency Surcharge USD 150.00
    Local Origin Fee USD 50.00
    Destination Charge
    Import THC USD 200.00
    """
    connector.current_card = MockCard(mock_text)
    
    charges = await connector.extract_charge_breakdown()
    print("Extracted charges in unit test:")
    found_emergency = False
    for c in charges:
        print(c)
        if c["name"] == "Emergency Surcharge":
            assert c["category"] == ChargeCategory.FREIGHT_SURCHARGE_INCLUDED.value
            assert "Forced" in c["reason"]
            found_emergency = True
        elif c["name"] == "Local Origin Fee":
            assert c["category"] == ChargeCategory.ORIGIN_CHARGE_EXCLUDED.value
        elif c["name"] == "Import THC":
            assert c["category"] == ChargeCategory.DESTINATION_CHARGE_EXCLUDED.value

    assert found_emergency, "Did not find Emergency Surcharge in parsed charges!"
    print("Unit test passed successfully!")

if __name__ == "__main__":
    asyncio.run(test_emergency_surcharge_override())
