"""
Test Maersk connector with Haiphong -> Mersin, Turkey route.
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

from carriers.maersk_connector import MaerskConnector
from models.schemas import RateSearchRequest

# Load environment variables
load_dotenv()

# Clear proxy variables for local testing to use local residential IP
for key in ["MAERSK_PROXY_USER", "MAERSK_PROXY_PASS", "BRIGHTDATA_PROXY_USER", "BRIGHTDATA_PROXY_PASS", "BRIGHTDATA_PROXY_SERVER"]:
    os.environ[key] = ""

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


async def main():
    print("[TEST-MAERSK-HP-MER] Initializing Maersk Connector...")
    connector = MaerskConnector()

    request = RateSearchRequest(
        origin="Haiphong, Vietnam [VNHPH]",
        destination="Mersin, Turkey [TRMER]",
        container_type="DRY 40H",
        container_quantity=1,
        weight_per_container_kg=20000,
        commodity="FAK",
        departure_date="tomorrow",
        carriers=["MAERSK"]
    )

    print(f"[TEST-MAERSK-HP-MER] Running search: {request.origin} -> {request.destination}...")
    try:
        status, quotes = await connector.run_full_search(request)
        print(f"\n[TEST-MAERSK-HP-MER] Run status: {status}")
        print(f"[TEST-MAERSK-HP-MER] Total matching quotes returned: {len(quotes)}")

        # Take screenshot if page is still open
        try:
            os.makedirs(os.path.join(current_dir, "scratch"), exist_ok=True)
            screenshot_path = os.path.join(current_dir, "scratch", "maersk_haiphong_mersin.png")
            if connector.page and not connector.page.is_closed():
                await connector.page.screenshot(path=screenshot_path)
                print(f"[TEST-MAERSK-HP-MER] Screenshot saved to: {screenshot_path}")
        except Exception as e:
            print(f"[TEST-MAERSK-HP-MER] Screenshot error: {e}")

        # Print returned quotes
        for i, q in enumerate(quotes):
            print(f"\n--- Quote {i+1} ({q.container_type}) ---")
            print(f"Carrier: {q.carrier_name}")
            print(f"Origin -> Destination: {q.origin_port} -> {q.destination_port}")
            print(f"ETD: {q.etd} | ETA: {q.eta} | Transit Time: {q.transit_time} days")
            print(f"Vessel: {q.vessel_name}")
            print(f"Total Amount: {q.total_amount} {q.currency}")
            print(f"Ocean Freight: {q.ocean_freight} {q.currency}")
            if q.charges:
                print("Charges breakdown:")
                for ch in q.charges:
                    print(f"  - {ch.charge_name}: {ch.amount} {ch.currency} (category: {ch.category})")

        # Check instance cache for all container types
        cache_key = (request.origin, request.destination, request.departure_date)
        cached_result = connector._cached_quotes.get(cache_key)
        if cached_result:
            _, cached_all = cached_result
            print(f"\n[TEST-MAERSK-HP-MER] Total cached quotes across all container types: {len(cached_all)}")
            by_type = {}
            for q in cached_all:
                by_type.setdefault(q.container_type, []).append(q)
            for c_type, q_list in by_type.items():
                print(f"  Container Type: {c_type} -> {len(q_list)} quotes")

    finally:
        print("[TEST-MAERSK-HP-MER] Closing connector...")
        await connector.close()
        print("[TEST-MAERSK-HP-MER] Done.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[TEST-MAERSK-HP-MER] Aborted by user.")
