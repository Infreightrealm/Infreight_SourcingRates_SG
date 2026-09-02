import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from models.schemas import RateSearchRequest
from carriers.cma_connector import CMAConnector

async def debug_customer_account():
    print("=======================================================")
    print("   Debugging CMA CGM Customer Account Selectors")
    print("=======================================================")

    connector = CMAConnector()
    logged_in = await connector.login()
    if not logged_in:
        print("Login failed!")
        return

    page = connector.page
    
    # Fill Origin THLCH
    print("Filling Origin THLCH...")
    origin_field = page.locator('input[placeholder*="Name / Code / Port" i]').first
    await origin_field.click()
    await origin_field.fill("")
    await origin_field.type("THLCH", delay=30)
    await page.wait_for_timeout(2000)
    await connector._select_cma_dropdown_option("Origin", "THLCH")

    # Fill Destination PRSJU
    print("Filling Destination PRSJU...")
    dest_field = page.locator('input[placeholder*="Name / Code / Port" i]').nth(1)
    await dest_field.click()
    await dest_field.fill("")
    await dest_field.type("PRSJU", delay=30)
    await page.wait_for_timeout(2000)
    await connector._select_cma_dropdown_option("Destination", "PRSJU")

    await page.wait_for_timeout(3000)
    await page.screenshot(path="scratch/cma_customer_account_debug.png", full_page=True)

    # Inspect all inputs and select-like elements via Playwright
    inputs = page.locator('input, .el-select')
    count = await inputs.count()
    print(f"\n--- Found {count} input / el-select elements ---")
    for i in range(count):
        el = inputs.nth(i)
        try:
            placeholder = await el.get_attribute("placeholder") or ""
            text = (await el.inner_text()).strip()
            name = await el.get_attribute("name") or ""
            id_attr = await el.get_attribute("id") or ""
            cls = await el.get_attribute("class") or ""
            print(f"Index {i}: id='{id_attr}' name='{name}' placeholder='{placeholder}' text='{text[:50]}' class='{cls[:50]}'")
        except Exception:
            pass

    # Check for Customer Account / Role specifically via Playwright locators
    role_locs = [
        'input[placeholder*="Select" i]',
        'div:has-text("Customer account")',
        'div:has-text("Role")',
        '.el-select',
        '[role="combobox"]'
    ]
    print("\n--- Playwright Locator Diagnostics ---")
    for sel in role_locs:
        try:
            loc = page.locator(sel)
            c = await loc.count()
            print(f"Selector '{sel}': count={c}")
            if c > 0:
                for idx in range(min(c, 5)):
                    print(f"   [{idx}] visible={await loc.nth(idx).is_visible()} text='{(await loc.nth(idx).inner_text()).strip()[:60]}'")
        except Exception as e:
            print(f"Selector '{sel}' error: {e}")

    await connector.close()

if __name__ == "__main__":
    asyncio.run(debug_customer_account())
