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

    print("Initializing ONEConnector for Jeddah test...")
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
        
        # Type Destination (Jeddah SAJED)
        print("[DEBUG] Typing Destination 'SAJED'...")
        destination_field = connector.page.get_by_role("combobox", name="Please search location").nth(1)
        await destination_field.click()
        await connector.page.keyboard.type("SAJED", delay=25)
        await connector.page.wait_for_timeout(2000)
        await connector._select_dropdown_option("Destination", "SAJED", "SAJED")
        
        print("[DEBUG] Selected both ports! Waiting 8 seconds to see if loading modal appears and disappears...")
        await connector.page.wait_for_timeout(8000)
        await connector.page.screenshot(path=os.path.join(artifact_dir, "one_jd_1_modal_check.png"))
        
        # Check if modal is still present
        is_modal_present = await connector.page.evaluate("""() => {
            return !!document.querySelector('[class*="Modal_dialog"], [class*="CarouselLoadingPopup"]');
        }""")
        print(f"[DEBUG] Is modal still present: {is_modal_present}")
        
        if is_modal_present:
            print("[DEBUG] Stuck modal detected even for Jeddah! Injecting JS bypass...")
            await connector.page.evaluate("""() => {
                const selectors = [
                    '[class*="Modal_dialog"]',
                    '[class*="CarouselLoadingPopup"]',
                    '[class*="CommonModal"]',
                    '[id^="headlessui-dialog"]',
                    '.fixed.inset-0',
                    'div[class*="backdrop"]',
                    'div[role="presentation"]'
                ];
                selectors.forEach(sel => {
                    document.querySelectorAll(sel).forEach(el => {
                        if (el.tagName !== 'BODY' && el.tagName !== 'HTML') el.remove();
                    });
                });
                document.body.style.overflow = 'unset';
                document.body.style.position = 'static';
                document.documentElement.style.overflow = 'unset';
            }""")
            await connector.page.wait_for_timeout(2000)
            await connector.page.screenshot(path=os.path.join(artifact_dir, "one_jd_2_modal_bypassed.png"))
            
        # Select Equipment DRY 20
        print("[DEBUG] Selecting Equipment...")
        equipment_field = connector.page.get_by_role("combobox", name="Select an Equipment Type").first
        await equipment_field.click()
        await connector.page.wait_for_timeout(1000)
        
        eq_options = connector.page.locator('[role="option"]:visible')
        eq_count = await eq_options.count()
        print(f"[DEBUG] Eq options: {eq_count}")
        for i in range(eq_count):
            opt_text = await eq_options.nth(i).inner_text()
            if "DRY 20" in opt_text:
                await eq_options.nth(i).click()
                print(f"[DEBUG] Selected: {opt_text}")
                break
                
        await connector.page.wait_for_timeout(1000)
        
    except Exception as e:
        print(f"[DEBUG] FAILED with exception: {e}")
        await connector.page.screenshot(path=os.path.join(artifact_dir, "one_jd_failed.png"))
        
    finally:
        await connector.close()

if __name__ == "__main__":
    asyncio.run(run_debug())
