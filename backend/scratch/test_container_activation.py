import asyncio
import os
import sys
from dotenv import load_dotenv

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)
sys.path.append(os.path.dirname(backend_dir))

load_dotenv(os.path.join(backend_dir, ".env"))

from carriers.oocl_connector import OOCLConnector

async def main():
    connector = OOCLConnector()
    await connector._init_browser()
    page = await connector.context.new_page()
    
    try:
        print("Logging in...")
        if not await connector._fs_login(page):
            print("Login failed.")
            return
            
        print("Waiting for redirect to home page...")
        for _ in range(15):
            if "/ui" in (page.url or ""):
                break
            await page.wait_for_timeout(1000)
            
        if "/ui" not in (page.url or ""):
            await page.goto(connector.FS_HOME_URL, wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)
            
        # Dismiss modals
        print("Dismissing modals...")
        for _ in range(4):
            await connector._fs_dismiss_modals(page)
            await page.wait_for_timeout(500)
            
        # Fill ports
        print("Filling origin port...")
        await connector._fs_fill_port(page, "origin", "Singapore")
        print("Filling destination port...")
        await connector._fs_fill_port(page, "destination", "Keelung")
        
        # Test activation methods
        container_field = page.locator('.cargo-input-wrap .input-container').first
        await container_field.wait_for(state="visible", timeout=10000)
        
        async def check_popover():
            return await page.evaluate("""() => {
                const pop = document.querySelector('.ant-popover:not(.ant-popover-hidden)');
                return !!pop;
            }""")
            
        # Method 1: Focus and press Enter
        print("\n--- Method 1: Focus and press Enter ---")
        await container_field.focus()
        await page.wait_for_timeout(300)
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(1500)
        if await check_popover():
            print("Method 1 SUCCESS!")
            await page.screenshot(path="scratch/activation_method_1.png")
            await page.keyboard.press("Escape")
            await page.wait_for_timeout(500)
        else:
            print("Method 1 FAILED.")
            
        # Method 2: Focus and press Space
        print("\n--- Method 2: Focus and press Space ---")
        await container_field.focus()
        await page.wait_for_timeout(300)
        await page.keyboard.press("Space")
        await page.wait_for_timeout(1500)
        if await check_popover():
            print("Method 2 SUCCESS!")
            await page.screenshot(path="scratch/activation_method_2.png")
            await page.keyboard.press("Escape")
            await page.wait_for_timeout(500)
        else:
            print("Method 2 FAILED.")
            
        # Method 3: Forced click on input-container
        print("\n--- Method 3: Forced click on input-container ---")
        await container_field.click(force=True)
        await page.wait_for_timeout(1500)
        if await check_popover():
            print("Method 3 SUCCESS!")
            await page.screenshot(path="scratch/activation_method_3.png")
            await page.keyboard.press("Escape")
            await page.wait_for_timeout(500)
        else:
            print("Method 3 FAILED.")
            
        # Method 4: Click container-input-icon
        print("\n--- Method 4: Click container-input-icon ---")
        await page.locator('.cargo-input-wrap .container-input-icon').first.click()
        await page.wait_for_timeout(1500)
        if await check_popover():
            print("Method 4 SUCCESS!")
            await page.screenshot(path="scratch/activation_method_4.png")
            await page.keyboard.press("Escape")
            await page.wait_for_timeout(500)
        else:
            print("Method 4 FAILED.")
            
        # Method 5: Click parent span popover-wrap
        print("\n--- Method 5: Click parent span popover-wrap ---")
        await page.locator('.cargo-input-wrap .popover-wrap').first.click()
        await page.wait_for_timeout(1500)
        if await check_popover():
            print("Method 5 SUCCESS!")
            await page.screenshot(path="scratch/activation_method_5.png")
            await page.keyboard.press("Escape")
            await page.wait_for_timeout(500)
        else:
            print("Method 5 FAILED.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await connector.close()

if __name__ == "__main__":
    asyncio.run(main())
