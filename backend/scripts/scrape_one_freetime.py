import asyncio
import os
import json
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

COUNTRIES = [
    "MALAYSIA", "TAIWAN", "CHINA", "VIETNAM", "PAKISTAN", "INDIA",
    "SAUDI ARABIA", "UNITED ARAB EMIRATES", "OMAN", "EGYPT", "INDONESIA",
    "AUSTRALIA", "THAILAND", "CAMBODIA",
    # Additional common shipping origins
    "SINGAPORE", "HONG KONG", "KOREA REPUBLIC OF", "JAPAN", "PHILIPPINES"
]

COUNTRY_CODES = {
    "MALAYSIA": "MY", "TAIWAN": "TW", "CHINA": "CN", "VIETNAM": "VN",
    "PAKISTAN": "PK", "INDIA": "IN", "SAUDI ARABIA": "SA",
    "UNITED ARAB EMIRATES": "AE", "OMAN": "OM", "EGYPT": "EG",
    "INDONESIA": "ID", "AUSTRALIA": "AU", "THAILAND": "TH", "CAMBODIA": "KH",
    "SINGAPORE": "SG", "HONG KONG": "HK", "KOREA REPUBLIC OF": "KR",
    "JAPAN": "JP", "PHILIPPINES": "PH"
}

DESTINATIONS = ["ASIA", "NORTH AMERICA", "LATIN AMERICA", "EUROPE", "AFRICA"]

async def login(page):
    username = os.getenv("ONE_USER_ID", "brian@cslive.com.my")
    password = os.getenv("ONE_PASSWORD", "Edison@2409")
    print("[ONE Freetime] Logging in...")
    await page.goto("https://ecomm.one-line.com/one-ecom/login")
    await page.wait_for_timeout(2000)
    await page.fill('input[name="username"]', username)
    await page.fill('input[name="password"]', password)
    await page.click('button[type="submit"], button:has-text("Login")')
    await page.wait_for_timeout(5000)
    try:
        concurrent_btn = page.locator('button:has-text("Force Login"), button:has-text("Disconnect other session")')
        if await concurrent_btn.is_visible(timeout=2000):
            print("[ONE Freetime] Handling concurrent login popup...")
            await concurrent_btn.click()
            await page.wait_for_timeout(2000)
    except:
        pass
    print("[ONE Freetime] Logged in successfully.")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        await login(page)
        
        # Load existing cache to merge new values
        cache_path = os.path.join("backend", "data", "one_freetime.json")
        freetime_cache = {}
        if os.path.exists(cache_path):
            try:
                with open(cache_path, "r") as f:
                    freetime_cache = json.load(f)
                print(f"[ONE Freetime] Loaded existing cache with {len(freetime_cache)} countries.")
            except Exception as e:
                print(f"[ONE Freetime] Error loading cache: {e}")

        # Only target newly added countries to save time
        TARGET_COUNTRIES = ["SINGAPORE", "HONG KONG", "KOREA REPUBLIC OF", "JAPAN", "PHILIPPINES"]

        for country in TARGET_COUNTRIES:
            code = COUNTRY_CODES[country]
            if code not in freetime_cache:
                freetime_cache[code] = {}
            
            for dest in DESTINATIONS:
                try:
                    print(f"\n[ONE Freetime] Scraping Export Detention for {country} to {dest}...")
                    
                    await page.goto("https://ecomm.one-line.com/one-ecom/prices/basic-tariff", wait_until="domcontentloaded")
                    await page.wait_for_timeout(4000)
                    
                    # Close popup if it exists
                    try:
                        await page.locator('button:has-text("Skip")').click(timeout=2000)
                        await page.wait_for_timeout(500)
                    except:
                        pass

                    frame = page.frame_locator('iframe[src*="CUP_HOM_3701"]').first
                    
                    # 1. Country
                    await frame.locator('#cvrgCntNm').fill('')
                    await page.wait_for_timeout(200)
                    await frame.locator('#cvrgCntNm').press_sequentially(country, delay=100)
                    
                    try:
                        await frame.locator('.ui-autocomplete li.ui-menu-item:visible').first.click(timeout=3000)
                    except Exception as e:
                        print(f"      [!] Failed to click autocomplete for {country}: {e}")
                        
                    await page.wait_for_timeout(2000)
                    
                    # 2. Bound: Outbound
                    await frame.locator('#outbound').click(force=True)
                    await page.wait_for_timeout(500)
                    
                    # 3. Destination Continent
                    await frame.locator('#orgDestContiCd').select_option(label=dest)
                    await page.wait_for_timeout(500)
                    
                    # 4. Tariff Type
                    try:
                        await frame.locator('#dmdtTrfCd').select_option(value='DET', timeout=2000)
                    except:
                        print(f"      [!] Used Combined Tariff for {country} to {dest}")
                        await frame.locator('#dmdtTrfCd').select_option(value='DEMDET')
                    await page.wait_for_timeout(500)
                    
                    # 5. Container Type: Dry
                    await frame.locator('body').evaluate('''() => {
                        document.getElementById('R').checked = false;
                        document.getElementById('F').checked = false;
                        document.getElementById('O').checked = false;
                        document.getElementById('T').checked = false;
                        document.getElementById('D').checked = true;
                    }''')
                    
                    # 6. Cargo Type: General
                    await frame.locator('body').evaluate('''() => {
                        document.getElementById('DGR').checked = false;
                        document.getElementById('RFR').checked = false;
                        document.getElementById('AWK').checked = false;
                        document.getElementById('DRY').checked = true;
                    }''')
                    
                    # 7. Search
                    await frame.locator('#btnSearch').click(force=True)
                    print(f"[ONE Freetime] Clicked Search for {country} to {dest}. Waiting for results...")
                    
                    try:
                        await frame.locator('tr.jqgrow').first.wait_for(state="visible", timeout=10000)
                    except:
                        pass # Might be empty or timed out
                        
                    await page.wait_for_timeout(2000) # Give it an extra second just to be fully rendered
                    
                    # Take screenshot for debugging!
                    await page.screenshot(path=f"C:\\Users\\Brian\\.gemini\\antigravity\\brain\\2febadc4-254a-470f-9d04-a43202bfc8dc\\artifacts\\debug_{country}_{dest}.png", full_page=True)
                    print(f"      [Debug] Screenshot saved to debug_{country}_{dest}.png")
                    
                    # Extract data
                    freedays = None
                    rows = await frame.locator('tr.jqgrow').all()
                    
                    for row in rows:
                        cells = await row.locator('td').all()
                        cell_texts = [await c.text_content() for c in cells]
                        print(f"      [Debug] Row cells: {cell_texts}")
                        
                        if len(cells) > 5:
                            # Iterate through cells to find the first numeric value that looks like free days
                            # or just use the 6th or 7th column based on the dump
                            for idx, text in enumerate(cell_texts):
                                if "YES" in text or "NO" in text:
                                    # Free day is usually right before the YES/NO columns
                                    try:
                                        freedays_text = cell_texts[idx-1]
                                        import re
                                        m = re.search(r'\d+', freedays_text)
                                        if m:
                                            freedays = int(m.group())
                                            break
                                    except:
                                        pass
                                        
                            if freedays is not None:
                                break
                    
                    if freedays is not None:
                        print(f"[ONE Freetime] Found {freedays} days for {country} to {dest}")
                        freetime_cache[code][dest] = freedays
                    else:
                        print(f"[ONE Freetime] No freetime data found for {country} to {dest}")
                        freetime_cache[code][dest] = None
                        
                except Exception as e:
                    print(f"[ONE Freetime] Error on {country} to {dest}: {e}")
                    freetime_cache[code][dest] = None
                
        # Save to JSON
        cache_path = os.path.join("backend", "data", "one_freetime.json")
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, "w") as f:
            json.dump(freetime_cache, f, indent=4)
            
        print(f"\n[ONE Freetime] Finished! Cache saved to {cache_path}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
