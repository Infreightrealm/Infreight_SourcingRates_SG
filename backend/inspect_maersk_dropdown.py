"""
Inspection script to dump the Maersk autocomplete dropdown structure.
"""
import asyncio
import sys
import os
from dotenv import load_dotenv
from carriers.maersk_connector import MaerskConnector
from models.schemas import RateSearchRequest

load_dotenv()

# Clear proxy variables for local testing
for key in ["MAERSK_PROXY_USER", "MAERSK_PROXY_PASS", "BRIGHTDATA_PROXY_USER", "BRIGHTDATA_PROXY_PASS", "BRIGHTDATA_PROXY_SERVER"]:
    os.environ[key] = ""

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


async def main():
    print("[INSPECT] Initializing Maersk Connector...")
    connector = MaerskConnector()
    try:
        logged_in = await connector.login()
        if not logged_in:
            print("[INSPECT] Login failed!")
            return

        print("[INSPECT] Navigating to Booking page...")
        await connector.page.goto(connector.QUOTE_URL, wait_until="domcontentloaded", timeout=40000)
        await connector.page.wait_for_timeout(5000)

        # Find and fill Origin
        origin_selectors = [
            'input#mc-input-from',
            'input[placeholder*="from" i]',
            'input[placeholder*="Enter city or port" i]'
        ]
        origin_field = None
        for selector in origin_selectors:
            field = connector.page.locator(selector).first
            if await field.is_visible(timeout=4000):
                origin_field = field
                print(f"[INSPECT] Found field using: {selector}")
                break

        if not origin_field:
            print("[INSPECT] Origin field not found!")
            return

        print("[INSPECT] Clicking and typing 'Singapore'...")
        await origin_field.click()
        await origin_field.fill("")
        await connector.page.wait_for_timeout(500)
        await origin_field.type("Singapore", delay=100)
        
        print("[INSPECT] Waiting 5 seconds for suggestions to load...")
        await connector.page.wait_for_timeout(5000)

        print("[INSPECT] Running JS DOM dump inside shadow roots...")
        dom_dump = await connector.page.evaluate("""
            () => {
                function dumpShadowRoots(root, depth = 0) {
                    let results = [];
                    const indent = "  ".repeat(depth);
                    
                    // Look for elements with attributes or text that might suggest dropdown options
                    const elements = root.querySelectorAll('*');
                    elements.forEach(el => {
                        const tagName = el.tagName.toLowerCase();
                        const id = el.id ? '#' + el.id : '';
                        const className = el.className && typeof el.className === 'string' ? '.' + el.className.trim().replace(/\\s+/g, '.') : '';
                        const role = el.getAttribute('role') || '';
                        const text = (el.innerText || el.textContent || '').trim().split('\\n')[0].substring(0, 50);
                        
                        // We only want to log interesting elements (listboxes, options, list items, autocomplete results)
                        const isInteresting = role || tagName === 'li' || tagName === 'ul' || className.includes('suggest') || className.includes('result') || className.includes('option') || text.toLowerCase().includes('singapore');
                        
                        if (isInteresting && text) {
                            results.push(`${indent}<${tagName}${id}${className} role="${role}"> -> "${text}"`);
                        }
                        
                        if (el.shadowRoot) {
                            results.push(`${indent}[Shadow Root of <${tagName}${id}${className}>]`);
                            results = results.concat(dumpShadowRoots(el.shadowRoot, depth + 1));
                        }
                    });
                    return results;
                }
                return dumpShadowRoots(document);
            }
        """)

        print("\n=== DOM DUMP RESULTS ===")
        for line in dom_dump:
            print(line)
        print("========================\n")

        # Save screenshot
        await connector.page.screenshot(path="maersk_inspect_dropdown.png")
        print("[INSPECT] Screenshot saved to maersk_inspect_dropdown.png")

    except Exception as e:
        print(f"[INSPECT] Error: {e}")
    finally:
        await connector.close()

if __name__ == "__main__":
    asyncio.run(main())
