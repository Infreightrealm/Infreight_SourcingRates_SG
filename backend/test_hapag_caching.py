# -*- coding: utf-8 -*-
"""Test multi-container search and caching for Hapag-Lloyd connector."""
import os
import asyncio
import time
from dotenv import load_dotenv
from carriers.hapag_lloyd_connector import HapagLloydConnector
from models.schemas import RateSearchRequest

async def test_caching():
    load_dotenv()
    
    has_creds = (
        (os.getenv("HAPAG_LLOYD_USERNAME") and os.getenv("HAPAG_LLOYD_PASSWORD")) or
        (os.getenv("HAPAG_LLOYD_USERNAME_ROW") and os.getenv("HAPAG_LLOYD_PASSWORD_ROW")) or
        (os.getenv("HAPAG_LLOYD_USERNAME_US_CA") and os.getenv("HAPAG_LLOYD_PASSWORD_US_CA")) or
        (os.getenv("HAPAG_LLOYD_USERNAME_EU") and os.getenv("HAPAG_LLOYD_PASSWORD_EU"))
    )
    if not has_creds:
        print("[TEST] [ERROR] Hapag-Lloyd credentials must be configured in your environment or a .env file.")
        return

    print("Initializing HapagLloydConnector...")
    connector = HapagLloydConnector()

    try:
        # Cycle 1: 20GP
        req1 = RateSearchRequest(
            origin="SGSIN",
            destination="DEHAM",
            container_type="20GP",
            container_quantity=1,
            weight_per_container_kg=20000,
            departure_date="tomorrow",
            search_window_days=7,
            carriers=["HAPAG_LLOYD"],
            hapag_region="US_CA"
        )

        print("\n--- CYCLE 1: 20GP (Initial search form submission) ---")
        t0 = time.time()
        status1, results1 = await connector.run_full_search(req1)
        dur1 = time.time() - t0
        print(f"Cycle 1 finished in {dur1:.2f}s. Status: {status1}, Quotes: {len(results1)}")
        spot1 = [r for r in results1 if "(SPOT)" in (r.vessel or "")]
        print(f"  Standard quotes: {len(results1) - len(spot1)}, Spot quotes: {len(spot1)}")
        for r in results1[:2]:
            print(f"  -> ETD: {r.etd} | Total: USD {r.final_freight_value} | Basic: USD {r.basic_ocean_freight} | Vessel: {r.vessel}")

        # Cycle 2: 40HQ (Should fast re-query via Edit panel to fetch 40HQ Spot quotes)
        req2 = RateSearchRequest(
            origin="SGSIN",
            destination="DEHAM",
            container_type="40HQ",
            container_quantity=1,
            weight_per_container_kg=20000,
            departure_date="tomorrow",
            search_window_days=7,
            carriers=["HAPAG_LLOYD"],
            hapag_region="US_CA"
        )

        print("\n--- CYCLE 2: 40HQ (Fast re-query via on-page Edit panel) ---")
        t1 = time.time()
        status2, results2 = await connector.run_full_search(req2)
        dur2 = time.time() - t1
        print(f"Cycle 2 finished in {dur2:.2f}s. Status: {status2}, Quotes: {len(results2)}")
        spot2 = [r for r in results2 if "(SPOT)" in (r.vessel or "")]
        print(f"  Standard quotes: {len(results2) - len(spot2)}, Spot quotes: {len(spot2)}")
        for r in results2[:2]:
            print(f"  -> ETD: {r.etd} | Total: USD {r.final_freight_value} | Basic: USD {r.basic_ocean_freight} | Vessel: {r.vessel}")

        # Cycle 3: 20GP again (Should resolve instantly via accumulated cache)
        print("\n--- CYCLE 3: 20GP (Instant cache verification) ---")
        t2 = time.time()
        status3, results3 = await connector.run_full_search(req1)
        dur3 = time.time() - t2
        print(f"Cycle 3 resolved in {dur3:.2f}s (Cache). Status: {status3}, Quotes: {len(results3)}")

    finally:
        await connector.close()

if __name__ == "__main__":
    asyncio.run(test_caching())
