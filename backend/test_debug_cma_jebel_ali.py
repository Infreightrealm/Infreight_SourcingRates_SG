import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from models.schemas import RateSearchRequest
from carriers.cma_connector import CMAConnector

def safe_str(s: str) -> str:
    return s.encode('ascii', 'ignore').decode('ascii').strip().replace('\n', ' ')

async def debug_cma():
    print("=======================================================")
    print("   Debugging CMA CGM Jebel Ali Form Flow")
    print("=======================================================")

    req = RateSearchRequest(
        origin="SGSIN",
        destination="AEJEA",
        container_type="40HQ",
        container_types=["40HQ"],
        container_quantity=1,
        weight_per_container_kg=20000,
        cargo_description="Auto parts and Bearings",
        carriers=["CMA"]
    )

    connector = CMAConnector()
    print("1. Logging into CMA CGM...")
    logged_in = await connector.login()
    if not logged_in:
        print("❌ Login failed!")
        return

    print("2. Filling Origin: SGSIN...")
    origin_field = connector.page.locator('input[placeholder*="Name / Code / Port" i]').nth(0)
    await origin_field.click()
    await origin_field.fill("")
    await origin_field.type("SGSIN", delay=30)
    await connector.page.wait_for_timeout(2000)
    await connector._select_cma_dropdown_option("Origin", "SGSIN")

    print("3. Filling Destination: AEJEA...")
    dest_field = connector.page.locator('input[placeholder*="Name / Code / Port" i]').nth(1)
    await dest_field.click()
    await dest_field.fill("")
    await dest_field.type("AEJEA", delay=30)
    await connector.page.wait_for_timeout(2000)

    # Click PORT option first
    suggestion_sel = 'ul[role="listbox"] li, ul.options li, li[role="option"]'
    suggestions = connector.page.locator(suggestion_sel)
    count = await suggestions.count()
    print(f"Dropdown options for AEJEA ({count}):")
    for i in range(count):
        text = safe_str(await suggestions.nth(i).inner_text())
        print(f"   Option #{i+1}: {text}")

    port_option = None
    for i in range(count):
        text = (await suggestions.nth(i).inner_text()).upper()
        if "AEJEA" in text and "PORT" in text:
            port_option = suggestions.nth(i)
            break
            
    if port_option:
        print(f"Clicking PORT option: {safe_str(await port_option.inner_text())}")
        await connector._hover_and_click(port_option)
    
    await connector.page.wait_for_timeout(3000)

    # Inspect all visible text / alerts / banners on page
    full_text = await connector.page.inner_text('body')
    print("\n--- PAGE TEXT AFTER SELECTING AEJEA PORT ---")
    for line in full_text.splitlines():
        line_clean = safe_str(line)
        if any(w in line_clean.lower() for w in ["looking for", "ramp", "pod", "aejea", "aekhl", "aejfr", "aeklf", "solutions", "apologize"]):
            print(f"   [FOUND BANNER TEXT]: {line_clean}")
    print("-------------------------------------------\n")

    # Check for RAMP option
    await dest_field.click()
    await dest_field.fill("")
    await dest_field.type("AEJEA", delay=30)
    await connector.page.wait_for_timeout(2000)

    suggestions = connector.page.locator(suggestion_sel)
    count = await suggestions.count()
    for i in range(count):
        text = (await suggestions.nth(i).inner_text()).upper()
        if "AEJEA" in text and ("RAMP" in text or "DOOR" in text):
            print(f"Clicking RAMP option: {safe_str(await suggestions.nth(i).inner_text())}")
            await connector._hover_and_click(suggestions.nth(i))
            break

    await connector.page.wait_for_timeout(2500)

    # Check for POD dropdown after clicking RAMP
    print("\n--- INSPECTING POD DROPDOWN ---")
    pod_inputs = connector.page.locator('input, [role="combobox"], .el-select, span, label')
    pod_count = await pod_inputs.count()
    print(f"Total element candidates on form: {pod_count}")
    for i in range(pod_count):
        try:
            el = pod_inputs.nth(i)
            ph = safe_str(await el.get_attribute("placeholder") or "")
            val = safe_str(await el.get_attribute("value") or "")
            txt = safe_str(await el.inner_text())
            if any(k in f"{ph} {val} {txt}".lower() for k in ["pod", "select"]):
                tag = await el.evaluate('e => e.tagName')
                print(f"   Field #{i+1}: tag={tag} ph='{ph}' val='{val}' text='{txt}'")
        except: pass
    print("-------------------------------\n")

if __name__ == "__main__":
    asyncio.run(debug_cma())
