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
        
        # Test targets
        targets = [
            (".cargo-input-wrap .placeholder-wrap", "placeholder-wrap"),
            (".cargo-input-wrap .input-container", "input-container"),
            (".cargo-input-wrap", "cargo-input-wrap"),
        ]
        
        for selector, name in targets:
            print(f"\n--- Testing click target: {name} ({selector}) ---")
            loc = page.locator(selector).first
            await loc.wait_for(state="visible", timeout=5000)
            await loc.click()
            await page.wait_for_timeout(1500)
            
            popover_visible = await page.evaluate("""() => {
                const pop = document.querySelector('.ant-popover:not(.ant-popover-hidden)');
                if (!pop) return false;
                // Check if it has container-related text
                return pop.textContent.includes('20GP') || pop.textContent.includes('40GP') || pop.textContent.includes('HQ');
            }""")
            
            print(f"Popover visible with container options: {popover_visible}")
            if popover_visible:
                # Save screenshot of successful state
                await page.screenshot(path=f"scratch/oocl_container_success_{name}.png")
                print(f"Saved successful screenshot to scratch/oocl_container_success_{name}.png")
                
                # Dump popover inner content
                inner_text = await page.evaluate("() => document.querySelector('.ant-popover:not(.ant-popover-hidden)').innerText")
                print(f"Popover text content:\n{inner_text}\n")
                
                # Close it using Escape so we can test next target
                await page.keyboard.press("Escape")
                await page.wait_for_timeout(500)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await connector.close()

if __name__ == "__main__":
    asyncio.run(main())
