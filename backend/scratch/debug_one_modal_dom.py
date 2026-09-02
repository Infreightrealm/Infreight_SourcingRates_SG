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

    print("Initializing ONEConnector for modal inspection...")
    connector = ONEConnector()
    await connector._init_browser()
    
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
        
        print("[DEBUG] Selected both ports! Waiting for modal to appear...")
        await connector.page.wait_for_timeout(5000)
        
        # Look for visible dialogs or modals in the DOM
        elements = await connector.page.evaluate("""() => {
            const results = [];
            // Find all elements
            const all = document.querySelectorAll('*');
            for (const el of all) {
                const style = window.getComputedStyle(el);
                // We care about elements that are visible, fixed/absolute, with high z-index or containing modal classes
                const isFixedOrAbsolute = style.position === 'fixed' || style.position === 'absolute';
                const hasHighZIndex = parseInt(style.zIndex) > 10;
                const isVisible = style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0';
                
                const className = el.className || '';
                const id = el.id || '';
                
                // Let's filter for items containing typical dialog/modal patterns
                const matchesPattern = /dialog|modal|popup|overlay|backdrop|loading|processing/i.test(className) || 
                                       /dialog|modal|popup|overlay|backdrop|loading|processing/i.test(id) || 
                                       el.getAttribute('role') === 'dialog';
                                       
                if (isVisible && (isFixedOrAbsolute || hasHighZIndex || matchesPattern)) {
                    // Check if it has text related to our modal
                    const text = el.innerText || '';
                    if (text.includes('FMC') || text.includes('Price Changes') || text.includes('Processing')) {
                        results.push({
                            tag: el.tagName,
                            id: id,
                            className: className,
                            role: el.getAttribute('role'),
                            zIndex: style.zIndex,
                            position: style.position,
                            textSnippet: text.substring(0, 150)
                        });
                    }
                }
            }
            return results;
        }""")
        
        print(f"[DEBUG] Found {len(elements)} matching modal elements:")
        for idx, el in enumerate(elements):
            print(f"  [{idx}] {el['tag']} (id='{el['id']}', class='{el['className']}', role='{el['role']}')")
            print(f"      z-index={el['zIndex']}, position={el['position']}")
            print(f"      Text: {el['textSnippet']}")
            print("-" * 50)
            
    except Exception as e:
        print(f"[DEBUG] FAILED with exception: {e}")
        
    finally:
        await connector.close()

if __name__ == "__main__":
    asyncio.run(run_debug())
