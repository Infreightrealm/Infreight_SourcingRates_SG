import asyncio
import os
import sys
import json

# Ensure backend directory is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from carriers.one_connector import ONEConnector
from models.schemas import RateSearchRequest

async def run_debug():
    if not os.getenv("ONE_USERNAME"):
        os.environ["ONE_USERNAME"] = "INFREIGHTSG"
    if not os.getenv("ONE_PASSWORD"):
        os.environ["ONE_PASSWORD"] = "IFSGa2020"

    print("Initializing ONEConnector for network monitoring...")
    connector = ONEConnector()
    await connector._init_browser()
    
    # Listen to network responses
    async def log_response(response):
        url = response.url
        # Only log requests to one-line.com and skip static files
        if "one-line.com" in url and not any(x in url for x in [".js", ".css", ".png", ".jpg", ".svg", ".woff", "assets"]):
            try:
                status = response.status
                print(f"[NET] Response: {status} | {url}")
                # Try to get JSON or text content
                content_type = response.headers.get("content-type", "")
                if "json" in content_type:
                    try:
                        json_data = await response.json()
                        # Shorten the printed JSON to avoid huge logs
                        json_str = json.dumps(json_data)
                        if len(json_str) > 500:
                            json_str = json_str[:500] + "..."
                        print(f"      JSON: {json_str}")
                    except Exception as je:
                        pass
                elif "text" in content_type:
                    try:
                        text_data = await response.text()
                        if len(text_data) > 200:
                            text_data = text_data[:200] + "..."
                        print(f"      TEXT: {text_data}")
                    except:
                        pass
            except Exception as e:
                pass

    connector.page.on("response", log_response)
    
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
        
        # Wait 15 seconds to monitor the network requests while "Processing"
        print("[DEBUG] Selected both ports! Let's wait 15 seconds and watch network/API responses...")
        await connector.page.wait_for_timeout(15000)
        
        await connector.page.screenshot(path=os.path.join(artifact_dir, "one_network_debug.png"))
        
    except Exception as e:
        print(f"[DEBUG] FAILED with exception: {e}")
        
    finally:
        await connector.close()

if __name__ == "__main__":
    asyncio.run(run_debug())
