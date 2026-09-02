import asyncio
import sys
import os
from dotenv import load_dotenv
from carriers.maersk_connector import MaerskConnector
from models.schemas import RateSearchRequest

load_dotenv()

# Clear proxy
for key in ["MAERSK_PROXY_USER", "MAERSK_PROXY_PASS", "BRIGHTDATA_PROXY_USER", "BRIGHTDATA_PROXY_PASS", "BRIGHTDATA_PROXY_SERVER"]:
    os.environ[key] = ""

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

async def main():
    connector = MaerskConnector()
    success = await connector.login()
    if not success:
        print("Login failed!")
        return

    # Navigate to booking page
    await connector.page.goto(connector.QUOTE_URL, wait_until="domcontentloaded")
    await connector.page.wait_for_timeout(3000)

    # Let's type SGSIN -> VNSGN first to enable commodity
    # Fill Origin
    origin_field = connector.page.locator('input[placeholder*="Enter city or port" i]').first
    await origin_field.click()
    await origin_field.fill("Singapore")
    await connector.page.wait_for_timeout(2000)
    
    # Click suggestion
    await connector.page.locator('mc-option[role="option"]').first.click()
    await connector.page.wait_for_timeout(1000)

    # Fill Dest
    dest_field = connector.page.locator('input[placeholder*="Enter city or port" i]').nth(1)
    await dest_field.click()
    await dest_field.fill("Ho Chi Minh")
    await connector.page.wait_for_timeout(2000)
    
    # Click suggestion
    await connector.page.locator('mc-option[role="option"]').nth(1).click()
    await connector.page.wait_for_timeout(2000)

    # Click commodity field
    commodity_field = connector.page.locator('input[placeholder*="minimum 2 characters" i], input[placeholder*="Commodity" i], [class*="commodity" i] input').first
    await commodity_field.click()
    await commodity_field.fill("")
    
    # Try typing "FAK"
    print("Typing FAK...")
    await commodity_field.type("FAK", delay=100)
    await connector.page.wait_for_timeout(2000)
    
    # Take screenshot of suggestions
    await connector.page.screenshot(path="maersk_commodity_fak.png")
    print("Saved maersk_commodity_fak.png")

    # Try typing "Freight"
    await commodity_field.click()
    await connector.page.keyboard.press("Control+A")
    await connector.page.keyboard.press("Backspace")
    print("Typing Freight...")
    await commodity_field.type("Freight", delay=100)
    await connector.page.wait_for_timeout(2000)
    await connector.page.screenshot(path="maersk_commodity_freight.png")
    print("Saved maersk_commodity_freight.png")

    await connector.close()

if __name__ == "__main__":
    asyncio.run(main())
