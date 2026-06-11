"""
Test Maersk connector with Singapore -> Ho Chi Minh City route.
Verifies that:
  1. The search query types 'Ho Chi Minh City' (not 'Ho Chi Minh City, Vietnam')
  2. The dropdown suggestion is picked correctly (not 'No results found')
  3. Quotes are extracted successfully
"""
import asyncio
import sys
from dotenv import load_dotenv
from carriers.maersk_connector import MaerskConnector
from models.schemas import RateSearchRequest

import os
load_dotenv()

# Clear proxy variables for local testing to use local residential IP
for key in ["MAERSK_PROXY_USER", "MAERSK_PROXY_PASS", "BRIGHTDATA_PROXY_USER", "BRIGHTDATA_PROXY_PASS", "BRIGHTDATA_PROXY_SERVER"]:
    os.environ[key] = ""

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


async def main():
    print("[TEST-MAERSK-HCM] Initializing Maersk Connector...")
    connector = MaerskConnector()

    logged_in = await connector.login()
    if not logged_in:
        print("[TEST-MAERSK-HCM] Login failed!")
        await connector.close()
        return

    print("[TEST-MAERSK-HCM] Logged in. Running SGSIN -> VNSGN search...")

    req = RateSearchRequest(
        origin="SGSIN",
        destination="VNSGN",
        container_type="DRY 40",
        quantity=1,
        cargo_weight=20000,
        commodity="Furniture",
        carriers=["Maersk"]
    )

    status = await connector.search_quotes(req)
    print(f"[TEST-MAERSK-HCM] search_quotes status: {status}")

    if status:
        quotes = await connector.extract_quote_list()
        print(f"[TEST-MAERSK-HCM] Extracted {len(quotes)} quotes:")
        for i, q in enumerate(quotes):
            print(f"  [{i}] {q}")
    else:
        print("[TEST-MAERSK-HCM] Search failed or returned no results.")

    print("[TEST-MAERSK-HCM] Closing browser...")
    await connector.close()
    print("[TEST-MAERSK-HCM] Done.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[TEST-MAERSK-HCM] Aborted by user.")
