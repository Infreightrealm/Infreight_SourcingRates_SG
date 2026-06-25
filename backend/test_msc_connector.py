import asyncio
import os
import time
from datetime import date
from carriers.msc_connector import MSCConnector
from models.schemas import RateSearchRequest

async def test_msc():
    print("Testing MSC Connector...")

    connector = MSCConnector()
    container_types = ["DRY 20", "DRY 40", "DRY 40H"]

    for idx, c_type in enumerate(container_types):
        print(f"\n==================================================")
        print(f"Starting search cycle {idx+1}/{len(container_types)} for container type {c_type}")
        print(f"==================================================")

        req = RateSearchRequest(
            carriers=["MSC"],
            origin="SGSIN",
            destination="DEHAM",
            service_term="CY/CY",
            container_type=c_type,
            container_types=container_types,
            container_quantity=1,
            weight_per_container_kg=18000,
            commodity="Furniture",
            departure_date=str(date.today()),
            search_window_days=14,
        )

        start_time = time.time()
        status, quotes = await connector.run_full_search(req)
        elapsed = time.time() - start_time

        print(f"Search completed in {elapsed:.2f} seconds with status: {status}")
        print(f"Extracted {len(quotes)} quote(s) for {c_type}:")
        for i, q in enumerate(quotes):
            print(f"  --- Quote {i+1} ---")
            print(f"  Vessel: {q.vessel} | Service: {q.service_name}")
            print(f"  Routing: {q.routing} | TT: {q.transit_time_days} days")
            print(f"  ETD: {q.etd} | ETA: {q.eta}")
            print(f"  Total Freight: {q.final_freight_value} {q.currency}")
            print(f"  Free Time (Dest): {q.free_time} days")
            print(f"  Included Surcharges: {len(q.included_freight_surcharges)}")
            for charge in q.included_freight_surcharges:
                print(f"    - {charge.name}: {charge.amount} {charge.currency}")
            print()

if __name__ == "__main__":
    asyncio.run(test_msc())

