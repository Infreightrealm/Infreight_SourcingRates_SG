import asyncio
import os
import json
import re
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

COUNTRIES = [
    "MALAYSIA", "TAIWAN", "CHINA", "VIETNAM", "PAKISTAN", "INDIA",
    "SAUDI ARABIA", "UNITED ARAB EMIRATES", "OMAN", "EGYPT", "INDONESIA",
    "AUSTRALIA", "THAILAND", "CAMBODIA",
    "SINGAPORE", "HONG KONG", "KOREA REPUBLIC OF", "JAPAN", "PHILIPPINES",
    # Turkey & European Countries
    "TURKEY", "UNITED KINGDOM", "GERMANY", "NETHERLANDS", "BELGIUM",
    "FRANCE", "ITALY", "SPAIN", "PORTUGAL", "GREECE", "POLAND",
    "DENMARK", "NORWAY", "SWEDEN", "FINLAND", "IRELAND",
    "ALBANIA", "AUSTRIA", "BULGARIA", "CROATIA", "CYPRUS",
    "CZECH REPUBLIC", "ESTONIA", "HUNGARY", "LATVIA", "LITHUANIA",
    "MALTA", "ROMANIA", "SLOVAKIA", "SLOVENIA", "SWITZERLAND", "UKRAINE"
]

COUNTRY_CODES = {
    "MALAYSIA": "MY", "TAIWAN": "TW", "CHINA": "CN", "VIETNAM": "VN",
    "PAKISTAN": "PK", "INDIA": "IN", "SAUDI ARABIA": "SA",
    "UNITED ARAB EMIRATES": "AE", "OMAN": "OM", "EGYPT": "EG",
    "INDONESIA": "ID", "AUSTRALIA": "AU", "THAILAND": "TH", "CAMBODIA": "KH",
    "SINGAPORE": "SG", "HONG KONG": "HK", "KOREA REPUBLIC OF": "KR",
    "JAPAN": "JP", "PHILIPPINES": "PH",
    # Turkey & European Countries
    "TURKEY": "TR", "UNITED KINGDOM": "GB", "GERMANY": "DE", "NETHERLANDS": "NL",
    "BELGIUM": "BE", "FRANCE": "FR", "ITALY": "IT", "SPAIN": "ES",
    "PORTUGAL": "PT", "GREECE": "GR", "POLAND": "PL", "DENMARK": "DK",
    "NORWAY": "NO", "SWEDEN": "SE", "FINLAND": "FI", "IRELAND": "IE",
    "ALBANIA": "AL", "AUSTRIA": "AT", "BULGARIA": "BG", "CROATIA": "HR",
    "CYPRUS": "CY", "CZECH REPUBLIC": "CZ", "ESTONIA": "EE", "HUNGARY": "HU",
    "LATVIA": "LV", "LITHUANIA": "LT", "MALTA": "MT", "ROMANIA": "RO",
    "SLOVAKIA": "SK", "SLOVENIA": "SI", "SWITZERLAND": "CH", "UKRAINE": "UA"
}

ORIGINS = ["ASIA", "NORTH AMERICA", "LATIN AMERICA", "EUROPE", "AFRICA"]

async def check_and_wait_for_captcha(page, timeout_sec=90):
    captcha_selectors = [
        '.geetest_holder', '.geetest_panel', '[class*="captcha" i]', 
        'iframe[src*="captcha" i]', 'iframe[src*="cargosmart" i]',
        'text=/verify/i', 'text=/captcha/i'
    ]
    detected = False
    for selector in captcha_selectors:
        try:
            if await page.locator(selector).first.is_visible(timeout=1000):
                detected = True
                break
        except:
            pass
            
    if detected:
        print("\n⚠️ [ONE Freetime] CAPTCHA detected! Please solve the CAPTCHA in the browser window.")
        print(f"Waiting up to {timeout_sec} seconds for you to react and solve it...")
        # Check every 2 seconds if the captcha selector is still visible
        for elapsed in range(0, timeout_sec, 2):
            still_visible = False
            for selector in captcha_selectors:
                try:
                    if await page.locator(selector).first.is_visible(timeout=500):
                        still_visible = True
                        break
                except:
                    pass
            if not still_visible:
                print("[ONE Freetime] CAPTCHA cleared! Continuing...")
                return
            await asyncio.sleep(2)
        print("[ONE Freetime] Timeout waiting for CAPTCHA to be solved. Proceeding anyway.")

async def login(page):
    username = os.getenv("ONE_USER_ID", "brian@cslive.com.my")
    password = os.getenv("ONE_PASSWORD", "Edison@2409")
    print("[ONE Freetime] Logging in...")
    await page.goto("https://ecomm.one-line.com/one-ecom/login")
    await page.wait_for_timeout(2000)
    await page.fill('input[name="username"]', username)
    await page.fill('input[name="password"]', password)
    await page.click('button[type="submit"], button:has-text("Login")')
    
    # Check for login captcha here
    await check_and_wait_for_captcha(page, timeout_sec=90)
    
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
        is_prod = os.name != "nt"
        browser_env = os.environ.copy()
        if is_prod:
            browser_env["DISPLAY"] = ":105"
            
        browser = await p.chromium.launch(
            headless=False,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
            ],
            env=browser_env,
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            ignore_https_errors=True,
        )
        page = await context.new_page()
        page.set_default_timeout(30000)
        
        await login(page)
        
        # Load existing cache to merge new values
        script_dir = os.path.dirname(os.path.abspath(__file__))
        cache_path = os.path.abspath(os.path.join(script_dir, "..", "data", "one_freetime.json"))
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        freetime_cache = {}
        if os.path.exists(cache_path):
            try:
                with open(cache_path, "r") as f:
                    freetime_cache = json.load(f)
                print(f"[ONE Freetime] Loaded existing cache with {len(freetime_cache)} countries.")
            except Exception as e:
                print(f"[ONE Freetime] Error loading cache: {e}")

        # Target all countries for inbound free time lookup
        for country in COUNTRIES:
            code = COUNTRY_CODES[country]
            if code not in freetime_cache:
                freetime_cache[code] = {}
            
            for origin_continent in ORIGINS:
                if origin_continent in freetime_cache[code] and freetime_cache[code][origin_continent] is not None:
                    print(f"[ONE Freetime] Skipping {country} from {origin_continent} (already cached: {freetime_cache[code][origin_continent]} days)")
                    continue
                try:
                    print(f"\n[ONE Freetime] Scraping Import Demurrage/Detention for {country} from {origin_continent}...")
                    
                    await page.goto("https://ecomm.one-line.com/one-ecom/prices/basic-tariff", wait_until="domcontentloaded")
                    await page.wait_for_timeout(4000)
                    
                    # Close popup if it exists
                    try:
                        await page.locator('button:has-text("Skip")').click(timeout=2000)
                        await page.wait_for_timeout(500)
                    except:
                        pass

                    frame = page.frame_locator('iframe[src*="CUP_HOM_3701"]').first
                    
                    # 1. Country (destination)
                    await frame.locator('#cvrgCntNm').fill('')
                    await page.wait_for_timeout(200)
                    await frame.locator('#cvrgCntNm').press_sequentially(country, delay=100)
                    
                    try:
                        autocomplete_items = frame.locator('.ui-autocomplete li.ui-menu-item:visible')
                        await autocomplete_items.first.wait_for(state="visible", timeout=5000)
                        count = await autocomplete_items.count()
                        clicked = False
                        for i in range(count):
                            text = (await autocomplete_items.nth(i).inner_text()).strip().upper()
                            if text == country.upper() or text.startswith(country.upper() + ",") or text.startswith(country.upper() + " "):
                                await autocomplete_items.nth(i).click()
                                clicked = True
                                print(f"      [ONE Freetime] Clicked autocomplete match: '{text}'")
                                break
                        if not clicked:
                            first_text = (await autocomplete_items.first.inner_text()).strip()
                            await autocomplete_items.first.click()
                            print(f"      [ONE Freetime] Fallback clicked first autocomplete: '{first_text}'")
                    except Exception as e:
                        print(f"      [!] Failed to click autocomplete for {country}: {e}")
                        
                    # Handle any 'no data' or modal warning dialog that might have popped up
                    try:
                        dialog_close = frame.locator('.ui-dialog-titlebar-close, button:has-text("Close")').first
                        if await dialog_close.is_visible(timeout=1000):
                            await dialog_close.click()
                            print("      [!] Dismissed popup dialog.")
                    except:
                        pass

                    await page.wait_for_timeout(2000)
                    
                    # 2. Bound: Inbound
                    await frame.locator('#inbound').click(force=True)
                    await page.wait_for_timeout(1500) # Wait for bound change to trigger AJAX
                    
                    # 3. Origin Continent
                    await frame.locator('#orgDestContiCd').select_option(label=origin_continent)
                    await page.wait_for_timeout(1500) # Wait for origin continent change to trigger AJAX
                    
                    # 4. Tariff Type
                    selected_tariff = False
                    for val in ['DEMDET', 'DET', 'DEM']:
                        try:
                            await frame.locator('#dmdtTrfCd').select_option(value=val, timeout=2000)
                            print(f"      [ONE Freetime] Selected Tariff Type: {val}")
                            selected_tariff = True
                            break
                        except:
                            continue
                    if not selected_tariff:
                        print(f"      [!] Warning: Failed to select any tariff type for {country} from {origin_continent}")
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
                    print(f"[ONE Freetime] Clicked Search for {country} from {origin_continent}. Waiting for results...")
                    
                    # Check for search captcha here
                    await check_and_wait_for_captcha(page, timeout_sec=90)
                    
                    try:
                        await frame.locator('tr.jqgrow').first.wait_for(state="visible", timeout=10000)
                    except:
                        pass # Might be empty or timed out
                        
                    await page.wait_for_timeout(2000)
                    
                    # Extract data
                    freedays = None
                    rows = await frame.locator('tr.jqgrow').all()
                    
                    for row in rows:
                        cells = await row.locator('td').all()
                        cell_texts = [await c.text_content() for c in cells]
                        print(f"      [Debug] Row cells: {cell_texts}")
                        
                        if len(cells) > 5:
                            for idx, text in enumerate(cell_texts):
                                if "YES" in text or "NO" in text:
                                    try:
                                        freedays_text = cell_texts[idx-1]
                                        m = re.search(r'\d+', freedays_text)
                                        if m:
                                            freedays = int(m.group())
                                            break
                                    except:
                                        pass
                                        
                            if freedays is not None:
                                break
                    
                    if freedays is not None:
                        print(f"[ONE Freetime] Found {freedays} days for {country} from {origin_continent}")
                        freetime_cache[code][origin_continent] = freedays
                    else:
                        print(f"[ONE Freetime] No freetime data found for {country} from {origin_continent}")
                        freetime_cache[code][origin_continent] = None
                        
                    # Save progress iteratively in case of interruption
                    with open(cache_path, "w") as f:
                        json.dump(freetime_cache, f, indent=4)
                        
                except Exception as e:
                    print(f"[ONE Freetime] Error on {country} from {origin_continent}: {e}")
                    freetime_cache[code][origin_continent] = None
                
        print(f"\n[ONE Freetime] Finished! Cache saved to {cache_path}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
