import asyncio
import sys
import os
from dotenv import load_dotenv
from carriers.maersk_connector import MaerskConnector
from models.schemas import RateSearchRequest

# Load environment variables
load_dotenv()

# Clear proxy variables for local testing to use local residential IP
for key in ["MAERSK_PROXY_USER", "MAERSK_PROXY_PASS", "BRIGHTDATA_PROXY_USER", "BRIGHTDATA_PROXY_PASS", "BRIGHTDATA_PROXY_SERVER"]:
    os.environ[key] = ""

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

async def run_test():
    print("[TEST] Initializing Maersk Connector...")
    connector = MaerskConnector()
    
    print("[TEST] Logging in to Maersk...")
    logged_in = await connector.login()
    if not logged_in:
        print("[TEST] Login failed!")
        await connector.close()
        return
        
    print("[TEST] Logged in. Searching SGSIN (Singapore) to DEHAM (Hamburg)...")
    req = RateSearchRequest(
        origin="SGSIN",
        destination="DEHAM",
        container_type="DRY 40",
        quantity=1,
        cargo_weight=20000,
        commodity="Furniture",
        carriers=["Maersk"]
    )
    
    # We use search_quotes to fill in the locations and inspect the behavior
    status = await connector.search_quotes(req)
    print(f"[TEST] search_quotes status: {status}")
    
    if status:
        quotes = await connector.extract_quote_list()
        print(f"[TEST] Extracted {len(quotes)} quotes.")
        for i, q in enumerate(quotes[:3]):
            print(f"  [{i}] {q}")
    else:
        print("[TEST] Search failed or returned no results.")

    print("[TEST] Closing browser...")
    await connector.close()
    print("[TEST] Test done.")

if __name__ == "__main__":
    try:
        asyncio.run(run_test())
    except KeyboardInterrupt:
        print("\n[TEST] Aborted by user.")
