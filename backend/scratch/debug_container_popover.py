import asyncio
import os
import sys
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
            
        # Dismiss modals
        print("Dismissing modals...")
        for _ in range(4):
            await connector._fs_dismiss_modals(page)
            await page.wait_for_timeout(500)
            
        # Fill ports
        print("Filling origin port...")
        await connector._fs_fill_port(page, "origin", "Singapore")
        print("Filling destination port...")
        await connector._fs_fill_port(page, "destination", "Keelung")
        await page.wait_for_timeout(1000)
        
        # Click container picker
        picker = page.locator('.cargo-input-wrap .input-container').first
        print("Clicking container picker...")
        await picker.click()
        await page.wait_for_timeout(2000)
        
        # Capture popover HTML specifically matching container text
        print("\n--- Dumping HTML structure of container rows inside Popover ---")
        popover_structure = await page.evaluate("""() => {
            const popovers = Array.from(document.querySelectorAll('.ant-popover'));
            const pop = popovers.find(p => p.textContent.includes('General') || p.textContent.includes('20GP'));
            if (!pop) return "Popover with container text not found";
            
            const rows = [];
            // Let's dump all children elements that contain inputs
            const allElements = pop.querySelectorAll('*');
            for (const el of allElements) {
                if (el.tagName === 'INPUT' || el.tagName === 'BUTTON') {
                    rows.push({
                        tag: el.tagName,
                        class: el.className,
                        id: el.id,
                        value: el.value || '',
                        html: el.outerHTML.substring(0, 300),
                        parent_text: (el.parentElement ? el.parentElement.textContent : '').trim()
                    });
                }
            }
            return {
                text: pop.innerText,
                html: pop.outerHTML.substring(0, 4000),
                inputs: rows
            };
        }""")
        
        if isinstance(popover_structure, str):
            print(popover_structure)
        else:
            print("Popover text content:")
            print(popover_structure['text'])
            print(f"\nFound {len(popover_structure['inputs'])} inputs/buttons inside container picker popover:")
            for idx, r in enumerate(popover_structure['inputs']):
                print(f"\nInput [{idx}] (Tag={r['tag']}, Class='{r['class']}', Value='{r['value']}'):")
                print(f"  Parent Text: '{r['parent_text']}'")
                print(f"  HTML: {r['html']}")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await connector.close()

if __name__ == "__main__":
    asyncio.run(main())
