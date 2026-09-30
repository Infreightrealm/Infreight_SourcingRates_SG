"""
Test ONE connector with Taichung -> New York route.
"""
import asyncio
import sys
import os
import json
from dotenv import load_dotenv

# Ensure backend directory is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from carriers.one_connector import ONEConnector
from models.schemas import RateSearchRequest

# Load environment variables
load_dotenv()

# Clear proxy variables for local testing to use local residential IP
for key in ["ONE_PROXY_USER", "ONE_PROXY_PASS", "BRIGHTDATA_PROXY_USER", "BRIGHTDATA_PROXY_PASS", "BRIGHTDATA_PROXY_SERVER"]:
    os.environ[key] = ""

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


async def main():
    print("[TEST-ONE-TXG-NYC] Initializing ONE Connector...")
    connector = ONEConnector()

    request = RateSearchRequest(
        origin="Taichung [TWTXG]",
        destination="New York, NY [USNYC]",
        container_type="DRY 40H",
        container_quantity=1,
        weight_per_container_kg=20000,
        commodity="FAK",
        departure_date="tomorrow",
        carriers=["ONE"]
    )

    print(f"[TEST-ONE-TXG-NYC] Running search: {request.origin} -> {request.destination} for {request.container_type}...")
    try:
        status, quotes = await connector.run_full_search(request)
        print(f"\n[TEST-ONE-TXG-NYC] Run status: {status}")
        print(f"[TEST-ONE-TXG-NYC] Total matching quotes returned: {len(quotes)}")

        # Save screenshot if page is open
        try:
            os.makedirs(os.path.join(current_dir, "scratch"), exist_ok=True)
            screenshot_path = os.path.join(current_dir, "scratch", "one_taichung_newyork.png")
            if connector.page and not connector.page.is_closed():
                await connector.page.screenshot(path=screenshot_path)
                print(f"[TEST-ONE-TXG-NYC] Screenshot saved to: {screenshot_path}")
        except Exception as e:
            print(f"[TEST-ONE-TXG-NYC] Screenshot error: {e}")

        # Print returned quotes
        for i, q in enumerate(quotes):
            print(f"\n--- Quote {i+1} ({q.container_type}) ---")
            print(f"Vessel: {q.vessel} | Service: {q.service_name} | Routing: {q.routing}")
            print(f"ETD: {q.etd} | ETA: {q.eta} | Transit: {q.transit_time_days} days")
            print(f"Final Freight: {q.final_freight_value} {q.currency} (Basic OF: {q.basic_ocean_freight} {q.currency})")
            print(f"Free Time: {q.free_time} days (Demurrage: {q.demurrage}, Detention: {q.detention})")
            if q.included_freight_surcharges:
                print("Included surcharges:")
                for ch in q.included_freight_surcharges[:5]:
                    print(f"  - {ch.name}: {ch.amount} {ch.currency} (category: {ch.category})")

        # Check instance cache for all container types
        cache_key = (request.origin, request.destination, request.departure_date)
        cached_result = connector._cached_quotes.get(cache_key)
        if cached_result:
            _, cached_all = cached_result
            print(f"\n[TEST-ONE-TXG-NYC] Total cached quotes across all container types: {len(cached_all)}")
            by_type = {}
            for q in cached_all:
                by_type.setdefault(q.container_type, []).append(q)
            for c_type, q_list in by_type.items():
                print(f"  Container Type: {c_type} -> {len(q_list)} quotes")

    finally:
        print("[TEST-ONE-TXG-NYC] Closing connector...")
        await connector.close()
        print("[TEST-ONE-TXG-NYC] Done.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[TEST-ONE-TXG-NYC] Aborted by user.")
