import asyncio
import os
from playwright.async_api import async_playwright
from carriers.greenx_connector import GreenXConnector
from services.port_manager import resolve_port_for_carrier

async def inspect():
    connector = GreenXConnector()
    await connector._init_browser()
    try:
        # Navigate to login
        print("Navigating to login...")
        await connector.page.goto(connector.LOGIN_URL, wait_until="domcontentloaded")
        await connector.page.wait_for_timeout(2000)
        await connector._clear_cookie_overlay()
        
        # Fill credentials
        username = os.getenv("GREENX_USERNAME", "INFREIGHT.SG@IN-FREIGHT.COM")
        password = os.getenv("GREENX_PASSWORD", "InfreightSGa2026")
        await connector.page.locator('input[type="email"]').first.fill(username)
        await connector.page.locator('input[type="password"]').first.fill(password)
        await connector.page.locator('button[type="submit"]').first.click()
        await connector.page.wait_for_timeout(5000)
        await connector._clear_cookie_overlay()
        
        # Navigate to quotes
        current_url = connector.page.url
        if "tabkey=" in current_url:
            tabkey = current_url.split("tabkey=")[1].split("&")[0]
            target_url = f"https://www.greenxtrade.com/_gx/GREENX_Quotes?tabkey={tabkey}"
            await connector.page.goto(target_url, wait_until="domcontentloaded")
        else:
            print("Failed to get tabkey from URL")
            return
            
        await connector.page.wait_for_timeout(3000)
        await connector._clear_cookie_overlay()
        
        # Type Singapore into Origin input
        origin_input = connector.page.locator('input[placeholder*="ORIGIN" i]').first
        await origin_input.click()
        await origin_input.fill("Singapore")
        await connector.page.wait_for_timeout(3000)
        
        # Find suggestions list container and capture its HTML
        # Usually it is a ul, a div with class containing autocomplete/dropdown/suggestions
        containers = await connector.page.locator('ul, [class*="dropdown" i], [class*="autocomplete" i], [class*="suggestions" i], [class*="menu" i]').all()
        print(f"Found {len(containers)} potential suggestion containers.")
        for idx, container in enumerate(containers):
            if await container.is_visible():
                html = await container.outer_html()
                # Print class and snippet of HTML
                cls = await container.get_attribute("class")
                text = await container.text_content()
                print(f"Container {idx} - Class: '{cls}', Text: '{text.strip()}'")
                with open(f"container_{idx}.html", "w", encoding="utf-8") as f:
                    f.write(html)
                print(f"Saved Container {idx} HTML to container_{idx}.html")
                
    finally:
        await connector.close()

if __name__ == "__main__":
    asyncio.run(inspect())
