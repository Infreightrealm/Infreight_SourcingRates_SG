import asyncio
import os
import sys

# Ensure backend directory is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from carriers.one_connector import ONEConnector
from models.schemas import RateSearchRequest

async def run_debug():
    if not os.getenv("ONE_USERNAME"):
        os.environ["ONE_USERNAME"] = "INFREIGHTSG"
    if not os.getenv("ONE_PASSWORD"):
        os.environ["ONE_PASSWORD"] = "IFSGa2020"

    print("Initializing ONEConnector for bypass testing...")
    connector = ONEConnector()
    await connector._init_browser()
    
    artifact_dir = r"C:\Users\Brian\.gemini\antigravity\brain\2febadc4-254a-470f-9d04-a43202bfc8dc"
    
    try:
        print("[DEBUG] Logging in...")
        await connector.page.goto(connector.LOGIN_URL, wait_until="domcontentloaded", timeout=30000)
        await connector.page.wait_for_timeout(2000)
        
        username = os.getenv("ONE_USERNAME")
        password = os.getenv("ONE_PASSWORD")
        
        userId_sel = 'input[name="userId"], input[id="userId"], input[name="username"]'
        await connector.page.locator(userId_sel).first.fill(username)
        pwd_sel = 'input[name="password"], input[id="password"], input[type="password"]'
        await connector.page.locator(pwd_sel).first.fill(password)
        
        submit_sel = 'button[type="submit"], button:has-text("Login"), button:has-text("Sign in")'
        await connector.page.locator(submit_sel).first.click()
        
        await connector.page.wait_for_url(lambda url: "login" not in url.lower() and "sign" not in url.lower(), timeout=15000)
        print("[DEBUG] Logged in successfully.")
        await connector.page.wait_for_timeout(3000)
        
        print("[DEBUG] Navigating to Spot Rate page...")
        await connector.page.goto(connector.QUOTE_URL, wait_until="domcontentloaded", timeout=30000)
        await connector.page.wait_for_timeout(4000)
        
        # Type Origin
        print("[DEBUG] Typing Origin 'SGSIN'...")
        origin_field = connector.page.get_by_role("combobox", name="Please search location").nth(0)
        await origin_field.click()
        await connector.page.keyboard.type("SGSIN", delay=25)
        await connector.page.wait_for_timeout(2000)
        await connector._select_dropdown_option("Origin", "SGSIN", "SGSIN")
        await connector.page.wait_for_timeout(1500)
        
        # Type Destination
        print("[DEBUG] Typing Destination 'MYPKG'...")
        destination_field = connector.page.get_by_role("combobox", name="Please search location").nth(1)
        await destination_field.click()
        await connector.page.keyboard.type("MYPKG", delay=25)
        await connector.page.wait_for_timeout(2000)
        await connector._select_dropdown_option("Destination", "MYPKG", "MYPKG")
        
        print("[DEBUG] Selected both ports! Waiting for stuck modal to appear...")
        await connector.page.wait_for_timeout(4000)
        await connector.page.screenshot(path=os.path.join(artifact_dir, "one_bypass_1_modal_active.png"))
        
        # Inject bypass JS to remove the stuck modal and restore body scroll
        print("[DEBUG] Injecting JS bypass to remove stuck loading modal and backdrop...")
        await connector.page.evaluate("""() => {
            console.log("BYPASS INJECTED: Removing stuck modals/dialogs...");
            
            // Remove headlessui dialogs and common modal containers
            const selectors = [
                '[class*="Modal_dialog"]',
                '[class*="CarouselLoadingPopup"]',
                '[class*="CommonModal"]',
                '[id^="headlessui-dialog"]',
                '.fixed.inset-0', // backdrop
                'div[class*="backdrop"]',
                'div[class*="Backdrop"]',
                'div[role="presentation"]' // headlessui wrapper sometimes uses role="presentation"
            ];
            
            let count = 0;
            selectors.forEach(sel => {
                document.querySelectorAll(sel).forEach(el => {
                    // Check if it's actually a modal backdrop or dialog, not the main body layout
                    if (el.tagName !== 'BODY' && el.tagName !== 'HTML') {
                        el.remove();
                        count++;
                    }
                });
            });
            
            // Restore body scroll lock set by headlessui
            document.body.style.overflow = 'unset';
            document.body.style.position = 'static';
            document.body.style.width = 'auto';
            document.documentElement.style.overflow = 'unset';
            
            console.log(`BYPASS COMPLETE: Removed ${count} element(s). restored scrolling.`);
        }""")
        
        await connector.page.wait_for_timeout(2000)
        await connector.page.screenshot(path=os.path.join(artifact_dir, "one_bypass_2_modal_removed.png"))
        
        # Verify equipment dropdown is now enabled
        print("[DEBUG] Checking equipment dropdown status...")
        is_disabled = await connector.page.evaluate("""() => {
            const el = document.querySelector('[role="combobox"][placeholder="Select an Equipment Type"], #downshift-0-input');
            return el ? el.disabled : null;
        }""")
        print(f"[DEBUG] Equipment dropdown disabled status: {is_disabled}")
        
        # Try to select Equipment DRY 20
        print("[DEBUG] Selecting Equipment Type...")
        equipment_field = connector.page.get_by_role("combobox", name="Select an Equipment Type").first
        await equipment_field.click()
        await connector.page.wait_for_timeout(1000)
        await connector.page.screenshot(path=os.path.join(artifact_dir, "one_bypass_3_eq_dropdown.png"))
        
        eq_options = connector.page.locator('[role="option"]:visible')
        eq_count = await eq_options.count()
        print(f"[DEBUG] Eq dropdown options count: {eq_count}")
        for i in range(eq_count):
            opt_text = await eq_options.nth(i).inner_text()
            if "DRY 20" in opt_text:
                await eq_options.nth(i).click()
                print(f"[DEBUG] Selected: {opt_text}")
                break
                
        await connector.page.wait_for_timeout(1000)
        
        # Quantity
        print("[DEBUG] Filling Quantity...")
        quantity_field = connector.page.locator('input[type="number"], input[aria-label*="quantity" i], input[name*="quantity" i], input[id*="quantity" i]').first
        await quantity_field.fill("1")
        
        # Weight
        print("[DEBUG] Filling Cargo Weight...")
        weight_field = connector.page.locator('input[placeholder="0"], input[aria-label*="weight" i], input[name*="weight" i], input[id*="weight" i]').first
        await weight_field.fill("10000")
        await weight_field.press("Enter")
        await connector.page.wait_for_timeout(1000)
        
        # Commodity
        print("[DEBUG] Filling Commodity...")
        commodity_field = connector.page.get_by_role("combobox", name="Please input Commodity Name or HS code").first
        await commodity_field.click()
        await connector.page.wait_for_timeout(500)
        await connector.page.keyboard.type("Furniture", delay=25)
        await connector.page.wait_for_timeout(2000)
        
        try:
            first_option = connector.page.locator('[role="option"]').first
            await first_option.wait_for(state="visible", timeout=3000)
            await first_option.click()
            print("[DEBUG] Clicked commodity suggestion")
        except Exception:
            await connector.page.keyboard.press("Enter")
            print("[DEBUG] Commodity suggestion failed, pressed Enter")
            
        await connector.page.wait_for_timeout(2000)
        await connector.page.screenshot(path=os.path.join(artifact_dir, "one_bypass_4_commodity_filled.png"))
        
        # Date Picker Section
        print("[DEBUG] Opening date picker...")
        date_field = connector.page.locator('text=/please select vessel departure date at origin/i').first
        try:
            await date_field.wait_for(state="visible", timeout=3000)
            await date_field.click(force=True)
        except Exception:
            date_field = connector.page.get_by_role("textbox", name="Please select vessel departure date at origin")
            await date_field.click(force=True)
            
        await connector.page.wait_for_timeout(2000)
        await connector.page.screenshot(path=os.path.join(artifact_dir, "one_bypass_5_calendar_picker.png"))
        
        # Try to select the first highlighted cell or any cell inside the calendar
        # We wait for the calendar container first
        calendar_sel = 'div[class*="Calendar"], .react-calendar, [class*="calendar-picker"]'
        try:
            await connector.page.locator(calendar_sel).first.wait_for(state="visible", timeout=5000)
            print("[DEBUG] Calendar picker visible. Clicking first highlighted date...")
            # Click date
            price_locator = connector.page.locator('[class*="date-picker-date-highlight"], .react-datepicker__day--highlighted').first
            if await price_locator.is_visible():
                await price_locator.click(force=True)
                print("[DEBUG] Selected highlighted date")
            else:
                # Click any non-disabled tile
                any_tile = connector.page.locator('.react-calendar__tile:not([disabled]), [class*="Calendar"] button:not([disabled])').first
                await any_tile.click(force=True)
                print("[DEBUG] Selected first available tile")
        except Exception as ce:
            print(f"[DEBUG] Calendar element wait/click failed: {ce}")
            
        await connector.page.wait_for_timeout(2000)
        await connector.page.screenshot(path=os.path.join(artifact_dir, "one_bypass_6_date_selected.png"))
        
        # Submit Search
        print("[DEBUG] Clicking GetQuote...")
        submit_btn = connector.page.locator('button:has-text("GetQuote"), button:has-text("Get Quote"), button:has-text("Search Rates"), button:has-text("View Quote"), button:has-text("view Quote"), button[type="submit"]').first
        await submit_btn.click(force=True)
        
        print("[DEBUG] Waiting for results...")
        await connector.page.wait_for_timeout(5000)
        await connector.page.screenshot(path=os.path.join(artifact_dir, "one_bypass_7_results.png"))
        
        print(f"[DEBUG] Completed bypass test. Final URL: {connector.page.url}")
        
    except Exception as e:
        print(f"[DEBUG] FAILED with exception: {e}")
        await connector.page.screenshot(path=os.path.join(artifact_dir, "one_bypass_failed.png"))
        
    finally:
        await connector.close()

if __name__ == "__main__":
    asyncio.run(run_debug())
