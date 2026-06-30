"""
Verification script for ONE multi-container implementation.
"""
import asyncio
import sys
import os
import json
from dotenv import load_dotenv
from carriers.one_connector import ONEConnector
from models.schemas import RateSearchRequest

# Load environment variables
load_dotenv()

# Set credentials directly for testing
os.environ["ONE_USERNAME"] = "INFREIGHTSG"
os.environ["ONE_PASSWORD"] = "IFSGa2020"

# Clear proxy variables for local testing to use local residential IP
for key in ["ONE_PROXY_USER", "ONE_PROXY_PASS", "BRIGHTDATA_PROXY_USER", "BRIGHTDATA_PROXY_PASS", "BRIGHTDATA_PROXY_SERVER"]:
    os.environ[key] = ""

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


async def main():
    print("[TEST-ONE-MULTI] Initializing ONE Connector...")
    connector = ONEConnector()

    print("[TEST-ONE-MULTI] Running Singapore (SGSIN) -> Hamburg, Germany (DEHAM) search for DRY 40H...")

    # We request DRY 40H, but the search form will input all 3 dry sizes (DRY 20, DRY 40, DRY 40H)
    request = RateSearchRequest(
        origin="SGSIN",
        destination="DEHAM",
        container_type="DRY 40H",
        container_quantity=1,
        weight_per_container_kg=20000,
        commodity="Furniture",
        departure_date="tomorrow",
        carriers=["ONE"]
    )

    status, quotes = await connector.run_full_search(request)
    print(f"\n[TEST-ONE-MULTI] Run status: {status}")
    print(f"[TEST-ONE-MULTI] Total matching quotes returned: {len(quotes)}")

    # Print the returned DRY 40H quotes
    for i, q in enumerate(quotes):
        print(f"\nQuote {i} (DRY 40H):")
        print(json.dumps(q.dict(), indent=2, default=str))

    # Check instance cache to see all 3 container types
    print("\n[TEST-ONE-MULTI] Checking all cached split quotes:")
    cache_key = (request.origin, request.destination, request.departure_date)
    cached_all = connector._cached_quotes.get(cache_key, [])
    print(f"[TEST-ONE-MULTI] Total cached quotes (all sizes): {len(cached_all)}")

    by_type = {"DRY 20": [], "DRY 40": [], "DRY 40H": []}
    for q in cached_all:
        if q.container_type in by_type:
            by_type[q.container_type].append(q)

    for c_type, q_list in by_type.items():
        print(f"\n--- CONTAINER TYPE: {c_type} (Count: {len(q_list)}) ---")
        if q_list:
            # Print the first quote in detail as a sample
            print(f"Sample Quote for {c_type}:")
            print(json.dumps(q_list[0].dict(), indent=2, default=str))

    await connector.close()
    print("\n[TEST-ONE-MULTI] Done.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[TEST-ONE-MULTI] Aborted by user.")
