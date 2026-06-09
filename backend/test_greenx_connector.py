import asyncio
import os
from carriers.greenx_connector import GreenXConnector
from models.schemas import RateSearchRequest

from datetime import date

async def test_greenx():
    # Set credentials if not already in env
    if not os.getenv("GREENX_USERNAME"):
        os.environ["GREENX_USERNAME"] = "INFREIGHT.SG@IN-FREIGHT.COM"
    if not os.getenv("GREENX_PASSWORD"):
        os.environ["GREENX_PASSWORD"] = "InfreightSGa2026"

    print("Initializing GreenXConnector...")
    connector = GreenXConnector()
    
    today = date.today().isoformat()  # e.g. "2026-06-09"
    print(f"Using departure date: {today}")

    request = RateSearchRequest(
        origin="SGSIN",
        destination="DEHAM",
        container_type="DRY 20",
        container_quantity=1,
        weight_per_container_kg=10000,
        commodity="General Cargo",
        departure_date=today,
        carriers=["GREENX"]
    )

    print("Running full search...")
    status, quotes = await connector.run_full_search(request)
    print(f"Search completed with status: {status}")
    print(f"Extracted {len(quotes)} quote(s):")
    for idx, q in enumerate(quotes):
        print(f"\n--- Quote {idx + 1} ---")
        print(f"ETD: {q.etd}")
        print(f"ETA: {q.eta}")
        print(f"Transit Time: {q.transit_time_days} days")
        print(f"Routing: {q.routing}")
        print(f"Service Name: {q.service_name}")
        print(f"Vessel: {q.vessel}")
        print(f"Basic Ocean Freight: {q.basic_ocean_freight} {q.currency}")
        print(f"Free Time (Detention at Dest): {q.free_time} days")
        print("Included Surcharges:")
        for charge in q.included_freight_surcharges:
            print(f"  - {charge.name}: {charge.amount} {charge.currency}")
        print("Excluded Surcharges:")
        for charge in q.excluded_charges:
            print(f"  - {charge.name}: {charge.amount} {charge.currency}")
        print(f"FINAL VALUE: {q.final_freight_value} {q.currency}")

if __name__ == "__main__":
    asyncio.run(test_greenx())
