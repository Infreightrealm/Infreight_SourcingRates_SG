import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from carriers.hapag_lloyd_connector import HapagLloydConnector

async def test_mapping():
    connector = HapagLloydConnector()
    print("Testing Freetime Mapping Injection...")
    
    # Simulate a quote search response formatting
    # HapagLloydConnector uses get_hapag_freetime(destination_country, equipment_type)
    
    test_cases = [
        ("Saudi Arabia", "20GP"),
        ("Saudi Arabia", "40GP"),
        ("USA", "20GP"),
        ("Germany", "40GP"),
        ("China", "20GP"),
        ("Kenya", "40GP"),
        ("Unknown Country", "20GP")
    ]
    
    for country, equip in test_cases:
        freetime = connector.get_hapag_freetime(country, equip)
        print(f"Destination: {country} | Equipment: {equip} -> Freetime: {freetime}")

if __name__ == "__main__":
    asyncio.run(test_mapping())
