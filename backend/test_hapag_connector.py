# -*- coding: utf-8 -*-
"""Hapag-Lloyd end-to-end test using run_full_search."""
import os
import asyncio
import json
from carriers.hapag_lloyd_connector import HapagLloydConnector
from models.schemas import RateSearchRequest

async def test_hapag():
    from dotenv import load_dotenv
    load_dotenv()
    
    if not os.getenv("HAPAG_LLOYD_USERNAME") or not os.getenv("HAPAG_LLOYD_PASSWORD"):
        print("[TEST] [ERROR] HAPAG_LLOYD_USERNAME and HAPAG_LLOYD_PASSWORD must be configured in your environment or a .env file.")
        return

    print("Initializing HapagLloydConnector...")
    connector = HapagLloydConnector()

    try:
        request = RateSearchRequest(
            origin="SGSIN",
            destination="MYPKG",
            container_type="DRY 40H",
            container_quantity=2,
            weight_per_container_kg=20000,
            departure_date="tomorrow",
            carriers=["HAPAG_LLOYD"]
        )

        print(f"Running full search flow for request: {request.origin} -> {request.destination}...")
        status, results = await connector.run_full_search(request)
        print(f"Search status: {status}")

        print(f"\nExtracted {len(results)} quotes:")
        for r in results:
            print(f"\nETD:          {r.etd}")
            print(f"ETA:          {r.eta}")
            print(f"Transit:      {r.transit_time_days} days")
            print(f"Service:      {r.service_name}")
            print(f"Vessel:       {r.vessel}")
            print(f"Total:        USD {r.final_freight_value}")
            print(f"Basic Freight: USD {r.basic_ocean_freight}")
            print(f"Surcharges:   {len(r.included_freight_surcharges)} items")
            for c in r.included_freight_surcharges:
                print(f"  - {c.name}: {c.amount} {c.currency}")
            print(f"Excluded:     {len(r.excluded_charges)} items")
            for c in r.excluded_charges:
                print(f"  - {c.name}: {c.amount} {c.currency}")

        # Save full results to JSON
        os.makedirs("scratch", exist_ok=True)
        results_path = "scratch/hapag_all_quotes.json"
        with open(results_path, "w", encoding="utf-8") as f:
            json.dump([json.loads(r.model_dump_json()) for r in results], f, indent=2)
        print(f"\nFull results saved to {results_path}")

    finally:
        await connector.close()

if __name__ == "__main__":
    asyncio.run(test_hapag())
