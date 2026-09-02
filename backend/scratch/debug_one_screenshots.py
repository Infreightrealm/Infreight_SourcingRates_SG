import asyncio
import os
import sys

# Reconfigure stdout to UTF-8 to handle emojis under Windows cmd/powershell
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Ensure backend directory is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from carriers.one_connector import ONEConnector
from models.schemas import RateSearchRequest

async def run_debug():
    if not os.getenv("ONE_USERNAME"):
        os.environ["ONE_USERNAME"] = "INFREIGHTSG"
    if not os.getenv("ONE_PASSWORD"):
        os.environ["ONE_PASSWORD"] = "IFSGa2020"

    print("Initializing ONEConnector for visual debugging...")
    connector = ONEConnector()
    
    await connector._init_browser()
    
    # Target directory for artifacts
    artifact_dir = r"C:\Users\Brian\.gemini\antigravity\brain\2febadc4-254a-470f-9d04-a43202bfc8dc"
    
    try:
        print("[DEBUG] Navigating to login page...")
        await connector.page.goto(connector.LOGIN_URL, wait_until="domcontentloaded", timeout=30000)
        await connector.page.wait_for_timeout(2000)
        await connector.page.screenshot(path=os.path.join(artifact_dir, "one_01_login_page.png"))
        
        # Fill credentials
        username = os.getenv("ONE_USERNAME")
        password = os.getenv("ONE_PASSWORD")
        
        userId_sel = 'input[name="userId"], input[id="userId"], input[name="username"]'
        await connector.page.locator(userId_sel).first.fill(username)
        
        pwd_sel = 'input[name="password"], input[id="password"], input[type="password"]'
        await connector.page.locator(pwd_sel).first.fill(password)
        await connector.page.screenshot(path=os.path.join(artifact_dir, "one_02_credentials_filled.png"))
        
        # Click login
        submit_sel = 'button[type="submit"], button:has-text("Login"), button:has-text("Sign in")'
        await connector.page.locator(submit_sel).first.click()
        print("[DEBUG] Clicked login, waiting for navigation...")
        
        await connector.page.wait_for_url(lambda url: "login" not in url.lower() and "sign" not in url.lower(), timeout=15000)
        print(f"[DEBUG] Logged in successfully. URL: {connector.page.url}")
        await connector.page.wait_for_timeout(3000)
        await connector.page.screenshot(path=os.path.join(artifact_dir, "one_03_dashboard.png"))
        
        # Navigate to Quote URL
        print("[DEBUG] Navigating to Spot Rate page...")
        await connector.page.goto(connector.QUOTE_URL, wait_until="domcontentloaded", timeout=30000)
        await connector.page.wait_for_timeout(4000)
        await connector.page.screenshot(path=os.path.join(artifact_dir, "one_04_quote_page_loaded.png"))
        
        # Clear overlays
        await connector._clear_overlays()
        await connector.page.screenshot(path=os.path.join(artifact_dir, "one_04_after_skip.png"))
        
        # Step 1: Type Origin
        print("[DEBUG] Typing Origin...")
        origin_field = connector.page.locator('input[placeholder="Please search location"]').first
        await origin_field.wait_for(state="attached", timeout=15000)
        await origin_field.click(force=True)
        await connector.page.keyboard.type("SGSIN", delay=25)
        await connector.page.wait_for_timeout(1000)
        
        # Select from dropdown
        print("[DEBUG] Selecting Origin from dropdown...")
        origin_selected = await connector._select_dropdown_option("Origin", "SGSIN", "SGSIN")
        print(f"[DEBUG] Origin selected: {origin_selected}")
        await connector.page.screenshot(path=os.path.join(artifact_dir, "one_05_origin_selected.png"))
        
        # Step 2: Type Destination
        print("[DEBUG] Typing Destination...")
        destination_field = connector.page.locator('input[placeholder="Please search location"]').last
        await destination_field.wait_for(state="attached", timeout=15000)
        await destination_field.click(force=True)
        await connector.page.keyboard.type("SAJED", delay=25)
        await connector.page.wait_for_timeout(1000)
        
        # Select from dropdown
        print("[DEBUG] Selecting Destination from dropdown...")
        dest_selected = await connector._select_dropdown_option("Destination", "SAJED", "SAJED")
        print(f"[DEBUG] Destination selected: {dest_selected}")
        await connector.page.screenshot(path=os.path.join(artifact_dir, "one_06_destination_selected.png"))
        
        # Wait for Equipment Type dropdown to become enabled
        print("[DEBUG] Waiting for Equipment dropdown to become enabled...")
        await connector.page.wait_for_function(
            """() => {
                const el = document.querySelector('[role="combobox"][placeholder="Select an Equipment Type"], #downshift-0-input');
                return el && !el.disabled;
            }""",
            timeout=30000
        )
        print("[DEBUG] Equipment dropdown is enabled.")
        await connector.page.screenshot(path=os.path.join(artifact_dir, "one_07_equipment_enabled.png"))
        
        # Step 3: Equipment Type
        print("[DEBUG] Selecting Equipment Type...")
        equipment_field = connector.page.get_by_role("combobox", name="Select an Equipment Type").first
        await equipment_field.click()
        await connector.page.wait_for_timeout(1000)
        
        # Select DRY 40H
        eq_options = connector.page.locator('[role="option"]:visible')
        eq_count = await eq_options.count()
        print(f"[DEBUG] Visible options in Eq dropdown: {eq_count}")
        for i in range(eq_count):
            opt_text = await eq_options.nth(i).inner_text()
            print(f"  - Option {i}: '{opt_text}'")
            if "DRY 40H" in opt_text:
                await eq_options.nth(i).click()
                print(f"[DEBUG] Clicked eq option: {opt_text}")
                break
        await connector.page.wait_for_timeout(1000)
        await connector.page.screenshot(path=os.path.join(artifact_dir, "one_08_eq_selected.png"))
        
        # Quantity
        quantity_field = connector.page.locator('input[type="number"], input[aria-label*="quantity" i], input[name*="quantity" i], input[id*="quantity" i]').first
        await quantity_field.fill("1")
        
        # Cargo Weight
        weight_field = connector.page.locator('input[placeholder="0"], input[aria-label*="weight" i], input[name*="weight" i], input[id*="weight" i]').first
        await weight_field.fill("10000")
        await weight_field.press("Enter")
        await connector.page.wait_for_timeout(1000)
        await connector.page.screenshot(path=os.path.join(artifact_dir, "one_09_weight_quantity.png"))
        
        # Commodity
        print("[DEBUG] Setting commodity...")
        commodity_field = connector.page.get_by_role("combobox", name="Please input Commodity Name or HS code").first
        await commodity_field.click()
        await connector.page.wait_for_timeout(500)
        await connector.page.keyboard.type("Furniture", delay=25)
        await connector.page.wait_for_timeout(2000)
        
        try:
            first_option = connector.page.locator('[role="option"]').first
            await first_option.wait_for(state="visible", timeout=3000)
            await first_option.click()
            print("[DEBUG] Commodity suggestion clicked")
        except Exception:
            await connector.page.keyboard.press("Enter")
            print("[DEBUG] Commodity dropdown didn't appear, pressed Enter")
        await connector.page.wait_for_timeout(2000)
        await connector.page.screenshot(path=os.path.join(artifact_dir, "one_10_commodity_selected.png"))
        
        # Date Picker Section
        print("[DEBUG] Clicking on date picker...")
        date_field = connector.page.locator('text=/please select vessel departure date at origin/i').first
        try:
            await date_field.wait_for(state="visible", timeout=3000)
            await date_field.click(force=True)
        except Exception:
            date_field = connector.page.get_by_role("textbox", name="Please select vessel departure date at origin")
            await date_field.click(force=True)
            
        await connector.page.wait_for_timeout(3000)
        await connector.page.screenshot(path=os.path.join(artifact_dir, "one_11_calendar_opened.png"))
        
        # Strategy 2: Click first highlighted date with price
        price_locator = connector.page.locator('[class*="date-picker-date-highlight"], .react-datepicker__day--highlighted').first
        try:
            await price_locator.wait_for(state="visible", timeout=5000)
            await price_locator.click(force=True)
            print("[DEBUG] Selected date from calendar using highlighted price tile")
        except Exception as e:
            print(f"[DEBUG] Could not find highlighted price tile: {e}")
            # Try to click any active tile
            try:
                any_cell = connector.page.locator('.react-datepicker__day:not([class*="disabled"]):not([class*="outside"])').first
                await any_cell.click(force=True)
                print("[DEBUG] Selected first available non-disabled calendar day")
            except Exception as e2:
                print(f"[DEBUG] Failed to select any calendar day: {e2}")
                
        await connector.page.wait_for_timeout(2000)
        await connector.page.screenshot(path=os.path.join(artifact_dir, "one_12_date_selected.png"))
        
        # Submit quote search
        print("[DEBUG] Attempting to click GetQuote/Search button...")
        submit_btn = connector.page.locator('button:has-text("GetQuote"), button:has-text("Get Quote"), button:has-text("Search Rates"), button:has-text("View Quote"), button:has-text("view Quote"), button[type="submit"]').first
        await submit_btn.click(force=True)
        print("[DEBUG] Submit button clicked. Waiting for results page load...")
        
        # Wait up to 15 seconds
        for sec in range(15):
            await connector.page.wait_for_timeout(1000)
            print(f"[DEBUG] Waited {sec+1} seconds... URL: {connector.page.url}")
            # Take a screenshot to monitor loading progress
            if (sec + 1) % 3 == 0:
                await connector.page.screenshot(path=os.path.join(artifact_dir, f"one_13_loading_{sec+1}.png"))
                
        # Check final state
        print(f"[DEBUG] Final URL: {connector.page.url}")
        await connector.page.screenshot(path=os.path.join(artifact_dir, "one_14_final_results_page.png"))
        
        # Count quote cards
        quote_cards = connector.page.locator('div[class*="NewQuoteSummary_body-card"]')
        count = await quote_cards.count()
        print(f"[DEBUG] Found {count} quote cards on the final page.")
        
    except Exception as e:
        print(f"[DEBUG] FAILED with exception: {e}")
        await connector.page.screenshot(path=os.path.join(artifact_dir, "one_failed.png"))
        
    finally:
        await connector.close()

if __name__ == "__main__":
    asyncio.run(run_debug())
