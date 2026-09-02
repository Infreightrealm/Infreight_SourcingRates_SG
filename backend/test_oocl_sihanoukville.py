import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from models.schemas import RateSearchRequest
from carriers.oocl_connector import OOCLConnector

async def run_test():
    print("=======================================================")
    print("   Testing OOCL FreightSmart: SGSIN -> KHKOS (Sihanoukville)")
    print("=======================================================")

    print(f"OOCL_USERNAME: {os.getenv('OOCL_USERNAME')}")

    req = RateSearchRequest(
        origin="SGSIN",
        destination="KHKOS",
        container_type="40HQ",
        container_types=["20GP", "40GP", "40HQ"],
        container_quantity=1,
        weight_per_container_kg=20000,
        cargo_description="General Cargo",
        departure_date="2026-08-20",
        search_window_days=28,
        carriers=["OOCL"]
    )

    connector = OOCLConnector()
    print("1. Running search for SGSIN -> KHKOS...")
    status = await connector.search_quotes(req)
    print(f"Status returned: {status}")

    if status.value in ["AVAILABLE_QUOTES_FOUND", "SUCCESS", "COMPLETED"]:
        print("2. Extracting quotes...")
        quotes = await connector.extract_quote_list()
        print(f"[SUCCESS] Extracted {len(quotes)} quotes!")
        for i, q in enumerate(quotes, 1):
            print(f"   Quote #{i}: Container: {q.get('container_type')} | Price: ${q.get('price_usd')} | ETD: {q.get('etd')} | ETA: {q.get('eta')} | Service: {q.get('service_name')} | Vessel: {q.get('vessel_name')}")
    else:
        print(f"Result: {status}")

if __name__ == "__main__":
    asyncio.run(run_test())
