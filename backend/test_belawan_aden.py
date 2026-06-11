"""
Test script to run Belawan (IDBLW) -> Aden (YEADE) route on Maersk and MSC.
"""
import asyncio
import sys
import os
from dotenv import load_dotenv
from models.schemas import RateSearchRequest
from carriers.maersk_connector import MaerskConnector
from carriers.msc_connector import MSCConnector

load_dotenv()

# Clear proxy variables for local testing to use local residential IP
for key in ["MAERSK_PROXY_USER", "MAERSK_PROXY_PASS", "BRIGHTDATA_PROXY_USER", "BRIGHTDATA_PROXY_PASS", "BRIGHTDATA_PROXY_SERVER"]:
    os.environ[key] = ""

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


async def test_maersk():
    print("\n=== TESTING MAERSK CONNECTOR ===")
    connector = MaerskConnector()
    try:
        logged_in = await connector.login()
        if not logged_in:
            print("[MAERSK] Login failed!")
            return

        req = RateSearchRequest(
            origin="IDBLW",
            destination="YEADE",
            container_type="DRY 40",
            quantity=1,
            cargo_weight=20000,
            commodity="Furniture",
            carriers=["Maersk"]
        )

        status = await connector.search_quotes(req)
        print(f"[MAERSK] search_quotes status: {status}")
        
        # Take a final screenshot to visually confirm success/status
        await connector.page.screenshot(path="maersk_belawan_aden_final.png")
        print("[MAERSK] Saved final screenshot to maersk_belawan_aden_final.png")
    except Exception as e:
        print(f"[MAERSK] Test crashed: {e}")
    finally:
        await connector.close()


async def test_msc():
    print("\n=== TESTING MSC CONNECTOR ===")
    connector = MSCConnector()
    try:
        req = RateSearchRequest(
            origin="IDBLW",
            destination="YEADE",
            container_type="DRY 40",
            quantity=1,
            cargo_weight=20000,
            commodity="Furniture",
            carriers=["MSC"]
        )

        status, quotes = await connector.run_full_search(req)
        print(f"[MSC] run_full_search status: {status}")
        print(f"[MSC] Extracted {len(quotes)} quote(s)")
    except Exception as e:
        print(f"[MSC] Test crashed: {e}")
    finally:
        await connector.close()


async def main():
    # Run Maersk
    await test_maersk()
    
    # Run MSC
    await test_msc()


if __name__ == "__main__":
    asyncio.run(main())
