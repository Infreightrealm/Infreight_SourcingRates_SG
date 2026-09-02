import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from models.schemas import RateSearchRequest
from carriers.cma_connector import CMAConnector

async def run_test():
    print("=======================================================")
    print("   Testing CMA CGM Connector: THLCH -> PRSJU (San Juan)")
    print("=======================================================")

    req = RateSearchRequest(
        origin="THLCH",
        destination="PRSJU",
        container_type="40HQ",
        container_types=["20GP", "40HQ"],
        container_quantity=1,
        weight_per_container_kg=10000,
        cargo_description="General Cargo",
        carriers=["CMA"]
    )

    connector = CMAConnector()
    print("1. Logging into CMA CGM...")
    logged_in = await connector.login()
    if not logged_in:
        print("Login failed!")
        return

    print("2. Running search for THLCH -> PRSJU...")
    status = await connector.search_quotes(req)
    print(f"Status returned: {status}")

    if status.value in ["AVAILABLE_QUOTES_FOUND", "SUCCESS", "COMPLETED"]:
        print("3. Extracting quotes...")
        quotes = await connector.extract_quote_list()
        print(f"[SUCCESS] Extracted {len(quotes)} quotes!")
        for i, q in enumerate(quotes[:5], 1):
            print(f"   Quote #{i}: Price: ${q.get('price_usd')} | ETD: {q.get('etd')} | ETA: {q.get('eta')} | Transit: {q.get('transit_days')}d | Vessel: {q.get('vessel_name')}")
    else:
        print(f"Result: {status}")

if __name__ == "__main__":
    asyncio.run(run_test())
