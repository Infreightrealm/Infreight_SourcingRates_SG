"""
Script to test your persistent Chrome-based Maersk connector login.
"""
import asyncio
import sys
from dotenv import load_dotenv
from carriers.maersk_connector import MaerskConnector

# Load environment variables
load_dotenv()

# Windows Proactor Event Loop fix for Playwright
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


async def main():
    print("[TEST-MAERSK] Initializing Maersk Connector...")
    connector = MaerskConnector()
    
    print("[TEST-MAERSK] Starting Login/Verification Flow...")
    success = await connector.login()
    
    if success:
        print("[TEST-MAERSK] ========================================================")
        print("[TEST-MAERSK] SUCCESS: Logged into Maersk Spot Portal successfully!")
        print("[TEST-MAERSK] Session and cookies saved inside your 'chrome_profile/'.")
        print("[TEST-MAERSK] The browser window will stay open for 10 minutes so you can inspect it.")
        print("[TEST-MAERSK] ========================================================")
        
        # Keep page active for inspection
        await asyncio.sleep(600)
    else:
        print("[TEST-MAERSK] FAILED: Login or Verification failed/timed out.")
        
    print("[TEST-MAERSK] Tearing down browser resources...")
    await connector.close()
    print("[TEST-MAERSK] Test finished.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[TEST-MAERSK] Aborted by user.")
