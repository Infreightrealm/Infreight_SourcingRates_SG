import asyncio
import os
import sys
from carriers.greenx_connector import GreenXConnector

# Set credentials if not already in env
if not os.getenv("GREENX_USERNAME"):
    os.environ["GREENX_USERNAME"] = "INFREIGHT.SG@IN-FREIGHT.COM"
if not os.getenv("GREENX_PASSWORD"):
    os.environ["GREENX_PASSWORD"] = "InfreightSGa2026"

async def test():
    connector = GreenXConnector()
    print("Logging in...")
    await connector.login()
    
    # Extract tabkey from URL
    current_url = connector.page.url
    print(f"Current URL: {current_url}")
    if "tabkey=" in current_url:
        tabkey = current_url.split("tabkey=")[1].split("&")[0]
        target_url = f"https://www.greenxtrade.com/_gx/GREENX_Quotes?tabkey={tabkey}"
        print(f"Navigating to Quotes tab directly: {target_url}")
        await connector.page.goto(target_url, wait_until="domcontentloaded", timeout=45000)
    else:
        print("tabkey not found, trying tab link click...")
        # Try click tab
        await connector._click_detail_tab(connector.page, "Quotes")
        
    await connector.page.wait_for_timeout(3000)
    await connector._clear_cookie_overlay()

    # 1. Query "Singapore" in Origin
    origin_selectors = [
        'input[placeholder*="ORIGIN" i]',
        'input[id*="origin" i]',
        'input[name*="origin" i]',
        'xpath=//label[contains(text(),"ORIGIN")]/following::input[1]'
    ]
    origin_input = None
    for sel in origin_selectors:
        try:
            loc = connector.page.locator(sel).first
            if await loc.is_visible():
                origin_input = loc
                break
        except:
            continue

    if origin_input:
        print("Found Origin input, typing 'Singapore'...")
        await origin_input.click()
        await origin_input.press("Control+A")
        await origin_input.press("Backspace")
        await origin_input.type("Singapore", delay=100)
        await connector.page.wait_for_timeout(3000)
        
        # Capture screenshot of dropdown
        await connector.page.screenshot(path="origin_suggestions.png")
        print("Saved origin_suggestions.png")
        
        # Get list items
        items = await connector.page.locator('ul li, [role="option"], [class*="dropdown" i] li, [class*="item" i]').all()
        print(f"Found {len(items)} suggestion elements for Origin:")
        for idx, item in enumerate(items):
            try:
                if await item.is_visible():
                    txt = await item.text_content()
                    print(f"  [{idx}] : {repr(txt.strip())}")
            except Exception as e:
                print(f"  [{idx}] Error getting text: {e}")
    else:
        print("Origin input not found")

    # 2. Query "Hamburg" in Destination
    dest_selectors = [
        'input[placeholder*="DESTINATION" i]',
        'input[id*="destination" i]',
        'input[name*="destination" i]',
        'xpath=//label[contains(text(),"DESTINATION")]/following::input[1]'
    ]
    dest_input = None
    for sel in dest_selectors:
        try:
            loc = connector.page.locator(sel).first
            if await loc.is_visible():
                dest_input = loc
                break
        except:
            continue

    if dest_input:
        print("\nFound Destination input, typing 'Hamburg'...")
        await dest_input.click()
        await dest_input.press("Control+A")
        await dest_input.press("Backspace")
        await dest_input.type("Hamburg", delay=100)
        await connector.page.wait_for_timeout(3000)
        
        # Capture screenshot of dropdown
        await connector.page.screenshot(path="dest_suggestions.png")
        print("Saved dest_suggestions.png")
        
        # Get list items
        items = await connector.page.locator('ul li, [role="option"], [class*="dropdown" i] li, [class*="item" i]').all()
        print(f"Found {len(items)} suggestion elements for Destination:")
        for idx, item in enumerate(items):
            try:
                if await item.is_visible():
                    txt = await item.text_content()
                    print(f"  [{idx}] : {repr(txt.strip())}")
            except Exception as e:
                print(f"  [{idx}] Error: {e}")
    else:
        print("Destination input not found")

    await connector.close()

if __name__ == "__main__":
    asyncio.run(test())
