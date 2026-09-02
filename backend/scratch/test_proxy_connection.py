import asyncio
import os
import sys
from playwright.async_api import async_playwright
from dotenv import load_dotenv

# Load env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

# Windows fix
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

async def test_proxy(port):
    print(f"\n=== TESTING PROXY PORT: {port} ===")
    proxy_user = os.getenv("MAERSK_PROXY_USER") or os.getenv("BRIGHTDATA_PROXY_USER")
    proxy_pass = os.getenv("MAERSK_PROXY_PASS") or os.getenv("BRIGHTDATA_PROXY_PASS")
    
    if not proxy_user or not proxy_pass:
        print("Error: Credentials not found in .env!")
        return
        
    proxy_server = f"http://brd.superproxy.io:{port}"
    print(f"Proxy server: {proxy_server}")
    print(f"Username: {proxy_user}")
    
    async with async_playwright() as p:
        profile_dir = os.path.join(os.path.dirname(__file__), f"test_profile_{port}")
        
        launch_kwargs = {
            "user_data_dir": profile_dir,
            "headless": False,
            "channel": "chrome",
            "ignore_https_errors": True,
            "proxy": {
                "server": proxy_server,
                "username": proxy_user,
                "password": proxy_pass,
            }
        }
        
        try:
            print("Launching browser...")
            context = await p.chromium.launch_persistent_context(**launch_kwargs)
            page = context.pages[0] if context.pages else await context.new_page()
            page.set_default_timeout(20000)
            
            print("Navigating to https://www.maersk.com/login ...")
            await page.goto("https://www.maersk.com/login", wait_until="load")
            print(f"Landed on: {page.url}")
            
            # Let's wait a few seconds and print the title
            await page.wait_for_timeout(3000)
            title = await page.title()
            print(f"Page Title: {title}")
            
            # Check for 403 / Akamai blocks
            content = await page.content()
            if "Forbidden" in content or "Access Denied" in content or "something went wrong" in content.lower():
                print("FAILED: Page loaded but content contains bot block indicators!")
            else:
                print("SUCCESS: Logged in or rendered page successfully!")
                
            await context.close()
        except Exception as e:
            print(f"FAILED with error: {e}")

async def main():
    # Test port 22225 first
    await test_proxy(22225)
    # Test port 33335 second
    await test_proxy(33335)

if __name__ == "__main__":
    asyncio.run(main())
