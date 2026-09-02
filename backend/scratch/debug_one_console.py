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

    print("Initializing ONEConnector with console monitoring...")
    connector = ONEConnector()
    await connector._init_browser()
    
    # Listen to console logs and errors
    def log_console(msg):
        if msg.type == "error":
            print(f"[CONSOLE ERROR] {msg.text}")
            if msg.location:
                print(f"                Location: {msg.location}")
        elif msg.type == "warning":
            print(f"[CONSOLE WARN] {msg.text}")
        else:
            # Only print logs that might be relevant (e.g. not random GA or analytics logs)
            text = msg.text
            if any(x in text.lower() for x in ["error", "fail", "route", "trip", "processing", "modal", "quote"]):
                print(f"[CONSOLE LOG] {text}")

    connector.page.on("console", log_console)
    
    # Also capture page errors (uncaught exceptions)
    def log_page_error(err):
        print(f"[PAGE EXCEPTION] {err}")
    connector.page.on("pageerror", log_page_error)
    
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
        
        # Wait 15 seconds to monitor console logs
        print("[DEBUG] Selected both ports! Let's wait 15 seconds and watch console...")
        await connector.page.wait_for_timeout(15000)
        
    except Exception as e:
        print(f"[DEBUG] FAILED with exception: {e}")
        
    finally:
        await connector.close()

if __name__ == "__main__":
    asyncio.run(run_debug())
