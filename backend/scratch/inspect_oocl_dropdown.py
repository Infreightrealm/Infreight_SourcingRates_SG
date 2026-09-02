import asyncio
import os
import sys
import re
from dotenv import load_dotenv

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)
sys.path.append(os.path.dirname(backend_dir))

load_dotenv(os.path.join(backend_dir, ".env"))

from carriers.oocl_connector import OOCLConnector

async def main():
    connector = OOCLConnector()
    await connector._init_browser()
    page = await connector.context.new_page()
    
    try:
        print("Logging in...")
        if not await connector._fs_login(page):
            print("Login failed.")
            return
            
        print("Waiting for redirect to home page...")
        for _ in range(15):
            if "/ui" in (page.url or ""):
                break
            await page.wait_for_timeout(1000)
            
        if "/ui" not in (page.url or ""):
            await page.goto(connector.FS_HOME_URL, wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)
            
        # Dismiss modals multiple times to ensure they are completely gone
        print("Dismissing modals...")
        for _ in range(5):
            await connector._fs_dismiss_modals(page)
            await page.wait_for_timeout(500)
            
        # Click the port input and type
        field = page.locator('input[placeholder*="Port or Door" i]').first
        await field.wait_for(state="visible", timeout=15000)
        
        print("Clicking and typing 'Singapore' into origin field...")
        await field.click()
        await field.fill("")
        await field.type("Singapore", delay=100)
        
        print("Waiting 3 seconds for suggestions dropdown to show...")
        await page.wait_for_timeout(3000)
        
        # Take a screenshot
        os.makedirs("scratch", exist_ok=True)
        await page.screenshot(path="scratch/oocl_singapore_typed.png")
        print("Saved screenshot to scratch/oocl_singapore_typed.png")
        
        # Read input value
        val = await field.input_value()
        print(f"Typed value in input field: '{val}'")
        
        # Dump all elements on page to inspect class/attributes
        print("Dumping all elements containing 'Singapore' in text...")
        elements_info = await page.evaluate("""() => {
            const results = [];
            const all = document.querySelectorAll('*');
            for (const el of all) {
                const text = (el.textContent || '').trim();
                const cls = el.className || '';
                if (text.toLowerCase().includes('singapore')) {
                    if (el.children.length <= 2 && text.length < 150) {
                        results.push({
                            tag: el.tagName,
                            class: cls,
                            role: el.getAttribute('role'),
                            text: text,
                            html: el.outerHTML.substring(0, 300)
                        });
                    }
                }
            }
            return results;
        }""")
        
        print(f"Found {len(elements_info)} elements containing 'Singapore':")
        for idx, el in enumerate(elements_info):
            print(f"[{idx}] Tag: {el['tag']}, Class: '{el['class']}', Role: '{el['role']}', Text: '{el['text']}'")
            print(f"    HTML: {el['html']}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await connector.close()

if __name__ == "__main__":
    asyncio.run(main())
