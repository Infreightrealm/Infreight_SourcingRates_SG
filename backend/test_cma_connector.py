"""CMA CGM end-to-end test — login + search + extract quotes."""
import os
# IMPORTANT: Clear ALL proxy env vars BEFORE any import triggers load_dotenv() from database.py.
# The burned Bright Data proxy IP causes DataDome hard-blocks on CMA CGM.
# CMA works fine on local IP without proxy.
for key in ["CMA_PROXY_USER", "CMA_PROXY_PASS", "MAERSK_PROXY_USER", "MAERSK_PROXY_PASS",
            "BRIGHTDATA_PROXY_USER", "BRIGHTDATA_PROXY_PASS", "BRIGHTDATA_PROXY_SERVER"]:
    os.environ[key] = ""

import asyncio
from carriers.cma_connector import CMAConnector
from models.schemas import RateSearchRequest

async def test_cma():
    if not os.getenv("CMA_USERNAME"):
        os.environ["CMA_USERNAME"] = "bookingsg@in-freight.com"
    if not os.getenv("CMA_PASSWORD"):
        os.environ["CMA_PASSWORD"] = "@IFSGc2023"

    print("Initializing CMAConnector...")
    connector = CMAConnector()
    
    try:
        print("Logging in...")
        login_success = await connector.login()
        print(f"Login success: {login_success}")
        if not login_success:
            return

        request = RateSearchRequest(
            origin="SGSIN",
            destination="MYPKG",
            container_type="DRY 40H",
            container_quantity=1,
            weight_per_container_kg=15000,
            commodity="Furniture",  # CMA auto-selects FAK regardless — this is ignored
            departure_date="tomorrow",
            carriers=["CMA"]
        )

        print("Running run_full_search...")
        status, quotes = await connector.run_full_search(request)
        print(f"Run status: {status}")
        print(f"Total normalized quotes returned: {len(quotes)}")
        for idx, q in enumerate(quotes):
            print(f"\nQuote {idx + 1}:")
            print(q.model_dump_json(indent=2))

    finally:
        await connector.close()

if __name__ == "__main__":
    asyncio.run(test_cma())
