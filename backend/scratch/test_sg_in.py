import asyncio
import sys
import os
from dotenv import load_dotenv

# Add backend directory to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from carriers.maersk_connector import MaerskConnector
from models.schemas import RateSearchRequest

# Load environment variables
load_dotenv()

# Windows Proactor Event Loop fix for Playwright
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

async def main():
    print("Initializing Maersk Connector...")
    connector = MaerskConnector()
    
    request = RateSearchRequest(
        origin="Singapore",
        destination="Port Klang",
        container_type="DRY 40H",
        container_quantity=1,
        weight_per_container_kg=10000,
        commodity="furniture",
        departure_date="tomorrow",
        carriers=["MAERSK"]
    )
    
    print("Running full search (which handles login and cookies automatically)...")
    status, quotes = await connector.run_full_search(request)
    print(f"\n==================================================")
    print(f"Search status: {status}")
    print(f"Extracted {len(quotes)} quotes:")
    for idx, q in enumerate(quotes):
        print(f"\n--- Quote {idx+1} ---")
        print(f"ETD: {q.etd}")
        print(f"ETA: {q.eta}")
        print(f"Transit Days: {q.transit_time_days}")
        print(f"Vessel: {q.vessel}")
        print(f"Service Name: {q.service_name}")
        print(f"Basic Ocean Freight: {q.basic_ocean_freight}")
        print(f"Final Freight Value: {q.final_freight_value}")
        print("Included Freight Surcharges:")
        for ch in q.included_freight_surcharges:
            print(f"  - {ch.name}: {ch.amount} {ch.currency} (Category: {ch.category}, Reason: {ch.reason})")
        print("Excluded Charges:")
        for ch in q.excluded_charges:
            print(f"  - {ch.name}: {ch.amount} {ch.currency} (Category: {ch.category}, Reason: {ch.reason})")
        print("Uncertain Charges:")
        for ch in q.uncertain_charges:
            print(f"  - {ch.name}: {ch.amount} {ch.currency} (Category: {ch.category}, Reason: {ch.reason})")
    print(f"==================================================\n")

    await connector.close()

if __name__ == "__main__":
    asyncio.run(main())
