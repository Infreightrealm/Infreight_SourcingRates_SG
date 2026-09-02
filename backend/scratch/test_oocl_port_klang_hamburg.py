import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

from models.schemas import RateSearchRequest
from carriers.oocl_connector import OOCLConnector

async def run_test():
    req_20 = RateSearchRequest(
        origin="Port Klang, Selangor, Malaysia [MYPKG]",
        destination="Hamburg, Hamburg, Germany [DEHAM]",
        container_type="20GP",
        container_types=["20GP", "40HQ"],
        container_quantity=1,
        weight_per_container_kg=20000,
        commodity="FAK",
        departure_date="2026-08-31",
        search_window_days=14,
        carriers=["OOCL"]
    )

    req_40 = req_20.model_copy(update={"container_type": "40HQ"})

    connector = OOCLConnector()
    try:
        print("\n--- Cycle 1: 20GP ---")
        status_20, quotes_20 = await connector.run_full_search(req_20)
        print(f"Status 20GP: {status_20}, count: {len(quotes_20)}")
        for q in quotes_20[:2]:
            print(f"  {q.container_type}: ${q.final_freight_value} | ETD {q.etd} | {q.vessel}")

        print("\n--- Cycle 2: 40HQ (cached) ---")
        status_40, quotes_40 = await connector.run_full_search(req_40)
        print(f"Status 40HQ: {status_40}, count: {len(quotes_40)}")
        for q in quotes_40[:2]:
            print(f"  {q.container_type}: ${q.final_freight_value} | ETD {q.etd} | {q.vessel}")
    finally:
        await connector.close()

if __name__ == "__main__":
    asyncio.run(run_test())
