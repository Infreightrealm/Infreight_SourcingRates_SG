import asyncio
import os
import sys
from dotenv import load_dotenv

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

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
            
        print("Navigating to home page...")
        if "/ui" not in (page.url or ""):
            await page.goto(connector.FS_HOME_URL, wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)
            
        for _ in range(5):
            await connector._fs_dismiss_modals(page)
            await page.wait_for_timeout(300)
            
        field = page.locator('input[placeholder*="Port or Door" i]').first
        await field.wait_for(state="visible", timeout=15000)
        
        print("Clicking and typing 'Port Klang'...")
        await field.click()
        await field.fill("")
        await field.type("Port Klang", delay=100)
        
        await page.wait_for_timeout(2500)
        
        os.makedirs("scratch", exist_ok=True)
        await page.screenshot(path="scratch/oocl_port_klang_dropdown.png")
        print("Saved screenshot to scratch/oocl_port_klang_dropdown.png")
        
        # Inspect all visible overlays and dropdown elements
        print("\n--- Inspecting Dropdowns ---")
        overlays_info = await page.evaluate("""() => {
            const results = [];
            const dropdowns = document.querySelectorAll('.ant-select-dropdown, .ant-popover, [role="listbox"], [class*="dropdown" i], [class*="popover" i]');
            dropdowns.forEach((dd, ddIdx) => {
                const items = [];
                const allDescendants = dd.querySelectorAll('*');
                allDescendants.forEach((el) => {
                    const text = (el.innerText || el.textContent || '').trim();
                    if (text && el.children.length === 0) {
                        items.push({
                            tag: el.tagName,
                            class: el.className,
                            role: el.getAttribute('role'),
                            text: text
                        });
                    }
                });
                results.push({
                    index: ddIdx,
                    tag: dd.tagName,
                    class: dd.className,
                    htmlSnippet: dd.outerHTML.substring(0, 400),
                    itemsCount: items.length,
                    items: items
                });
            });
            return results;
        }""")
        
        for ov in overlays_info:
            print(f"\nOverlay #{ov['index']}: Tag={ov['tag']}, Class='{ov['class']}'")
            print(f"HTML snippet: {ov['htmlSnippet']}")
            print(f"Leaf items ({ov['itemsCount']}):")
            for it in ov['items']:
                print(f"  [{it['tag']}] class='{it['class']}' text='{it['text']}'")
                
    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        await connector.close()

if __name__ == "__main__":
    asyncio.run(main())
