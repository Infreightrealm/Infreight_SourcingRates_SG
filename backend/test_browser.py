"""
Script to test Playwright browser launching using your REAL Google Chrome
installation with a persistent local profile.
"""
import asyncio
import os
import sys
from playwright.async_api import async_playwright

# Fix for Windows: Use ProactorEventLoop for subprocess support (required for Playwright)
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


async def main():
    print("[TEST] Initializing Playwright...")
    async with async_playwright() as p:
        # Create a local profile directory inside the backend folder
        profile_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chrome_profile")
        print(f"[TEST] Using persistent Chrome profile at: {profile_dir}")
        
        print("[TEST] Launching YOUR local Google Chrome with persistent profile...")
        context = await p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            channel="chrome",  # Launches your actual installed Google Chrome browser!
            headless=False,
        )
        
        # In persistent context, one page is usually opened automatically
        page = context.pages[0] if context.pages else await context.new_page()
        
        target_url = "https://www.cma-cgm.com/ebusiness/pricing/instant-Quoting"
        print(f"[TEST] Navigating to: {target_url}")
     
            
        print("[TEST] ========================================================")
        print("[TEST] SUCCESS: Persistent Real Google Chrome launched!")
        print("[TEST] The window will stay open for testing.")
        print("[TEST] Any logins or cookies set will be remembered in 'chrome_profile/'!")
        print("[TEST] ========================================================")
        
        # Keep browser open for testing
        await asyncio.sleep(10000)
        
        print("[TEST] Closing browser...")
        await context.close()
        print("[TEST] Test finished successfully!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[TEST] Aborted by user.")
