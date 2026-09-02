import os
import asyncio
from playwright.async_api import async_playwright

async def run_diagnose():
    from dotenv import load_dotenv
    load_dotenv()
    
    username = os.getenv("ONE_USERNAME")
    password = os.getenv("ONE_PASSWORD")
    if not username or not password:
        print("[ERROR] Credentials not found.")
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        print("[DIAG] Navigating to login...")
        await page.goto("https://ecomm.one-line.com/ecom/CUP_HOM_3116.do")
        await page.wait_for_timeout(2000)
        
        # simplified login
        try:
            await page.fill('input[name="usrId"]', username)
            await page.fill('input[name="usrPwd"]', password)
            await page.click('#btn1')
            await page.wait_for_load_state('networkidle')
            print("[DIAG] Logged in")
        except Exception as e:
            print(f"[DIAG] Login failed: {e}")
            await browser.close()
            return
            
        print("[DIAG] Navigating to Quote booking...")
        await page.goto("https://ecomm.one-line.com/one-ecom/prices/one-quote-booking")
        await page.wait_for_load_state('networkidle')
        await page.wait_for_timeout(3000)
        
        # Origin and Destination (to trigger the rest of the form)
        print("[DIAG] Filling Origin and Destination...")
        await page.fill('input[name="origin"]', "SGSIN")
        await page.wait_for_timeout(1000)
        await page.keyboard.press("ArrowDown")
        await page.keyboard.press("Enter")
        
        await page.fill('input[name="destination"]', "EGALY")
        await page.wait_for_timeout(1000)
        await page.keyboard.press("ArrowDown")
        await page.keyboard.press("Enter")
        
        print("[DIAG] Waiting for Commodity...")
        await page.wait_for_timeout(2000)
        
        # Take a screenshot before filling commodity
        await page.screenshot(path="scratch/one_commodity_before.png", full_page=True)
        
        try:
            commodity_field = page.get_by_role("combobox", name="Please input Commodity Name or HS code").first
            await commodity_field.click()
            await page.keyboard.type("Furniture", delay=50)
            
            print("[DIAG] Typed Furniture. Waiting 3s for dropdown...")
            await page.wait_for_timeout(3000)
            
            await page.screenshot(path="scratch/one_commodity_dropdown.png", full_page=True)
            
            # Print HTML of the listbox if exists
            html = await page.evaluate('''() => {
                const lb = document.querySelector('[role="listbox"]');
                return lb ? lb.outerHTML : "No listbox found";
            }''')
            print("[DIAG] Listbox HTML:")
            print(html)
            
        except Exception as e:
            print(f"[DIAG] Error during commodity: {e}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_diagnose())
